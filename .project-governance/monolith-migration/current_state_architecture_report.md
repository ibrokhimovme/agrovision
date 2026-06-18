# AgroVision — Current State Architecture Report (Microservices)

**Audit date:** 2026-06-18
**Method:** Static inspection of repository (`services/`, `shared/`, `frontend/`, `docker-compose*.yml`). No runtime tracing performed.
**Status:** Source of truth for migration planning. Supersedes assumptions in `project_architecture.md` memory where they conflict (see §8).

---

## 1. Service Inventory

| Service | Port | Owns DB | Migrations | Notable |
|---|---|---|---|---|
| api-gateway | 8000 | none | 0 | Pure reverse proxy + JWT verification, no business logic |
| identity-service | 8001 | identity_db | 2 | Only service that issues/signs JWTs |
| farm-service | 8002 | farm_db | 1 | |
| livestock-service | 8003 | livestock_db | 3 | Largest service; has unimplemented `_future` tables |
| inventory-service | 8004 | inventory_db | 1 | |
| finance-service | 8005 | finance_db | 2 | |
| notification-service | 8006 | notification_db | 1 | WebSocket manager, no auth on WS endpoint |
| reporting-service | 8007 | reporting_db (configured, unused) | 0 | Stateless; aggregates via direct HTTP to livestock/finance |

All 8 follow identical Clean Architecture layering: `app/api → app/application → app/domain ← app/infrastructure`, with per-service `migrations/`, `tests/{unit,integration}/`, `Dockerfile`, and a `requirements.txt` that just points at `shared/requirements-base.txt`.

## 2. Inter-Service Dependencies

- **Gateway proxy (sync, expected path):** all frontend traffic enters via api-gateway's `ROUTE_MAP` (full table in §5) and is forwarded to the owning service. Gateway adds `X-User-Id` / `X-User-Roles` / `X-Farm-Id` headers after JWT verification; downstream services trust these headers and do **not** re-verify the JWT.
- **Direct service-to-service HTTP (bypasses gateway) — the one real exception:** `reporting-service` has two HTTP clients —
  - `app/infrastructure/clients/livestock_client.py` → livestock-service (`get_batch`, `get_weight_metrics`, `get_feed_summary`, `get_mortality_summary`)
  - `app/infrastructure/clients/finance_client.py` → finance-service (`get_cost_summary`, `get_profit`, `get_sales_summary`)

  Both use `httpx.AsyncClient` against env-configured service URLs (mirroring the gateway's own config).
- **No other direct service-to-service HTTP calls exist.**

## 3. RabbitMQ Usage

- **Exchange:** `agrovision.events` (topic), declared identically (byte-for-byte) in every service's `app/infrastructure/messaging/publisher.py`, including api-gateway.
- **Publishing:** zero `publisher.publish(...)` calls found anywhere in application/use-case code. The publisher class is never instantiated or `.connect()`-ed in any service's `main.py` lifespan.
- **Consuming:** no consumer code, queue declarations, or consume loops exist anywhere in the repo.
- **Conclusion: RabbitMQ is fully scaffolded but entirely dead at runtime.** No event has ever been published or consumed in the current codebase.
- **Event schema inventory** (`shared/events/schemas.py`): 16 "active" schemas (FarmCreatedEvent, FarmUpdatedEvent, BatchOpenedEvent, BatchClosedEvent, FeedConsumedEvent, WaterConsumedEvent, MortalityRecordedEvent, VaccinationCompletedEvent, MedicationRecordedEvent, WeightSampledEvent, InventoryReceivedEvent, InventoryDispatchedEvent, InventoryUpdatedEvent, LowStockAlertEvent, ExpiryAlertEvent, ExpenseCreatedEvent, SaleRecordedEvent) + 8 `*_FutureRelease` placeholders (animal-level tracking, slaughter, disease incidents, treatments, revenue, payments, sales orders) explicitly unimplemented.
- **Aspirational-but-missing consumer:** code comments in `identity-service/app/domain/models/user.py` and `livestock-service/app/domain/models/animal.py` claim `farms_ref` is "populated via FarmCreatedEvent consumer" — no such consumer exists. `farms_ref` is a denormalized read-model table duplicated in both identity-service and livestock-service, currently unpopulated/stale by construction.

## 4. Database Usage

- Single Postgres **instance**, 7 logical **databases** (one per service that owns data; api-gateway and reporting-service own none in practice). Created via `infrastructure/postgres/init.sql`.
- Redis: single instance, separate DB index per service (0 gateway, 1 farm, 2 livestock, 3 inventory, 4 finance, 5 notification, 6 reporting).
- Table inventory by service:
  - identity_db: users, roles, role_permissions, individual_permissions, farms_ref (duplicate/stale, see §3)
  - farm_db: farms, buildings, sections
  - livestock_db: batches, weight_samplings, mortality_records, farms_ref (duplicate/stale), animals_future (unimplemented), feed_consumptions, vaccination_records, vaccination_schedules, medication_records, daily_health_logs, disease_incidents_future (unimplemented)
  - inventory_db: warehouses, stock_items, stock_batches, stock_movements
  - finance_db: expenses, sales_orders, sales_order_lines, payments, sale_records, customers
  - notification_db: notifications
  - reporting_db: no tables, no migrations — service is stateless

## 5. API Contracts

- **Gateway `ROUTE_MAP`** (`services/api-gateway/app/api/v1/router.py`):

| Prefix | Target Service |
|---|---|
| /auth, /users, /roles | identity-service |
| /farms, /buildings | farm-service |
| /animals, /batches, /vaccinations, /vaccination-schedules, /health-records, /mortality, /slaughter | livestock-service |
| /warehouses, /stock-items, /inventory | inventory-service |
| /expenses, /sales, /profit, /revenue, /payments | finance-service |
| /notifications | notification-service |
| /reports | reporting-service |

  Note: `/slaughter`, `/revenue`, `/payments` are pre-wired routes with no corresponding endpoint module yet (future features).
- **Shared response contracts** (`shared/contracts/api_standards.py`): `APIResponse`, `PaginatedResponse`, `PaginationMeta`/`PaginationParams`, `ErrorResponse` — used identically by all 8 services.
- **Shared exceptions** (`shared/exceptions`): `EntityNotFoundError`, `BusinessRuleViolationError`, `DuplicateEntityError`, `AuthenticationError` — used identically by all 8 services.

## 6. Shared Packages

`shared/` (repo root, included in every service's Docker build context, `PYTHONPATH=/app`):
- `shared/models/base.py` — `Base`, `UUIDPrimaryKeyMixin`, `AuditMixin` (every service's ORM models inherit these)
- `shared/exceptions/__init__.py` — common exception hierarchy
- `shared/contracts/api_standards.py` — response envelopes
- `shared/events/schemas.py` — event schema definitions (currently unused at runtime, see §3)
- `shared/utils/pagination.py`, `shared/utils/datetime_utils.py`

## 7. Authentication

- **Centralized at the gateway**: `services/api-gateway/app/middleware/auth.py` is the sole JWT-verification point. Downstream services trust `X-User-Id`/`X-User-Roles` headers and do not re-verify the JWT (by design, per code comment referencing ADR-002).
- identity-service is the only service that issues/signs JWTs and owns `passlib`/`python-jose`.
- Other services carry a vestigial `JWT_SECRET_KEY`/`JWT_ALGORITHM` setting in `core/config.py` (copy-pasted template) but never call `jwt.decode`/`jwt.encode` — dead config, safe to drop.
- **Known gap (carry into monolith as a tracked fix, not a blocker):** notification-service's WebSocket endpoint (`/ws/{user_id}`) documents a `token` query param but never validates it. Not currently exposed via gateway/nginx and unused by the frontend (frontend has no WS client at all — `notificationService.ts` uses REST polling).

## 8. Frontend Dependencies

- Single shared axios instance (`frontend/src/services/api.ts`), `baseURL` from `VITE_API_BASE_URL` (defaults to `/api/v1`), with a 401 interceptor that calls `/auth/refresh`.
- Every other service file (`inventoryService.ts`, `batchService.ts`, `userService.ts`, `notificationService.ts`, `reportService.ts`) reuses this single client.
- **Confirmed: the frontend never talks to a service port directly — all calls go through the gateway.** This means the frontend requires zero changes for the gateway-facing contract as long as the monolith preserves the same `/api/v1/...` paths and response envelopes.
- No WebSocket client exists in the frontend, despite notification-service exposing one — real-time delivery is currently unused/dead on the client side.

## 9. docker-compose Topology

- Infra containers: `postgres` (single instance, all DBs), `redis`, `rabbitmq` (single vhost `agrovision`).
- App containers: all 8 services, built from repo root context using `services/<name>/Dockerfile`.
- `frontend` (own Dockerfile) and `nginx` (port 80, serves frontend + proxies to gateway).
- `api-gateway` does not `depends_on` the 7 downstream services — no startup-order guarantee between them (calls are made at request time via env-configured URLs).
- `docker-compose.dev.yml` is a pure override: bind-mounts each service's `app/` + shared `shared/` for hot reload, `uvicorn --reload`. No additional containers.

## 10. Headline Implication for Migration

The "microservices" architecture is **structural scaffolding with almost no live cross-service runtime coupling**:
- RabbitMQ pub/sub: 100% dead code — nothing to preserve behaviorally, only the schema *definitions* are worth keeping (as an internal contract, optionally).
- Real network coupling other than the gateway proxy: exactly two HTTP client calls, both from reporting-service into livestock-service and finance-service.
- Each service's internal layering already maps 1:1 onto sensible monolith module boundaries.
- Auth is already centralized — carries over as a single middleware in the monolith with no design change.
- Frontend already only knows about one base URL — no frontend rewrite required structurally, only response-shape compatibility must be preserved.

This significantly lowers migration risk: the hard problem is **database consolidation** (7 DBs → fewer) and **resolving the `farms_ref` duplication**, not untangling live event-driven behavior.

# AgroVision — Target Architecture (Modular Monolith)

**Status:** DESIGN ONLY. Not implemented. No code has been written against this design yet.
**Depends on:** `current_state_architecture_report.md` (read first).

---

## 1. Goal

Replace 8 independently-deployed FastAPI services + RabbitMQ + 7 Postgres databases with **one FastAPI application**, internally organized into modules with the same bounded-context boundaries the services already use, while preserving every existing API path, request/response contract, and business rule.

## 2. Module Map

One Python package, e.g. `app/`, with one module per existing service:

```
app/
  identity/      (was identity-service)
  farm/          (was farm-service)
  poultry/       (was livestock-service — renamed to match BRD/SRS domain language)
  inventory/     (was inventory-service)
  finance/       (was finance-service)
  reporting/     (was reporting-service)
  notifications/ (was notification-service)
  shared/        (was repo-root shared/ — unchanged, becomes an internal package)
  gateway/       (was api-gateway — becomes the app's auth middleware + top-level router, not a proxy)
  main.py        (single FastAPI() instance, mounts each module's router)
```

Each module keeps its **internal** layering unchanged: `api/` (FastAPI router), `application/` (use cases), `domain/` (models, repository interfaces), `infrastructure/` (repository impls, infra clients). This is a lift, not a rewrite — see §6.

**Module boundary rule:** a module may only import another module's `api`-layer DTOs or a small set of explicitly exported domain interfaces — never another module's `infrastructure` or ORM models directly. This is the in-process analogue of "services only talk over HTTP" and is what keeps the monolith "modular" rather than a ball of mud. Enforce with import-linter or a simple custom lint rule in M6.

## 3. Database Strategy

- **Single Postgres database**, one schema per module (`identity`, `farm`, `poultry`, `inventory`, `finance`, `notifications`; `reporting` has no schema, same as today). This preserves logical separation and makes a future re-split easier, while collapsing 7 connection pools into 1.
- **Alembic:** one consolidated `alembic` setup with per-module migration directories (or a single linear history with module-prefixed revision names) — decided in M4, not now.
- **`farms_ref` duplication resolved:** since identity and poultry modules will live in the same process, the denormalized `farms_ref` read-model is no longer needed — those modules can either (a) query the `farm` module's repository directly through its public interface, or (b) keep a thin read-only projection if cross-schema joins are undesirable. Decision deferred to `migration_decisions.md`.

## 4. Inter-Module Communication

- **Replaces gateway proxy:** the single FastAPI app's router includes each module's router directly under the same `/api/v1/...` prefixes currently in the gateway's `ROUTE_MAP` — external API surface is unchanged.
- **Replaces reporting-service's HTTP clients:** `LivestockClient`/`FinanceClient` (currently `httpx` calls) become direct in-process calls into `poultry`'s and `finance`'s application-layer use cases (or a small read-only query interface each module exports). No network hop, same data.
- **Replaces RabbitMQ (optional, since it's currently dead code — see audit §3):** if event-driven behavior is wanted in the monolith (e.g. to finally let `notifications` react to domain events), implement a minimal **in-process event bus** (sync dispatch, in the `shared` module) using the existing `shared/events/schemas.py` schemas as the event contract. This is opt-in scope — not required to reach a working monolith. Tracked as M3, can be descoped without blocking M4–M8.

## 5. Auth

- Carries over almost unchanged: JWT verification becomes a single FastAPI dependency/middleware applied to the whole app (today it's already centralized in the gateway — this is the lowest-risk part of the migration).
- Per-module vestigial `JWT_SECRET_KEY` configs (currently dead in farm/livestock/inventory/finance/notification/reporting) are deleted — only one auth config remains.
- The notification-service WebSocket auth gap (token query param documented but never checked) should be fixed as part of the monolith cutover, not carried forward silently.

## 6. What Does NOT Change

- Clean-architecture layering inside each module (api/application/domain/infrastructure).
- Shared contracts (`APIResponse`, `PaginatedResponse`, `ErrorResponse`) and shared exceptions — these already live in `shared/` and need no change.
- External API paths and response shapes — frontend requires no changes (confirmed in audit §8: frontend only ever calls the gateway base URL).
- Business logic, validation rules, and domain models — moved, not rewritten.

## 7. Deployment Shape (target)

- One Docker image / one container running `uvicorn app.main:app`, one Postgres container, one Redis container (single DB index, namespaced keys per module if needed). Nginx still serves frontend + proxies to the single app.
- RabbitMQ container removed only after M3 decision is finalized and verified (anti-destruction rule — not before M7).

## 8. Open Decisions (to be resolved in `migration_decisions.md` before M2 starts)

1. Keep RabbitMQ/event-bus concept as in-process pub/sub, or drop entirely since it's unused today?
2. `farms_ref` duplication: direct cross-module call vs. retained read projection?
3. Single Alembic history vs. per-module migration chains?
4. Rename `livestock` → `poultry` (matches BRD/SRS Uzbek domain language) — confirm before any code references change.

# AgroVision — Development Backlog
**Authority:** Flat task list derived from master_roadmap.md. Updated after every task completion.  
**Version:** 1.0 | **Created:** 2026-06-16 | **Last Updated:** 2026-06-16

---

## Backlog Statistics

```
Total Tasks:        ~130
COMPLETED:           0  (Phase 0 and 1 verified via CH-001–CH-005, pre-dates this backlog)
IN_PROGRESS:         0
NOT_STARTED:       ~130
BLOCKED:             0
DEFERRED:           17  (see FUTURE_RELEASE section)
```

---

## PHASE 0 — Repository Validation `VERIFIED_COMPLETE`

All deliverables completed via CH-001 – CH-004 (pre-backlog). Evidence in project_memory.md.

---

## PHASE 1 — Runtime Readiness `VERIFIED_COMPLETE`

All deliverables completed via CH-005 (pre-backlog). Evidence in project_memory.md.

---

## PHASE 2 — Identity Service `NOT_STARTED`

### F-02-01: Database Schema and Migrations

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-02-01-01 | Alembic migration: `users` table | NOT_STARTED | — |
| T-02-01-02 | Alembic migration: `roles`, `role_permissions` tables | NOT_STARTED | — |
| T-02-01-03 | Alembic migration: `individual_permissions` table | NOT_STARTED | — |
| T-02-01-04 | Alembic migration: `farms_ref` table (read model in identity_db) | NOT_STARTED | — |
| T-02-01-05 | Alembic migration: `user_roles` association table | NOT_STARTED | — |
| T-02-01-06 | Seed script: 8 system roles (farm_owner, farm_director, farm_manager, veterinarian, accountant, warehouse_manager, sales_personnel, farm_worker) | NOT_STARTED | — |
| T-02-01-07 | Seed script: default admin/superuser | NOT_STARTED | — |

### F-02-02: Repository Implementation

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-02-02-01 | `AbstractUserRepository` interface in `domain/repositories/user_repository.py` | NOT_STARTED | — |
| T-02-02-02 | `SQLAlchemyUserRepository` in `infrastructure/database/repositories/` | NOT_STARTED | — |
| T-02-02-03 | Implement `get_by_email()`, `get_by_id()`, `list_users()` | NOT_STARTED | — |
| T-02-02-04 | Implement `increment_failed_attempts()`, `lock_account()`, `reset_failed_attempts()` | NOT_STARTED | — |
| T-02-02-05 | Implement `create_user()` with bcrypt hash | NOT_STARTED | — |
| T-02-02-06 | Implement `update_user()` | NOT_STARTED | — |

### F-02-03: Use Cases

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-02-03-01 | Wire `AuthenticateUserUseCase.execute()` to real SQLAlchemy repository | NOT_STARTED | — |
| T-02-03-02 | Implement `RefreshTokenUseCase` | NOT_STARTED | — |
| T-02-03-03 | Implement `LogoutUseCase` (Redis token blacklist) | NOT_STARTED | — |
| T-02-03-04 | Implement `CreateUserUseCase` | NOT_STARTED | — |
| T-02-03-05 | Implement `GetCurrentUserUseCase` | NOT_STARTED | — |

### F-02-04: API Endpoints

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-02-04-01 | `POST /api/v1/auth/login` | NOT_STARTED | — |
| T-02-04-02 | `POST /api/v1/auth/refresh` | NOT_STARTED | — |
| T-02-04-03 | `POST /api/v1/auth/logout` | NOT_STARTED | — |
| T-02-04-04 | `GET /api/v1/users/me` | NOT_STARTED | — |
| T-02-04-05 | `POST /api/v1/users/` | NOT_STARTED | — |
| T-02-04-06 | `GET /api/v1/users/` | NOT_STARTED | — |
| T-02-04-07 | `GET /api/v1/users/{id}` | NOT_STARTED | — |
| T-02-04-08 | `PATCH /api/v1/users/{id}` | NOT_STARTED | — |
| T-02-04-09 | `GET /api/v1/roles/` | NOT_STARTED | — |

### F-02-05: API Gateway JWT Middleware

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-02-05-01 | Complete JWT verification middleware (signature + expiry) | NOT_STARTED | — |
| T-02-05-02 | Forward `X-User-Id`, `X-User-Roles`, `X-Farm-Id` headers | NOT_STARTED | — |
| T-02-05-03 | Return 401 on invalid/expired token | NOT_STARTED | — |
| T-02-05-04 | Redis token blacklist check | NOT_STARTED | — |

### F-02-06: Tests

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-02-06-01 | Unit tests: `AuthenticateUserUseCase` | NOT_STARTED | — |
| T-02-06-02 | Unit tests: `RefreshTokenUseCase`, `LogoutUseCase` | NOT_STARTED | — |
| T-02-06-03 | Integration tests: auth endpoints | NOT_STARTED | — |
| T-02-06-04 | Integration tests: user CRUD endpoints | NOT_STARTED | — |

---

## PHASE 3 — Frontend Foundation `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-03-01-01 | Install and configure React Router v6 | NOT_STARTED | — |
| T-03-01-02 | `ProtectedRoute` component | NOT_STARTED | — |
| T-03-01-03 | Login page (Uzbek labels) | NOT_STARTED | — |
| T-03-01-04 | Connect Login to identity-service API | NOT_STARTED | — |
| T-03-01-05 | JWT token storage (secure, not localStorage) | NOT_STARTED | — |
| T-03-01-06 | Auto token refresh on 401 | NOT_STARTED | — |
| T-03-02-01 | Main layout: sidebar + header + content | NOT_STARTED | — |
| T-03-02-02 | Sidebar navigation in Uzbek | NOT_STARTED | — |
| T-03-02-03 | Mobile-responsive layout (360px min) | NOT_STARTED | — |
| T-03-02-04 | Header: user name, farm name, logout | NOT_STARTED | — |
| T-03-03-01 | Axios instance with JWT interceptor | NOT_STARTED | — |
| T-03-03-02 | Global error handler (401, 403) | NOT_STARTED | — |
| T-03-03-03 | Redux auth slice | NOT_STARTED | — |
| T-03-03-04 | Loading spinner component | NOT_STARTED | — |
| T-03-03-05 | Toast notification component | NOT_STARTED | — |

---

## PHASE 4 — Poultry Batch Management `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-04-01-01 | Migration: `farms`, `buildings`, `sections` (farm_db) | NOT_STARTED | — |
| T-04-01-02 | `AbstractFarmRepository` + SQLAlchemy implementation | NOT_STARTED | — |
| T-04-01-03 | `POST /api/v1/farms/` | NOT_STARTED | — |
| T-04-01-04 | `GET /api/v1/farms/` | NOT_STARTED | — |
| T-04-01-05 | `POST /api/v1/farms/{id}/buildings/` | NOT_STARTED | — |
| T-04-01-06 | `POST /api/v1/buildings/{id}/sections/` | NOT_STARTED | — |
| T-04-01-07 | `GET /api/v1/farms/{id}/sections/` | NOT_STARTED | — |
| T-04-01-08 | Publish `FarmCreatedEvent` | NOT_STARTED | — |
| T-04-02-01 | Migration: `batches`, `farms_ref` (livestock_db) | NOT_STARTED | — |
| T-04-02-02 | Migration: `weight_samplings`, `mortality_records` | NOT_STARTED | — |
| T-04-02-03 | Migration: `vaccination_records`, `vaccination_schedules` | NOT_STARTED | — |
| T-04-02-04 | Migration: `medication_records`, `daily_health_logs` | NOT_STARTED | — |
| T-04-03-01 | `AbstractBatchRepository` interface | NOT_STARTED | — |
| T-04-03-02 | `SQLAlchemyBatchRepository` | NOT_STARTED | — |
| T-04-03-03 | `OpenBatchUseCase` | NOT_STARTED | — |
| T-04-03-04 | `ActivateBatchUseCase` (quarantine → active, 7-day min) | NOT_STARTED | — |
| T-04-03-05 | `CloseBatchUseCase` → publish `BatchClosedEvent` | NOT_STARTED | — |
| T-04-03-06 | `GetBatchUseCase` | NOT_STARTED | — |
| T-04-03-07 | `ListBatchesUseCase` (paginated, filterable) | NOT_STARTED | — |
| T-04-04-01 | `POST /api/v1/batches/` | NOT_STARTED | — |
| T-04-04-02 | `GET /api/v1/batches/` | NOT_STARTED | — |
| T-04-04-03 | `GET /api/v1/batches/{id}` | NOT_STARTED | — |
| T-04-04-04 | `PATCH /api/v1/batches/{id}` | NOT_STARTED | — |
| T-04-04-05 | `POST /api/v1/batches/{id}/activate` | NOT_STARTED | — |
| T-04-04-06 | `POST /api/v1/batches/{id}/close` | NOT_STARTED | — |
| T-04-05-01 | Frontend: batch list page | NOT_STARTED | — |
| T-04-05-02 | Frontend: open new batch form (Uzbek) | NOT_STARTED | — |
| T-04-05-03 | Frontend: batch detail page | NOT_STARTED | — |
| T-04-05-04 | Frontend: activate batch button | NOT_STARTED | — |
| T-04-05-05 | Frontend: close batch dialog | NOT_STARTED | — |
| T-04-06-01 | Unit tests: batch use cases | NOT_STARTED | — |
| T-04-06-02 | Unit test: state machine | NOT_STARTED | — |
| T-04-06-03 | Integration tests: batch endpoints | NOT_STARTED | — |

---

## PHASE 5 — Feed Consumption `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-05-01-01 | `FeedConsumption` domain model | NOT_STARTED | — |
| T-05-01-02 | Fields: batch_id, farm_id, feed_date, feed_type, quantity_kg, water_liters, age_days, recorded_by | NOT_STARTED | — |
| T-05-01-03 | Migration: `feed_consumptions` table | NOT_STARTED | — |
| T-05-02-01 | `RecordFeedConsumptionUseCase` | NOT_STARTED | — |
| T-05-02-02 | `GetBatchFeedHistoryUseCase` | NOT_STARTED | — |
| T-05-02-03 | FCR calculation helper | NOT_STARTED | — |
| T-05-02-04 | Publish `FeedConsumedEvent` | NOT_STARTED | — |
| T-05-03-01 | `POST /api/v1/batches/{id}/feed/` | NOT_STARTED | — |
| T-05-03-02 | `GET /api/v1/batches/{id}/feed/` | NOT_STARTED | — |
| T-05-03-03 | `GET /api/v1/batches/{id}/feed/summary` | NOT_STARTED | — |
| T-05-04-01 | Frontend: feed recording form | NOT_STARTED | — |
| T-05-04-02 | Frontend: water field on feed form | NOT_STARTED | — |
| T-05-04-03 | Frontend: feed history table | NOT_STARTED | — |

---

## PHASE 6 — Mortality Tracking `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-06-01 | `RecordMortalityUseCase` | NOT_STARTED | — |
| T-06-02 | `GetMortalityHistoryUseCase` | NOT_STARTED | — |
| T-06-03 | `POST /api/v1/batches/{id}/mortality/` | NOT_STARTED | — |
| T-06-04 | `GET /api/v1/batches/{id}/mortality/` | NOT_STARTED | — |
| T-06-05 | `GET /api/v1/batches/{id}/mortality/summary` | NOT_STARTED | — |
| T-06-06 | Publish `MortalityRecordedEvent` | NOT_STARTED | — |
| T-06-07 | Frontend: mortality form | NOT_STARTED | — |
| T-06-08 | Frontend: mortality stats cards | NOT_STARTED | — |
| T-06-09 | Unit tests | NOT_STARTED | — |
| T-06-10 | Integration tests | NOT_STARTED | — |

---

## PHASE 7 — Vaccination Management `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-07-01 | `CreateVaccinationScheduleUseCase` | NOT_STARTED | — |
| T-07-02 | `GenerateBatchVaccinationPlanUseCase` | NOT_STARTED | — |
| T-07-03 | `RecordVaccinationUseCase` | NOT_STARTED | — |
| T-07-04 | `MarkOverdueVaccinationsUseCase` | NOT_STARTED | — |
| T-07-05 | `POST /api/v1/vaccination-schedules/` | NOT_STARTED | — |
| T-07-06 | `GET /api/v1/batches/{id}/vaccinations/` | NOT_STARTED | — |
| T-07-07 | `PATCH /api/v1/vaccinations/{id}/complete` | NOT_STARTED | — |
| T-07-08 | Publish `VaccinationCompletedEvent` | NOT_STARTED | — |
| T-07-09 | Frontend: vaccination calendar | NOT_STARTED | — |
| T-07-10 | Frontend: execute vaccination button | NOT_STARTED | — |
| T-07-11 | Unit + integration tests | NOT_STARTED | — |

---

## PHASE 8 — Weight Sampling `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-08-01 | `RecordWeightSamplingUseCase` | NOT_STARTED | — |
| T-08-02 | `GetGrowthMetricsUseCase` (ADG, FCR) | NOT_STARTED | — |
| T-08-03 | `POST /api/v1/batches/{id}/weight/` | NOT_STARTED | — |
| T-08-04 | `GET /api/v1/batches/{id}/weight/` | NOT_STARTED | — |
| T-08-05 | `GET /api/v1/batches/{id}/weight/metrics` | NOT_STARTED | — |
| T-08-06 | Publish `WeightSampledEvent` | NOT_STARTED | — |
| T-08-07 | Frontend: weight form | NOT_STARTED | — |
| T-08-08 | Frontend: ADG metric card | NOT_STARTED | — |
| T-08-09 | Unit + integration tests | NOT_STARTED | — |

---

## PHASE 9 — Inventory Integration `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-09-01 | Migration: `warehouses`, `stock_items`, `stock_batches`, `stock_movements` (inventory_db) | NOT_STARTED | — |
| T-09-02 | `AbstractStockRepository` + SQLAlchemy implementation | NOT_STARTED | — |
| T-09-03 | `ReceiveStockUseCase` (FIFO/FEFO) | NOT_STARTED | — |
| T-09-04 | `DispatchStockUseCase` | NOT_STARTED | — |
| T-09-05 | `GetStockLevelUseCase` | NOT_STARTED | — |
| T-09-06 | Low-stock alert → publish `LowStockAlertEvent` | NOT_STARTED | — |
| T-09-07 | Expiry alert → publish `ExpiryAlertEvent` | NOT_STARTED | — |
| T-09-08 | RabbitMQ consumer: feed/vaccination/medication events → auto-dispatch stock | NOT_STARTED | — |
| T-09-09 | `POST /api/v1/warehouses/` | NOT_STARTED | — |
| T-09-10 | `POST /api/v1/stock-items/` | NOT_STARTED | — |
| T-09-11 | `POST /api/v1/stock-items/{id}/receive` | NOT_STARTED | — |
| T-09-12 | `GET /api/v1/stock-items/` | NOT_STARTED | — |
| T-09-13 | `GET /api/v1/stock-items/{id}/movements` | NOT_STARTED | — |
| T-09-14 | Frontend: inventory list page | NOT_STARTED | — |
| T-09-15 | Frontend: receive stock form | NOT_STARTED | — |
| T-09-16 | Unit + integration tests | NOT_STARTED | — |

---

## PHASE 10 — Cost Tracking `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-10-01 | Migration: `expenses`, `sale_records`, `farms_ref` (finance_db) | NOT_STARTED | — |
| T-10-02 | `Expense` domain model | NOT_STARTED | — |
| T-10-03 | Consumer: `batch.feed.consumed` → FEED expense | NOT_STARTED | — |
| T-10-04 | Consumer: `batch.vaccination.completed` → VACCINE expense | NOT_STARTED | — |
| T-10-05 | Consumer: `batch.medication.recorded` → MEDICINE expense | NOT_STARTED | — |
| T-10-06 | `RecordManualExpenseUseCase` | NOT_STARTED | — |
| T-10-07 | `GetBatchCostSummaryUseCase` | NOT_STARTED | — |
| T-10-08 | `POST /api/v1/expenses/` | NOT_STARTED | — |
| T-10-09 | `GET /api/v1/batches/{id}/expenses` | NOT_STARTED | — |
| T-10-10 | `GET /api/v1/batches/{id}/cost-summary` | NOT_STARTED | — |
| T-10-11 | Frontend: cost summary card on batch detail | NOT_STARTED | — |
| T-10-12 | Unit + integration tests | NOT_STARTED | — |

---

## PHASE 11 — Sales Management `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-11-01 | `SaleRecord` domain model | NOT_STARTED | — |
| T-11-02 | Migration: `sale_records` table | NOT_STARTED | — |
| T-11-03 | `RecordSaleUseCase` | NOT_STARTED | — |
| T-11-04 | `POST /api/v1/batches/{id}/sales` | NOT_STARTED | — |
| T-11-05 | `GET /api/v1/batches/{id}/sales` | NOT_STARTED | — |
| T-11-06 | Publish `SaleRecordedEvent` | NOT_STARTED | — |
| T-11-07 | Frontend: sale record form | NOT_STARTED | — |
| T-11-08 | Frontend: sales list on batch detail | NOT_STARTED | — |
| T-11-09 | Unit + integration tests | NOT_STARTED | — |

---

## PHASE 12 — Profit Analysis `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-12-01 | `CalculateBatchProfitUseCase` | NOT_STARTED | — |
| T-12-02 | `GET /api/v1/batches/{id}/profit` | NOT_STARTED | — |
| T-12-03 | Consumer: `batch.batch.closed` → auto-calculate profit | NOT_STARTED | — |
| T-12-04 | Frontend: profit card on closed batch | NOT_STARTED | — |
| T-12-05 | Frontend: cost vs revenue breakdown | NOT_STARTED | — |
| T-12-06 | Unit + integration tests | NOT_STARTED | — |

---

## PHASE 13 — Notifications `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-13-01 | Migration: `notifications` table (notification_db) | NOT_STARTED | — |
| T-13-02 | Consumer: vaccination overdue → notification | NOT_STARTED | — |
| T-13-03 | Consumer: `inventory.alert.low_stock` → notification | NOT_STARTED | — |
| T-13-04 | Consumer: `batch.mortality.recorded` (above threshold) → notification | NOT_STARTED | — |
| T-13-05 | WebSocket endpoint `ws://host/api/v1/ws/{user_id}` | NOT_STARTED | — |
| T-13-06 | `GET /api/v1/notifications/` | NOT_STARTED | — |
| T-13-07 | `PATCH /api/v1/notifications/{id}/read` | NOT_STARTED | — |
| T-13-08 | Frontend: notification bell in header | NOT_STARTED | — |
| T-13-09 | Frontend: notification drawer | NOT_STARTED | — |
| T-13-10 | Unit + integration tests | NOT_STARTED | — |

---

## PHASE 14 — Reporting `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-14-01 | Reporting service: API client for livestock-service | NOT_STARTED | — |
| T-14-02 | Reporting service: API client for finance-service | NOT_STARTED | — |
| T-14-03 | `GenerateBatchReportUseCase` | NOT_STARTED | — |
| T-14-04 | Batch performance card (FCR, ADG, mortality rate, cost, profit) | NOT_STARTED | — |
| T-14-05 | `GET /api/v1/reports/batch/{id}` | NOT_STARTED | — |
| T-14-06 | `GET /api/v1/reports/batch/{id}/pdf` | NOT_STARTED | — |
| T-14-07 | Frontend: "Hisobot" button on batch detail | NOT_STARTED | — |
| T-14-08 | Frontend: report preview page | NOT_STARTED | — |
| T-14-09 | Unit + integration tests | NOT_STARTED | — |

---

## PHASE 15 — MVP Stabilization `NOT_STARTED`

| Task ID | Task | Status | Completed |
|---------|------|--------|-----------|
| T-15-01 | E2E test: full primary workflow | NOT_STARTED | — |
| T-15-02 | Performance test: report generation < 5s | NOT_STARTED | — |
| T-15-03 | Security review: JWT + OWASP Top 10 | NOT_STARTED | — |
| T-15-04 | Uzbek language audit (all UI) | NOT_STARTED | — |
| T-15-05 | Mobile responsiveness test (360px) | NOT_STARTED | — |
| T-15-06 | Audit trail verification | NOT_STARTED | — |
| T-15-07 | Backup and restore test | NOT_STARTED | — |
| T-15-08 | User guide (Uzbek) | NOT_STARTED | — |
| T-15-09 | Deployment guide | NOT_STARTED | — |
| T-15-10 | UAT test script | NOT_STARTED | — |

---

## DEFERRED — FUTURE_RELEASE Items

The following will not be implemented in MVP. Require explicit approval to activate.

| ID | Feature | Target | Reason |
|----|---------|--------|--------|
| DR-01 | Email + SMS notifications | Phase 2 | Provider integration; WebSocket sufficient for MVP |
| DR-02 | Scheduled PDF/Excel report delivery | Phase 2 | On-demand sufficient for MVP |
| DR-03 | Advanced sales orders + customer registry | Phase 2 | Simple SaleRecord covers MVP |
| DR-04 | Debtor/creditor (AR/AP) management | Phase 2 | Simple payment_status covers MVP |
| DR-05 | Transport management (SF-19) | Phase 2 | Outside primary batch workflow |
| DR-06 | Formal slaughter module (SF-20) | Phase 2 | batch.batch.closed with reason=slaughter covers MVP |
| DR-07 | Workforce scheduling | Phase 2 | Outside primary batch workflow |
| DR-08 | Formal DiseaseIncident case management | Phase 2 | DailyHealthLog + MedicationRecord sufficient |
| DR-09 | Individual animal tracking (Animal model) | Phase 3+ | No RFID infrastructure; batch management sufficient |
| DR-10 | Cattle / sheep / goat management | Phase 3+ | MVP is poultry only |
| DR-11 | RFID / ear tag scanning | Phase 3+ | No infrastructure |
| DR-12 | Dairy operations | Phase 3+ | Separate domain |
| DR-13 | IoT sensor integration | Phase 3+ | BRD §6.3 future scope |
| DR-14 | Government inspection workflows | Phase 3+ | No regulatory API specs |
| DR-15 | Multi-language support (Russian, English) | Phase 3+ | Uzbek only for MVP |
| DR-16 | SSO / enterprise identity | Phase 3+ | Not required for MVP farm size |
| DR-17 | Historical archiving UI (SF-24) | Phase 3+ | Data retained per NFR; UI deferred |

---

## Completed Items Log

*(Updated after every task completion)*

| Date | Task ID | Description | Phase | Files Changed |
|------|---------|-------------|-------|---------------|
| 2026-06-16 | PRE-BACKLOG | Repository validation, governance, ADR records (CH-001–CH-004) | P-00 | See project_memory.md CH-001–CH-004 |
| 2026-06-16 | PRE-BACKLOG | Runtime readiness, docker infrastructure (CH-005) | P-01 | See project_memory.md CH-005 |

---

*development_backlog.md — AgroVision Task Tracker v1.0*  
*Created: 2026-06-16 | Append-only log. Never delete history.*

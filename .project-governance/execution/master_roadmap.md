# AgroVision — Master Development Roadmap
**Authority:** This is the canonical execution plan for AgroVision MVP.  
**Scope:** Poultry Production Management Platform — Uzbekistan  
**Architecture:** ADR-002 (microservices) + ADR-003 (MVP scope)  
**Version:** 1.0 | **Created:** 2026-06-16

---

## Roadmap Overview

Primary workflow driving all phases:
```
Batch Arrival → Feeding → Water → Vaccination → Medication
→ Mortality → Growth (Weight) → Batch Close → Cost → Sale → Profit
```

Total phases: 16 (Phase 0 – Phase 15)

---

## Phase Dependency Graph

```
P-00 Repository Validation ──► P-01 Runtime Readiness
                                      │
                                      ▼
                               P-02 Identity Service
                                   │         │
                                   ▼         ▼
                         P-03 Frontend    P-04 Poultry Batch
                          Foundation         Management
                               │                │
                               │         ┌──────┼──────┬──────────┐
                               │         ▼      ▼      ▼          ▼
                               │      P-05   P-06   P-07        P-08
                               │      Feed  Mortlty  Vacc.    Weight
                               │      Cons.  Track.  Mgmt.   Sampling
                               │         │      │      │          │
                               │         └──────┴──────┴──────────┘
                               │                      │
                               │                      ▼
                               │              P-09 Inventory
                               │               Integration
                               │                      │
                               │                      ▼
                               │              P-10 Cost Tracking
                               │                      │
                               │                      ▼
                               │              P-11 Sales Management
                               │                      │
                               │                      ▼
                               │              P-12 Profit Analysis
                               │                  │        │
                               │                  ▼        ▼
                               └──────────► P-13 Notif. P-14 Reporting
                                                   │         │
                                                   └────┬────┘
                                                        ▼
                                               P-15 MVP Stabilization
```

---

## Phase 0 — Repository Validation

**Goal:** Confirm the repository structure, governance, and architecture documents are complete and correct.  
**Status:** VERIFIED_COMPLETE (2026-06-16)  
**Complexity:** Low  
**Dependencies:** None

### Deliverables
- [x] 8 microservice skeleton directories with layered structure
- [x] `shared/` package (events, contracts, models, utils, exceptions)
- [x] `infrastructure/` (nginx, postgres init, rabbitmq definitions)
- [x] `frontend/` React + TypeScript scaffolding
- [x] `docs/architecture/`, `docs/api/`, `docs/development/`
- [x] `.project-governance/project_memory.md` — authoritative governance baseline
- [x] ADR-001, ADR-002, ADR-003 recorded and approved
- [x] All SF-01 – SF-24 mapped to services
- [x] All BP-01 – BP-17 mapped to services
- [x] Event schemas defined (MVP + Future Release)

### Acceptance Criteria
- All 8 service directories exist with `app/`, `migrations/`, `tests/` subdirectories
- `shared/events/schemas.py` defines all MVP event classes
- `docs/architecture/service-ownership.md` maps all 24 SRS features to services
- Governance documents are complete and consistent

---

## Phase 1 — Runtime Readiness

**Goal:** Ensure the entire platform can be started with a single command and all services pass health checks.  
**Status:** VERIFIED_COMPLETE (2026-06-16)  
**Complexity:** Medium  
**Dependencies:** P-00

### Deliverables
- [x] `docker-compose.yml` — full composition with health checks
- [x] All service Dockerfiles build from repo root (shared/ accessible)
- [x] `PYTHONPATH=/app` set in all Dockerfiles
- [x] `shared/__init__.py` — shared is a proper Python package
- [x] PostgreSQL health check + 7 databases initialized
- [x] Redis health check + password auth
- [x] RabbitMQ health check + exchange/queue definitions
- [x] All 8 FastAPI services have HEALTHCHECK directives
- [x] Startup ordering enforced via `depends_on: condition: service_healthy`
- [x] Frontend container with nginx SPA config
- [x] Nginx reverse proxy serving all routes
- [x] `.env` + `.env.example` + `.dockerignore`
- [x] `start.sh`, `stop.sh`, `restart.sh` scripts
- [x] `docker-compose.dev.yml` with hot-reload volumes

### Acceptance Criteria
- `docker compose up --build` starts all containers without manual intervention
- All service `/health` endpoints return 200
- RabbitMQ management UI accessible at :15672
- All service Swagger UIs accessible at :8001 – :8007/docs

---

## Phase 2 — Identity Service

**Goal:** Implement complete authentication and user management so all other services can verify identity.  
**Status:** NOT_STARTED  
**Complexity:** High  
**Dependencies:** P-01  
**Services Impacted:** identity-service, api-gateway  
**BRD:** §5 (Stakeholders), §6.1 item 19  
**SRS:** §5.1 (Authentication), §5.2 (Users and Permissions), §5.26 (Flexible Permissions), SF-01  

### Epic: E-02 — Authentication and User Management

#### Feature F-02-01: Database Schema and Migrations

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-02-01-01 | Create Alembic initial migration for `users` table | §5 | §5.1 | NOT_STARTED |
| T-02-01-02 | Create migration for `roles` and `role_permissions` tables | §5 | §5.2 | NOT_STARTED |
| T-02-01-03 | Create migration for `individual_permissions` table | §5 | §5.26 | NOT_STARTED |
| T-02-01-04 | Create migration for `farms_ref` table (read model) | §5 | §5.2 | NOT_STARTED |
| T-02-01-05 | Create migration for `user_roles` association table | §5 | §5.2 | NOT_STARTED |
| T-02-01-06 | Create seed script for 8 system roles with display names | §5 | §5.2 | NOT_STARTED |
| T-02-01-07 | Create seed script for default admin user | §5 | §5.1 | NOT_STARTED |

#### Feature F-02-02: Repository Implementation

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-02-02-01 | Implement `AbstractUserRepository` in `domain/repositories/` | §5 | §5.1 | NOT_STARTED |
| T-02-02-02 | Implement `SQLAlchemyUserRepository` in `infrastructure/database/` | §5 | §5.1 | NOT_STARTED |
| T-02-02-03 | Implement `get_by_email()`, `get_by_id()` methods | §5 | §5.1 | NOT_STARTED |
| T-02-02-04 | Implement `increment_failed_attempts()`, `lock_account()`, `reset_failed_attempts()` | §5 | NFR Security | NOT_STARTED |
| T-02-02-05 | Implement `create_user()` with bcrypt password hash | §5 | §5.1 | NOT_STARTED |
| T-02-02-06 | Implement `update_user()`, `list_users()` | §5 | §5.2 | NOT_STARTED |

#### Feature F-02-03: Authentication Use Cases

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-02-03-01 | Complete `AuthenticateUserUseCase.execute()` — wire to real repository | §5 | §5.1 | NOT_STARTED |
| T-02-03-02 | Implement `RefreshTokenUseCase` — validate refresh token, issue new access token | §5 | §5.1 | NOT_STARTED |
| T-02-03-03 | Implement `LogoutUseCase` — blacklist token in Redis | §5 | §5.1 | NOT_STARTED |
| T-02-03-04 | Implement `CreateUserUseCase` — validates email uniqueness, hashes password, assigns role | §5 | §5.2 | NOT_STARTED |
| T-02-03-05 | Implement `GetCurrentUserUseCase` — returns user profile | §5 | §5.2 | NOT_STARTED |

#### Feature F-02-04: API Endpoints

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-02-04-01 | `POST /api/v1/auth/login` — email + password → JWT tokens | §5 | §5.1 | NOT_STARTED |
| T-02-04-02 | `POST /api/v1/auth/refresh` — refresh token → new access token | §5 | §5.1 | NOT_STARTED |
| T-02-04-03 | `POST /api/v1/auth/logout` — invalidate current session | §5 | §5.1 | NOT_STARTED |
| T-02-04-04 | `GET /api/v1/users/me` — current user profile | §5 | §5.2 | NOT_STARTED |
| T-02-04-05 | `POST /api/v1/users/` — create user (Farm Owner role required) | §5 | §5.2 | NOT_STARTED |
| T-02-04-06 | `GET /api/v1/users/` — list users for farm (Director+ role) | §5 | §5.2 | NOT_STARTED |
| T-02-04-07 | `GET /api/v1/users/{id}` — get user detail | §5 | §5.2 | NOT_STARTED |
| T-02-04-08 | `PATCH /api/v1/users/{id}` — update user (name, phone, role) | §5 | §5.2 | NOT_STARTED |
| T-02-04-09 | `GET /api/v1/roles/` — list available system roles | §5 | §5.2 | NOT_STARTED |

#### Feature F-02-05: API Gateway JWT Verification

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-02-05-01 | Complete JWT middleware in api-gateway — verify signature, check expiry | §5 | §5.1, §11 | NOT_STARTED |
| T-02-05-02 | Forward `X-User-Id`, `X-User-Roles`, `X-Farm-Id` headers to downstream services | §5 | §5.1 | NOT_STARTED |
| T-02-05-03 | Return 401 on invalid/expired token | §5 | §5.1, NFR Security | NOT_STARTED |
| T-02-05-04 | Token blacklist check (Redis) for logged-out tokens | §5 | NFR Security | NOT_STARTED |

#### Feature F-02-06: Tests

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-02-06-01 | Unit tests for `AuthenticateUserUseCase` — happy path, wrong password, locked account | §5 | §5.1 | NOT_STARTED |
| T-02-06-02 | Unit tests for `RefreshTokenUseCase` and `LogoutUseCase` | §5 | §5.1 | NOT_STARTED |
| T-02-06-03 | Integration tests for all auth endpoints | §5 | §5.1 | NOT_STARTED |
| T-02-06-04 | Integration tests for user CRUD endpoints | §5 | §5.2 | NOT_STARTED |

### Acceptance Criteria — Phase 2
- A user can log in with email + password and receive JWT tokens
- Account locks after 5 failed login attempts for 15 minutes
- Tokens expire after 30 minutes; refresh token works
- Logout invalidates the session (token blacklisted in Redis)
- Farm Owner can create users and assign roles
- API Gateway correctly forwards user identity headers to all downstream services
- All tests pass

---

## Phase 3 — Frontend Foundation

**Goal:** Build the React SPA shell: routing, auth flow, layout, API client, and design system foundations.  
**Status:** NOT_STARTED  
**Complexity:** Medium  
**Dependencies:** P-02  
**Services Impacted:** frontend  
**BRD:** §8 (Constraints — Uzbek UI, simplicity), §7.5 (Usability)  
**SRS:** §6.4 (Usability NFR), §6.5 (Localization)

### Epic: E-03 — React Application Foundation

#### Feature F-03-01: Routing and Auth Shell

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-03-01-01 | Install and configure React Router v6 | §8 | §6.4 | NOT_STARTED |
| T-03-01-02 | Create `ProtectedRoute` component — redirect to login if not authenticated | §5 | §5.1 | NOT_STARTED |
| T-03-01-03 | Create Login page with email + password form (Uzbek labels) | §8 | §5.1 | NOT_STARTED |
| T-03-01-04 | Connect Login to identity-service `/auth/login` endpoint | §8 | §5.1 | NOT_STARTED |
| T-03-01-05 | Store JWT tokens in httpOnly cookie or memory (not localStorage) | §5 | NFR Security | NOT_STARTED |
| T-03-01-06 | Implement automatic token refresh on 401 response | §5 | §5.1 | NOT_STARTED |

#### Feature F-03-02: Layout and Navigation

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-03-02-01 | Main app layout: sidebar + header + content area | §8 | §6.4 | NOT_STARTED |
| T-03-02-02 | Sidebar navigation in Uzbek (Partiyalar, Ozuqlantirish, Emlaш, etc.) | §8 | §6.4 | NOT_STARTED |
| T-03-02-03 | Mobile-responsive layout (collapse sidebar on mobile, hamburger menu) | §24 | §6.4 | NOT_STARTED |
| T-03-02-04 | Header with user name, farm name, logout button | §5 | §6.4 | NOT_STARTED |

#### Feature F-03-03: API Client and Global State

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-03-03-01 | Configure Axios instance with base URL + JWT auth interceptor | §8 | §6.4 | NOT_STARTED |
| T-03-03-02 | Global error handler: 401 → redirect to login, 403 → error page | §5 | §6.4 | NOT_STARTED |
| T-03-03-03 | Redux Toolkit slice for auth state (user, token, isAuthenticated) | §5 | §5.1 | NOT_STARTED |
| T-03-03-04 | Loading spinner component for async operations | §8 | §6.4 | NOT_STARTED |
| T-03-03-05 | Toast notification component for success/error feedback | §8 | §6.4 | NOT_STARTED |

### Acceptance Criteria — Phase 3
- Login page loads at `/login`, accepts credentials, stores tokens, redirects to dashboard
- Unauthenticated users are redirected to login from any protected route
- Layout renders correctly on 360px mobile and 1280px desktop widths
- API client attaches JWT to all requests and refreshes on 401 automatically

---

## Phase 4 — Poultry Batch Management

**Goal:** Implement the core batch lifecycle: open a batch, track status, close a batch.  
**Status:** NOT_STARTED  
**Complexity:** High  
**Dependencies:** P-02, P-03  
**Services Impacted:** livestock-service, farm-service  
**BRD:** §6.1 item 2, §9 BP-01 – BP-03  
**SRS:** §5.3 (SF-03), UC-02, UC-10  
**Primary Workflow Step:** Batch Arrival

### Epic: E-04 — Poultry Batch Lifecycle

#### Feature F-04-01: Farm Service — Farm and Section Catalog

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-04-01-01 | Alembic migration: `farms`, `buildings`, `sections` tables (farm_db) | §6.1 | §5.3 | NOT_STARTED |
| T-04-01-02 | Implement `AbstractFarmRepository` + SQLAlchemy implementation | §6.1 | §5.3 | NOT_STARTED |
| T-04-01-03 | `POST /api/v1/farms/` — create farm | §6.1 | §5.3 | NOT_STARTED |
| T-04-01-04 | `GET /api/v1/farms/` — list farms for user | §6.1 | §5.3 | NOT_STARTED |
| T-04-01-05 | `POST /api/v1/farms/{id}/buildings/` — add building | §6.1 | §5.3 | NOT_STARTED |
| T-04-01-06 | `POST /api/v1/buildings/{id}/sections/` — add section | §6.1 | §5.3 | NOT_STARTED |
| T-04-01-07 | `GET /api/v1/farms/{id}/sections/` — list sections for farm | §6.1 | §5.3 | NOT_STARTED |
| T-04-01-08 | Publish `FarmCreatedEvent` on farm creation → farm_id synced to other services | §6.1 | §5.3 | NOT_STARTED |

#### Feature F-04-02: Livestock Service — Batch Database

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-04-02-01 | Alembic migration: `batches`, `farms_ref` tables (livestock_db) | §6.1 | SF-03 | NOT_STARTED |
| T-04-02-02 | Alembic migration: `weight_samplings`, `mortality_records` tables | §6.1 | SF-03 | NOT_STARTED |
| T-04-02-03 | Alembic migration: `vaccination_records`, `vaccination_schedules` tables | §6.1 | SF-07 | NOT_STARTED |
| T-04-02-04 | Alembic migration: `medication_records`, `daily_health_logs` tables | §6.1 | SF-08 | NOT_STARTED |

#### Feature F-04-03: Batch Use Cases

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-04-03-01 | Implement `AbstractBatchRepository` interface | §6.1 | SF-03 | NOT_STARTED |
| T-04-03-02 | Implement `SQLAlchemyBatchRepository` (CRUD + filters) | §6.1 | SF-03 | NOT_STARTED |
| T-04-03-03 | `OpenBatchUseCase` — creates batch in QUARANTINE status, assigns batch_code | BP-01 | UC-02 | NOT_STARTED |
| T-04-03-04 | `ActivateBatchUseCase` — transition QUARANTINE → ACTIVE (enforces 7-day minimum) | BP-03 | SF-03 | NOT_STARTED |
| T-04-03-05 | `CloseBatchUseCase` — transition ACTIVE → CLOSED, publish BatchClosedEvent | BP-15 | UC-10 | NOT_STARTED |
| T-04-03-06 | `GetBatchUseCase` — fetch batch with summary stats | §6.1 | SF-03 | NOT_STARTED |
| T-04-03-07 | `ListBatchesUseCase` — paginated list with filters (status, species, date range) | §6.1 | SF-03 | NOT_STARTED |

#### Feature F-04-04: Batch API Endpoints

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-04-04-01 | `POST /api/v1/batches/` — open new batch | BP-01, BP-02 | UC-02 | NOT_STARTED |
| T-04-04-02 | `GET /api/v1/batches/` — list batches (paginated, filterable) | §6.1 | SF-03 | NOT_STARTED |
| T-04-04-03 | `GET /api/v1/batches/{id}` — batch detail with live stats | §6.1 | SF-03 | NOT_STARTED |
| T-04-04-04 | `PATCH /api/v1/batches/{id}` — update batch notes/metadata | §6.1 | SF-03 | NOT_STARTED |
| T-04-04-05 | `POST /api/v1/batches/{id}/activate` — end quarantine | BP-03 | SF-03 | NOT_STARTED |
| T-04-04-06 | `POST /api/v1/batches/{id}/close` — close batch (with reason) | BP-15 | UC-10 | NOT_STARTED |

#### Feature F-04-05: Frontend — Batch Pages

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-04-05-01 | Batch list page (shows all active batches, status badges, bird count) | §8 | §6.4 | NOT_STARTED |
| T-04-05-02 | "Yangi partiya qo'shish" form (open new batch — Uzbek labels) | §8 | UC-02 | NOT_STARTED |
| T-04-05-03 | Batch detail page (header: species, count, placement date, status) | §8 | SF-03 | NOT_STARTED |
| T-04-05-04 | "Karantindan chiqarish" button (activate batch from quarantine) | §8 | BP-03 | NOT_STARTED |
| T-04-05-05 | "Partiyani yopish" dialog (close batch with reason selector) | §8 | UC-10 | NOT_STARTED |

#### Feature F-04-06: Tests

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-04-06-01 | Unit tests: OpenBatchUseCase, ActivateBatchUseCase, CloseBatchUseCase | BP-01–03 | SF-03 | NOT_STARTED |
| T-04-06-02 | Unit test: BatchStatus state machine (valid + invalid transitions) | BP-03 | SF-03 | NOT_STARTED |
| T-04-06-03 | Integration tests: all batch endpoints | §6.1 | SF-03 | NOT_STARTED |

### Acceptance Criteria — Phase 4
- A Farm Manager can create a new batch specifying species, count, placement date, section
- Batch starts in QUARANTINE status; cannot be activated before 7 days (BP-03)
- Batch transitions: quarantine → active → closed only (no skipping)
- Batch list shows all batches with current status and bird count
- Batch detail shows summary stats (current count, mortality count, days active)

---

## Phase 5 — Feed Consumption

**Goal:** Daily feed consumption recording per batch with FCR calculation.  
**Status:** NOT_STARTED  
**Complexity:** Medium  
**Dependencies:** P-04  
**Services Impacted:** livestock-service (new FeedConsumption model), inventory-service  
**BRD:** §6.1 item 6, §9 BP-04  
**SRS:** §5.10 (SF-10), §5.11 (SF-11 simplified)  
**Primary Workflow Step:** Feeding + Water Consumption

### Epic: E-05 — Daily Feed and Water Recording

#### Feature F-05-01: Feed Consumption Model and Migration

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-05-01-01 | Create `FeedConsumption` domain model in livestock-service | BP-04 | SF-10 | NOT_STARTED |
| T-05-01-02 | Fields: batch_id, farm_id, feed_date, feed_type, quantity_kg, water_liters, age_days, recorded_by | BP-04 | SF-10 | NOT_STARTED |
| T-05-01-03 | Alembic migration: `feed_consumptions` table | BP-04 | SF-10 | NOT_STARTED |

#### Feature F-05-02: Feed Use Cases

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-05-02-01 | `RecordFeedConsumptionUseCase` — validates batch is ACTIVE, records feed + water | BP-04 | SF-10 | NOT_STARTED |
| T-05-02-02 | `GetBatchFeedHistoryUseCase` — paginated list of daily records | BP-04 | SF-10 | NOT_STARTED |
| T-05-02-03 | FCR calculation helper: total_feed_kg / weight_gain_kg (computed on demand) | §3.4 PG-01 | SF-10 | NOT_STARTED |
| T-05-02-04 | Publish `FeedConsumedEvent` → inventory-service consumes for stock deduction (Phase 9) | BP-04 | SF-10 | NOT_STARTED |

#### Feature F-05-03: Feed API Endpoints

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-05-03-01 | `POST /api/v1/batches/{id}/feed/` — record daily feed + water | BP-04 | SF-10 | NOT_STARTED |
| T-05-03-02 | `GET /api/v1/batches/{id}/feed/` — list feed records (paginated) | BP-04 | SF-10 | NOT_STARTED |
| T-05-03-03 | `GET /api/v1/batches/{id}/feed/summary` — total feed, average daily, FCR if weight data exists | BP-04 | SF-10 | NOT_STARTED |

#### Feature F-05-04: Frontend — Feed Recording

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-05-04-01 | Feed recording form on batch detail page (Uzbek: "Kunlik ozuqlantirish") | §8 | SF-10 | NOT_STARTED |
| T-05-04-02 | Water field on same form (Uzbek: "Suv iste'moli, litr") | §8 | SF-11 | NOT_STARTED |
| T-05-04-03 | Feed history table on batch detail page | §8 | SF-10 | NOT_STARTED |

### Acceptance Criteria — Phase 5
- Farm Manager can record daily feed (kg) and water (liters) per batch
- Cannot record feed for CLOSED or non-existent batch
- Feed history list shows all daily records in reverse chronological order
- FCR shows on batch summary when weight data is available

---

## Phase 6 — Mortality Tracking

**Goal:** Daily mortality recording with cause logging. Batch `current_count` auto-decremented.  
**Status:** NOT_STARTED  
**Complexity:** Low–Medium  
**Dependencies:** P-04  
**Services Impacted:** livestock-service  
**BRD:** §6.1 item 16, §9 BP-15, BP-16  
**SRS:** §5.18 (SF-18), UC-04  
**Primary Workflow Step:** Mortality Tracking

### Epic: E-06 — Mortality Recording

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-06-01 | `RecordMortalityUseCase` — record daily count, decrement `batch.current_count`, validate count ≤ current | BP-15 | UC-04 | NOT_STARTED |
| T-06-02 | `GetMortalityHistoryUseCase` — paginated mortality records with totals | BP-15 | SF-18 | NOT_STARTED |
| T-06-03 | `POST /api/v1/batches/{id}/mortality/` — record mortality event | BP-15 | UC-04 | NOT_STARTED |
| T-06-04 | `GET /api/v1/batches/{id}/mortality/` — list mortality records | BP-15 | SF-18 | NOT_STARTED |
| T-06-05 | `GET /api/v1/batches/{id}/mortality/summary` — total deaths, mortality rate %, cause breakdown | BP-15 | SF-18 | NOT_STARTED |
| T-06-06 | Publish `MortalityRecordedEvent` (already defined in shared/events/schemas.py) | BP-15 | SF-18 | NOT_STARTED |
| T-06-07 | Frontend: mortality form on batch detail page (Uzbek: "Kunlik o'lim") | §8 | UC-04 | NOT_STARTED |
| T-06-08 | Frontend: mortality stats on batch detail — total, rate %, daily chart placeholder | §8 | SF-18 | NOT_STARTED |
| T-06-09 | Unit tests: RecordMortalityUseCase (count validation, current_count decrement) | BP-15 | SF-18 | NOT_STARTED |
| T-06-10 | Integration tests: mortality endpoints | BP-15 | SF-18 | NOT_STARTED |

### Acceptance Criteria — Phase 6
- Manager can record mortality count (with optional cause) per batch per day
- `batch.current_count` decrements atomically on each mortality record
- Cannot record mortality count > current_count
- Mortality rate = (total_deaths / initial_count) × 100 computed correctly
- `MortalityRecordedEvent` published to RabbitMQ

---

## Phase 7 — Vaccination Management

**Goal:** Vaccination schedule templates auto-generate planned events per batch. Record executions.  
**Status:** NOT_STARTED  
**Complexity:** High  
**Dependencies:** P-04  
**Services Impacted:** livestock-service  
**BRD:** §6.1 item 8, §9 BP-07  
**SRS:** §5.7 (SF-07), UC-03  
**Primary Workflow Step:** Vaccination

### Epic: E-07 — Vaccination Schedule and Execution

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-07-01 | `CreateVaccinationScheduleUseCase` — create age-based schedule template for species | BP-07 | SF-07 | NOT_STARTED |
| T-07-02 | `GenerateBatchVaccinationPlanUseCase` — on batch open, create `PLANNED` records from schedule | BP-07 | SF-07 | NOT_STARTED |
| T-07-03 | `RecordVaccinationUseCase` — mark PLANNED record as COMPLETED, link to inventory item | BP-07 | UC-03 | NOT_STARTED |
| T-07-04 | `MarkOverdueVaccinationsUseCase` — scheduled daily check, PLANNED → OVERDUE if past date | BP-07 | SF-07 | NOT_STARTED |
| T-07-05 | `POST /api/v1/vaccination-schedules/` — create schedule template | BP-07 | SF-07 | NOT_STARTED |
| T-07-06 | `GET /api/v1/batches/{id}/vaccinations/` — list vaccination plan for batch | BP-07 | SF-07 | NOT_STARTED |
| T-07-07 | `PATCH /api/v1/vaccinations/{id}/complete` — record vaccine execution | BP-07 | UC-03 | NOT_STARTED |
| T-07-08 | Publish `VaccinationCompletedEvent` on execution | BP-07 | SF-07 | NOT_STARTED |
| T-07-09 | Frontend: vaccination calendar on batch detail page | §8 | SF-07 | NOT_STARTED |
| T-07-10 | Frontend: "Emlash bajarildi" button on overdue/planned vaccination | §8 | UC-03 | NOT_STARTED |
| T-07-11 | Unit + integration tests for all vaccination use cases | BP-07 | SF-07 | NOT_STARTED |

### Acceptance Criteria — Phase 7
- System auto-creates planned vaccinations when a batch is opened (from schedule template)
- Overdue vaccinations are detectable (scheduled_at < now and status = PLANNED)
- Veterinarian can record vaccination execution, linking to vaccine inventory item
- `VaccinationCompletedEvent` published to RabbitMQ

---

## Phase 8 — Weight Sampling

**Goal:** Periodic weight sampling for ADG (Average Daily Gain) and FCR computation.  
**Status:** NOT_STARTED  
**Complexity:** Medium  
**Dependencies:** P-04  
**Services Impacted:** livestock-service  
**BRD:** §3.4 PG-01, §6.1 item 9, §9 BP-08  
**SRS:** §5.6 (SF-06)  
**Primary Workflow Step:** Growth Monitoring

### Epic: E-08 — Weight Sampling and Growth Metrics

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-08-01 | `RecordWeightSamplingUseCase` — record sample weight, compute avg from total/size | BP-08 | SF-06 | NOT_STARTED |
| T-08-02 | `GetGrowthMetricsUseCase` — compute ADG from weight sampling history | BP-08 | SF-06 | NOT_STARTED |
| T-08-03 | `POST /api/v1/batches/{id}/weight/` — record weight sampling | BP-08 | SF-06 | NOT_STARTED |
| T-08-04 | `GET /api/v1/batches/{id}/weight/` — list weight samplings | BP-08 | SF-06 | NOT_STARTED |
| T-08-05 | `GET /api/v1/batches/{id}/weight/metrics` — ADG, FCR (if feed data present) | BP-08 | SF-06 | NOT_STARTED |
| T-08-06 | Publish `WeightSampledEvent` | BP-08 | SF-06 | NOT_STARTED |
| T-08-07 | Frontend: weight sampling form on batch detail | §8 | SF-06 | NOT_STARTED |
| T-08-08 | Frontend: ADG metric card on batch dashboard | §8 | SF-06 | NOT_STARTED |
| T-08-09 | Unit + integration tests | BP-08 | SF-06 | NOT_STARTED |

### Acceptance Criteria — Phase 8
- Manager can record sample size and total weight → system computes average_weight_kg
- ADG computed from progression of weight samplings across batch age
- FCR = total_feed_kg / (current_avg_weight × current_count - initial_weight) when feed data available
- Weight history displayed chronologically with age_days

---

## Phase 9 — Inventory Integration

**Goal:** Warehouse and stock management for feed, vaccines, and medicines. FIFO/FEFO dispatch.  
**Status:** DONE  
**Complexity:** High  
**Dependencies:** P-04  
**Services Impacted:** inventory-service  
**BRD:** §6.1 items 10–11, §9 BP-09  
**SRS:** §5.12 (SF-12), §5.13 (SF-13), UC-05, UC-11  
**Primary Workflow Step:** Supports Feed, Vaccination, Medication phases

### Epic: E-09 — Stock Management

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-09-01 | Alembic migration: `warehouses`, `stock_items`, `stock_batches`, `stock_movements` (inventory_db) | BP-09 | SF-12 | DONE |
| T-09-02 | Implement `AbstractStockRepository` + SQLAlchemy implementation | BP-09 | SF-12 | DONE |
| T-09-03 | `ReceiveStockUseCase` — receive stock batch with expiry date, cost, FIFO/FEFO ordering | BP-09 | UC-05 | DONE |
| T-09-04 | `DispatchStockUseCase` — dispatch from stock (FIFO: oldest batch first; FEFO: nearest expiry first) | BP-09 | BP-09 | DONE |
| T-09-05 | `GetStockLevelUseCase` — current quantity available per item per warehouse | BP-09 | SF-12 | DONE |
| T-09-06 | Low-stock alert: publish `LowStockAlertEvent` when quantity < min_threshold | BP-09 | SF-12 | DEFERRED |
| T-09-07 | Expiry alert: publish `ExpiryAlertEvent` when stock_batch.expiry_date < today + 7 days | BP-09 | SF-12 | DEFERRED |
| T-09-08 | RabbitMQ consumer: consume `FeedConsumedEvent`, `VaccinationCompletedEvent`, `MedicationRecordedEvent` → auto-dispatch stock | BP-09 | SF-12 | DEFERRED |
| T-09-09 | `POST /api/v1/warehouses/` — create warehouse | BP-09 | SF-13 | DONE |
| T-09-10 | `POST /api/v1/stock-items/` — create stock item (feed type, vaccine, medicine) | BP-09 | SF-12 | DONE |
| T-09-11 | `POST /api/v1/stock-items/{id}/receive` — receive stock batch | BP-09 | UC-05 | DONE |
| T-09-12 | `GET /api/v1/stock-items/` — list stock with current quantities | BP-09 | SF-12 | DONE |
| T-09-13 | `GET /api/v1/stock-items/{id}/movements` — stock movement history | BP-09 | SF-12 | DONE |
| T-09-14 | Frontend: inventory list page | §8 | SF-12 | DONE |
| T-09-15 | Frontend: receive stock form | §8 | UC-05 | DONE |
| T-09-16 | Unit + integration tests | BP-09 | SF-12 | DONE |

### Acceptance Criteria — Phase 9
- Warehouse Manager can receive stock with quantity, unit price, expiry date
- FIFO/FEFO dispatch rule enforced — oldest/nearest-expiry batch depleted first
- Low stock alert triggers when quantity < defined minimum
- Stock automatically dispatched when feed/vaccination/medication events arrive via RabbitMQ

---

## Phase 10 — Cost Tracking

**Goal:** Automatic batch expense tracking. Every feed, vaccine, medication event creates an expense.  
**Status:** DONE  
**Complexity:** Medium  
**Dependencies:** P-05, P-07, P-09  
**Services Impacted:** finance-service  
**BRD:** §3.3 FG-01, §6.1 items 12, 15, §9 BP-11  
**SRS:** §5.14 (SF-14), §5.15 (SF-15)  
**Primary Workflow Step:** Cost Tracking

### Epic: E-10 — Batch Expense Accumulation

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-10-01 | Alembic migration: `expenses`, `sale_records`, `farms_ref` (finance_db) | BP-11 | SF-14 | DONE |
| T-10-02 | `Expense` model: batch_id, expense_type (FEED/VACCINE/MEDICINE/CHICK/OTHER), amount_uzs, source_event_id | BP-11 | SF-15 | DONE |
| T-10-03 | RabbitMQ consumer: `batch.feed.consumed` → create FEED expense | BP-11 | SF-15 | DEFERRED |
| T-10-04 | RabbitMQ consumer: `batch.vaccination.completed` → create VACCINE expense | BP-11 | SF-15 | DEFERRED |
| T-10-05 | RabbitMQ consumer: `batch.medication.recorded` → create MEDICINE expense | BP-11 | SF-15 | DEFERRED |
| T-10-06 | `RecordManualExpenseUseCase` — manual expense entry (e.g., chick purchase price, labor) | BP-11 | SF-14 | DONE |
| T-10-07 | `GetBatchCostSummaryUseCase` — total cost per expense category for a batch | FG-01 | SF-15 | DONE |
| T-10-08 | `POST /api/v1/expenses/` — manual expense entry | BP-11 | SF-14 | DONE |
| T-10-09 | `GET /api/v1/expenses/batch/{id}` — list all expenses for batch | BP-11 | SF-15 | DONE |
| T-10-10 | `GET /api/v1/expenses/batch/{id}/cost-summary` — cost breakdown by category | FG-01 | SF-15 | DONE |
| T-10-11 | Frontend: cost summary card on batch detail | §8 | SF-15 | DONE |
| T-10-12 | Unit + integration tests | BP-11 | SF-15 | DONE |

### Acceptance Criteria — Phase 10
- Every feed/vaccination/medication event automatically creates a linked expense record
- Batch cost summary shows total and breakdown (feed, vaccine, medicine, chick purchase, other)
- Manual expenses can be added (e.g., labor, electricity)
- All amounts in UZS (Uzbek Sum)

---

## Phase 11 — Sales Management

**Goal:** Simple batch sale record: customer name, quantity sold, price per kg, total revenue.  
**Status:** DONE  
**Complexity:** Medium  
**Dependencies:** P-10  
**Services Impacted:** finance-service, livestock-service  
**BRD:** §3.3 FG-02, §6.1 items 13, §9 BP-12  
**SRS:** §5.17 (SF-17), §5.18 (SF-16, simplified)  
**Primary Workflow Step:** Sale

### Epic: E-11 — Sales Record

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-11-01 | `SaleRecord` model: batch_id, customer_name, customer_phone, quantity_kg, price_per_kg_uzs, total_revenue_uzs, payment_status, sold_at | BP-12 | SF-17 | DONE |
| T-11-02 | Alembic migration: `sale_records` table | BP-12 | SF-17 | DONE |
| T-11-03 | `RecordSaleUseCase` — validates batch is ACTIVE or CLOSED, records sale | BP-12 | SF-17 | DONE |
| T-11-04 | `POST /api/v1/sales/batch/{id}` — record a sale | BP-12 | SF-17 | DONE |
| T-11-05 | `GET /api/v1/sales/batch/{id}` — list sales for batch | BP-12 | SF-17 | DONE |
| T-11-06 | Publish `SaleRecordedEvent` (already defined in shared/events/schemas.py) | BP-12 | SF-17 | DEFERRED |
| T-11-07 | Frontend: sale record form on batch detail | §8 | SF-17 | DONE |
| T-11-08 | Frontend: sales list on batch detail | §8 | SF-17 | DONE |
| T-11-09 | Unit + integration tests | BP-12 | SF-17 | DONE |

### Acceptance Criteria — Phase 11
- Manager can record a sale with customer name, weight sold, price per kg
- Total revenue = quantity_kg × price_per_kg computed automatically
- Payment status: PAID / PENDING
- `SaleRecordedEvent` published; finance-service records revenue

---

## Phase 12 — Profit Analysis

**Goal:** Batch profit = total revenue − total cost. Displayed immediately after batch close.  
**Status:** NOT_STARTED  
**Complexity:** Medium  
**Dependencies:** P-10, P-11  
**Services Impacted:** finance-service  
**BRD:** §3.3 FG-01, §3.1 SG-03  
**SRS:** SF-15, SF-16  
**Primary Workflow Step:** Profit Analysis

### Epic: E-12 — Batch Profit Calculation

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-12-01 | `CalculateBatchProfitUseCase` — total_revenue − total_cost = gross_profit; profit_margin % | FG-01 | SF-15 | NOT_STARTED |
| T-12-02 | `GET /api/v1/batches/{id}/profit` — profit analysis for a batch | FG-01 | SF-16 | NOT_STARTED |
| T-12-03 | RabbitMQ consumer: `batch.batch.closed` → auto-trigger profit calculation | FG-01 | SF-15 | NOT_STARTED |
| T-12-04 | Frontend: profit card on closed batch detail | §8 | SF-16 | NOT_STARTED |
| T-12-05 | Frontend: profit = revenue − cost breakdown (per kg metrics) | §8 | SF-16 | NOT_STARTED |
| T-12-06 | Unit + integration tests | FG-01 | SF-15 | NOT_STARTED |

### Acceptance Criteria — Phase 12
- Profit calculated automatically when batch is closed
- Profit card shows: total revenue, total cost, gross profit, profit margin %, cost per kg, revenue per kg
- Profit calculation is correct: revenue from all sale records − expenses from all expense records

---

## Phase 13 — Notifications

**Goal:** In-app WebSocket alerts for vaccination overdue, low stock, high mortality.  
**Status:** NOT_STARTED  
**Complexity:** Medium  
**Dependencies:** P-12  
**Services Impacted:** notification-service  
**BRD:** §6.1 item 20  
**SRS:** §5.22 (SF-22), §5.23 (SF-23 simplified)  

### Epic: E-13 — In-App Notifications

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-13-01 | Alembic migration: `notifications` table | SF-22 | SF-22 | NOT_STARTED |
| T-13-02 | RabbitMQ consumer: `batch.vaccination.completed` (OVERDUE) → create notification | BP-07 | SF-22 | NOT_STARTED |
| T-13-03 | RabbitMQ consumer: `inventory.alert.low_stock` → create notification | BP-09 | SF-22 | NOT_STARTED |
| T-13-04 | RabbitMQ consumer: `batch.mortality.recorded` — if daily_count > threshold → create notification | BP-15 | SF-22 | NOT_STARTED |
| T-13-05 | WebSocket endpoint: `ws://host/api/v1/ws/{user_id}` — push notifications on connect | SF-22 | SF-22 | NOT_STARTED |
| T-13-06 | `GET /api/v1/notifications/` — list notifications (unread first) | SF-22 | SF-22 | NOT_STARTED |
| T-13-07 | `PATCH /api/v1/notifications/{id}/read` — mark as read | SF-22 | SF-22 | NOT_STARTED |
| T-13-08 | Frontend: notification bell in header with unread count | §8 | SF-22 | NOT_STARTED |
| T-13-09 | Frontend: notification drawer with list | §8 | SF-22 | NOT_STARTED |
| T-13-10 | Unit + integration tests | SF-22 | SF-22 | NOT_STARTED |

### Acceptance Criteria — Phase 13
- Overdue vaccinations trigger notification within 1 minute (SRS NFR)
- Low stock triggers notification to warehouse manager
- Mortality above threshold triggers notification to farm manager/director
- WebSocket delivers real-time notifications to connected users
- Notifications persist in database and are fetchable via REST API

---

## Phase 14 — Reporting

**Goal:** On-demand batch performance card with FCR, mortality rate, cost, and profit. PDF export.  
**Status:** NOT_STARTED  
**Complexity:** High  
**Dependencies:** P-12, P-13  
**Services Impacted:** reporting-service  
**BRD:** §3.1 SG-03, §3.5 VG-01  
**SRS:** §5.21 (SF-21)  

### Epic: E-14 — Batch Performance Report

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-14-01 | Reporting service API client for livestock-service (batch data) | SG-03 | SF-21 | NOT_STARTED |
| T-14-02 | Reporting service API client for finance-service (cost + profit data) | SG-03 | SF-21 | NOT_STARTED |
| T-14-03 | `GenerateBatchReportUseCase` — aggregate batch data from multiple services | SG-03 | SF-21 | NOT_STARTED |
| T-14-04 | Batch performance card: FCR, ADG, mortality rate, total feed, total cost, revenue, profit | SG-03 | SF-21 | NOT_STARTED |
| T-14-05 | `GET /api/v1/reports/batch/{id}` — on-demand batch report (JSON) | SG-03 | SF-21 | NOT_STARTED |
| T-14-06 | PDF export: `GET /api/v1/reports/batch/{id}/pdf` — PDF batch performance report | §8 | SF-21 | NOT_STARTED |
| T-14-07 | Frontend: "Hisobot" button on batch detail page | §8 | SF-21 | NOT_STARTED |
| T-14-08 | Frontend: report preview page | §8 | SF-21 | NOT_STARTED |
| T-14-09 | Unit + integration tests | SG-03 | SF-21 | NOT_STARTED |

### Acceptance Criteria — Phase 14
- On-demand batch report compiles data from livestock + finance services in < 5 seconds (SRS NFR)
- Report includes: FCR, ADG, mortality rate, total feed consumed, total cost breakdown, revenue, profit
- PDF export renders correctly and is printable (for government inspectors)

---

## Phase 15 — MVP Stabilization

**Goal:** End-to-end testing, performance tuning, bug fixes, and production readiness.  
**Status:** NOT_STARTED  
**Complexity:** High  
**Dependencies:** All prior phases  
**BRD:** §10 (Acceptance Criteria)  
**SRS:** §13 (Acceptance Criteria), AC-01 – AC-07  

### Epic: E-15 — MVP Production Readiness

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-15-01 | End-to-end test: full primary workflow (batch open → feed → mortality → vacc. → close → profit) | AC-01 | AC-01 | NOT_STARTED |
| T-15-02 | Performance test: report generation < 5 seconds under load | AC-02 | §6.1 | NOT_STARTED |
| T-15-03 | Security review: JWT security, OWASP Top 10 check | AC-06 | §11 | NOT_STARTED |
| T-15-04 | Uzbek language audit: all UI labels, error messages, notifications in Uzbek | §8 | §6.4 | NOT_STARTED |
| T-15-05 | Mobile responsiveness test on 360px viewport | §24 | §6.4 | NOT_STARTED |
| T-15-06 | Audit trail verification: all critical operations logged with user + timestamp | VG-02 | SF-23 | NOT_STARTED |
| T-15-07 | Backup and restore test (SRS AC-07) | AC-07 | AC-07 | NOT_STARTED |
| T-15-08 | Documentation: User guide for primary workflow (Uzbek) | AC-08 | AC-08 | NOT_STARTED |
| T-15-09 | Deployment guide: production checklist | AC-08 | AC-08 | NOT_STARTED |
| T-15-10 | UAT preparation: test script for primary workflow | AC-05 | AC-05 | NOT_STARTED |

### Acceptance Criteria — Phase 15 (MVP Release Gate)
- 100% of MVP functional requirements implemented and verified
- Primary workflow completes end-to-end without errors
- Report generation < 5 seconds
- All UI in Uzbek language
- No critical security vulnerabilities
- Backup restore test passed
- UAT scenarios documented and ready

---

---

## Phase 16 — Farm Management CRUD

**Goal:** Allow users to fully manage farms: create, edit, delete, view buildings and sections. Fix batch creation section selector.  
**Status:** NOT_STARTED  
**Complexity:** Medium  
**Dependencies:** P-04 VERIFIED_COMPLETE  
**Services Impacted:** farm-service, frontend  
**BRD:** §6.1 item 1, SF-02  
**SRS:** §5.3

### Epic: E-16 — Farm CRUD and Section Cascade

#### Feature F-16-01: Farm Backend (Missing Endpoints)

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-16-01-01 | `PATCH /api/v1/farms/{id}` — edit farm name, region, farm_type | §6.1 | §5.3 | NOT_STARTED |
| T-16-01-02 | `DELETE /api/v1/farms/{id}` — soft delete (blocked if active batches exist) | §6.1 | §5.3 | NOT_STARTED |
| T-16-01-03 | `GET /api/v1/farms/{id}/buildings` — list buildings for a farm | §6.1 | §5.3 | NOT_STARTED |
| T-16-01-04 | `POST /api/v1/farms/{id}/buildings` — create building | §6.1 | §5.3 | NOT_STARTED |
| T-16-01-05 | `GET /api/v1/buildings/{id}/sections` — list sections for a building | §6.1 | §5.3 | NOT_STARTED |
| T-16-01-06 | `POST /api/v1/buildings/{id}/sections` — create section | §6.1 | §5.3 | NOT_STARTED |

#### Feature F-16-02: Farm Frontend

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-16-02-01 | "Yangi ferma qo'shish" modal/form on FarmListPage (Uzbek labels) | §8 | §5.3 | NOT_STARTED |
| T-16-02-02 | Farm detail page — shows farm info + buildings list + sections per building | §8 | §5.3 | NOT_STARTED |
| T-16-02-03 | Edit farm inline or modal (name, region, farm_type) | §8 | §5.3 | NOT_STARTED |
| T-16-02-04 | Delete farm confirmation dialog (blocked if active batches exist) | §8 | §5.3 | NOT_STARTED |

#### Feature F-16-03: Batch Creation Section Fix (BN-FIX-01)

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| BN-FIX-01-01 | Backend: `GET /api/v1/farms/{id}/buildings` (may be covered by T-16-01-03) | BP-01 | §5.3 | NOT_STARTED |
| BN-FIX-01-02 | Backend: `GET /api/v1/buildings/{id}/sections` (may be covered by T-16-01-05) | BP-01 | §5.3 | NOT_STARTED |
| BN-FIX-01-03 | Frontend: Replace `section_id` UUID text field in NewBatchPage with cascade farm → building → section dropdown. User must never manually type a UUID. | BP-01 | UC-02 | NOT_STARTED |

### Acceptance Criteria — Phase 16
- Farm Owner can create a new farm via form (no UUID required)
- Farm Owner can edit farm name, region, farm_type
- Farm Owner can delete a farm (blocked with error message if active batches exist)
- Farm detail page shows all buildings and sections under the farm
- NewBatchPage shows farm → building → section dropdowns; no UUID field exposed to user

---

## Phase 17 — User Management UI

**Goal:** Admin/Farm Owner can create, view, edit, and enable/disable users via the UI.  
**Status:** NOT_STARTED  
**Complexity:** Low (backend is complete)  
**Dependencies:** P-02 VERIFIED_COMPLETE (backend already done)  
**Services Impacted:** frontend only  
**BRD:** §5 (Stakeholders), §6.1 item 19  
**SRS:** §5.2, §5.26 (flexible permissions), SF-01

### Epic: E-17 — User Management Frontend

| Task ID | Description | BRD | SRS | Status |
|---------|-------------|-----|-----|--------|
| T-17-01-01 | Add "Foydalanuvchilar" nav item to Sidebar (visible to farm_owner, farm_director roles) | §5 | §5.2 | NOT_STARTED |
| T-17-01-02 | Create `/users` route in App.tsx | §5 | §5.2 | NOT_STARTED |
| T-17-01-03 | UsersPage — user list table (full_name, email, role badge, is_active status) | §5 | §5.2 | NOT_STARTED |
| T-17-01-04 | "Yangi foydalanuvchi" form — full_name, email, password, role selector (Uzbek labels) | §5 | §5.2 | NOT_STARTED |
| T-17-01-05 | Edit user modal — change full_name, phone, role assignment | §5 | §5.2 | NOT_STARTED |
| T-17-01-06 | Enable/disable user toggle — calls `PATCH /users/{id}` with `is_active` field | §5 | §5.2 | NOT_STARTED |
| T-17-01-07 | `frontend/src/services/userService.ts` — API client for users and roles endpoints | §5 | §5.2 | NOT_STARTED |

### Acceptance Criteria — Phase 17
- Farm Owner can see list of all users for their farm
- Farm Owner can create a new user (Worker, Manager, etc.) without any UUID input
- Farm Owner can assign/change a user's role
- Farm Owner can disable a user (they can no longer log in)
- Farm Owner can re-enable a disabled user
- "Foydalanuvchilar" link visible in sidebar for owner/director roles

---

## Deferred Features (FUTURE_RELEASE)

The following features are explicitly out of MVP scope per ADR-003. Do not implement without explicit approval.

| Feature | BRD/SRS Ref | Target Phase |
|---------|-------------|-------------|
| Email and SMS notifications | SRS §5.22 | Phase 2 (Post-MVP) |
| Scheduled PDF/Excel report delivery | SRS §5.21 | Phase 2 |
| Advanced sales orders with line items | SRS §5.17 | Phase 2 |
| Debtor/creditor (AR/AP) management | SRS §5.14 | Phase 2 |
| Transport management (SF-19, BP-13) | SRS §5.19 | Phase 2 |
| Formal slaughter module (SF-20) | SRS §5.20 | Phase 2 |
| Workforce scheduling | SRS §6.1 | Phase 2 |
| Formal DiseaseIncident case management | SRS §5.8 | Phase 2 |
| Individual animal tracking (Animal model) | SRS §5.4, §5.5 | Phase 3+ |
| Cattle, sheep, goat management | SRS §5.4 | Phase 3+ |
| RFID / ear tag tracking | BRD §6.3 | Phase 3+ |
| Dairy operations | BRD §6.3 | Phase 3+ |
| IoT sensor integration | BRD §6.3 | Phase 3+ |
| Government inspection workflows | BRD §6.3 | Phase 3+ |
| Multi-language support | BRD §6.3 | Phase 3+ |
| SSO / enterprise identity | BRD §6.3 | Phase 3+ |
| Historical archiving UI (SF-24) | SRS §5.24 | Phase 3+ |

---

*master_roadmap.md — AgroVision Development Roadmap v1.0*  
*Created: 2026-06-16 | Do not delete — append and update only*

# AgroVision — Project State (Authoritative Execution Record)
**This is the ONLY trusted source for project execution status.**  
**Do not rely on memory, prior conversations, or task descriptions.**  
**Rebuild understanding from this file + repository inspection every session.**

---

## HOW TO USE THIS FILE

```
EVERY SESSION START:
  1. Read this file completely
  2. Read .project-governance/project_memory.md
  3. Read .project-governance/execution/phase_status.md
  4. Inspect repository for current phase evidence
  5. Verify status through code — never trust labels alone
  6. Report current state before acting

EVERY TASK COMPLETION:
  1. Append to CHANGE LEDGER (bottom of this file)
  2. Update PHASE VERIFICATION RECORDS (this file)
  3. Update phase_status.md
  4. Update development_backlog.md
  5. Append CH-XXX to project_memory.md Change History
```

---

## Git Attribution Policy (Permanent — Effective 2026-06-17)

**This policy overrides any default tool or agent behavior.**

### Prohibited in all commit messages:
- `Co-Authored-By` / `Co-authored-by`
- `Generated-By` / `Generated-by`
- `Created-By` / `Created-by`
- `Authored-By` / `Authored-by`
- Any reference to Claude, Anthropic, AI Assistant, AI Generated, or similar

### Required commit format:
```
git commit -m "single-line description"
```
Single line only. No trailers. No metadata. No attribution.

### Repository ownership:
Sole contributor is the repository owner (ibrokhimovme). No AI attribution permitted.

### Verification (checked at every repository audit):
- [ ] No `Co-Authored-By` trailers in unpushed commits
- [ ] No `Co-authored-by` trailers in unpushed commits
- [ ] No Claude / Anthropic references in commit messages
- [ ] No AI-generated attribution metadata in any commit
- [ ] All new commit recommendations use single-line format only

### Authority:
See `.project-governance/execution/implementation_rules.md §13` for full policy.
See `docs/development/commit-conventions.md` for commit format rules.

---

## Active Execution Context

```
Current Date:          2026-06-17
Current Phase:         P-09 (Inventory Integration) — NEXT TO EXECUTE
Last Verified Phase:   P-08 (Weight Sampling) — VERIFIED_COMPLETE
Overall Progress:      9 / 16 phases verified complete (56.25%)
Next Action:           Execute Phase 9 — Inventory Integration
Blocker:               None
```

---

## Phase State Summary

| Phase | Name | State | Last Verified | Verifier |
|-------|------|-------|---------------|----------|
| P-00 | Repository Validation | VERIFIED_COMPLETE | 2026-06-16 | Engineering Steward |
| P-01 | Runtime Readiness | VERIFIED_COMPLETE | 2026-06-16 | Engineering Steward |
| P-02 | Identity Service | VERIFIED_COMPLETE | 2026-06-17 | Engineering Steward |
| P-03 | Frontend Foundation | VERIFIED_COMPLETE | 2026-06-17 | Engineering Steward |
| P-04 | Poultry Batch Management | VERIFIED_COMPLETE | 2026-06-17 | Engineering Steward |
| P-05 | Feed Consumption | VERIFIED_COMPLETE | 2026-06-17 | Engineering Steward |
| P-06 | Mortality Tracking | VERIFIED_COMPLETE | 2026-06-17 | Engineering Steward |
| P-07 | Vaccination Management | VERIFIED_COMPLETE | 2026-06-17 | Engineering Steward |
| P-08 | Weight Sampling | VERIFIED_COMPLETE | 2026-06-17 | Engineering Steward |
| P-09 | Inventory Integration | NOT_STARTED | — | — |
| P-10 | Cost Tracking | NOT_STARTED | — | — |
| P-11 | Sales Management | NOT_STARTED | — | — |
| P-12 | Profit Analysis | NOT_STARTED | — | — |
| P-13 | Notifications | NOT_STARTED | — | — |
| P-14 | Reporting | NOT_STARTED | — | — |
| P-15 | MVP Stabilization | NOT_STARTED | — | — |

---

## Phase Verification Records

---

### P-00 — Repository Validation

**State:** VERIFIED_COMPLETE  
**Start Date:** 2026-06-16  
**Completion Date:** 2026-06-16  
**Last Verification Date:** 2026-06-16  
**Verifier:** Engineering Steward

**Expected Deliverables:**
- 8 microservice directories with layered structure
- shared/ package (events, contracts, models, utils, exceptions)
- infrastructure/ (nginx, postgres, rabbitmq)
- frontend/ React + TypeScript scaffolding
- Governance system (.project-governance/project_memory.md)
- ADR-001, ADR-002, ADR-003 recorded
- All SF and BP mapped to services
- Event schemas defined

**Actual Deliverables:**
- ✓ services/{api-gateway,identity,farm,livestock,inventory,finance,notification,reporting}-service/
- ✓ shared/events/schemas.py (MVP + Future Release event classes)
- ✓ shared/contracts/api_standards.py
- ✓ shared/models/base.py
- ✓ shared/exceptions/__init__.py
- ✓ shared/utils/ (datetime_utils.py, pagination.py)
- ✓ infrastructure/nginx/, infrastructure/postgres/init.sql, infrastructure/rabbitmq/
- ✓ frontend/ with package.json, tsconfig.json, vite.config.ts, src/
- ✓ .project-governance/project_memory.md (full BRD/SRS analysis, ADRs, CH-001–CH-005)
- ✓ docs/architecture/service-ownership.md (SF-01–SF-24, BP-01–BP-17 mapped)
- ✓ docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md

**Verification Checklist:**
- [x] All 8 service directories exist
- [x] Each service has: app/{api,application,domain,infrastructure}/ + migrations/ + tests/
- [x] shared/ is importable as Python package (shared/__init__.py exists)
- [x] 24 SRS features mapped to services
- [x] 17 BPs mapped to services
- [x] MVP event contracts defined with routing keys

**Evidence:**
- `find services/ -type d | wc -l` → 120+ directories
- `shared/events/schemas.py` → FarmCreatedEvent, BatchOpenedEvent, FeedConsumedEvent, MortalityRecordedEvent, VaccinationCompletedEvent, WeightSampledEvent, SaleRecordedEvent + others
- `docs/architecture/service-ownership.md` → full traceability matrix

**Verification Result:** VERIFIED_COMPLETE  
**Notes:** CH-001 through CH-004 in project_memory.md document all creation work.

---

### P-01 — Runtime Readiness

**State:** VERIFIED_COMPLETE  
**Start Date:** 2026-06-16  
**Completion Date:** 2026-06-16  
**Last Verification Date:** 2026-06-16  
**Verifier:** Engineering Steward

**Expected Deliverables:**
- docker-compose.yml with all services + health checks
- All Dockerfiles build from repo root (shared/ accessible)
- PostgreSQL init with 7 databases
- RabbitMQ with exchange and queue definitions
- Redis with password auth
- All FastAPI services with HEALTHCHECK
- startup scripts

**Actual Deliverables:**
- ✓ docker-compose.yml — 8 FastAPI services + postgres + redis + rabbitmq + nginx + frontend
- ✓ All Dockerfiles use `context: .` (repo root), COPY shared/, PYTHONPATH=/app, HEALTHCHECK
- ✓ infrastructure/postgres/init.sql — creates identity_db, farm_db, livestock_db, inventory_db, finance_db, notification_db, reporting_db
- ✓ infrastructure/rabbitmq/definitions.json — agrovision.events exchange + consumer queues
- ✓ infrastructure/rabbitmq/rabbitmq.conf — vhost configuration
- ✓ Redis: REDISCLI_AUTH env var set for health check
- ✓ shared/__init__.py created
- ✓ frontend/nginx.conf created (SPA fallback)
- ✓ .env + .env.example + .dockerignore
- ✓ start.sh, stop.sh, restart.sh
- ✓ docker-compose.dev.yml with hot-reload shared/ volume mounts

**Verification Checklist:**
- [x] docker-compose.yml defines `condition: service_healthy` for all depends_on
- [x] All 8 FastAPI Dockerfiles have HEALTHCHECK directive
- [x] Redis healthcheck uses REDISCLI_AUTH env var
- [x] infrastructure/postgres/init.sql creates 7 databases
- [x] shared/__init__.py exists
- [x] .env file exists
- [x] start.sh exists and is executable

**Evidence:**
- `docker-compose.yml` lines: 8 FastAPI services, postgres health check, redis health check, rabbitmq health check
- `services/identity-service/Dockerfile` — HEALTHCHECK present, PYTHONPATH=/app, copies shared/
- `infrastructure/postgres/init.sql` — 7 CREATE DATABASE statements

**Verification Result:** VERIFIED_COMPLETE  
**Known Gap:** All routers are empty stubs. No business logic. No migrations run. Containers start and pass health checks but serve no meaningful API yet.  
**Notes:** CH-005 in project_memory.md documents all runtime fixes.

---

### P-02 — Identity Service

**State:** VERIFIED_COMPLETE  
**Start Date:** 2026-06-17  
**Completion Date:** 2026-06-17  
**Last Verification Date:** 2026-06-17  
**Verifier:** Engineering Steward

**Verification Checklist:**
- [x] `services/identity-service/migrations/versions/001_initial_identity_schema.py` exists
- [x] `SQLAlchemyUserRepository` in `infrastructure/database/repositories/user_repository_impl.py`
- [x] `POST /api/v1/auth/login` returns JWT access + refresh tokens
- [x] `POST /api/v1/auth/refresh` rotates access token
- [x] `POST /api/v1/auth/logout` blacklists token in Redis
- [x] `POST /api/v1/users/`, `GET /users/me`, `GET /users/{id}`, `PATCH /users/{id}`, `GET /roles/`
- [x] Account lockout after 5 failed attempts (ACCOUNT_LOCKED rule)
- [x] bcrypt password hashing (direct bcrypt, not passlib)
- [x] Seed script: 8 system roles + admin@agrovision.uz
- [x] API Gateway Redis blacklist check added
- [x] 16/16 tests passed

**Verification Result:** VERIFIED_COMPLETE  
**Notes:** CL-002 documents all files. bcrypt 4.x incompatibility with passlib resolved by direct bcrypt module.

---

### P-03 — Frontend Foundation

**State:** VERIFIED_COMPLETE  
**Start Date:** 2026-06-17  
**Completion Date:** 2026-06-17  
**Last Verification Date:** 2026-06-17  
**Verifier:** Engineering Steward

**Actual Deliverables:**
- ✓ `frontend/src/App.tsx` — BrowserRouter, Routes, ProtectedRoute, AppLayout wrapper, ToastContainer
- ✓ `frontend/src/pages/Login.tsx` — Uzbek login form (react-hook-form + zod), connects to /auth/login then /users/me
- ✓ `frontend/src/components/layout/Layout.tsx` — Sidebar + Header + scrollable main content
- ✓ `frontend/src/components/layout/Sidebar.tsx` — Uzbek nav: Bosh sahifa, Fermalar, Parrandalar, Ombor, Moliya, Hisobotlar; mobile overlay
- ✓ `frontend/src/components/layout/Header.tsx` — user avatar, full_name, logout button
- ✓ `frontend/src/components/ui/Toast.tsx` — Zustand-based toast system, auto-dismiss 4s, 4 types
- ✓ `frontend/src/components/ui/Spinner.tsx` — animated spinner (sm/md/lg)
- ✓ `frontend/src/services/api.ts` — Zustand token injection, auto-refresh on 401 with retry queue, clearAuth on refresh failure
- ✓ `services/identity-service/seeds/seed_roles.py` — removed stale CryptContext reference (bug fix)

**Verification Checklist:**
- [x] React Router v6 configured with BrowserRouter + nested Routes
- [x] ProtectedRoute redirects unauthenticated users to /login
- [x] Login page renders Uzbek labels (Tizimga Kirish, Email manzil, Parol, Kirish)
- [x] Login calls POST /auth/login then GET /users/me, stores via setAuth()
- [x] Auth store (Zustand persist) holds user + accessToken + refreshToken
- [x] API client reads accessToken from Zustand store (not localStorage)
- [x] 401 response triggers refresh → retry → clearAuth fallback
- [x] Sidebar renders 6 Uzbek nav items with active-link highlighting
- [x] Mobile hamburger menu + overlay for sidebar at <lg breakpoint
- [x] Toast notifications: success/error/warning/info with auto-dismiss
- [x] Spinner component: sm/md/lg sizes
- [x] TypeScript: `npx tsc --noEmit` → 0 errors
- [x] Vite build: `vite build` → success (344 kB bundle)

**Verification Result:** VERIFIED_COMPLETE  
**Notes:** No icon library needed — inline SVGs used throughout. Tailwind responsive breakpoints handle 360px minimum (lg=1024px toggle for sidebar).

---

### P-04 — Poultry Batch Management

**State:** VERIFIED_COMPLETE  
**Start Date:** 2026-06-17  
**Completion Date:** 2026-06-17  
**Last Verification Date:** 2026-06-17  
**Verifier:** Engineering Steward

**Verification Checklist:**
- [x] `farm_db` has tables: farms, buildings, sections (migration 001)
- [x] `livestock_db` has tables: batches, weight_samplings, mortality_records, farms_ref (migration 001) + vaccination_records, vaccination_schedules, medication_records, daily_health_logs (migration 002)
- [x] `GET /api/v1/batches/` returns paginated batch list
- [x] `POST /api/v1/batches/` creates batch with QUARANTINE status
- [x] `POST /api/v1/batches/{id}/activate` enforces 7-day quarantine minimum (BP-03)
- [x] `POST /api/v1/batches/{id}/close` transitions to CLOSED
- [x] Invalid state transitions raise InvalidStateTransitionError → 422
- [x] Frontend: BatchListPage, BatchDetailPage, NewBatchPage, FarmListPage
- [x] 9/9 unit tests pass (state machine + quarantine enforcement)

**Key files:**
- `services/farm-service/migrations/versions/001_initial_farm_schema.py`
- `services/livestock-service/migrations/versions/001_initial_livestock_schema.py`
- `services/livestock-service/migrations/versions/002_add_health_tables.py`
- `services/livestock-service/app/application/use_cases/activate_batch.py` (BP-03 quarantine enforcement)
- `services/livestock-service/tests/unit/test_activate_batch.py`
- `frontend/src/pages/livestock/{BatchListPage,BatchDetailPage,NewBatchPage}.tsx`
- `frontend/src/pages/farms/FarmListPage.tsx`

**Verification Result:** VERIFIED_COMPLETE  
**Notes:** P-04 was implemented in prior commits but not tracked. Gap analysis found 3 missing items: migration 002 (health tables), quarantine enforcement in ActivateBatchUseCase, and corresponding tests. All 3 gaps fixed in CL-004.

---

### P-05 through P-15

**State:** NOT_STARTED  
**Details:** See individual sections in master_roadmap.md and development_backlog.md  
**No verification performed — dependencies not yet met**

---

## Phase History

| Phase | Start Date | Completion Date | Duration | Files Modified |
|-------|-----------|-----------------|----------|---------------|
| P-00 | 2026-06-16 | 2026-06-16 | 1 day | 80+ (see CH-001–CH-004) |
| P-01 | 2026-06-16 | 2026-06-16 | 1 day | 15+ (see CH-005) |
| P-02 | 2026-06-17 | 2026-06-17 | 1 day | 21 files (see CL-002) |
| P-03 | 2026-06-17 | 2026-06-17 | 1 day | 9 files (see CL-003) |
| P-04 | 2026-06-17 | 2026-06-17 | 1 day | 30+ files (see CL-004) |
| P-05 | 2026-06-17 | 2026-06-17 | 1 day | 13 files (see CL-005) |
| P-06 | 2026-06-17 | 2026-06-17 | 1 day | 12 files (see CL-006) |
| P-07 | 2026-06-17 | 2026-06-17 | 1 day | 14 files (see CL-007) |
| P-08 | 2026-06-17 | 2026-06-17 | 1 day | 11 files (see CL-008) |

---

## Change Ledger (Append-Only)

Every modification to the project must be recorded here. Never delete entries.

---

### CL-003
- **Date:** 2026-06-17
- **Task:** Phase 3 — Frontend Foundation
- **Files Created:**
  - `frontend/src/pages/Login.tsx`
  - `frontend/src/components/layout/Layout.tsx`
  - `frontend/src/components/layout/Sidebar.tsx`
  - `frontend/src/components/layout/Header.tsx`
  - `frontend/src/components/ui/Toast.tsx`
  - `frontend/src/components/ui/Spinner.tsx`
- **Files Modified:**
  - `frontend/src/App.tsx` (added Layout, ToastContainer, real LoginPage import)
  - `frontend/src/services/api.ts` (Zustand token injection, auto-refresh on 401)
  - `services/identity-service/seeds/seed_roles.py` (removed stale CryptContext reference)
- **Verification:** TypeScript 0 errors, Vite build success (344 kB)
- **Impact:** Frontend is fully navigable with auth flow, Uzbek UI, and responsive layout. P-04 dependencies met.

### CL-002
- **Date:** 2026-06-17
- **Task:** Phase 2 — Identity Service full implementation
- **Files Created:**
  - `services/identity-service/migrations/versions/001_initial_identity_schema.py`
  - `services/identity-service/app/infrastructure/database/repositories/user_repository_impl.py`
  - `services/identity-service/app/infrastructure/cache/redis_client.py`
  - `services/identity-service/app/application/use_cases/refresh_token.py`
  - `services/identity-service/app/application/use_cases/logout.py`
  - `services/identity-service/app/application/use_cases/create_user.py`
  - `services/identity-service/app/application/use_cases/get_current_user.py`
  - `services/identity-service/app/application/dtos/auth_dtos.py`
  - `services/identity-service/app/application/dtos/user_dtos.py`
  - `services/identity-service/app/api/v1/endpoints/auth.py`
  - `services/identity-service/app/api/v1/endpoints/users.py`
  - `services/identity-service/app/api/v1/endpoints/roles.py`
  - `services/identity-service/seeds/seed_roles.py`
  - `services/identity-service/tests/unit/test_authenticate.py`
  - `services/identity-service/tests/unit/test_refresh_logout.py`
  - `services/identity-service/tests/integration/test_auth_endpoints.py`
- **Files Modified:**
  - `services/identity-service/app/api/v1/router.py`
  - `services/identity-service/app/main.py`
  - `services/identity-service/app/core/config.py`
  - `services/identity-service/app/application/use_cases/authenticate.py`
  - `services/identity-service/migrations/env.py`
  - `services/identity-service/alembic.ini`
  - `services/identity-service/tests/conftest.py`
  - `services/api-gateway/app/middleware/auth.py`
- **Verification:** 16/16 tests passed
- **Impact:** Identity service is production-ready (pending live DB migration). API Gateway blacklist check added.

### CL-001
- **Date:** 2026-06-17
- **Task:** Project State and Execution Framework Creation
- **Reason:** User instruction to establish persistent state-driven execution system
- **Files Created:**
  - `.project-governance/project_state.md` (this file)
  - `.project-governance/execution/master_roadmap.md`
  - `.project-governance/execution/development_backlog.md`
  - `.project-governance/execution/phase_status.md`
  - `.project-governance/execution/implementation_rules.md`
- **Impact:**
  - Execution framework established; all future development governed by these documents
  - P-00 and P-01 baseline verified from repository inspection
  - P-02 (Identity Service) identified as next phase
  - ~130 tasks defined across 14 remaining phases
  - 17 FUTURE_RELEASE items explicitly deferred
- **Requirements Implemented:** None (governance only)
- **Services Impacted:** None (governance only)

---

### CL-004
- **Date:** 2026-06-17
- **Task:** Phase 4 — Poultry Batch Management — gap fix and verification
- **Context:** P-04 was already partially implemented in prior commits (391e21c, 2f99fc2, 7d50a79) but not tracked in project_state.md. Gap analysis found 3 missing items.
- **Files Created (gap fixes):**
  - `services/livestock-service/migrations/versions/002_add_health_tables.py` — vaccination_records, vaccination_schedules, medication_records, daily_health_logs tables
  - `services/livestock-service/tests/unit/test_activate_batch.py` — 4 tests for quarantine enforcement (BP-03)
- **Files Modified (gap fixes):**
  - `services/livestock-service/app/application/use_cases/activate_batch.py` — added 7-day quarantine minimum check (BP-03)
- **Pre-existing files verified (from prior commits):**
  - `services/farm-service/migrations/versions/001_initial_farm_schema.py`
  - `services/farm-service/app/infrastructure/database/repositories/farm_repository_impl.py`
  - `services/farm-service/app/api/v1/endpoints/farms.py`
  - `services/farm-service/app/application/use_cases/{create_farm,get_farm,list_farms}.py`
  - `services/livestock-service/migrations/versions/001_initial_livestock_schema.py`
  - `services/livestock-service/app/infrastructure/database/repositories/batch_repository_impl.py`
  - `services/livestock-service/app/api/v1/endpoints/batches.py`
  - `services/livestock-service/app/application/use_cases/{create_batch,activate_batch,close_batch,get_batch,list_batches,update_batch}.py`
  - `services/livestock-service/tests/unit/test_batch_state_machine.py`
  - `services/livestock-service/tests/integration/test_batch_endpoints.py`
  - `frontend/src/pages/livestock/{BatchListPage,BatchDetailPage,NewBatchPage}.tsx`
  - `frontend/src/pages/farms/FarmListPage.tsx`
- **Verification:** 9/9 unit tests passed
- **Requirements implemented:** SF-03 (batch lifecycle), BP-01 (acquisition), BP-02 (arrival), BP-03 (quarantine 7-day minimum), UC-02 (open batch), UC-10 (close batch)
- **Services impacted:** livestock-service, farm-service, frontend

---

### CL-005
- **Date:** 2026-06-17
- **Task:** Phase 5 — Feed Consumption
- **Files Created:**
  - `services/livestock-service/app/domain/models/feed.py`
  - `services/livestock-service/app/domain/repositories/feed_repository.py`
  - `services/livestock-service/app/infrastructure/database/repositories/feed_repository_impl.py`
  - `services/livestock-service/app/application/dtos/feed_dtos.py`
  - `services/livestock-service/app/application/use_cases/record_feed.py`
  - `services/livestock-service/app/application/use_cases/get_feed_history.py`
  - `services/livestock-service/app/api/v1/endpoints/feed.py`
  - `services/livestock-service/migrations/versions/003_add_feed_consumptions.py`
  - `services/livestock-service/tests/unit/test_record_feed.py`
- **Files Modified:**
  - `services/livestock-service/app/api/v1/router.py` (added feed router)
  - `frontend/src/types/index.ts` (FeedRecord, FeedSummary types)
  - `frontend/src/services/batchService.ts` (feedService with 3 methods)
  - `frontend/src/pages/livestock/BatchDetailPage.tsx` (feed form + history table)
- **Verification:** 13/13 unit tests passed; TypeScript 0 errors; Vite build success (366 kB)
- **Requirements implemented:** SF-10 (feed management), SF-11 (water simplified), BP-04 (feeding), BP-05 (water)
- **Services impacted:** livestock-service, frontend

---

### CL-006
- **Date:** 2026-06-17
- **Task:** Phase 6 — Mortality Tracking
- **Files Created:**
  - `services/livestock-service/migrations/versions/004_add_mortality_records.py`
  - `services/livestock-service/app/domain/repositories/mortality_repository.py`
  - `services/livestock-service/app/infrastructure/database/repositories/mortality_repository_impl.py`
  - `services/livestock-service/app/application/dtos/mortality_dtos.py`
  - `services/livestock-service/app/application/use_cases/record_mortality.py`
  - `services/livestock-service/app/application/use_cases/get_mortality_history.py`
  - `services/livestock-service/app/api/v1/endpoints/mortality.py`
  - `services/livestock-service/tests/unit/test_record_mortality.py`
- **Files Modified:**
  - `services/livestock-service/app/api/v1/router.py` (mortality router included)
  - `frontend/src/types/index.ts` (MortalityRecord, MortalitySummary types)
  - `frontend/src/services/batchService.ts` (mortalityService with 3 methods)
  - `frontend/src/pages/livestock/BatchDetailPage.tsx` (mortality summary, form, history table; SummaryCard color prop)
- **Verification:** 19/19 unit tests passed; TypeScript 0 errors; Vite build success (371 kB)
- **Requirements implemented:** SF-18 (mortality tracking), BP-15 (active batch only), BP-16 (count decrement)
- **Services impacted:** livestock-service, frontend

---

### CL-007
- **Date:** 2026-06-17
- **Task:** Phase 7 — Vaccination Management
- **Files Modified:**
  - `services/livestock-service/app/domain/models/health.py` (vaccine_inventory_item_id/quantity/unit → Optional)
- **Files Created:**
  - `services/livestock-service/app/domain/repositories/vaccination_repository.py`
  - `services/livestock-service/app/infrastructure/database/repositories/vaccination_repository_impl.py`
  - `services/livestock-service/app/application/dtos/vaccination_dtos.py`
  - `services/livestock-service/app/application/use_cases/create_vaccination_schedule.py`
  - `services/livestock-service/app/application/use_cases/generate_batch_vaccination_plan.py`
  - `services/livestock-service/app/application/use_cases/record_vaccination.py`
  - `services/livestock-service/app/application/use_cases/get_batch_vaccinations.py`
  - `services/livestock-service/app/api/v1/endpoints/vaccination.py`
  - `services/livestock-service/tests/unit/test_vaccination.py`
  - `services/livestock-service/app/api/v1/router.py` (vaccination_router added)
  - `frontend/src/types/index.ts` (VaccinationRecord, VaccinationSchedule types)
  - `frontend/src/services/batchService.ts` (vaccinationService with 5 methods)
  - `frontend/src/pages/livestock/BatchDetailPage.tsx` (vaccination table + Bajarildi button, VaccStatusBadge)
- **Verification:** 28/28 unit tests passed; TypeScript 0 errors; Vite build success (375 kB)
- **Requirements implemented:** SF-07 (vaccination management), BP-07 (schedule templates), UC-03 (vaccination execution)
- **Services impacted:** livestock-service, frontend

---

### CL-008
- **Date:** 2026-06-17
- **Task:** Phase 8 — Weight Sampling
- **Files Created:**
  - `services/livestock-service/app/domain/repositories/weight_repository.py`
  - `services/livestock-service/app/infrastructure/database/repositories/weight_repository_impl.py`
  - `services/livestock-service/app/application/dtos/weight_dtos.py`
  - `services/livestock-service/app/application/use_cases/record_weight_sampling.py`
  - `services/livestock-service/app/application/use_cases/get_weight_history.py`
  - `services/livestock-service/app/api/v1/endpoints/weight.py`
  - `services/livestock-service/tests/unit/test_weight_sampling.py`
- **Files Modified:**
  - `services/livestock-service/app/api/v1/router.py` (weight_router added)
  - `frontend/src/types/index.ts` (WeightSampling, GrowthMetrics types)
  - `frontend/src/services/batchService.ts` (weightService with 3 methods)
  - `frontend/src/pages/livestock/BatchDetailPage.tsx` (weight form, ADG/FCR cards, history table)
- **Verification:** 36/36 unit tests passed; TypeScript 0 errors; Vite build success (379 kB)
- **Requirements implemented:** SF-06 (weight sampling), BP-08 (ADG/FCR computation)
- **Services impacted:** livestock-service, frontend

---

*project_state.md — AgroVision Authoritative Execution State*  
*Created: 2026-06-17 | Version: 1.0*  
*IMPORTANT: Always append to Change Ledger. Never delete or overwrite history.*

# AgroVision — Backlog Items v2

**Status:** PLANNING ONLY — no implementation authorized. All items below are status `NOT_STARTED`.
**Date:** 2026-06-18
**Companion documents:** `master_roadmap.md`, `execution_phases.md`, `phase_dependencies.md`, `verification_checklists.md`
**Format convention:** flat task list per phase, mirroring `development_backlog.md`'s style, scoped against the modular monolith (`app/<module>/`) rather than the old per-service layout.

Two phases (EX-11, EX-12) have their task lists marked **CONDITIONAL — PENDING CLARIFICATION** since their headline requirement names were given without a specified improvement (see `execution_phases.md` and `phase_dependencies.md` §5). Their listed tasks are the clarification step itself plus the one unconditional sub-item each.

---

## EX-01 — Account Foundation — **VERIFIED_COMPLETE (2026-06-18)**

| Task ID | Description | Status |
|---|---|---|
| T-EX01-01 | Design `Account` entity (fields, relationships, cardinality to Farm and User) | DONE — `app/identity/domain/models/account.py`: `id`, `name`, `owner_user_id` (FK→users), `is_active`, audit columns |
| T-EX01-02 | Decide Alembic-wiring question (wire it up now vs. continue direct schema bootstrap) and record the decision | DONE — see `decision_log.md` BMD-009: continue direct schema bootstrap, Alembic stays deferred |
| T-EX01-03 | Implement `Account` model and table (new schema or existing `identity`/`farm` schema — to be decided) | DONE — table `identity.accounts`, explicit `__table_args__ = {"schema": "identity"}` (required for Farm's cross-schema FK to resolve, same lesson as the M8/CL-030 bug) |
| T-EX01-04 | Add `Farm.account_id` FK, migrate existing Farm rows to a valid Account | DONE — column + FK added, backfilled via `infrastructure/postgres/migrations_v2/001_ex01_account_foundation.sql`, applied to the live `agrovision` database |
| T-EX01-05 | Define User-to-Account relationship and update `User` model accordingly | DONE — `User.account_id` (nullable FK→`identity.accounts.id`) added in `app/identity/domain/models/user.py` |
| T-EX01-06 | Update seed scripts to create at least one Account before seeding Farms | DONE — `seed_identity.py` creates `ACCOUNT_TOSHKENT_BROILER_ID` and assigns it to the owner/manager/accountant/worker/vet users; `seed_farm.py` sets it on the seeded farm |
| T-EX01-07 | Unit tests for Account creation, Farm-to-Account assignment, and orphan-prevention | PARTIAL — verified via live-DB integration check (backfill produced 0 orphaned farms among real data; 1 pre-existing test row with an invalid `owner_user_id` zero-UUID predates this work and was left as documented, not silently fixed); no dedicated automated unit-test file was added (no `tests/` convention currently exists for `app/identity` post-M7 — see `repository_cleanup_backlog.md` CLEAN-05, a pre-existing gap, not introduced here) |

**Live verification performed (2026-06-18):** SQL migration applied to the running `agrovision` database (`docker exec agrovision-postgres-1 psql ... -f 001_ex01_account_foundation.sql`) — 2 accounts backfilled from real existing data (admin + farm owner), 0 orphaned farms among valid data, 1 known pre-existing bad test row (`owner_user_id` = zero UUID) left undisturbed. `monolith` container rebuilt and restarted — reached `healthy`. Full smoke test passed post-rebuild: login (200), farms list (200), farm detail (200), batches list (200), users list (200), farm create (201) and delete (204) write-path regression check. SQLAlchemy mapper configuration verified to resolve the new cross-schema FK strings (`identity.accounts.id`) without the `NoReferencedTableError` class of bug seen in M8/CL-030.

## EX-02 — Farm Management Revision — **VERIFIED_COMPLETE (2026-06-18)**

| Task ID | Description | Status |
|---|---|---|
| T-EX02-01 | Update `CreateFarmRequest`/`UpdateFarmRequest` DTOs to include account context | DONE — `FarmResponse` now exposes `account_id` (read-only). `CreateFarmRequest`/`UpdateFarmRequest` deliberately do NOT accept a client-supplied `account_id` — it's derived server-side from the caller's JWT (`X-Account-Id` header), never user-selectable, per the original scope note |
| T-EX02-02 | Update farm list/get use cases to scope by Account | DONE — `list_farms`, `get_farm`, `update_farm`, `delete_farm`, `create_farm` use cases all account-aware; JWT now carries `account_id` claim (`authenticate.py`, `refresh_token.py`), propagated via a new `X-Account-Id` header (`auth_middleware.py`) |
| T-EX02-03 | Update `FarmListPage.tsx`/farm create-edit modal to reflect account scoping (likely implicit, not user-selectable) | DONE (no frontend change needed) — confirmed scoping is fully transparent server-side via existing JWT/header propagation, exactly as predicted; zero frontend changes required |
| T-EX02-04 | Regression test: existing active-batch delete-guard still works unchanged | **FINDING, not a regression**: live inspection found `DeleteFarmUseCase`/`soft_delete` has **no active-batch guard in the backend at all** — only the frontend's delete-confirmation modal text claims one ("Agar faol partiyalar mavjud bo'lsa, bu amal bloklanadi"). This pre-dates EX-02 and is unrelated to account-scoping; documented here per the "never assume complete" rule rather than silently treated as already covered. Not fixed — adding a new business rule is outside EX-02's approved scope (account-awareness only); flagged as a candidate for a future, separately-approved backlog item |
| T-EX02-05 | Negative-path test: cross-account farm access is denied | DONE — verified live: owner@toshkent-broiler.uz received 404 on a farm belonging to a different Account; received 200 on their own account's farms |

**Mid-implementation correction (discovered via live verification, not assumed):** the original design used "account_id is None" as the super-admin bypass condition. Live testing found the platform super-admin (`admin@agrovision.uz`) legitimately owns an Account too (from pre-existing test data), which would have made them invisible to all farms under naive account scoping — a real regression in oversight capability, not a feature removal anyone asked for. Fixed by switching the bypass condition to the actual `super_admin` role (already carried in the existing `X-User-Roles` header) instead of account-id-nullity. See `decision_log.md` BMD-010.

**Live verification performed (2026-06-18):** monolith rebuilt and restarted (healthy) after each of two implementation passes. Verified: owner-scoped list returns exactly their account's 2 farms; super-admin list returns all active farms (2) unrestricted despite having their own account; owner GET on another account's farm → 404; owner GET on their own account's farm → 200; super-admin GET on any farm → 200; farm create automatically inherits the caller's `account_id` (verified via a real create+update+delete cycle, cleaned up afterward); full cross-module regression (health, batches, users, report, buildings — all 200) passed.

## EX-03 — Building & Section Simplification — **VERIFIED_COMPLETE (2026-06-18)**

| Task ID | Description | Status |
|---|---|---|
| T-EX03-01 | Remove `SectionType.QUARANTINE` from backend enum | DONE — `app/farm/domain/models/farm.py`; verified live: `POST .../sections` with `section_type:"quarantine"` now returns 422 |
| T-EX03-02 | Confirm `SectionType.ISOLATION` remains untouched (no code change, verification only) | DONE — confirmed present in enum and in the frontend select; a `storage`-typed section create/cleanup cycle verified the remaining 3 types (`production`/`isolation`/`storage`) all still work |
| T-EX03-03 | Update `FarmDetailPage.tsx` section-type select to drop the "Karantin" option | DONE — option removed, `SECTION_TYPE_LABELS` map updated |
| T-EX03-04 | Update `scripts/seed/seed_farm.py` to remove the "Karantin bloki"/"Karantin bo'limi" demo data | DONE — building/section removed from seed data; unused `BUILDING_QUARANTINE_ID`/`SECTION_QUARANTINE_ID` constants removed from `config.py` |
| T-EX03-05 | Data migration plan for any existing rows with the removed section type (if production data exists by execution time) | DONE — found exactly 1 live row (the seeded "Karantin bo'limi"), verified zero batches referenced it, wrote and applied `infrastructure/postgres/migrations_v2/002_ex03_section_simplification.sql` (includes a defensive `RAISE EXCEPTION` guard re-checking zero batch references at apply time, not just at authoring time) |

**Additional fix found via TypeScript verification (not pre-planned):** `frontend/src/pages/livestock/NewBatchPage.tsx` had a `section_type === 'quarantine'` comparison in its section-dropdown label logic, which `tsc --noEmit` correctly flagged as a type error once `quarantine` was removed from the `SectionType` union — fixed by removing that branch. This confirms the value of running the full TypeScript check rather than only grepping for the literal string "quarantine" (this file wasn't in the initial grep result set the same way the others were, since the match was a comparison expression, not a label string).

**Live verification performed (2026-06-18):** Python `py_compile` clean; `scripts/check_module_boundaries.py` clean; frontend `tsc --noEmit` clean; frontend `vite build` succeeds. SQL migration applied to the live database (verified before: 1 quarantine section + its now-orphaned building existed, 0 batches referenced it; verified after: 0 quarantine sections, 0 buildings named like "Karantin"). Monolith and frontend containers rebuilt and restarted — both healthy. Live test: creating a section with `section_type: "quarantine"` → 422 with a clear enum-validation message; creating one with `section_type: "storage"` → 201 (then cleaned up). Full regression (health, farms, batches, frontend root) all 200.

## EX-04 — Batch Lifecycle Simplification

| Task ID | Description | Status |
|---|---|---|
| T-EX04-01 | Collapse `BatchStatus` enum to `{ACTIVE, COMPLETED}` | DONE — `app/poultry/domain/models/animal.py` |
| T-EX04-02 | Update `VALID_TRANSITIONS` to `ACTIVE → COMPLETED` only | DONE — `Batch.transition_to()` |
| T-EX04-03 | Remove `quarantine_end_date` column | DONE — removed from model/DTOs/use-cases/frontend; dropped live via migration 003 |
| T-EX04-04 | Remove `activate_batch.py` use case and its endpoint | DONE — file deleted, `POST /batches/{id}/activate` removed from `batches.py`; verified live 404 |
| T-EX04-05 | Update `create_batch.py` so new batches start `ACTIVE` directly | DONE — verified live via a real create-batch call |
| T-EX04-06 | Remove `slaughter` from `BatchCloseReason` | DONE — verified live: `close_reason: "slaughter"` returns 422 |
| T-EX04-07 | Remove `_Animal_FutureRelease` model and `AnimalStatus` enum | DONE — also removed the dormant multi-species `Species` enum (frontend + backend), since it was unused outside that skeleton |
| T-EX04-08 | Remove RFID/tag-number-shaped fields tied to individual-bird tracking | DONE — removed along with `_Animal_FutureRelease` (those fields only existed on that model) |
| T-EX04-09 | Update `scripts/seed/seed_livestock.py` to seed batches directly as their final status (no quarantine-then-activate step) | DONE — demo batch now inserted directly as `completed`; `seed_notifications.py`'s quarantine/activation narrative notifications removed, `config.py`'s unused `BATCH_ACTIVATED` constant removed, `verify.py`'s stale building/section/status assertions corrected |
| T-EX04-10 | Update all frontend status-label/badge maps (`DashboardPage.tsx`, `BatchListPage.tsx`, `BatchDetailPage.tsx`, `ReportsPage.tsx`) to the new 2-value set | DONE — also fixed `FinancePage.tsx` (caught by `tsc --noEmit`, not grep) |
| T-EX04-11 | Remove the "Faollashtirish" (Activate) button and `quarantine_end_date` info card from `BatchDetailPage.tsx` | DONE — also removed the now-dead `handleActivate` handler and `slaughter` close-reason option |
| T-EX04-12 | Update/replace `NewBatchPage.tsx`'s `zod` schema to match the new lifecycle | DONE — verified the form already had no `quarantine_end_date` field; no schema change needed |
| T-EX04-13 | Full grep verification: zero remaining quarantine/slaughter/RFID/individual-bird references outside governance docs | DONE — repo-wide grep confirms zero hits outside explanatory comments referencing this decision; built frontend bundle also confirmed clean |

## EX-05 — Batch Auto Naming

| Task ID | Description | Status |
|---|---|---|
| T-EX05-01 | Finalize naming convention with business owner | DONE — `decision_log.md` BMD-012: farm-prefixed sequential (`{FARM_CODE}-{YEAR}-{SEQ}`), fully automatic, no manual override |
| T-EX05-02 | Implement server-side identifier generation in `create_batch.py` | DONE — derives `FARM_CODE` from `Farm.name` via a cross-schema raw-SQL read (`AbstractBatchRepository.get_farm_name()`, module-boundary-safe); sequence via `count_batches_with_code_prefix()` |
| T-EX05-03 | Add database-level uniqueness constraint for the chosen scope (per-farm) | DONE — `infrastructure/postgres/migrations_v2/004_ex05_batch_auto_naming.sql`: `batch_code SET NOT NULL` + `UNIQUE (farm_id, batch_code)`; verified live with both a successful generation test and a rejected duplicate-insert test |
| T-EX05-04 | Update `NewBatchPage.tsx` to reflect the new convention | DONE — removed the "Partiya kodi" free-text input and its zod schema field entirely (fully automatic, no input needed) |
| T-EX05-05 | Remove the UUID-fragment fallback display logic from all frontend pages that show a batch identifier | DONE — `BatchListPage.tsx`, `BatchDetailPage.tsx`, `DashboardPage.tsx`, `ReportsPage.tsx`, and `FinancePage.tsx` (found via grep, not on the original list); `BatchReportPage.tsx` deliberately left as-is (separate, still-nullable `app/reporting` DTO, out of this phase's stated "frontend" scope) |

## EX-06 — Daily Feed Tracking Revision

| Task ID | Description | Status |
|---|---|---|
| T-EX06-01 | Update `record_feed.py`'s status-gate rule (`FEED_BATCH_NOT_ACTIVE`) to the new 2-state model | DONE (no code change needed) — the gate was already `status != ACTIVE`, which automatically inherited EX-04's enum collapse; verified live (422 on COMPLETED, 201 on ACTIVE) |
| T-EX06-02 | Confirm/expand `RecordFeedRequest` schema with business owner if any new field is wanted | DONE — reconfirmed sufficient via direct code read; no new field requested |
| T-EX06-03 | Regression test: historical feed records remain queryable after the status-model migration | DONE — verified live against the demo batch's historical (pre-EX-04) feed records |

## EX-07 — Daily Mortality Tracking Revision

| Task ID | Description | Status |
|---|---|---|
| T-EX07-01 | Update `record_mortality.py`'s status-gate rule (`MORTALITY_BATCH_NOT_ACTIVE`) to the new 2-state model | DONE (no code change needed) — gate already `status != ACTIVE`; verified live (422 on COMPLETED, 201 on ACTIVE) |
| T-EX07-02 | Regression test: `current_count` decrement and "exceeds current count" validation still work | DONE — verified live: exceeds-count rejected (422), valid record correctly decremented count by 2, reverted after test |
| T-EX07-03 | Confirm/expand `RecordMortalityRequest` schema with business owner if any new field is wanted | DONE — reconfirmed sufficient via direct code read; no new field requested |

## EX-08 — Daily Weight Tracking Revision

| Task ID | Description | Status |
|---|---|---|
| T-EX08-01 | Update `record_weight_sampling.py`'s status-gate rule (`WEIGHT_BATCH_NOT_ACTIVE`) to the new 2-state model | DONE (no code change needed) — gate already `status != ACTIVE`; verified live (422 on COMPLETED, 201 on ACTIVE) |
| T-EX08-02 | Regression test: average-weight and age_days computation still correct | DONE — verified live: 150kg/100 sample → 1.500 kg avg, age_days=8 computed correctly |
| T-EX08-03 | Confirm/expand `RecordWeightRequest` schema with business owner if any new field is wanted | DONE — reconfirmed sufficient via direct code read; no new field requested |

## EX-09 — Medication Workflow Alignment

| Task ID | Description | Status |
|---|---|---|
| T-EX09-01 | Verify current status-gating state of `MedicationRecord` creation (research, not assumption) | DONE — found no creation pathway existed at all (no use case/repo/endpoint/UI); raised to the user, decision recorded as BMD-013 |
| T-EX09-02 | Add `ACTIVE`-only status gate to medication recording, if not already present | DONE — built the full create/list CRUD plumbing (DTOs, repository, use cases, endpoint, frontend UI) with the gate included from the start, since none of the plumbing existed to add a gate to |
| T-EX09-03 | Confirm vaccination recording is left untouched (verification only, per BMD-008) | DONE — `record_vaccination.py` and all other vaccination files confirmed unmodified |

## EX-10 — Inventory Linkage Hardening

| Task ID | Description | Status |
|---|---|---|
| T-EX10-01 | Write cost/benefit note on FK-hardening for `Warehouse.farm_id`, `StockMovement.warehouse_id`, `FeedConsumption.feed_inventory_item_id` | DONE — `decision_log.md` BMD-014: zero orphans, recommend proceed |
| T-EX10-02 (conditional on T-EX10-01's recommendation) | Add real FK constraints, after a zero-orphan data check | DONE — `infrastructure/postgres/migrations_v2/005_ex10_inventory_linkage_hardening.sql`; zero-orphan check performed before writing the migration, not after |
| T-EX10-03 | Regression test: Inventory module's page routing/independence unaffected | DONE — no route/page files touched; module boundary lint clean; negative-path FK rejection verified live with zero orphaned rows left behind |

## EX-11 — Finance Improvements — **VERIFIED_COMPLETE**

Business-owner scope (verbatim, see `decision_log.md` BMD-015): track supplier
debt, track customer debt, track partial payments, track outstanding
balances, show debtor/creditor summary in Finance. Explicitly excludes
budgeting, forecasting, and advanced accounting — MVP focused on real
poultry farm operations.

| Task ID | Description | Status |
|---|---|---|
| T-EX11-01 | Obtain business-owner clarification on what "Finance Improvements" should concretely include | DONE — exact scope provided directly by business owner, recorded verbatim in `decision_log.md` BMD-015 |
| T-EX11-02 | Verify (grep) that no slaughter-specific cost/sale category exists anywhere in Finance | DONE — `grep -rniE "slaughter\|so'yish" app/finance` returned zero matches |
| T-EX11-03 | Extend `SalePaymentStatus` enum with `PARTIAL`; add `amount_paid`/`outstanding_amount` to `SaleRecord`, server-computed from amount paid vs total | DONE — `app/finance/domain/models/finance.py` |
| T-EX11-04 | Add new `Supplier` model (minimal: farm_id, name, phone, address, is_active) | DONE — `app/finance/domain/models/finance.py` |
| T-EX11-05 | Add `supplier_id`/`amount_paid`/computed `outstanding_amount`+`payment_status` to `Expense` | DONE — `app/finance/domain/models/finance.py` |
| T-EX11-06 | New use cases: `record_sale_payment`, `record_expense_payment`, `create_supplier`, `list_suppliers`, `get_debtor_creditor_summary` | DONE — `app/finance/application/use_cases/` |
| T-EX11-07 | New/extended DTOs, repositories (`update`, `list_outstanding_by_farm`), and endpoints (`PATCH /sales/{id}/payment`, `PATCH /expenses/{id}/payment`, `POST`/`GET /suppliers/`, `GET /debtors-creditors-summary`) | DONE — `app/finance/application/dtos/`, `app/finance/domain/repositories/`, `app/finance/infrastructure/database/repositories/`, `app/finance/api/v1/endpoints/` |
| T-EX11-08 | SQL migration adding `suppliers` table, `expenses.supplier_id`/`amount_paid`, `sale_records.amount_paid`, with data-preserving backfill | DONE — `infrastructure/postgres/migrations_v2/006_ex11_finance_debt_tracking.sql`, applied live, zero-orphan backfill verified |
| T-EX11-09 | Frontend: `types/index.ts`, `batchService.ts` (`supplierService`, `debtService`, payment-recording calls), `FinancePage.tsx` (new Qarzlar/debt tab, supplier picker, partial-payment forms), `BatchDetailPage.tsx` badge consistency fix | DONE |
| T-EX11-10 | Live regression: positive path (partial sale payment, overpay clamp, supplier creation, expense debt, payment completion) and negative path (zero/negative amount rejected with 422) verified; test artifacts cleaned up, exact pre-test row counts/values restored | DONE |

## EX-12 — Reporting Improvements — **VERIFIED_COMPLETE**

Business-owner scope (verbatim intent, see `decision_log.md` BMD-016): Cross-Farm and Cross-Batch Trend Reporting — batch performance comparison, mortality trends, weight growth trends, feed consumption trends, revenue and profit trends, farm-to-farm comparison. Viewable in the Reports section, using charts and tables. Explicitly excludes scheduled reports, email delivery, Telegram delivery, advanced forecasting — "keep reporting focused on operational poultry farm analytics."

| Task ID | Description | Status |
|---|---|---|
| T-EX12-01 | Obtain business-owner clarification on what "Reporting Improvements" should concretely include | DONE — candidates presented directly in prose (per BMD-015's lesson); business owner provided exact scope, recorded verbatim in `decision_log.md` BMD-016 |
| T-EX12-02 | Remove quarantine-count and slaughter-close-reason references from the existing batch performance card | DONE — confirmed via grep that none exist in `app/reporting` or `ReportsPage.tsx` (already cleaned up by EX-04; only a documenting comment remains, no actual code) |
| T-EX12-03 | New `GetFarmBatchPerformanceUseCase`: lists a farm's batches and runs the existing `GenerateBatchReportUseCase` concurrently for each, sorted chronologically by `placement_date` — single dataset serving batch comparison + all four trend chart types | DONE — `app/reporting/application/use_cases/get_farm_batch_performance.py` |
| T-EX12-04 | New `GetFarmComparisonUseCase`: aggregates per-batch data across multiple farms (sum totals, average rates) into one row per farm, for farm-to-farm comparison | DONE — `app/reporting/application/use_cases/get_farm_comparison.py`, new `FarmComparisonRow` DTO |
| T-EX12-05 | New endpoints: `GET /reports/farms/{farm_id}/batch-performance`, `GET /reports/farm-comparison?farm_ids=...`; new `LivestockClient.list_batches()` | DONE — `app/reporting/api/v1/endpoints/reports.py`, `app/reporting/infrastructure/clients/livestock_client.py` |
| T-EX12-06 | Bug fix: `generate_batch_report.py` read the wrong field names (`mortality_rate_pct`/`survival_rate_pct`) from the mortality summary, causing every batch report's mortality rate to be silently null since before EX-12 — fixed to read the correct `mortality_rate` field and source `survival_rate_pct` from the batch's own `survival_rate` | DONE — required for the "mortality trends" deliverable to render real data; verified live before/after, existing single-batch JSON/PDF endpoints re-verified unaffected |
| T-EX12-07 | Frontend: new "Tendensiyalar" (Trends) tab in `ReportsPage.tsx` — batch comparison table, mortality/weight/feed/revenue-profit trend line charts (`recharts`, previously an unused dependency), farm-to-farm comparison bar chart + table; existing per-batch card grid moved under a "Partiyalar" tab | DONE |
| T-EX12-08 | New `reportService.getFarmBatchPerformance()`/`getFarmComparison()`; new `FarmComparisonRow` frontend type | DONE — `frontend/src/services/reportService.ts`, `frontend/src/types/index.ts` |
| T-EX12-09 | Live regression: positive path (batch-performance and farm-comparison endpoints tested against real seeded data, through the monolith directly and through nginx) and negative path (malformed `farm_ids` UUID — found returning 500, fixed to 422; empty-batches farm returns empty list, not an error) verified | DONE |
| T-EX12-10 | `py_compile`, `scripts/check_module_boundaries.py`, frontend `tsc --noEmit` all clean | DONE |

## EX-13 — Farm Detail View Redesign — **VERIFIED_COMPLETE**

| Task ID | Description | Status |
|---|---|---|
| T-EX13-01 | Add a batches-for-this-farm section to `FarmDetailPage.tsx` using the existing `farm_id`-filtered batch query | DONE — new "Partiyalar" table section added, loaded via the existing `GET /batches/?farm_id=...` (`batchService.listBatches`), no backend change |
| T-EX13-02 | Evaluate whether a new composite "farm detail + batch summary" backend endpoint is needed, or the existing per-call approach suffices | DONE — existing per-call approach suffices; this section only needs fields already on `BatchResponse` (batch_code, species, status, current_count, survival_rate, placement_date), no cross-module aggregation like EX-12's reporting trends required |
| T-EX13-03 | Reflect EX-04's new batch status set and EX-05's new naming convention in this page's batch display | DONE — status badge uses the same ACTIVE/COMPLETED labels as `ReportsPage.tsx`/`FinancePage.tsx`; `batch_code` (EX-05 auto-naming) displayed and linked to `/livestock/{id}` |
| T-EX13-04 | Reflect EX-03's simplified `SectionType` catalogue in this page's section display/selector | DONE — confirmed already correct (production/isolation/storage, no quarantine) prior to this phase; no change needed |
| T-EX13-05 | Regression test: existing Building/Section inline create/edit forms still function | DONE — `handleAddBuilding`/`handleAddSection` and their JSX were not modified; verified live that the backing `GET /farms/{id}/buildings` endpoint still returns correct data after the change |

## EX-14 — Dashboard Redesign — **VERIFIED_COMPLETE**

| Task ID | Description | Status |
|---|---|---|
| T-EX14-01 | Remove quarantine-denominated stat cards from `DashboardPage.tsx` | DONE — verified already satisfied before this phase started (mechanical consequence of EX-04); only 2 non-quarantine stat cards exist (Faol partiyalar, Faol parrandalar) |
| T-EX14-02 | Finalize the new analytics KPI/chart set (coordinate with EX-12's clarification outcome) | DONE — FCR/profit trend chart + multi-farm KPI rollup table (batch count, avg FCR, avg mortality %, total profit), both reusing EX-12's `GetFarmBatchPerformanceUseCase`/`GetFarmComparisonUseCase` exactly as anticipated in `phase_dependencies.md` |
| T-EX14-03 | Implement at least one trend/time-series visualization, backed by new `app/reporting` aggregation capability | DONE — `recharts` line chart (FCR + gross profit per batch, chronological) via `reportService.getFarmBatchPerformance()`; no new backend endpoint needed, reused EX-12's |
| T-EX14-04 | Confirm Dashboard remains the post-login landing page (no routing change) | DONE — confirmed `App.tsx` still routes `/` to `DashboardPage`, unchanged |
| T-EX14-05 | Confirm Dashboard content stays read-only/analytical, with no duplication of FarmDetailPage's operational controls | DONE — new sections are chart/table only (no create/edit forms); existing "Active batches" table and quick-link cards (already read-only navigation, not inline management) left as-is |

## EX-15 — User Management Revision — **VERIFIED_COMPLETE**

| Task ID | Description | Status |
|---|---|---|
| T-EX15-01 | Update `UsersPage.tsx` to allow Account-scoped (multi-farm) user listing/creation | DONE — backend `GET /users/` lists account-wide via new `list_by_account` when `farm_id` is omitted (decision_log.md BMD-017); frontend now calls it with no farm filter by default |
| T-EX15-02 | Add farm-selection (or "all farms in account") capability to the create/edit-user flow | DONE — new farm `<select>` added to the create-user modal, populated from the account's own `farmService.listFarms()`; new "Ferma" column added to the user table |
| T-EX15-03 | Regression test: RBAC role/permission union logic is unchanged | DONE — `User.has_permission()`/`Role.has_permission()` not touched; verified via `configure_mappers()` and live login/auth flow still working correctly after the change |
| T-EX15-04 | Negative-path test: cross-account user-management access is denied | DONE — verified live: creating a user against another account's farm, and listing users filtered by another account's farm, both correctly return HTTP 404 with zero rows leaked; enforcement reuses EX-02's existing `GetFarmUseCase` account check transitively via a new in-process `FarmClient`, per decision_log.md BMD-017 |

## EX-16 — Archive System

| Task ID | Description | Status |
|---|---|---|
| T-EX16-01 | Design `is_archived` flag/mechanism on `Batch` (and evaluate whether `Farm` needs it too) | DONE — `is_archived`/`archived_at`/`archived_by` added to `Batch` (migration `007_ex16_archive_system.sql`); `Farm` evaluated and explicitly decided against — the business owner's policy only covers batches, decision_log.md BMD-018 |
| T-EX16-02 | Decide archive trigger: manual, time-based after COMPLETED, or both | DONE — manual only, per the business owner's explicit policy (decision_log.md BMD-018); automatic/scheduled/time-based archiving and retention policies are explicitly out of scope |
| T-EX16-03 | Decide who can un-archive (role/permission requirement) | DONE — "Account Owner" and "Farm Director" per policy, mapped onto the existing `farm_owner` role (+ `super_admin`) since neither named role exists in the RBAC catalog and adding them is out of scope (decision_log.md BMD-018) |
| T-EX16-04 | Implement archive/un-archive API and exclude archived batches from default Dashboard/Farm-detail views | DONE — `POST /batches/{id}/archive`, `POST /batches/{id}/unarchive`; `GET /batches/` `archived` filter (default `false` = active-only, used unchanged by Dashboard/FarmDetailPage); new "Arxiv" tab in `BatchListPage.tsx` |
| T-EX16-05 | Verify archived batches remain fully queryable/exportable via Reports (no auditability loss) | DONE — Reports' Trends tab requests `archived=all` with a Faol/Arxivlangan/Barchasi filter toggle; verified live an archived batch still appears in `/reports/farms/{id}/batch-performance?archived=all` with `is_archived: true` |
| T-EX16-06 | Explicit negative test: no code path performs a hard delete as part of archiving | DONE — code review confirms no `DELETE` statement was added; live test verified mortality/expense record counts for the archived test batch were unchanged before/after an archive→unarchive cycle |

---

## Cross-Phase Closing Tasks

| Task ID | Description | Status |
|---|---|---|
| T-EXALL-01 | Full-codebase grep sweep for quarantine/slaughter/RFID/individual-bird references; confirm zero hits outside governance/historical documents | NOT_STARTED |
| T-EXALL-02 | End-to-end smoke test across the full priority chain (Account → Farm → Building → Batch → Daily Feed/Mortality/Weight → Completed → Archived → Reported) | NOT_STARTED |
| T-EXALL-03 | Append a summary entry to `project_state.md`'s Change Ledger documenting the v2 execution, per the repository's append-only history convention | NOT_STARTED |

---

*Backlog Items v2 — AgroVision Business Model Revision Initiative — 2026-06-18*
*Planning only. Every item above is NOT_STARTED. No implementation has been performed or authorized.*

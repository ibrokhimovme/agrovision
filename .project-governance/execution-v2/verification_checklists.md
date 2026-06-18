# AgroVision — Verification Checklists v2

**Status:** PLANNING ONLY — these checklists are not yet executable since no implementation has occurred. They define what "done" means for each phase, to be checked off only after that phase is actually implemented and tested.
**Date:** 2026-06-18
**Companion documents:** `master_roadmap.md`, `execution_phases.md`, `phase_dependencies.md`, `backlog_items.md`
**Format convention:** mirrors `project_state.md`'s Phase Verification Records and `migration_verification.md`'s gate style, so future sessions can apply the same "verify, don't trust labels" discipline used throughout this repository's history.

---

## EX-01 — Account Foundation — VERIFIED_COMPLETE (2026-06-18)

- [x] `Account` entity exists with at least: id, name, status (active/inactive), created_at — `app/identity/domain/models/account.py`, table `identity.accounts`
- [x] `Farm.account_id` FK exists and is enforced (not a bare column) — confirmed via live `\d farm.farms`: `FOREIGN KEY (account_id) REFERENCES identity.accounts(id)`
- [x] Every existing Farm row has a valid `account_id` after migration (zero orphaned farms) — verified: 0 orphaned among real data; 1 pre-existing test row with an invalid (zero-UUID) `owner_user_id` predates this work and is documented, not silently backfilled with fabricated data
- [x] At least one User-to-Account relationship path exists and is testable — verified live: `owner@toshkent-broiler.uz` and the platform admin both resolve to real `identity.accounts` rows; all 5 Toshkent Broiler Ferma staff users carry the same `account_id`
- [x] No regression: existing farm-scoped queries (batches by farm, buildings by farm) still return correct results after the Account layer is introduced — verified live: login (200), farms list (200), farm detail (200), batches list (200), users list (200) all passed against the rebuilt container
- [x] Decision recorded on Alembic wiring — `decision_log.md` BMD-009: direct schema bootstrap continues, Alembic stays deferred
- [x] (Additional, beyond the original checklist) Write-path regression check: farm create (201) and delete (204) both function correctly with the new nullable `account_id` column present

## EX-02 — Farm Management Revision — VERIFIED_COMPLETE (2026-06-18)

- [x] Farm create/edit forms (backend + frontend) include account context — backend: yes (`account_id` derived server-side, exposed read-only on `FarmResponse`); frontend: no change needed, confirmed transparent
- [x] Farm list query is scoped by the requesting user's Account, not just by personal ownership — verified live: owner sees exactly their account's farms
- [x] Existing active-batch delete-guard behavior is unchanged (regression check, not a new feature) — **finding, not a pass/fail**: no such guard exists in the backend today (frontend text claims one); documented as a pre-existing gap in `backlog_items.md` T-EX02-04, not introduced or fixed by this phase
- [x] A user from Account A cannot see or modify a Farm belonging to Account B (negative-path test) — verified live: 404 on cross-account GET, 200 on same-account GET
- [x] (Discovered during verification, addressed) Super-admin bypass must use the `super_admin` role, not "account_id is None" — a real super-admin in live data owns an Account too; fixed before declaring this phase complete (`decision_log.md` BMD-010)

## EX-03 — Building & Section Simplification — VERIFIED_COMPLETE (2026-06-18)

- [x] `SectionType.QUARANTINE` no longer exists in the backend enum — verified live: API returns 422 enum-validation error for `section_type: "quarantine"`
- [x] `SectionType.ISOLATION` still exists, unchanged (explicit non-removal per BMD-002) — verified present in enum, frontend select, and via a live create/cleanup test of a still-valid type
- [x] Frontend section-type select no longer offers "Karantin" as an option — verified in `FarmDetailPage.tsx`; also found and fixed a second leftover reference in `NewBatchPage.tsx`'s section-dropdown label (caught by `tsc --noEmit`, not by grep alone)
- [x] Seed data no longer creates a "Karantin bloki"/"Karantin bo'limi" building/section — `seed_farm.py` updated, unused ID constants removed from `config.py`
- [x] No remaining database rows reference the removed quarantine section type after migration — verified live: 0 quarantine sections, 0 "Karantin"-named buildings, after applying `002_ex03_section_simplification.sql` (which itself re-verified zero batch references before deleting, via a `RAISE EXCEPTION` guard)

## EX-04 — Batch Lifecycle Simplification — VERIFIED_COMPLETE (2026-06-18)

- [x] `BatchStatus` enum contains exactly `{ACTIVE, COMPLETED}` — no third value — `app/poultry/domain/models/animal.py`; confirmed live via `configure_mappers()` + enum dump
- [x] `quarantine_end_date` column removed — dropped via `infrastructure/postgres/migrations_v2/003_ex04_batch_lifecycle_simplification.sql`; verified live: 0 rows in `information_schema.columns` for that column
- [x] `QUARANTINE_MINIMUM_7_DAYS` rule removed — the entire `activate_batch.py` use case (and its `/activate` endpoint) was deleted, since "activation" as a distinct action no longer exists once there is no quarantine stage to activate out of
- [x] New batches are created directly in `ACTIVE` status — verified via a real live `POST /batches/` call (test batch `EX04-VERIFY-TEST`, cleaned up after verification)
- [x] `BatchCloseReason.slaughter` no longer exists in the enum — verified live: `POST /batches/{id}/close` with `close_reason: "slaughter"` returns 422
- [x] `_Animal_FutureRelease` model, `AnimalStatus` enum, `Species` (multi-species) enum, and RFID/tag-shaped fields removed from both backend (`app/poultry/domain/models/animal.py`) and frontend (`frontend/src/types/index.ts`) — verified via repo-wide grep: zero references remaining outside historical/governance documents
- [x] State machine `VALID_TRANSITIONS` reflects exactly `ACTIVE → COMPLETED` (one transition) — `Batch.transition_to()`
- [x] Seed scripts updated — `seed_livestock.py` inserts the demo batch directly as `completed` (no two-step quarantine-then-activate pattern existed or remains); `seed_notifications.py`'s quarantine-ending/activated notification entries removed; `config.py`'s unused `BATCH_ACTIVATED` constant removed; `verify.py`'s stale EX-03-era assertions (3 buildings/3 sections/1 quarantine section, status='closed') corrected to match current seed shape
- [x] Regression check: feed/mortality/weight daily-ops endpoints still function correctly against an ACTIVE batch — verified live: mortality record against the `COMPLETED` demo batch rejected with `MORTALITY_BATCH_NOT_ACTIVE` (422), same call against an `ACTIVE` batch succeeds (201); test record cleaned up after verification
- [x] (Additional, beyond the original checklist) Frontend fully updated and rebuilt: `BatchListPage.tsx`, `BatchDetailPage.tsx` (removed "Faollashtirish" button, `quarantine_end_date` info card, `handleActivate`), `DashboardPage.tsx` (removed quarantine stat cards and the now-invalid `status: 'quarantine'` API call), `ReportsPage.tsx`, `FinancePage.tsx` (caught by `tsc --noEmit`, not grep — a `status === 'closed'` comparison with no remaining overlap), `batchService.ts` (removed `activateBatch()`, `quarantine_end_date` payload fields) — confirmed via `tsc --noEmit` (clean) and a rebuilt container serving a bundle with zero "quarantine"/"karantin"/"slaughter" strings
- [x] (Additional, beyond the original checklist) Live data migration applied and verified: 2 pre-existing `quarantine` batches → `active`, 1 `closed` batch → `completed` (decision recorded as BMD-011); post-migration `SELECT DISTINCT status` returns only `{active, completed}`

## EX-05 — Batch Auto Naming — VERIFIED_COMPLETE (2026-06-18)

- [x] A finalized naming convention is documented and agreed with the business owner before implementation begins — presented via `AskUserQuestion` (farm-prefixed sequential vs. building/section-prefixed vs. date+sequence; fully-automatic vs. server-generated-with-override); decision recorded as `decision_log.md` BMD-012 before any code was written
- [x] `batch_code` is mandatory — no batch can be created without a valid identifier — `Batch.batch_code` is `nullable=False`; `CreateBatchRequest` has no client-facing `batch_code` field at all (always server-generated)
- [x] The identifier is fully server-generated (no manual override, per the business owner's chosen policy) — verified live: a `POST /batches/` call that included a `batch_code: "HACKED-001"` field in the payload was silently ignored (Pydantic drops unknown fields), server generated `TOSHKENT-2026-003` instead
- [x] A database-level uniqueness constraint enforces no duplicate identifiers per farm — `infrastructure/postgres/migrations_v2/004_ex05_batch_auto_naming.sql` adds `UNIQUE (farm_id, batch_code)`; verified live: a direct `INSERT` reusing an existing farm+code pair was rejected by Postgres with a constraint-violation error
- [x] Frontend no longer falls back to displaying a raw UUID fragment as a batch's name under any code path — removed from `BatchListPage.tsx`, `BatchDetailPage.tsx`, `DashboardPage.tsx`, `ReportsPage.tsx`, `FinancePage.tsx` (the last one caught by grep, not by the original task list, since `Batch.batch_code` became a non-optional `string` and the `??` fallback there was dead code); `frontend/src/pages/reports/BatchReportPage.tsx`'s fallback was deliberately left alone — it reads a separate, still-nullable `BatchReport` DTO from the `app/reporting` module, which is out of EX-05's explicitly stated "frontend" scope
- [x] (Additional, beyond the original checklist) The previously-existing (but UI-unused) ability to edit `batch_code` via `PATCH /batches/{id}` was removed from `UpdateBatchRequest` too — left in place, it would have silently reintroduced the manual-override path the business owner explicitly declined

## EX-06 — Daily Feed Tracking Revision — VERIFIED_COMPLETE (2026-06-18)

- [x] Feed recording's status-gate rejects `COMPLETED` batches and accepts `ACTIVE` batches (quarantine-specific wording/logic removed) — verified this required **no code change**: `record_feed.py`'s gate was already `batch.status != BatchStatus.ACTIVE`, which automatically tracks whatever `BatchStatus` contains; EX-04's enum collapse already made this correct. Verified live: `POST .../feed` against the `COMPLETED` demo batch → 422 `FEED_BATCH_NOT_ACTIVE`; same call against an `ACTIVE` batch → 201 (test record cleaned up after)
- [x] Existing request schema fields (`feed_date`, `quantity_kg`, `water_liters`, `feed_type`, `age_days`, `feed_inventory_item_id`, `notes`) reconfirmed sufficient — read `feed_dtos.py` directly; matches exactly what `execution_phases.md` listed as adequate; no business-owner request for additional fields exists in the current instruction, so none were added
- [x] Regression check: historical feed records (created under the old 3-status model) remain readable/queryable without error — verified live: `GET .../feed` on the demo batch (originally seeded under the old `closed` status, now `completed`) returns its full historical record set correctly
- [x] (Additional, beyond the original checklist) Repo-wide grep confirms zero quarantine/karantin wording anywhere in the feed use case, DTOs, endpoint, or frontend feed-recording UI

## EX-07 — Daily Mortality Tracking Revision — VERIFIED_COMPLETE (2026-06-18)

- [x] Mortality recording's status-gate rejects `COMPLETED` and accepts `ACTIVE` (quarantine-specific wording/logic removed) — verified this required **no code change**, same finding as EX-06: `record_mortality.py`'s gate was already `status != BatchStatus.ACTIVE`. Verified live: 422 `MORTALITY_BATCH_NOT_ACTIVE` on the `COMPLETED` demo batch; 201 on an `ACTIVE` batch
- [x] `current_count` decrement logic and the "cannot exceed current count" validation are confirmed unchanged and still working — verified live: a `quantity: 999999` request against an `ACTIVE` batch (current_count 4992) → 422 `MORTALITY_EXCEEDS_CURRENT_COUNT`; a valid `quantity: 2` request correctly decremented `current_count` from 4992 → 4990 (test record + count change reverted after verification)
- [x] Existing request schema fields reconfirmed sufficient — `quantity`, `deceased_at`, `cause_category`, `cause_description`, `disposal_method` all present in `mortality_dtos.py`, matching `execution_phases.md`'s adequacy note exactly; no new field requested
- [x] Regression check: historical mortality records remain readable/queryable — confirmed via the demo batch's mortality summary (8 historical events, 42 total deaths, seeded under the old 3-status model) still resolving correctly
- [x] (Additional, beyond the original checklist) Repo-wide grep confirms zero quarantine/karantin wording anywhere in the mortality use case, DTOs, or endpoint

## EX-08 — Daily Weight Tracking Revision — VERIFIED_COMPLETE (2026-06-18)

- [x] Weight sampling's status-gate rejects `COMPLETED` and accepts `ACTIVE` (quarantine-specific wording/logic removed) — verified this required **no code change**, same finding as EX-06/EX-07: `record_weight_sampling.py`'s gate was already `status != BatchStatus.ACTIVE`. Verified live: 422 `WEIGHT_BATCH_NOT_ACTIVE` on the `COMPLETED` demo batch; 201 on an `ACTIVE` batch
- [x] ADG/FCR-supporting computation (average weight, age_days) confirmed unchanged and still correct — verified live: a `sample_size: 100, total_sample_weight_kg: 150` request correctly computed `average_weight_kg: 1.500` and `age_days: 8` (measured 8 days after the batch's `placement_date`); test record deleted after verification
- [x] Existing request schema fields reconfirmed sufficient — `sample_size`, `total_sample_weight_kg`, `measured_at`, `notes` all present in `weight_dtos.py`, matching `execution_phases.md`'s adequacy note exactly; no new field requested
- [x] Regression check: historical weight records remain readable/queryable — confirmed via the demo batch's 6 historical samplings (seeded under the old 3-status model) still resolving correctly
- [x] (Additional, beyond the original checklist) Repo-wide grep confirms zero quarantine/karantin wording anywhere in the weight-sampling use case, DTOs, or endpoint

## EX-09 — Medication Workflow Alignment — VERIFIED_COMPLETE (2026-06-18)

- [x] Verification performed (not assumed) on whether `MedicationRecord` creation was already status-gated before this phase started — found it had **no creation pathway at all**: no use case, repository, endpoint, or frontend UI existed anywhere; only a dormant ORM model + seed-populated table. Presented to the user via `AskUserQuestion`; decision to build the missing plumbing recorded as `decision_log.md` BMD-013.
- [x] A gate consistent with feed/mortality/weight (`ACTIVE`-only, `COMPLETED` rejected) was added as part of building the new `record_medication.py` use case — verified live: 422 `MEDICATION_BATCH_NOT_ACTIVE` on the `COMPLETED` demo batch; 201 on an `ACTIVE` batch
- [x] Vaccination recording confirmed untouched (explicitly out of scope per BMD-008) — `record_vaccination.py` not modified; grep confirms no changes to any vaccination file
- [x] (Additional, beyond the original checklist) Full CRUD plumbing built: DTOs, abstract + SQLAlchemy repository, two use cases, a new `medication.py` endpoint (wired into `router.py`), and a complete frontend record/history UI in `BatchDetailPage.tsx` with a medicine picker sourced from `inventory.stock_items` (`item_type === 'medicine'`). Verified live: create, list, and the historical 2 seed records all resolve correctly (test record created and deleted during verification, original 2-row state restored); `tsc --noEmit`, `py_compile`, `scripts/check_module_boundaries.py`, and `configure_mappers()` all clean; built frontend bundle confirmed to contain the new UI text

## EX-10 — Inventory Linkage Hardening — VERIFIED_COMPLETE (2026-06-18)

- [x] A cost/benefit note exists recommending whether to proceed with FK-hardening — `decision_log.md` BMD-014: zero orphans found, near-zero migration risk, real named benefit → proceed with all three
- [x] All three relationships have real FK constraints, and existing data passed a zero-orphan check **before** the constraint was added — verified live via direct SQL on all three tables, zero orphans found prior to writing `005_ex10_inventory_linkage_hardening.sql`; constraints confirmed present afterward via `\d`
- [x] Inventory's module boundary, page routing, and independence from Farm/Batch navigation are unchanged — no route/page files touched; `scripts/check_module_boundaries.py` clean (FK target strings are not Python imports, so the lint rule is unaffected)
- [x] (Additional, beyond the original checklist) Negative-path regression: a direct SQL insert of a warehouse with a random `farm_id`, and a stock movement with a random `warehouse_id`, were both correctly rejected by the new constraints with zero orphaned rows left behind; normal warehouse/feed/medication endpoint reads confirmed unaffected

## EX-11 — Finance Improvements — VERIFIED_COMPLETE (2026-06-18)

- [x] Business-owner clarification obtained on what "Finance Improvements" concretely means — exact scope provided directly (not via structured options), recorded verbatim in `decision_log.md` BMD-015
- [x] Finalized scope note written into `backlog_items.md`'s EX-11 section
- [x] No slaughter-specific cost/sale category exists anywhere in Finance — confirmed via `grep -rniE "slaughter|so'yish" app/finance` (zero matches)
- [x] Supplier debt tracking: new `Supplier` model + `Expense.supplier_id`/`amount_paid`; verified live (create supplier, record expense with partial debt, record completing payment, confirm `payment_status` transitions pending→partial→paid correctly)
- [x] Customer debt tracking: `SaleRecord.amount_paid`/`outstanding_amount`, server-computed `payment_status` (now 3-valued: paid/pending/partial); verified live against the pre-existing 'pending' UAT sale record
- [x] Partial payments: `PATCH /sales/{id}/payment` and `PATCH /expenses/{id}/payment` record incremental payments; verified live, including an overpayment attempt that correctly clamped to the exact outstanding amount rather than erroring
- [x] Outstanding balances: `outstanding_amount` computed property on both `SaleRecord` and `Expense`
- [x] Debtor/creditor summary shown in Finance: new `GET /debtors-creditors-summary` endpoint + new "Qarzlar" tab in `FinancePage.tsx`, aggregating by customer (name+phone) and by real `Supplier` entity; verified live with correct totals before and after test data changes
- [x] No budgeting, forecasting, or advanced accounting introduced — confirmed by design (no budget/forecast model, table, or endpoint added); dormant `SalesOrder`/`Payment`/`Customer`/`PaymentStatus` left untouched, not revived
- [x] Migration `006_ex11_finance_debt_tracking.sql` applied live with a data-preserving backfill (zero-`NULL` check passed); all test artifacts removed afterward and exact pre-test row counts/values (14 expenses, 0 suppliers, the 2 original sale_records) confirmed restored
- [x] `py_compile`, `scripts/check_module_boundaries.py`, `configure_mappers()`, and frontend `tsc --noEmit` all clean

## EX-12 — Reporting Improvements — VERIFIED_COMPLETE (2026-06-18)

- [x] Business-owner clarification obtained on what "Reporting Improvements" concretely means — candidates presented directly in prose (per BMD-015's lesson), business owner specified Cross-Farm and Cross-Batch Trend Reporting, recorded verbatim in `decision_log.md` BMD-016
- [x] Finalized scope note written into `backlog_items.md`'s EX-12 section
- [x] The existing batch performance card no longer references quarantine count or slaughter as a close reason — confirmed via grep, zero matches in `app/reporting` and `ReportsPage.tsx` (already clean from EX-04)
- [x] Batch performance comparison: new `GET /reports/farms/{farm_id}/batch-performance` endpoint + table in the new "Tendensiyalar" tab; verified live against real seeded data
- [x] Mortality trends: line chart over `mortality_rate_pct`, chronologically ordered by batch placement date; required fixing a pre-existing field-name bug (`mortality_rate` vs `mortality_rate_pct`) that had been silently returning null in every batch report — fixed and verified live (non-null values before/after; existing single-batch JSON/PDF report endpoints re-verified unaffected by the fix)
- [x] Weight growth trends: line chart over `latest_avg_weight_kg`
- [x] Feed consumption trends: line chart over `total_feed_kg` and `fcr`
- [x] Revenue and profit trends: line chart over `total_revenue_uzs` and `gross_profit_uzs`
- [x] Farm-to-farm comparison: new `GET /reports/farm-comparison?farm_ids=...` endpoint, new `GetFarmComparisonUseCase` aggregating sum/average across farms, bar chart + table; verified live across all 4 seeded farms (3 with zero batches correctly show zero/null aggregates, not errors)
- [x] Reports viewable in the Reports section: new "Tendensiyalar" tab added alongside the existing "Partiyalar" tab in `ReportsPage.tsx`, no new route needed
- [x] Charts and tables used where appropriate: `recharts` (a previously-unused frontend dependency) for line/bar charts, HTML tables for the comparison/performance data grids
- [x] No scheduled reports, email delivery, Telegram delivery, or advanced forecasting introduced — confirmed by design (all new endpoints are synchronous on-demand `GET`s; no new tables, background jobs, or delivery-channel integration)
- [x] Negative-path regression: a malformed `farm_ids` UUID was found to return an uncaught 500, fixed to a proper 422; a farm with zero batches correctly returns an empty list rather than erroring
- [x] `py_compile`, `scripts/check_module_boundaries.py`, and frontend `tsc --noEmit` all clean; both endpoints additionally verified live end-to-end through nginx (matching real browser access), not just against the monolith directly

## EX-13 — Farm Detail View Redesign — VERIFIED_COMPLETE (2026-06-18)

- [x] `FarmDetailPage` displays the farm's batches — new "Partiyalar" table section, using the existing `farm_id`-filtered batch query (`GET /batches/?farm_id=...`); no new backend endpoint needed
- [x] Displayed batch data reflects the new `ACTIVE`/`COMPLETED` status set (no quarantine badge/label remains anywhere on this page) — confirmed via grep, zero quarantine references in the file before or after this change
- [x] Displayed batch identifiers reflect the new auto-naming convention from EX-05 — `batch_code` shown and linked to `/livestock/{id}`
- [x] Section-type display already reflected EX-03's simplified catalogue (production/isolation/storage) — confirmed unchanged, no quarantine label present
- [x] Regression: Building/Section inline create/edit forms untouched (`handleAddBuilding`/`handleAddSection` byte-for-byte unmodified); backing `GET /farms/{id}/buildings` endpoint re-verified live and still returns correct data
- [x] frontend `tsc --noEmit` clean; new batches section text confirmed present in the built bundle; both the farm-detail and batch-list API calls verified live through nginx with correct auth

## EX-14 — Dashboard Redesign — VERIFIED_COMPLETE (2026-06-18)

- [x] Quarantine-denominated stat cards ("Karantin" batch count, "Karantindagi parrandalar" bird count) no longer exist on the dashboard — confirmed already satisfied before this phase started (EX-04 mechanical fix); only 2 stat cards exist (Faol partiyalar, Faol parrandalar)
- [x] At least one genuine trend/analytics visualization exists (not just point-in-time counts) — FCR + gross profit line chart per batch (chronological), plus a multi-farm KPI rollup table (batch count, avg FCR, avg mortality %, total profit), both reusing EX-12's `GetFarmBatchPerformanceUseCase`/`GetFarmComparisonUseCase`
- [x] Dashboard remains the post-login landing page (confirmed unchanged per BMD-005 — this phase changes content, not navigational position) — verified `App.tsx` still routes `/` to `DashboardPage`
- [x] Dashboard does not duplicate FarmDetailPage's operational controls (read-only/analytical framing preserved, per BMD-005) — new sections are chart/table only, no create/edit forms added
- [x] frontend `tsc --noEmit` clean; new chart/table text confirmed present in the built bundle; both the farm-batch-performance and farm-comparison API calls verified live through nginx with correct auth, matching the exact calls the dashboard now makes

## EX-15 — User Management Revision — VERIFIED_COMPLETE (2026-06-18)

- [x] A Farm Owner/Account-admin user can view and manage users across every Farm within their Account, not just one farm — verified live: `GET /users/` with no `farm_id` returned all 5 users across the seeded Toshkent Broiler account
- [x] User creation/edit flow allows selecting which Farm(s) within the Account a new user should be scoped to — new farm `<select>` in the create-user modal, populated from the account's own farm list
- [x] Existing role/permission union logic (RBAC) is verified unchanged — `has_permission()` methods on `User`/`Role` not touched; `configure_mappers()` clean; live login/auth confirmed still working
- [x] A user from one Account cannot appear in or be managed from another Account's user-management view (negative-path test) — verified live: creating a user against, and listing users filtered by, a different account's farm both correctly returned HTTP 404 with zero rows leaked into the database
- [x] `account_id` now correctly set on newly-created users (previously always `NULL` — a pre-existing gap found and fixed, see decision_log.md BMD-017); `py_compile`, `scripts/check_module_boundaries.py`, `configure_mappers()`, and frontend `tsc --noEmit` all clean; all three calls `UsersPage.tsx` makes (`/users/`, `/farms/`, `/roles/`) verified live through nginx

## EX-16 — Archive System — VERIFIED_COMPLETE (2026-06-18)

- [x] An `is_archived` (or equivalent) flag/mechanism exists and is exposed via API — `is_archived`/`archived_at`/`archived_by` on `Batch`, exposed in `BatchResponse`/`BatchReportResponse`; migration `007_ex16_archive_system.sql` applied live, backfilled `is_archived=false` on all 4 existing rows with 0 nulls
- [x] Archiving a batch removes it from default/active views (Dashboard, Farm Detail batch list) without deleting any underlying data — verified live: archived `B-2026-001` disappeared from `GET /batches/?farm_id=...` default (`archived=false`) results while mortality/expense row counts for that batch (8/13) stayed identical before and after
- [x] An authorized user can un-archive a batch, restoring its visibility — verified live: `farm_owner` un-archived the batch via `POST /batches/{id}/unarchive`, and it reappeared in the default batch list immediately after
- [x] Archived batches remain fully queryable/exportable via Reports (per BR-019/VG-02 — auditability is never reduced by archiving) — verified live: `GET /reports/farms/{id}/batch-performance?archived=all` returned the archived batch with `is_archived: true`; `ReportsPage.tsx`'s Trends tab gained a Faol/Arxivlangan/Barchasi filter
- [x] No code path anywhere performs a hard delete as part of the archive action (explicit negative check, since this is the constraint BMD-007 exists to protect) — code review: `archive()`/`unarchive()` only mutate `is_archived`/`archived_at`/`archived_by`; no `DELETE` statement exists anywhere in the new code
- [x] Negative-path test: an unauthorized role cannot archive/un-archive — verified live: `farm_worker` attempting `POST /batches/{id}/unarchive` was correctly denied with HTTP 403
- [x] Negative-path test: an `ACTIVE` batch cannot be archived — verified live: attempting to archive an `ACTIVE` batch correctly returned HTTP 422 with `BATCH_ARCHIVE_REQUIRES_COMPLETED`
- [x] `py_compile`, `scripts/check_module_boundaries.py`, `configure_mappers()`, and frontend `tsc --noEmit` all clean; backend (`monolith`) and frontend Docker images rebuilt and verified serving the new code through nginx; all test state restored afterward (test batch unarchived, no rows added/removed)

---

## Cross-Phase Final Verification (run once all 16 phases are implemented)

- [ ] Full grep of the codebase for "quarantine"/"karantin" (case-insensitive) returns zero hits outside of governance/historical documents (`business-revision/`, `execution-v2/`, `monolith-migration/`, `project_state.md`'s change ledger, BRD/SRS source files which are never edited)
- [ ] Full grep for "slaughter"/"so'yish" (batch-close-reason context) returns zero hits outside governance/historical documents
- [ ] Full grep for RFID/tag-number/individual-animal-tracking code returns zero hits outside governance/historical documents
- [ ] A full smoke test (login → create farm under an account → create building/section → create batch with auto-generated name → record feed/mortality/weight → mark batch completed → view in archive → generate report) passes end-to-end
- [ ] `project_state.md`'s Change Ledger receives a new entry summarizing the v2 execution, in keeping with this repository's "never delete or overwrite history, always append" convention

---

*Verification Checklists v2 — AgroVision Business Model Revision Initiative — 2026-06-18*
*Planning only. No checklist item has been executed or verified yet — none can be, since no implementation has occurred.*

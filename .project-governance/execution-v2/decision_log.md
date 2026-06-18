# AgroVision — Business Model Revision: Decision Log

**Date:** 2026-06-18
**Status:** ACTIVE — governs all of `execution-v2/`
**Authority:** User instruction ("Using the Business Revision Report, rebuild the project roadmap... Highest priority: Account → Farm → Building → Batch → ...") — this instruction is treated as the business owner's sign-off on `business-revision/gap_analysis.md` §4's open questions (OQ-REV-01 through OQ-REV-07).
**Supersedes:** Open questions in `.project-governance/business-revision/gap_analysis.md` §4 are now CLOSED, as recorded below. The `business-revision/` documents are NOT edited or deleted (immutable history per governance convention) — this log records what changed and why.

Numbering convention: **BMD-0xx** ("Business Model Decision"), parallel to the migration initiative's `MD-0xx` convention in `monolith-migration/migration_decisions.md`.

---

### BMD-001 — Account is a new, real entity above Farm

**Resolves:** OQ-REV-05 (Gap Analysis §4.5)
**Decision:** AgroVision introduces a new `Account` entity that owns one or more `Farm` entities. This is **not** a no-op — it is a genuine new top-level entity, confirmed by the user's explicit priority chain: `Account → Farm → Building → Batch → ...`.
**Implication:** `Farm.owner_user_id` (today a bare column, 1 farm : 1 owner) must be reconsidered as `Farm.account_id` (FK to `Account`), with the account being the ownership/billing/tenancy boundary, and a Farm Owner user being associated with an `Account` rather than directly and singularly with one `Farm`. Exact cardinality (one user per account vs. multiple users per account with sub-roles) is scoped in EX-01, not decided in full here — this decision only confirms the entity must exist and sits above Farm.
**Out of scope for this decision:** whether `Account` introduces billing/subscription concepts — nothing in the request implies commercial/billing scope; `Account` is being introduced purely as an organizational/ownership container.

---

### BMD-002 — Quarantine is removed entirely, including as a section/place type

**Resolves:** OQ-REV-01 (partially), OQ-REV-02 (Gap Analysis §4.1, §4.2)
**Decision:** `BatchStatus.QUARANTINE` is removed. Allowed batch statuses become exactly `ACTIVE` and `COMPLETED`. `SectionType.QUARANTINE` is also removed — the user's "Remove: Quarantine workflows" is read as covering the place/type concept as well as the batch-status concept, since both exist solely to serve the quarantine business process (BP-03/BR-004) that no longer applies.
**Implication:** `quarantine_end_date` (column on `Batch`) and the `QUARANTINE_MINIMUM_7_DAYS` business rule in `activate_batch.py` are removed, not just renamed. The batch state machine becomes `ACTIVE → COMPLETED` (one transition only — see BMD-003 for what triggers the initial ACTIVE state).
**Note:** `SectionType.ISOLATION` is a separate, narrower concept (a sick-bird isolation area, not a mandatory new-arrival holding period) and is **not** automatically removed by this decision — it is explicitly out of scope for BMD-002 and is carried forward as-is unless a future decision addresses it. Flagged for confirmation in EX-03's scoping, not resolved here.

---

### BMD-003 — CLOSED is replaced by COMPLETED; slaughter is removed as a close reason

**Resolves:** OQ-REV-01 (Gap Analysis §4.1)
**Decision:** The terminal batch status is named `COMPLETED` (not `CLOSED`). Per the user's explicit "Remove: Slaughter workflows," the `BatchCloseReason` enum's `slaughter` value is removed. Remaining close reasons (sale, transfer, disease, other — exact final set to be confirmed in EX-04 scoping) describe how a batch reached COMPLETED, without a dedicated slaughter-specific workflow, slaughter documentation, or BP-14-style veterinary-clearance gate.
**Implication:** A new batch starts at `ACTIVE` directly (no QUARANTINE intermediate stage) and ends at `COMPLETED`. This is a two-state model, not three.

---

### BMD-004 — Individual bird tracking and RFID are permanently removed, not just MVP-deferred

**Resolves:** part of the new "Remove" list (not a prior open question — net-new instruction)
**Decision:** The dormant `_Animal_FutureRelease` model, its `AnimalStatus` enum, and any RFID/tag-number fields or hardware-interface references tied to individual-bird tracking are removed from the codebase and from forward-looking planning documents. Previously (ADR-003), these were preserved as inactive "future release" skeletons on the assumption AgroVision might expand to individual-animal/livestock tracking later. **This assumption is now explicitly overridden**: the platform is permanently batch-only for poultry, by this decision, not by temporary MVP scoping.
**Implication:** This is a stronger statement than ADR-003's original deferral — it changes "not now" to "not ever, by current design." A future reversal would require a new ADR, exactly as ADR-003 itself required a new decision to narrow scope from the original generic enterprise platform.

---

### BMD-005 — Dashboard remains the analytics landing page; Farms gets its own enhanced detail view

**Resolves:** OQ-REV-03 (Gap Analysis §4.3)
**Decision:** Both "Dashboard Redesign" and "Farm Detail View" appear as separate, independently named requirements in the user's instruction (items 1 and 3). This is read as confirming: Dashboard continues to exist as a distinct, analytics-focused landing page (per Business Revision Report §1) — it is not being replaced by Farms. Separately, Farm Detail View is enhanced to show its batches/buildings inline (per Business Revision Report §2). Farms becoming "the primary operational view" (original business principle) is interpreted as Farms being the place where day-to-day batch/building operations are *managed*, while Dashboard remains the place where cross-farm KPIs are *monitored* — these are complementary, not competing, views.

---

### BMD-006 — Batch naming becomes server-generated/auto-named, not optional free text

**Resolves:** OQ-REV-06 (Gap Analysis §4.6)
**Decision:** "Batch Auto Naming" is now an explicit requirement (item 4). The exact convention (farm-prefixed sequential, date+sequence, etc.) is scoped in EX-05, but the direction is settled: batch identification becomes **system-generated and mandatory**, replacing today's optional free-text `batch_code` and its accidental UUID-fragment fallback.

---

### BMD-007 — Archive System is authorized as new, additive-only work

**Resolves:** OQ-REV-07 (Gap Analysis §4.7)
**Decision:** "Archive System" is now an explicit requirement (item 9). Per the Business Revision Report §3's risk note, archiving must be implemented as an **additive visibility mechanism** (e.g. an `is_archived` flag/filter) and must never delete or become indistinguishable from deletion — this does not conflict with the BRD's 7-year retention constraint (BR-019) precisely because nothing is removed, only hidden from default/active views. Exact triggers (manual vs. time-based) are scoped in EX-16.

---

### BMD-008 — Daily operations (feed/mortality/weight) get dedicated phases; medication and vaccination are treated differently

**Resolves:** OQ-REV-04 (Gap Analysis §4.4)
**Decision:** Daily Feed Tracking, Daily Mortality Tracking, and Daily Weight Tracking are each named as standalone requirements (items 6, 7, 8) and also appear individually in the priority chain — each gets its own execution phase rather than being folded into one "daily ops" phase. **Medication** appears in the priority chain (between Weight and Inventory) but is *not* named in the 11 numbered requirements — it is scoped as a smaller, dependent phase (EX-09) rather than a headline feature, addressing only the consistency gap already flagged in the Business Revision Report (medication/vaccination currently has no ACTIVE-only status gate, unlike feed/mortality/weight). **Vaccination** is named in neither the priority chain nor the requirements list — it is treated as out of scope for this revision (no phase created), left exactly as it is today, and not subject to any removal either (it is not on the "Remove" list).

---

### BMD-009 — Alembic remains deferred; EX-01 continues the direct-schema-bootstrap convention

**Resolves:** T-EX01-02 (decision required before implementing EX-01)
**Date:** 2026-06-18 (recorded during EX-01 execution)
**Decision:** EX-01's `accounts` table and the `account_id` columns on `farms`/`users` were applied via a new manual SQL script (`infrastructure/postgres/migrations_v2/001_ex01_account_foundation.sql`), following the same manual-apply convention established by `init_monolith.sql` (M4) — not via Alembic. Wiring up a full schema-aware Alembic setup remains deferred (per `migration_decisions.md` MD-008) and is not being incidentally introduced as a side effect of this phase. This decision may be revisited if a future phase's data-migration complexity (e.g. EX-04's batch-status collapse) makes manual SQL scripts genuinely inadequate — not assumed here.
**Rationale:** Introducing Alembic was not part of EX-01's approved scope (`execution_phases.md` lists it only as a question to decide, not a mandate to build); building it now would be scope expansion beyond the approved roadmap item.

---

### BMD-010 — Account-scoping bypass uses the `super_admin` role, not account-id-nullity

**Date:** 2026-06-18 (recorded during EX-02 execution)
**Decision:** Whether a caller's farm-visibility is unrestricted (sees every farm/can act on every farm regardless of Account) is determined by the presence of the `super_admin` role in their JWT roles claim — not by whether their own `account_id` is null.
**Why this needed a decision:** The original EX-02 implementation used "`account_id` is None" as the unrestricted-bypass condition, reasoning that only an account-less platform admin would need to see everything. Live verification against the real database found this premise false: `admin@agrovision.uz` (the seeded super-admin) legitimately owns an Account in the live data (from a farm they created during earlier ad-hoc UAT testing), so they are not account-less. Under the original logic, the super-admin would have been scoped to their own (empty) Account and have seen zero farms — a real loss of platform-oversight capability that nobody asked to remove.
**Fix:** Reused the already-existing `X-User-Roles` header (populated since M5) to check for `super_admin` membership at the farm endpoint layer, instead of introducing a new JWT claim or header. No identity-module change beyond the `account_id` claim already added for BMD-001's purposes.
**Scope note:** This is a correction discovered while faithfully implementing EX-02's approved scope ("a user should see farms belonging to their Account") — not new functionality. The alternative (leaving the bug in place) would have silently broken admin oversight, which is a regression, not a feature anyone approved removing.

---

### BMD-011 — EX-04 status migration mapping for pre-existing live data

**Date:** 2026-06-18 (recorded during EX-04 execution)
**Decision:** Pre-existing live `poultry.batches` rows are migrated as: `quarantine` → `active` (the only non-terminal state left under BMD-002/BMD-003), `closed` → `completed` (BMD-003's rename, same terminal meaning). No row had `close_reason = 'slaughter'`, so the enum value was dropped with no compensating data rewrite needed.
**Why this needed a decision:** Live data inspection (not assumed) found 2 pre-existing `quarantine` batches (`B-2026-06`, `UAT-TEST-01` — earlier test/UAT artifacts, not created by this initiative) and 1 `closed` batch (`B-2026-001`, the seeded full-lifecycle demo). A status collapse needed an explicit, recorded mapping rather than an ad-hoc choice baked silently into the migration SQL.
**Applied via:** `infrastructure/postgres/migrations_v2/003_ex04_batch_lifecycle_simplification.sql` — also drops the now-unused `quarantine_end_date` column. Verified live post-apply: `SELECT DISTINCT status FROM poultry.batches` returns only `active`/`completed`.

---

### BMD-012 — Batch auto-naming convention: farm-prefixed sequential, fully automatic

**Date:** 2026-06-18 (recorded during EX-05 execution)
**Resolves:** `execution_phases.md` EX-05's explicit "to be finalized with the business owner" naming-convention gate.
**Decision:** `batch_code` is mandatory and always server-generated as `{FARM_CODE}-{YEAR}-{SEQ}` — e.g. `TOSHKENT-2026-001` — where `FARM_CODE` is derived from the farm's name (first word, uppercased, alphanumeric-only, capped at 12 chars, falling back to `FARM` if that yields nothing usable), `YEAR` is the batch's placement-date year, and `SEQ` is a per-farm-per-year sequence (count of existing batches for that farm whose code already starts with `{FARM_CODE}-{YEAR}-`, plus one), zero-padded to 3 digits. The code is **fully automatic — no manual override at create time, and no longer editable after creation** (the prior, unused `batch_code` field was removed from `UpdateBatchRequest` too, since allowing a post-hoc rename would silently reintroduce the override path the business owner explicitly declined).
**Presented options (via AskUserQuestion, business-owner sign-off obtained directly):** farm-prefixed sequential (chosen) vs. building/section-prefixed vs. pure date+sequence; and fully automatic (chosen) vs. server-generated-with-optional-override.
**Why no new `Farm.code` field was added:** `FARM_CODE` is derived from the existing `Farm.name` at generation time rather than introducing a new column — keeps the change additive-only within the poultry module and avoids a farm-module schema change (and a farm-admin UI to manage it) that nobody asked for. Since `batch_code` is a stored snapshot (not recomputed later), a farm being renamed after a batch is created does not retroactively change that batch's already-generated code.
**Module-boundary note:** generating the code requires reading `farm.farms.name` from the poultry module. Per `scripts/check_module_boundaries.py`, poultry may not import `app.farm`'s domain/infrastructure internals. Resolved by adding `AbstractBatchRepository.get_farm_name()`, implemented as a raw cross-schema SQL `SELECT name FROM farm.farms WHERE id = :farm_id` inside poultry's own repository — no Python import of `app.farm.*` is introduced, consistent with the existing cross-schema FK (`Batch.farm_id` already references `farm.farms.id` directly).
**Applied via:** `infrastructure/postgres/migrations_v2/004_ex05_batch_auto_naming.sql` — sets `batch_code NOT NULL` and adds a `UNIQUE (farm_id, batch_code)` constraint. No backfill needed: all 4 pre-existing live rows already had non-null, per-farm-unique codes (live data inspection performed before writing the migration).

---

### BMD-013 — Medication recording: build the missing CRUD plumbing, not just a finding note

**Date:** 2026-06-18 (recorded during EX-09 execution)
**Resolves:** a scope question raised mid-phase, presented to the user via `AskUserQuestion`.
**Background:** `execution_phases.md` EX-09 assumed medication recording was a live, already-gated feature needing only a status-gate alignment (like EX-06/07/08). Verification found this premise false: `MedicationRecord` existed only as a dormant ORM model + DB table, populated solely by seed data — no use case, repository, endpoint, or frontend UI existed at any layer. There was nothing to "gate" because there was no live write path at all.
**Options presented:** (a) document the gap as a finding and do nothing further (the EX-02 delete-guard precedent), or (b) build the missing CRUD plumbing now, turning medication into a real feature for the first time.
**Decision:** (b) — build it. The user explicitly chose this over the more conservative documentation-only option.
**What was built:** `app/poultry/application/dtos/medication_dtos.py` (`RecordMedicationRequest`/`MedicationRecordResponse`), `app/poultry/domain/repositories/medication_repository.py` + `infrastructure/database/repositories/medication_repository_impl.py`, `app/poultry/application/use_cases/{record_medication,get_medication_history}.py`, `app/poultry/api/v1/endpoints/medication.py` (wired into `router.py`) — all mirroring the existing feed/mortality pattern exactly, including the same `ACTIVE`-only status gate (`MEDICATION_BATCH_NOT_ACTIVE`). Frontend: `MedicationRecord` type, `medicationService` (`frontend/src/services/batchService.ts`), and a full record-and-history UI section in `BatchDetailPage.tsx` (a medicine picker sourced from `inventory.stock_items` filtered to `item_type === 'medicine'`, since `medicine_inventory_item_id` is a required FK and no UUID free-text entry would be usable by farm workers).
**Scope boundary respected:** no new medication-*protocol* features were added (no dosage scheduling, no withdrawal-period tracking) — only the basic create/list capability that feed/mortality/weight already had. This matches `execution_phases.md`'s "Out of scope: any new medication-protocol features" — the CRUD plumbing itself is the alignment fix once the premise (that it already existed) turned out to be false, not a protocol-level feature expansion.
**No DB migration needed:** `medicine_inventory_item_id` was already `NOT NULL` on the pre-existing model/table — no schema change required, only new application-layer code.

---

### BMD-014 — Inventory linkage hardening: proceed with all three FK constraints

**Date:** 2026-06-18 (recorded during EX-10 execution)
**Resolves:** `execution_phases.md` EX-10's cost/benefit evaluation gate ("Evaluate (not necessarily implement, pending cost/benefit)...").
**Cost/benefit note:** Live data inspection found **zero orphaned rows** across all three identified bare-UUID references (`inventory.warehouses.farm_id`, `inventory.stock_movements.warehouse_id`, `poultry.feed_consumptions.feed_inventory_item_id`) — meaning the migration risk is effectively nil. The benefit (closing a real, named data-integrity gap from the Business Revision Report §11 footnote) is concrete and the implementation pattern (cross-schema `ForeignKey` + explicit `__table_args__ = {"schema": ...}` where needed) is already well-established from EX-01/EX-05. Given near-zero cost and a real, explicitly-flagged benefit, the decision is to proceed with all three rather than defer.
**Decision:** Harden all three references with real FK constraints. No change to Inventory's module boundary, page routing, or independence from Farm/Batch navigation (explicitly preserved, per phase scope).
**Wider blast radius found during implementation:** making `poultry.feed_consumptions.feed_inventory_item_id` reference `inventory.stock_items.id` cross-schema required giving `StockItem` an explicit `__table_args__ = {"schema": "inventory"}` (the M8/CL-030 lesson) — which in turn required re-qualifying `StockItem`'s own two existing in-module referrers (`StockBatch.stock_item_id`, `StockMovement.stock_item_id`) from bare `"stock_items.id"` to `"inventory.stock_items.id"`, since a table's metadata key cannot simultaneously be both bare and schema-qualified. `Warehouse` did **not** need a schema declaration of its own — nothing cross-schema targets it, only `StockItem.warehouse_id` (same-module, stays bare) — so the blast radius was contained to the `StockItem` side only.
**Applied via:** `infrastructure/postgres/migrations_v2/005_ex10_inventory_linkage_hardening.sql` — three guarded `ALTER TABLE ... ADD CONSTRAINT` statements. Verified live: normal reads/writes across warehouses/feed/medication endpoints unaffected; two direct negative-path SQL inserts (a warehouse with a random `farm_id`, a stock movement with a random `warehouse_id`) were both correctly rejected by the new constraints, with no orphaned rows left behind by the rejected transactions.

---

### BMD-015 — Finance Improvements (EX-11): exact scope provided directly by business owner

**Date:** 2026-06-18 (recorded during EX-11 execution)
**Resolves:** `backlog_items.md` T-EX11-01 ("Finance Improvements" was CONDITIONAL/PENDING CLARIFICATION).
**Process note:** An `AskUserQuestion` structured multi-choice prompt (presenting candidate scopes: cost-driver breakdown, debtor/creditor tracking, budget-vs-actual, or skip) was rejected by the business owner, who instead replied directly with the complete scope below. Preference noted for future phases with the same CONDITIONAL marker (EX-12): offer to state scope directly rather than defaulting to structured options once it's clear the owner already has an answer in mind.
**Scope (verbatim from business owner):**
> - Track supplier debt
> - Track customer debt
> - Track partial payments
> - Track outstanding balances
> - Show debtor/creditor summary in Finance
>
> Do not implement budgeting.
> Do not implement forecasting.
> Do not implement advanced accounting.
> Keep MVP focused on real poultry farm operations.

**Design decisions made to satisfy this scope, while not exceeding it:**
1. **Extended the live, simple `SaleRecord`/`Expense` models** rather than reviving the dormant, more complex `SalesOrder`/`SalesOrderLine`/`Payment`/`Customer` models found during investigation (which were never wired to any use case, repository, endpoint, or frontend — a "dormant model" pattern previously also seen with `MedicationRecord` in EX-09). Reviving that machinery would have meant building a formal sales-order/credit-limit workflow, which exceeds "keep MVP focused" and risks drifting toward the explicitly excluded "advanced accounting."
2. **`SalePaymentStatus`**: added a third value `PARTIAL` to the existing binary `PAID`/`PENDING` enum, rather than switching to the dormant `PaymentStatus` enum (which has `OVERDUE`/`WRITTEN_OFF` — out of scope) or renaming anything live clients depend on.
3. **Server-computed payment status**: for both `SaleRecord` and `Expense`, the payment/outstanding state is always derived from `amount_paid` vs the total — never trusted as a client-supplied value — so the two can never drift out of sync. `Expense.payment_status` is a Python property (not a stored column) since nothing else in the schema needed to query/filter on it as a column; `SaleRecord.payment_status` stays a stored column since it predates this change and other code already reads it as one.
4. **New minimal `Supplier` model** (id, farm_id, name, phone, address, is_active) — no stored `credit_limit`/`current_debt`, unlike the dormant `Customer` model, so there is exactly one source of truth (live `Expense` rows) for supplier debt, not two.
5. **No new `Customer` entity** — `SaleRecord.customer_name`/`customer_phone` (free text) remain the debtor identity, consistent with the model's own pre-existing docstring describing it as "MVP alternative to full SalesOrder workflow." Debtors are aggregated by (name, phone) pair, not a foreign key.
6. **Partial payments are an ongoing capability**, not just a one-time flag at creation: new `PATCH /sales/{id}/payment` and `PATCH /expenses/{id}/payment` endpoints record incremental payments, clamped so `amount_paid` can never exceed the total (verified live: an intentional overpayment attempt clamped to the exact outstanding amount rather than erroring or overshooting).
7. **Backward compatibility**: `amount_paid` is optional on both `RecordSaleRequest` and `RecordManualExpenseRequest`. If omitted, it's derived from the old `payment_status` field (sales) or defaults to "fully paid" (expenses) — preserving the pre-EX-11 assumption that a manually-recorded expense with no declared supplier was already settled.
**Applied via:** `infrastructure/postgres/migrations_v2/006_ex11_finance_debt_tracking.sql` — new `finance.suppliers` table; `finance.expenses.supplier_id`/`amount_paid` (backfilled `amount_paid = amount`, i.e. assumed settled, for all 14 pre-existing rows, none of which had a supplier); `finance.sale_records.amount_paid` (backfilled from existing `payment_status`: the one `paid` row got the full total, the one `pending` row got 0). Verified live: zero-`NULL` backfill check passed; full positive-path test (create supplier, record expense with supplier debt, record partial then completing payment, confirm `debtors-creditors-summary` aggregates correctly) and negative-path test (zero/negative payment amount rejected with HTTP 422; overpayment clamps rather than erroring) both passed; all test artifacts (test supplier, test expense, test sale payment) removed afterward and exact pre-test row counts/values confirmed restored.

---

### BMD-016 — Reporting Improvements (EX-12): Cross-Farm and Cross-Batch Trend Reporting

**Date:** 2026-06-18 (recorded during EX-12 execution)
**Resolves:** `backlog_items.md` T-EX12-01 ("Reporting Improvements" was CONDITIONAL/PENDING CLARIFICATION).
**Process note:** Following BMD-015's lesson, candidate scopes were presented directly in prose (not via `AskUserQuestion`), and the business owner replied with a complete, concrete scope.
**Scope (business owner, verbatim intent):** Implement EX-12 as Cross-Farm and Cross-Batch Trend Reporting — batch performance comparison, mortality trends, weight growth trends, feed consumption trends, revenue and profit trends, farm-to-farm comparison. Reports must be viewable in the Reports section, using charts and tables where appropriate. Explicitly excludes scheduled reports, email delivery, Telegram delivery, and advanced forecasting — "keep reporting focused on operational poultry farm analytics."

**Design decisions made to satisfy this scope:**
1. **"Trend" = batch-over-batch, not daily time-series.** Per ADR-003's Batch-First Principle, AgroVision's MVP has no continuous cross-batch daily time series — feed/mortality/weight are recorded per batch and summarized into one report per batch. The natural, lowest-effort, highest-value interpretation of "trend" here is each metric plotted across a farm's batches in chronological order (by `placement_date`), which directly answers "is this farm's FCR/mortality/profit improving batch over batch?" — exactly what an operational farm owner needs, without inventing a new daily-granularity aggregation layer that the explicit "no advanced forecasting" boundary would caution against anyway.
2. **Reused `GenerateBatchReportUseCase` and `BatchReportResponse` as the foundation** for the new `GetFarmBatchPerformanceUseCase` (lists a farm's batches, then runs the existing per-batch report concurrently for each) rather than writing a parallel aggregation path. This means "batch performance comparison" and all four chart types (mortality/weight/feed/revenue-profit trends) are different views over one dataset, not four separate backend computations.
3. **New `GetFarmComparisonUseCase`** aggregates that same per-batch data across multiple farms (sum for totals, average for rates/ratios) into one row per farm, for "farm-to-farm comparison." Takes an explicit `farm_ids` list from the caller rather than querying the farm module internally — avoids needing to forward the original request's `X-Account-Id`/role headers into an in-process call (the farm module's list/get endpoints are account-scoped per EX-02 and would silently return nothing without those headers; batch/expense/sales endpoints used elsewhere in reporting are not account-scoped, so this account-context gap is specific to the farm module and was deliberately worked around at the API boundary instead of plumbing auth context through every internal client).
4. **Found and fixed a pre-existing bug while building the mortality trend chart**: `generate_batch_report.py` was reading `mortality_summary["mortality_rate_pct"]` and `mortality_summary["survival_rate_pct"]`, but `MortalitySummaryResponse` only ever returned a field named `mortality_rate` (no `_pct` suffix) and never returned `survival_rate_pct` at all — so every batch report's mortality rate had been silently null since this code was first written, predating EX-12 entirely. Fixed to read `mortality_rate` (with the correct field name) and to source `survival_rate_pct` from the batch's own `survival_rate` field (already computed and returned by the batch endpoint) instead. This was in-scope to fix because the explicitly-requested "mortality trends" deliverable would otherwise render empty charts.
5. **No new persistence, no scheduling, no delivery channel.** All new endpoints are synchronous, on-demand `GET`s composed from existing data — no new tables, no background jobs, no email/Telegram integration, consistent with the explicit exclusions.
**Applied via:** new use cases `get_farm_batch_performance.py`, `get_farm_comparison.py`; new endpoints `GET /reports/farms/{farm_id}/batch-performance` and `GET /reports/farm-comparison?farm_ids=...`; new `LivestockClient.list_batches()`; new `FarmComparisonRow` DTO; bug fix in `generate_batch_report.py`. Frontend: new "Tendensiyalar" tab in `ReportsPage.tsx` using `recharts` (already a frontend dependency, previously unused) for line/bar charts plus HTML tables, alongside the existing per-batch card grid (now under a "Partiyalar" tab). Verified live: batch-performance and farm-comparison endpoints tested against real seeded data through both the monolith directly and through nginx (matching real browser access); a malformed `farm_ids` UUID was found to 500 and was fixed to return a proper 422; an empty-batches farm correctly returns an empty list rather than erroring; the mortality-rate bug fix was verified to produce correct non-null values before and after, with the existing single-batch JSON/PDF report endpoints re-tested afterward to confirm they still work correctly with the fix in place.

---

### BMD-017 — User Management Revision (EX-15): account-aware user listing/creation, cross-account denial

**Date:** 2026-06-18 (recorded during EX-15 execution)
**Resolves:** `execution_phases.md` EX-15 — no business-owner clarification was needed (the scope was unambiguous), but the implementation required several technical design decisions worth recording.
**Findings during investigation:** `UsersPage.tsx` derived its single `farmId` from `currentUser.farm_id` and could only list/create users for that one farm. The backend `GET /users/` endpoint required a mandatory `farm_id` with zero account-boundary enforcement — any caller could pass any farm's UUID with no check at all. `User.account_id` already existed as a column (added in EX-01, explicitly documented there as "full enforcement is EX-02/EX-15 scope, not this phase's") but `CreateUserUseCase` never set it — every user created to date has `account_id = NULL` regardless of who created them.

**Design decisions made:**
1. **Cross-account validation reuses EX-02's existing enforcement transitively**, rather than duplicating account-membership logic in the identity module. A new in-process `FarmClient` (mirroring `app/reporting`'s `LivestockClient`/`FinanceClient` ASGI-transport pattern) calls the farm module's own `GET /farms/{id}` — which already 404s for a farm outside the caller's account, per `GetFarmUseCase`'s EX-02 logic. If that 404s, `users.py` raises the same `EntityNotFoundError`. This means the identity module never needs to know about `farm.farms`'s schema directly, preserving module boundaries, and the cross-account check is exactly as strict as the farm module's own — no risk of the two drifting out of sync.
2. **A new user's `account_id` is resolved from the target farm, not the caller's own account_id**, when a `farm_id` is given. This matters for the superuser case: a platform super-admin creating a user for someone else's farm must have that user end up scoped to the farm's account, not the superuser's own (which is typically `None`). For a non-superuser caller, this is equivalent in practice since `FarmClient.get_farm` already guarantees the farm belongs to their own account (otherwise it 404s first).
3. **A non-superuser caller with no `farm_id` and no account context creates nothing** (`EntityNotFoundError("Account", "none")`, mapped to 404) — there is no sensible account to assign. A superuser in the same situation is allowed to create an account-less/farm-less user (e.g. another platform admin), mirroring `User.account_id`'s own nullable-for-superuser design.
4. **`GET /users/` without `farm_id` now lists account-wide** (`list_by_account`), the core T-EX15-01 deliverable. With `farm_id` given, it still lists for that one farm (T-EX15-02 retained), but now with the same cross-account 404 check added defensively. A non-superuser with no account context gets an empty list, not an error — same "see nothing, not everything" precedent as `ListFarmsUseCase`.
**Applied via:** `app/identity/domain/repositories/user_repository.py`/`user_repository_impl.py` (`list_by_account`), `app/identity/application/use_cases/create_user.py` (`account_id` field), `app/identity/infrastructure/clients/farm_client.py` (new), `app/identity/api/v1/endpoints/users.py` (account/role header handling, `_is_superuser`, cross-account checks on both create and farm-filtered list), `app/identity/application/dtos/user_dtos.py` (`UserResponse.account_id` exposed for the admin UI). Frontend: `UsersPage.tsx` rewritten to list account-wide by default, with a farm selector added to the create-user form and a new "Ferma" column in the user table. Verified live: account-wide listing returns the correct 5 users for the seeded Toshkent Broiler account; creating a user against a same-account farm correctly inherits that account; creating a user against, and listing users filtered by, a different account's farm were both correctly denied with HTTP 404 and zero rows leaked; all test artifacts removed afterward.

---

### BMD-018 — Archive System (EX-16): manual-only archiving, role mapping, additive-only guarantee

**Date:** 2026-06-18 (recorded during EX-16 execution)
**Resolves:** `execution_phases.md` EX-16's two explicitly-deferred open questions (trigger mechanism, authorized roles) — the business owner gave a precise, complete policy on request:
- Trigger: manual only (no automatic/scheduled/time-based archiving, no retention policies — explicitly out of scope for MVP).
- Authorized roles: "Account Owner" and "Farm Director" can archive and un-archive.
- Archive effects: batch `status` stays `COMPLETED` (archiving is an orthogonal flag, not a new status); archived batches disappear from default Dashboard/Farm views; remain fully visible, searchable, and exportable in Reports; no data deletion; no audit history removal.
- Visibility: default Farm/Dashboard views show ACTIVE (non-archived) batches only; a new Archive view shows ARCHIVED batches only; Reports show both with archive filter support.

**Design decisions made:**
1. **Role-mapping pragmatic decision**: the RBAC catalog (`scripts/seed/seed_identity.py`) has no `account_owner` or `farm_director` role — only `super_admin`, `farm_owner`, `farm_manager`, `accountant`, `farm_worker`, `veterinarian` exist, and EX-15 explicitly kept RBAC redesign out of scope. Archive/un-archive authority is mapped onto the existing `farm_owner` role (the only seeded role at that authority level) plus the standard `super_admin` bypass. This is a deliberate, documented approximation of "Account Owner and Farm Director," not a silent assumption — recorded here and in code comments (`_can_archive` in `batches.py`, `canArchive` in `BatchListPage.tsx`) so it can be revisited if/when those roles are ever introduced.
2. **Archiving is restricted to `COMPLETED` batches** (`Batch.archive()` raises `BATCH_ARCHIVE_REQUIRES_COMPLETED` otherwise) — consistent with `phase_dependencies.md` tying EX-16's meaning to EX-04's `COMPLETED` state, and with the business reality that an in-progress batch isn't a candidate for archiving.
3. **`is_archived`/`archived_at`/`archived_by` are new orthogonal columns on `Batch`**, not a new `BatchStatus` value — status vocabulary (`ACTIVE`/`COMPLETED`) is untouched, matching the stated policy ("Batch status remains COMPLETED").
4. **A single `archived` query parameter (`'false'` default / `'true'` / `'all'`) threads through the batch list endpoint, the repository, and reporting's `LivestockClient`/use cases**, rather than separate booleans or endpoints. Default (`'false'`) gives every existing caller (Dashboard, FarmDetailPage, BatchListPage, the picker dropdowns) the correct "active/non-archived only" behavior with zero code changes on their part; the new Archive view explicitly passes `'true'`; Reports' Trends tab explicitly passes `'all'` with a UI filter toggle, satisfying "Reports must support both ACTIVE and ARCHIVED with archive filter support" without changing Dashboard's reuse of the same underlying use case.
5. **No hard delete anywhere** — `archive()`/`unarchive()` only flip the `is_archived` flag and timestamp/actor fields; no `DELETE` statement was added anywhere in this phase. Verified live: mortality/expense record counts for the test batch were identical before and after an archive→unarchive cycle.
**Applied via:** `app/poultry/domain/models/animal.py` (`is_archived`/`archived_at`/`archived_by` columns, `archive()`/`unarchive()` methods), migration `infrastructure/postgres/migrations_v2/007_ex16_archive_system.sql`, `AbstractBatchRepository.list_by_farm`/`SQLAlchemyBatchRepository` (`archived` filter param), new `ArchiveBatchUseCase`/`UnarchiveBatchUseCase`, new `POST /batches/{id}/archive` and `POST /batches/{id}/unarchive` endpoints with `_can_archive` role check, `archived` query param on `GET /batches/` and both reporting endpoints, `LivestockClient.list_batches`/`GetFarmBatchPerformanceUseCase`/`GetFarmComparisonUseCase` archive passthrough, `BatchResponse`/`BatchReportResponse` exposing the new fields. Frontend: `BatchListPage.tsx` gained a "Joriy"/"Arxiv" tab and role-gated Arxivlash/Arxivdan chiqarish buttons; `ReportsPage.tsx`'s Trends tab gained a Faol/Arxivlangan/Barchasi filter and an "Arxivlangan" badge. Verified live end-to-end against real seeded data through nginx: archiving a COMPLETED batch as `farm_owner` correctly hid it from the default batch list while it remained visible under `archived=true` and under Reports' `archived=all` (with `is_archived: true` in the row); a `farm_worker` attempting to unarchive was correctly denied with HTTP 403; attempting to archive an `ACTIVE` batch was correctly rejected with a 422 business-rule error; un-archiving restored the batch to the default view; all related mortality/expense records remained intact throughout (no deletion); test state was fully restored afterward (batch unarchived, no rows added/removed).

---

## Summary: Open Questions Closed By This Decision Log

| Open Question | Resolution | Decision |
|---|---|---|
| OQ-REV-01 | COMPLETED is a new terminal state (slaughter-free), not a pure rename of CLOSED | BMD-003 |
| OQ-REV-02 | Quarantine removed as both batch status and section type | BMD-002 |
| OQ-REV-03 | Dashboard stays as landing page; Farms gets enhanced detail view; both coexist | BMD-005 |
| OQ-REV-04 | Feed/Mortality/Weight each get dedicated phases; no unified "daily tasks" view requested | BMD-008 |
| OQ-REV-05 | Account is a real new entity above Farm, confirmed by explicit priority chain | BMD-001 |
| OQ-REV-06 | Batch naming becomes mandatory and system-generated | BMD-006 |
| OQ-REV-07 | Archive System authorized, additive-only, no conflict with retention rules | BMD-007 |

All seven open questions from `business-revision/gap_analysis.md` are now CLOSED. `execution-v2/master_roadmap.md`, `execution_phases.md`, `phase_dependencies.md`, `verification_checklists.md`, and `backlog_items.md` are built directly on these eight decisions.

---

*Decision Log — AgroVision Business Model Revision Initiative — 2026-06-18*
*This document records decisions only. No code, schema, or frontend implementation has occurred as a result of this log.*

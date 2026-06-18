# AgroVision — Execution Phases v2 (Detailed)

**Status:** PLANNING ONLY — no implementation authorized.
**Date:** 2026-06-18
**Index:** see `master_roadmap.md` §4 for the phase overview table. This document gives full detail per phase.

Each phase entry follows the same structure used successfully in the monolith migration (`migration_backlog.md`) and the original roadmap (`master_roadmap.md`): Goal, Current State, Scope, Out of Scope, Removals Applied, Dependencies, Deliverables.

---

## EX-01 — Account Foundation

**Goal:** Introduce `Account` as a new top-level entity that owns one or more `Farm`s, establishing the root of the priority chain.

**Current state:** No `Account`/`Organization` entity exists anywhere in `app/identity` or elsewhere. `Farm.owner_user_id` is a bare column implying a 1:1 farm-to-owner relationship; `User.farm_id` ties one user to at most one farm.

**Scope:**
- Design (not yet implement) a new `Account` entity: identity, name, status (active/inactive), and its relationship to `Farm` (one Account → many Farms).
- Design how a `User` relates to an `Account` (e.g. a Farm Owner's account, with staff users scoped to specific farms within that account).
- Define what happens to `Farm.owner_user_id` — likely superseded by `Farm.account_id`, with the owning user derived from the Account rather than stored redundantly on each Farm.
- Define account-level vs. farm-level permission boundaries (does an Account-level role exist above today's per-farm RBAC roles?).

**Out of scope:** Billing, subscriptions, multi-account-per-user scenarios (a user belonging to more than one unrelated Account), or any commercial/tenancy-tier concept — none of this was implied by the request; keep the entity minimal (ownership/grouping only).

**Removals applied:** None (this phase is additive).

**Dependencies:** None — this is the root of the chain and the first phase.

**Deliverables (planning-stage only, per the "do not implement" constraint — actual deliverables become code once this phase is authorized for execution):**
- An Account data-model design note (fields, relationships, cardinality)
- A migration-impact note (since Alembic isn't wired up for the monolith yet — `migration_decisions.md` MD-008 — this phase must also decide whether to finally wire up Alembic or continue with direct schema bootstrap, given a real new entity is being introduced)
- Updated `Farm` relationship design (`account_id` FK)
- Updated `User`-to-`Account`/`Farm` relationship design

---

## EX-02 — Farm Management Revision

**Goal:** Make Farm CRUD account-aware, building on the already-complete P-16 Farm Management CRUD work.

**Current state:** Farm CRUD (create/edit/delete/list) is fully implemented (P-16, `CL-018`) and works well — delete is guarded against active batches, edit covers name/region/type/address/notes. The only gap is that Farm has no `account_id` and farm ownership is single-user (`owner_user_id`), not account-scoped.

**Scope:**
- Add `account_id` to Farm creation/edit flows once EX-01's Account entity exists.
- Update farm list filtering: a user should see farms belonging to their Account (not just farms they personally created).
- Re-confirm the existing active-batch delete guard still makes sense unchanged (it does — no change needed there).

**Out of scope:** Rebuilding farm CRUD from scratch — this phase is a targeted revision of working code, not a rewrite.

**Removals applied:** None directly (Farm CRUD doesn't reference quarantine/slaughter/RFID/individual-bird concepts).

**Dependencies:** EX-01 (Account must exist before Farm can be account-scoped).

**Deliverables:**
- Updated Farm create/edit forms and backend DTOs to include account context
- Updated farm-list query to scope by account
- Confirmation note that existing delete-guard logic is unaffected

---

## EX-03 — Building & Section Simplification

**Goal:** Strip quarantine-related typing from the Building/Section hierarchy, keeping it purely operational (per the original "Building details are operational entities only" principle).

**Current state:** `Building` has no type field (name/capacity/notes only — already operational-only, no change needed there). `Section` has `SectionType = {QUARANTINE, PRODUCTION, ISOLATION, STORAGE}`.

**Scope:**
- Remove `SectionType.QUARANTINE` (per BMD-002).
- Confirm `SectionType.ISOLATION` is explicitly retained as-is for this phase (per BMD-002's note — sick-bird isolation is a distinct, narrower concept not targeted by the quarantine removal) unless a future decision says otherwise.
- Update the section-type catalogue everywhere it's duplicated (backend enum, frontend select options in `FarmDetailPage.tsx`, any seed data referencing a "Karantin bo'limi" section).
- Update seed data (`scripts/seed/seed_farm.py`) to stop creating a dedicated quarantine building/section as part of the standard demo dataset.

**Out of scope:** Changing the Farm→Building→Section FK structure itself (already sound, per Business Revision Report §11) — only the `SectionType` value set changes.

**Removals applied:** Quarantine (section type).

**Dependencies:** None structurally, but should land before or alongside EX-04 (Batch Lifecycle Simplification) since both touch the same "quarantine" concept and should be verified together to avoid a half-migrated state (e.g. a batch with no quarantine status but still placed in a section labeled quarantine).

**Deliverables:**
- Updated `SectionType` enum (backend)
- Updated section-type select options (frontend)
- Updated seed scripts (no quarantine building/section in demo data)

---

## EX-04 — Batch Lifecycle Simplification

**Goal:** Reduce `Batch.status` to exactly `ACTIVE`/`COMPLETED`, and strip slaughter, RFID, and individual-bird code paths.

**Current state:** `BatchStatus = {QUARANTINE, ACTIVE, CLOSED}` with a strict linear state machine and a hard-coded 7-day quarantine-minimum business rule (`activate_batch.py`). `BatchCloseReason` includes `slaughter`. A dormant `_Animal_FutureRelease` model and `AnimalStatus` enum exist alongside RFID/tag-number-shaped fields, unused by any live code path but present in the schema/codebase.

**Scope:**
- Collapse `BatchStatus` to `{ACTIVE, COMPLETED}` (per BMD-002/BMD-003). New batches start `ACTIVE` directly — no intermediate quarantine stage, no `activate_batch` use case needed at all (a batch is active from creation; "activation" as a distinct action disappears).
- Remove `quarantine_end_date` column and the `QUARANTINE_MINIMUM_7_DAYS` rule entirely.
- Remove `slaughter` from `BatchCloseReason` (per BMD-003); confirm remaining close reasons with the business owner during this phase's detailed task breakdown (sale/transfer/disease/other are the candidates carried forward from the Business Revision Report, not yet individually re-confirmed).
- Remove `_Animal_FutureRelease`, `AnimalStatus`, and any RFID/tag-number-shaped fields tied to individual-bird tracking (per BMD-004) — this is a permanent removal, not a re-deferral.
- Update the state-machine logic (`Batch.transition_to()` / `VALID_TRANSITIONS`) to the new two-state model: `ACTIVE → COMPLETED` only.

**Out of scope:** Batch naming (separate phase, EX-05) and the daily-ops use cases' status-gate wording (separate phases, EX-06/07/08/09 — though they depend on this phase's enum change).

**Removals applied:** Quarantine (batch status), Slaughter, RFID, Individual bird.

**Dependencies:** Should be sequenced together with EX-03 (see EX-03's note). No other phase should start migrating to ACTIVE/COMPLETED-only assumptions before this phase's enum/state-machine change is final, since nearly every other phase (EX-05 through EX-14) reads or assumes batch status in some way.

**Deliverables:**
- Updated `BatchStatus` enum and state machine
- Updated `BatchCloseReason` enum (slaughter removed)
- Removal of `_Animal_FutureRelease`/`AnimalStatus`/RFID-shaped fields
- Removal of the `activate_batch` use case and its endpoint (no longer meaningful with no quarantine stage to exit)
- Updated seed data (batches seeded directly as ACTIVE, no quarantine-then-activate two-step)

---

## EX-05 — Batch Auto Naming

**Goal:** Replace the optional free-text `batch_code` with a mandatory, system-generated batch identifier.

**Current state:** `batch_code` is `Optional[str]`, free text, not auto-generated, duplicate-checked only when supplied. The frontend falls back to a UUID fragment when blank.

**Scope:**
- Define a concrete naming convention (to be finalized with the business owner during this phase's detailed task breakdown — candidates noted in the Business Revision Report §4: farm-prefixed sequential, building/section-prefixed, or date+sequence).
- Make batch identification mandatory and server-generated (or server-validated if a manual override is still desired — to be decided during detailed scoping, not assumed here).
- Enforce uniqueness per farm (or per account, depending on the chosen convention) at the database level, not just application-level duplicate-checking.
- Remove the UUID-fragment fallback display logic from the frontend once a real identifier always exists.

**Out of scope:** Renaming/relabeling already-existing historical batch codes — a migration strategy for existing data (if any production data exists by the time this is implemented) is a separate concern from the forward-looking naming convention design.

**Removals applied:** None directly.

**Dependencies:** EX-04 (cleaner to introduce mandatory naming at the same time the lifecycle simplification lands, though not strictly blocking — could run in parallel per `master_roadmap.md`'s sequencing note).

**Deliverables:**
- A finalized naming-convention specification
- Updated `create_batch.py` (server-side generation/validation)
- Updated `NewBatchPage.tsx` (reflects the new convention; removes the free-text placeholder pattern if generation is fully automatic)
- Database-level uniqueness constraint

---

## EX-06 — Daily Feed Tracking Revision

**Goal:** Confirm/update the feed-recording workflow against the new two-state batch model.

**Current state:** Fully implemented (`record_feed.py`), gated to `BatchStatus.ACTIVE`, rejecting both QUARANTINE and CLOSED today.

**Scope:**
- Update the status gate from "ACTIVE only, reject QUARANTINE/CLOSED" to "ACTIVE only, reject COMPLETED" (mechanically simpler — one excluded state instead of two).
- Confirm the existing request schema (`feed_date`, `quantity_kg`, `water_liters`, `feed_type`, `age_days`, `feed_inventory_item_id`, `notes`) still meets the "Daily Feed Tracking" requirement as named, or identify any additional fields the business owner wants (none specified in the current instruction — treat the existing schema as sufficient unless told otherwise).

**Out of scope:** New feed-related features beyond the status-gate update (e.g. feed recommendation engines) — none were requested.

**Removals applied:** Quarantine (status gate wording).

**Dependencies:** EX-04 (batch status enum must be finalized first).

**Deliverables:**
- Updated status-gate error rule (renamed/simplified)
- Confirmation note on existing schema adequacy

---

## EX-07 — Daily Mortality Tracking Revision

**Goal:** Same kind of revision as EX-06, applied to mortality recording.

**Current state:** Fully implemented (`record_mortality.py`), gated to ACTIVE, validates against `current_count`, atomically decrements count.

**Scope:**
- Update the status gate the same way as EX-06.
- Confirm existing schema (`quantity`, `deceased_at`, `cause_category`, `cause_description`, `disposal_method`) is sufficient.

**Out of scope:** Disposal/sanitary workflow expansion (BP-16) — not requested.

**Removals applied:** Quarantine (status gate wording).

**Dependencies:** EX-04.

**Deliverables:**
- Updated status-gate error rule
- Confirmation note on existing schema adequacy

---

## EX-08 — Daily Weight Tracking Revision

**Goal:** Same kind of revision as EX-06/EX-07, applied to weight sampling.

**Current state:** Fully implemented (`record_weight_sampling.py`), gated to ACTIVE, computes average weight and age_days server-side.

**Scope:**
- Update the status gate the same way as EX-06/EX-07.
- Confirm existing schema (`sample_size`, `total_sample_weight_kg`, `measured_at`, `notes`) is sufficient.

**Out of scope:** New growth-analytics computation beyond what already exists (ADG/FCR) — covered instead under EX-12 (Reporting Improvements) if expansion is wanted.

**Removals applied:** Quarantine (status gate wording).

**Dependencies:** EX-04.

**Deliverables:**
- Updated status-gate error rule
- Confirmation note on existing schema adequacy

---

## EX-09 — Medication Workflow Alignment

**Goal:** Bring medication recording's status-gating in line with feed/mortality/weight, closing the consistency gap noted in the Business Revision Report (§6–8 cross-cutting note) and reflecting Medication's place in the priority chain.

**Current state:** A `MedicationRecord` model exists (from the original ADR-003 MVP health simplification — replacing formal `DiseaseIncident` case management). The vaccination use case (`record_vaccination.py`) was found to have **no** `BatchStatus` gate at all. Medication recording specifically was not independently re-verified by the research agents in this initiative and should be checked at the start of this phase's detailed scoping (it may already be correctly gated, or may share vaccination's gap — confirm before assuming).

**Scope:**
- Verify whether `MedicationRecord` creation is currently gated by batch status; if not, add the same `ACTIVE`-only gate used by feed/mortality/weight, for consistency with the new two-state model.
- Leave vaccination recording untouched (per BMD-008 — vaccination is out of scope for this revision, named in neither the priority chain nor the requirements list, and not on the removal list either).

**Out of scope:** Any new medication-protocol features (dosage scheduling, withdrawal-period tracking) — not requested; this phase is a consistency/alignment fix, not a feature expansion.

**Removals applied:** Quarantine (status gate wording, if/once a gate is added or updated).

**Dependencies:** EX-04.

**Deliverables:**
- Verification note on Medication's current gating status
- Updated/added status gate if needed

---

## EX-10 — Inventory Linkage Hardening

**Goal:** Confirm Inventory's "remains separate" status (already true) and address the minor data-integrity gaps noted during research, without changing its module boundary.

**Current state:** Inventory is already a fully separate module (own schema, own top-level nav). `Warehouse.farm_id` and `StockMovement.warehouse_id` are bare UUID columns with no FK constraint; `FeedConsumption.feed_inventory_item_id` (in the poultry module) is similarly a bare, unenforced reference to a `StockItem`.

**Scope:**
- Evaluate (not necessarily implement, pending cost/benefit decided during this phase's detailed scoping) adding real FK constraints for `Warehouse.farm_id`, `StockMovement.warehouse_id`, and `FeedConsumption.feed_inventory_item_id`, to close the latent data-integrity gap noted in the Business Revision Report §11's footnote.
- No change to Inventory's page/route structure, module boundary, or its independence from Farm/Batch navigation — that independence is explicitly confirmed correct and must be preserved.

**Out of scope:** Any new inventory features (new item types, new movement types) — not requested; this is a hardening-only phase.

**Removals applied:** None.

**Dependencies:** EX-04 (if `FeedConsumption.feed_inventory_item_id` FK-hardening is pursued, it should happen after the poultry module's other EX-04/EX-06 changes to avoid migration churn on the same table twice).

**Deliverables:**
- A cost/benefit note on FK-hardening for the three identified bare-UUID references
- (Conditional) added FK constraints, if the cost/benefit note recommends proceeding

---

## EX-11 — Finance Improvements — RESOLVED & VERIFIED_COMPLETE (2026-06-18)

**Goal:** Address "Finance Improvements" (requirement #10) and ensure finance no longer carries any slaughter-specific framing.

**Resolution:** Business owner provided the exact scope directly (not via the candidate list originally drafted below) — see `decision_log.md` BMD-015. Scope: track supplier debt, customer debt, partial payments, outstanding balances; show a debtor/creditor summary in Finance. Explicitly excludes budgeting, forecasting, and advanced accounting.

**Original state (pre-EX-11):** `finance` module supported manual expense recording, sale records, and batch profit calculation (cost vs. revenue), with no debt/payment-status tracking beyond a binary paid/pending flag on sales. No slaughter-specific cost category was ever identified — confirmed again via grep during this phase, with zero matches.

**Implementation:** Extended the live `SaleRecord`/`Expense` models (added `amount_paid`/`outstanding_amount`, a new `Supplier` model, server-computed payment status) rather than reviving the dormant, unwired `SalesOrder`/`Payment`/`Customer` models found during investigation — see `backlog_items.md` EX-11 section and `project_state.md` CL-042 for the full file list and live verification record.

**Removals applied:** Slaughter-related cost/sale framing — none existed; reconfirmed via grep, zero matches.

**Dependencies:** EX-04 (batch close-reason simplification affects what "batch cost summary at completion" means) — satisfied, no conflict found.

---

## EX-12 — Reporting Improvements — RESOLVED & VERIFIED_COMPLETE (2026-06-18)

**Goal:** Address "Reporting Improvements" (requirement #11), including removing quarantine/slaughter-related KPIs from any report.

**Resolution:** Business owner specified Cross-Farm and Cross-Batch Trend Reporting directly (candidates were presented in prose, per the BMD-015 lesson, rather than via `AskUserQuestion`) — see `decision_log.md` BMD-016. Scope: batch performance comparison, mortality trends, weight growth trends, feed consumption trends, revenue and profit trends, farm-to-farm comparison; viewable in the Reports section with charts and tables. Explicitly excludes scheduled reports, email delivery, Telegram delivery, advanced forecasting.

**Original state (pre-EX-12):** `app/reporting` provided only an on-demand single-batch performance card (FCR, mortality rate, cost, profit) with JSON and PDF export. No cross-batch/cross-farm aggregate or trend reporting existed.

**Implementation:** New `GetFarmBatchPerformanceUseCase`/`GetFarmComparisonUseCase` reuse the existing per-batch `GenerateBatchReportUseCase` rather than building a parallel aggregation path — "trend" is interpreted as batch-over-batch (chronological by placement date) rather than continuous daily time series, consistent with ADR-003's Batch-First Principle. A pre-existing field-name bug that silently nulled out every batch's mortality rate was found and fixed while building the mortality trend chart. See `backlog_items.md` EX-12 section and `project_state.md` for the full file list and live verification record.

**Removals applied:** Quarantine, Slaughter (KPIs/labels in reports) — none existed; reconfirmed via grep, zero matches (already cleaned up by EX-04).

**Dependencies:** EX-04 (status model) — satisfied, no conflict found.

---

## EX-13 — Farm Detail View Redesign — VERIFIED_COMPLETE (2026-06-18)

**Goal:** Address "Farm Detail View" (requirement #3) by surfacing a farm's batches and operational status directly on `FarmDetailPage`, per the Business Revision Report §2.

**Resolution:** Implemented exactly as scoped below — no clarification was needed for this phase (unlike EX-11/EX-12). New "Partiyalar" (batches) table section added to `FarmDetailPage.tsx`, reusing the existing `GET /batches/?farm_id=...` call; the per-call approach was confirmed sufficient (T-EX13-02), since this section only needs fields already present on `BatchResponse`. See `backlog_items.md` EX-13 section and `project_state.md` for the full file list and live verification record.

**Original state (pre-EX-13):** `FarmDetailPage.tsx` showed farm header info, Buildings, and Sections — but zero batch data. A farm's batches had to be found by navigating to the separate Livestock/Batches section and filtering by farm.

**Scope:**
- Add a batches-for-this-farm section to `FarmDetailPage`, using the already-existing `GET /api/v1/batches/?farm_id=...` capability (no new backend endpoint strictly required, though a composite "farm detail + batch summary" endpoint could be considered during detailed scoping if the per-call approach proves insufficient).
- Reflect the new two-state batch model (EX-04) and new auto-generated batch naming (EX-05) in how batches are displayed here.
- Reflect the simplified `SectionType` catalogue (EX-03) in how sections are displayed/selected here (this page already owns the section-type selector).

**Out of scope:** Changing the routing structure (e.g. nesting batches under `/farms/:id/batches` as a distinct route) — this phase adds an inline section to the existing page; a deeper routing change is only needed if a future decision says farm-nested batch routes are required (not specified by the current instruction, which lists "Farm Detail View" as augmenting the existing page).

**Removals applied:** Quarantine (labels/badges currently present in this page's section-type display).

**Dependencies:** EX-02 (account-aware farm), EX-03 (section types), EX-04 (batch status), EX-05 (batch naming) — this phase is intentionally late in the sequence because it composes outputs from all four.

**Deliverables:**
- Updated `FarmDetailPage.tsx` design showing an inline batches section
- Updated section-type display reflecting EX-03's simplified catalogue

---

## EX-14 — Dashboard Redesign — VERIFIED_COMPLETE (2026-06-18)

**Goal:** Address "Dashboard Redesign" (requirement #1) — make the dashboard genuinely analytics-focused, per Business Revision Report §1 and BMD-005 (dashboard stays the landing page).

**Resolution:** Implemented exactly as scoped below, no clarification needed (the quarantine stat cards had already been mechanically removed by EX-04, and EX-12's `app/reporting` aggregation capability — built in anticipation of this dependency — was reused directly rather than building new backend work). Added an FCR/profit trend chart and a multi-farm KPI rollup table to `DashboardPage.tsx`, both backed by EX-12's `GetFarmBatchPerformanceUseCase`/`GetFarmComparisonUseCase`. See `backlog_items.md` EX-14 section and `project_state.md` for the full file list and live verification record.

**Original state (pre-EX-14):** Single-farm KPI-card-and-table view; no trend charts; no multi-farm rollup; reporting module had no aggregation endpoints to draw on (resolved by EX-12).

**Scope:**
- Remove the quarantine-denominated stat cards (mechanical consequence of EX-04).
- Add genuine analytics: trend visualization (e.g. FCR/mortality over time) and/or multi-farm (now multi-account-aware, per EX-01/EX-02) KPI rollups — exact KPI set to be finalized during this phase's detailed scoping, informed by whatever new aggregation capability EX-12 (Reporting Improvements) ends up building, since the two phases likely share backend work.
- Re-confirm BMD-005's framing (Dashboard = monitoring/analytics, Farms = operational management) is reflected in the redesigned page's content choices (i.e., don't duplicate FarmDetailPage's operational batch-management controls here — keep this page read-only/analytical).

**Out of scope:** Replacing Dashboard as the landing page, or removing the farm-selector pattern entirely (BMD-005 keeps Dashboard in its current navigational position; it only changes its *content* to be more analytical and to drop quarantine framing).

**Removals applied:** Quarantine (stat cards/KPIs).

**Dependencies:** EX-04 (status model), and should be scoped together with EX-12 (Reporting Improvements) since both want new aggregation capability from `app/reporting`.

**Deliverables:**
- Updated `DashboardPage.tsx` design (cards/charts list, finalized after EX-12's clarification)
- Removed quarantine stat cards

---

## EX-15 — User Management Revision — VERIFIED_COMPLETE (2026-06-18)

**Goal:** Address "User Management" (requirement #5) by making it account-aware, closing the gap noted in Business Revision Report §9/§10.

**Resolution:** Implemented exactly as scoped below, no clarification needed. Backend `GET /users/` is now account-wide by default (`list_by_account`), and `CreateUserUseCase` now actually sets `User.account_id` (a pre-existing gap — it was always `NULL` regardless of who created the user, since EX-01 added the column but EX-15 was always intended to be where enforcement landed). Cross-account denial reuses EX-02's existing `GetFarmUseCase` account check transitively via a new in-process `FarmClient`. See `decision_log.md` BMD-017, `backlog_items.md` EX-15 section, and `project_state.md` for the full file list and live verification record.

**Original state (pre-EX-15):** `UsersPage.tsx` was single-farm-scoped (derived `farmId` from the current user, no farm selector when creating a user). RBAC (role templates ∪ individual permissions) was otherwise sound and matched SRS §4.1/§11.2 closely — no change needed to the permission-union logic itself, confirmed unchanged.

**Scope:**
- Once EX-01 (Account) exists, allow a Farm Owner/Account-level admin to manage users across all farms within their Account, not just one farm.
- Add farm selection (or "all farms in this account") when creating/editing a user, if the Account now owns multiple farms.
- Re-confirm the existing role/permission union logic is unaffected — this phase changes *scope* (which farms a user-management action can reach), not the *permission model* itself.

**Out of scope:** Redesigning RBAC itself (role templates, individual permission grants) — explicitly confirmed unaffected by Business Revision Report §9.

**Removals applied:** None.

**Dependencies:** EX-01 (Account must exist first), EX-02 (Farm must be account-scoped first).

**Deliverables:**
- Updated `UsersPage.tsx` design (multi-farm-aware user creation/listing within an Account)
- Confirmation note that RBAC logic itself is unchanged

---

## EX-16 — Archive System

**Goal:** Address "Archive System" (requirement #9), per Business Revision Report §3 and BMD-007 — additive-only, never a deletion path.

**Current state:** Does not exist in any form (SF-24 was deferred to Future Release under ADR-003 and never built).

**Scope:**
- Design an `is_archived` (or equivalent) flag/mechanism on `Batch` (and possibly `Farm`, if a whole inactive farm needs archiving — to be confirmed during detailed scoping) that removes the item from default/active views (Dashboard, Farm Detail batch list) without deleting any data.
- Define the trigger: manual action by an authorized user, automatic time-based archiving after a batch reaches `COMPLETED`, or both — to be decided during this phase's detailed scoping (not assumed here).
- Define who can un-archive, and confirm archived batches remain fully searchable/reportable (per BRD's audit-readiness goal VG-02 and the 7-year retention constraint BR-019) — archiving must never reduce auditability.

**Out of scope:** Any data deletion or purge mechanism — explicitly forbidden by BMD-007 and the underlying BRD retention constraint.

**Removals applied:** None (this phase is additive; it has no relationship to the quarantine/slaughter/RFID/individual-bird removals beyond the fact that "COMPLETED" — defined in EX-04 — is the state archiving applies to).

**Dependencies:** EX-04 (must know what COMPLETED means before designing what triggers archiving).

**Deliverables:**
- An archive-trigger and visibility-rule design note
- A confirmation note that the design preserves full searchability/reportability of archived records

---

*Execution Phases v2 — AgroVision Business Model Revision Initiative — 2026-06-18*
*Planning only. No implementation performed or authorized. Detailed task-level breakdowns (backlog items) are in `backlog_items.md`; this document defines phase-level scope only.*

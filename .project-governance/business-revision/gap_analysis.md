# AgroVision — Business Model Revision: Gap Analysis

**Date:** 2026-06-18
**Status:** ANALYSIS ONLY — no code, database, or frontend changes made or proposed for implementation here.
**Inputs reviewed:** BRD (`1. BRD_AgroVision_Farm_Management_qism1.docx`), SRS v1.1 (`2. SRS_AgroVision_Farm_Management_v1.1.docx`), ADR-001/002/003, `project_state.md`, `project_memory.md`, `master_roadmap.md`, `development_backlog.md`, live inspection of `app/` (backend) and `frontend/src/` (frontend).
**Companion documents:** `business_revision_report.md`, `backlog_revision_plan.md`, `updated_execution_strategy.md` (this same directory).

---

## 1. Purpose

The user has issued six new business principles that supersede prior assumptions baked into the BRD, SRS, and the implemented system. This document maps each new principle against (a) what the BRD/SRS currently say, (b) what the backend (`app/`) currently implements, and (c) what the frontend currently implements — and classifies the result as **COMPATIBLE**, **REQUIRES CHANGE**, or **DEPRECATED CONCEPT**.

---

## 2. New Business Principles vs. Current State

### 2.1 Principle: Quarantine is removed completely. Allowed statuses: ACTIVE, COMPLETED.

| Layer | Current State | Classification |
|---|---|---|
| BRD | §9.3 (BP-03 "Karantin boshqaruvi") mandates a minimum quarantine period (7–14 days poultry, ≥21 days cattle) before a batch may enter the main section. BR-004 makes this a hard, system-enforced rule. | **DEPRECATED CONCEPT** — BRD/SRS text explicitly contradicts the new principle. |
| SRS | §7.3 batch entity has `Holati (karantin/faol/yopilgan)`. UC-02 ("Yangi parranda partiyasini ochish") step explicitly auto-places a new batch into the quarantine section. §8 BR-004 is a "Kritik" rule. | **DEPRECATED CONCEPT** |
| Backend | `app/poultry/domain/models/animal.py`: `BatchStatus = {QUARANTINE, ACTIVE, CLOSED}` (3 values, not 2). `VALID_TRANSITIONS` enforces QUARANTINE → ACTIVE → CLOSED, strictly linear. `create_batch.py` forces every new batch into QUARANTINE. `activate_batch.py` enforces a hard-coded 7-day minimum (rule `QUARANTINE_MINIMUM_7_DAYS`) before a batch may move to ACTIVE. `quarantine_end_date` is a real DB column on `batches`. Separately, `app/farm`'s `SectionType` enum also includes `QUARANTINE` as a section/place type (independent of batch status — confirmed by both research agents as two unrelated "quarantine" concepts that aren't unified). `feed`/`mortality`/`weight` use cases gate on `BatchStatus.ACTIVE` only — a QUARANTINE batch cannot receive any daily record today. | **REQUIRES CHANGE** — both the `BatchStatus` enum/state machine and the `SectionType.QUARANTINE` value must be addressed; `CLOSED` must be renamed/mapped to `COMPLETED` (see open question below on whether this is a rename or a semantic change). |
| Frontend | `BatchStatus` type and 5+ duplicated label/badge maps (`DashboardPage.tsx`, `BatchListPage.tsx`, `BatchDetailPage.tsx`, `ReportsPage.tsx`, `FarmDetailPage.tsx` section-type label) all reference `'quarantine'`/`'Karantin'`. Dashboard has two dedicated KPI cards ("Karantin" batch count, "Karantindagi parrandalar" bird count). `BatchDetailPage` shows an "Faollashtirish" (Activate) button only when `status === 'quarantine'`, plus a `quarantine_end_date` info card. Daily-record forms (feed/mortality/weight/sales/expense) are conditionally rendered only `if batch.status === 'active'` — a quarantine batch shows no daily-entry UI at all today. `SectionType` select in `FarmDetailPage.tsx` includes a "Karantin" option for sections. Seed data (`scripts/seed/seed_farm.py`, `seed_livestock.py`) creates a real "Karantin bloki" building/section and places a batch there during quarantine. | **REQUIRES CHANGE** — at minimum 5 frontend files, the type definitions, the seed scripts, and the section-type catalogue. |

**Open question (flag for business owner, not resolved here):** Is `CLOSED` simply being renamed to `COMPLETED` with identical semantics (sale/slaughter/transfer/disease/other close reasons preserved), or does "COMPLETED" imply a new semantic (e.g. only reachable when a batch finishes its full natural cycle, with "closed early/disease" handled differently)? This affects whether `BatchCloseReason` needs to change. Recorded as **OQ-REV-01** in the Business Revision Report.

**Open question — SectionType:** Does removing quarantine as a *batch status* also mean removing `quarantine` as a *section type* (i.e., no farm location is specially designated for isolation any more), or does the farm still physically have an isolation/quarantine area, just not tied to a mandatory batch lifecycle stage? Recorded as **OQ-REV-02**.

---

### 2.2 Principle: Dashboard must become analytics-focused.

| Layer | Current State | Classification |
|---|---|---|
| BRD/SRS | SRS §3.1.1 already describes the dashboard as KPI/role-based ("Boshqaruv paneli... foydalanuvchining roliga muvofiq KPI larni... taqdim etish", with FCR/ADG/mortality/stock/sales KPIs, charts, drill-down). VG-01 (BRD §2.5) calls for "real-time dashboards with top 10 KPIs." | **COMPATIBLE** — the *requirement* for an analytics dashboard already exists in the source documents; only the *implementation* lags. |
| Backend | No dedicated analytics/aggregation endpoints exist. `app/reporting` only provides a single-batch performance card (FCR, mortality, cost, profit) for one batch at a time — there is no cross-farm or cross-batch aggregate, trend, or KPI-over-time endpoint. | **REQUIRES CHANGE** — new aggregation endpoints needed (e.g. fleet-wide FCR trend, mortality trend, multi-farm KPI rollup). |
| Frontend | `DashboardPage.tsx` is single-farm-scoped (dropdown selector, not multi-farm aggregate), shows 4 static count/sum `StatCard`s and a "current batches" table — no charts, no trends, no drill-down, no top-10-KPI framing. It is closer to an operational status board than an analytics dashboard. | **REQUIRES CHANGE** — needs charts/trends and (per principle 3 below) likely needs to surface farm-level navigation rather than duplicate farm-detail information. |

---

### 2.3 Principle: Farms become the primary operational view.

| Layer | Current State | Classification |
|---|---|---|
| BRD/SRS | SRS §3.1.3 "Ferma boshqaruvi interfeysi" already lists farm cards showing "hozirgi partiyalar" (current batches) and "ish ko'rsatkichlari" (performance indicators) as part of the farm interface's expected output — i.e., the SRS already implies batches should be visible from the farm view. | **COMPATIBLE** — SRS already anticipates farm-centric batch visibility; current implementation just hasn't built it. |
| Backend | `GET /api/v1/farms/{id}` and the buildings/sections sub-resources exist (P-16). No endpoint currently returns "batches for this farm with current status" bundled with the farm detail response — `BatchListPage` queries batches independently via `farm_id` filter, not through a farm-detail composite endpoint. | **REQUIRES CHANGE (additive)** — likely needs a farm-detail-with-batches composite view, or the frontend simply needs to call the existing batches-by-farm endpoint from within `FarmDetailPage`. |
| Frontend | Confirmed by research: `FarmDetailPage.tsx` currently shows **only** buildings/sections — no batch data inline. Batches live as a fully separate top-level nav item ("Parrandalar") sibling to "Fermalar," not nested under it. Dashboard, not Farms, is the first/primary nav item today. | **REQUIRES CHANGE** — this is the single largest IA (information architecture) change implied by the new principles: batches need to surface inside/under the farm view, and Farms likely needs elevated priority over (or absorption of) today's separate Dashboard-as-landing-page pattern. |

**Open question:** "Farms become the primary operational view" — does this mean farms replace the dashboard as the post-login landing page, or does it mean batches/buildings move to be sub-views of Farms (nested routes) while Dashboard remains the landing page but becomes purely analytics (per 2.2)? These two readings produce different IA. Recorded as **OQ-REV-03**.

---

### 2.4 Principle: Inventory remains separate.

| Layer | Current State | Classification |
|---|---|---|
| BRD/SRS | SRS §3.1.7 describes inventory as its own interface, BRD §6.1 item 10 lists it as a distinct capability area. | **COMPATIBLE** |
| Backend | `app/inventory` is already a fully separate module (own schema, own models: `Warehouse`, `StockItem`, `StockBatch`, `StockMovement`), linked to farms only via a bare (non-FK-enforced) `farm_id` column — no structural coupling to batches beyond an optional, unenforced `feed_inventory_item_id` reference from feed records. | **COMPATIBLE — no change required.** |
| Frontend | `InventoryPage.tsx` is already a standalone top-level nav item/route, not nested under Farms or Batches. | **COMPATIBLE — no change required.** |

This principle is a **confirmation of existing architecture**, not a change driver. No gap.

---

### 2.5 Principle: Building details are operational entities only.

| Layer | Current State | Classification |
|---|---|---|
| BRD/SRS | SRS §7.2 "Bino (Building)" attributes include a `Bino turi (parranda zali/og'il/karantin/yemxona)` (building *type*, including a quarantine type) — i.e., the SRS currently ties building typing partly to compliance/lifecycle concepts (karantin), not purely operational concerns (housing type, feed room). | **REQUIRES REVIEW** — partially contradicts "operational entities only" framing if "karantin" is read as a lifecycle/compliance type rather than a purely physical attribute. |
| Backend | `Building` model today has only `name`, `capacity`, `notes` — **no type field at all**; typing exists one level down, on `Section` (`SectionType = {QUARANTINE, PRODUCTION, ISOLATION, STORAGE}`). So the backend already diverges from the SRS's building-type concept (SRS types a *building*; backend types a *section*) and already includes non-purely-operational values (`QUARANTINE`, `ISOLATION`) at the section level. | **REQUIRES CHANGE** if "operational entities only" means `SectionType` should be reduced to purely physical/operational categories (e.g. housing/production/storage) with `QUARANTINE`/`ISOLATION` removed as a side effect of 2.1. |
| Frontend | `FarmDetailPage.tsx` building form has no type selector (consistent with backend). Section form's type selector includes `Karantin`/`Izolyatsiya`/`Saqlash`/`Ishlab chiqarish`. | **REQUIRES CHANGE** — same section-type catalogue change as above. |

This principle mostly **reinforces principle 2.1** (removing quarantine) rather than introducing a separate new requirement — the only standalone implication is confirming buildings should stay attribute-light (name/capacity/notes), which is already true today.

---

### 2.6 Principle: Daily operations become core workflow.

| Layer | Current State | Classification |
|---|---|---|
| BRD/SRS | ADR-003's MVP primary workflow diagram is already daily-operations-centric (Arrival → Feed → Water → Medication → Vaccination → Mortality → Weight → Close → Profit). §21 of `project_memory.md` documents this as the approved MVP definition. | **COMPATIBLE** — this is already the stated design intent. |
| Backend | Feed, mortality, and weight-sampling use cases and endpoints already exist and are fully implemented under `app/poultry`, each gated to `ACTIVE`-status batches. Vaccination recording exists but currently has **no** status gate (can be recorded in any batch status) — an inconsistency relative to the other three daily-ops endpoints. | **MOSTLY COMPATIBLE** — once quarantine is removed (2.1) and the gate becomes "must be ACTIVE, not COMPLETED" instead of "must be ACTIVE, not QUARANTINE/CLOSED," the daily-ops endpoints need no structural change, only a status-set update. The vaccination gating inconsistency is a pre-existing gap worth flagging regardless of this revision. |
| Frontend | Confirmed: feed/mortality/weight/sales/expense forms already exist inside `BatchDetailPage.tsx`, gated by `status === 'active'`. This is already "daily operations as a core, frequently-used workflow" at the UI level — it just isn't elevated to a top-level dashboard/IA concern (today it's nested three clicks deep: Livestock list → batch detail → scroll to form). | **REQUIRES REVIEW** — the functionality exists; whether "daily operations become core workflow" implies promoting these forms to a more prominent place in the IA (e.g. a dedicated "today's tasks" view reachable from the farm or dashboard) is an open IA question, not a backend gap. |

**Open question:** does "daily operations become core workflow" require a new aggregate/cross-batch "today's tasks" or "pending daily entries" view (e.g. a checklist across all active batches), or is it satisfied by the existing per-batch forms once they're reachable more directly from the new Farm-primary IA (2.3)? Recorded as **OQ-REV-04**.

---

## 3. Summary Table — Compatible / Requires Change / Deprecated

| Area | Compatible | Requires Change | Deprecated |
|---|---|---|---|
| Quarantine concept (status + section type) | — | Yes (extensive) | Yes (BR-004, BP-03 as currently written) |
| Dashboard | Requirement already exists in SRS | Yes (implementation: charts/trends, multi-farm rollup) | — |
| Farms as primary view | SRS already implies farm→batch visibility | Yes (IA: nest/surface batches under farm; landing page decision) | — |
| Archive strategy | — | Yes (currently no archive mechanism for COMPLETED/CLOSED batches at all — SF-24 was deferred to Future Release in ADR-003 §23) | — |
| Batch naming strategy | — | Yes (currently optional free-text `batch_code`, no convention, no auto-generation) | — |
| Inventory separation | Already separate, both layers | — | — |
| Building/section typing | — | Yes (section type catalogue, tied to 2.1/2.5) | Karantin/Isolation as section types, pending OQ-REV-02 |
| Daily feed/mortality/weight workflow | Already implemented, already core to MVP design | Minor (status-set update only) | — |
| User management workflow | Existing RBAC (role + individual permission union) functions today | Pending clarification — see §4 | — |
| Account hierarchy workflow | — | **No such concept currently exists** (see §4) | — |
| Factory/building hierarchy workflow | Farm→Building→Section hierarchy exists and is FK-enforced (mostly) | Minor (cross-schema FK gaps noted below) | — |

---

## 4. Items Requiring Direct Business Clarification Before Backlog Work Can Be Scoped

These are listed in the Business Revision Report in more detail; surfaced here because they block accurate gap classification:

1. **OQ-REV-01:** Is `COMPLETED` a rename of `CLOSED` or a new semantic state?
2. **OQ-REV-02:** Does removing quarantine as a batch status also remove it as a section/place type?
3. **OQ-REV-03:** Does "Farms become the primary operational view" replace the Dashboard as landing page, or just restructure navigation (batches nested under farms) while Dashboard remains the landing page in its new analytics form?
4. **OQ-REV-04:** Is a new cross-batch "daily tasks" aggregate view required, or do the existing per-batch forms satisfy "daily operations become core workflow" once reachable more directly?
5. **OQ-REV-05 ("Account hierarchy workflow"):** The current system has no `Account`/`Organization` entity above `Farm` at all — `User.farm_id` ties one user to at most one farm, and `Farm.owner_user_id` ties one farm to one owner. There is no concept of a company/account that owns multiple farms with delegated sub-accounts, and no manager/subordinate (`reports_to`) relationship between users. The phrase "account hierarchy workflow" in the new requirements has no current system analogue to compare against — **needs a definition from the business owner** (e.g. is this: (a) one owner account managing multiple farms, (b) a reporting-line hierarchy among employees, or (c) something else?) before any gap can be meaningfully assessed.
6. **OQ-REV-06 ("Batch naming strategy"):** Needs a definition of the desired convention (auto-generated sequential code? farm-prefixed code? still free text but mandatory?) before the current optional-free-text `batch_code` can be evaluated as compliant or not.
7. **OQ-REV-07 ("Archive strategy"):** SRS §6.1 item 24/SF-24 (historical archiving, 7-year retention) was explicitly deferred to "Future Release" under ADR-003 — it has **never been implemented in any form** (no archive table, no archive endpoint, no UI). The new business model's request to "analyze archive strategy" is being raised against a feature that doesn't exist yet at all, not one that needs revision — recorded for the Business Revision Report and Backlog Revision Plan as a **net-new analysis topic**, not a regression check.

---

*Gap Analysis — AgroVision Business Model Revision Initiative — 2026-06-18*
*Authored under explicit "do not implement" constraint. No code, schema, or frontend changes were made in producing this document.*

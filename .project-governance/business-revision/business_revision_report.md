# AgroVision — Business Model Revision Report

**Date:** 2026-06-18
**Status:** ANALYSIS ONLY — no implementation performed.
**Companion documents:** `gap_analysis.md`, `backlog_revision_plan.md`, `updated_execution_strategy.md`

This report analyzes each of the eleven requirement areas named in the revision request, in light of the gap analysis. For each area: current state, what the new business principles imply, risks, and a recommendation framed as analysis (not a build order).

---

## 1. Dashboard Redesign

**Current state:** Single-farm, KPI-card-and-table view (`DashboardPage.tsx`). Selects one farm via dropdown, shows 4 `StatCard`s (active batch count, quarantine batch count, active bird count, quarantine bird count), a combined batches table, a low-stock alert banner, and 3 quick-link tiles.

**Implication of new principles:** Two of the four existing `StatCard`s are quarantine-denominated and disappear once 2.1 (no quarantine) lands — the dashboard's current KPI set is roughly halved by this change alone, independent of any analytics redesign. "Analytics-focused" additionally implies trend-over-time visualization (FCR/mortality/ADG trends), which doesn't exist anywhere in the system today (the reporting module produces a point-in-time card per batch, not a time series).

**Risk:** If the dashboard is redesigned before the IA decision in OQ-REV-03 (does Dashboard remain the landing page, or do Farms take that role) is made, the work may need to be redone. Recommend resolving OQ-REV-03 first.

**Recommendation (analysis, not a build instruction):** Treat the dashboard redesign as two independent changes that should be sequenced: (a) remove the quarantine-denominated cards/labels (mechanical, low risk, falls out of 2.1's batch-status change), and (b) add genuine analytics (trends, multi-farm rollups) — the latter requires new backend aggregation endpoints (`app/reporting` has none today) and is a materially larger effort than (a).

---

## 2. Farm Details Redesign

**Current state:** `FarmDetailPage.tsx` shows farm header info + Buildings (inline create) + Sections-per-building (inline create, with a type selector that includes quarantine/isolation). It shows **zero** batch information — a farm's current batches must be found by navigating away to the separate "Parrandalar" (Livestock) section and filtering by farm.

**Implication:** "Farms become the primary operational view" most directly implies closing this exact gap — a farm's current batches, and likely a roll-up of that farm's daily-ops status (e.g. how many batches need today's feed/mortality/weight entry), should appear on `FarmDetailPage` itself.

**Risk:** Without resolving OQ-REV-03, it's unclear whether "Parrandalar" (Livestock/Batches) becomes a sub-route nested under a specific farm (`/farms/:id/batches`) or stays a top-level route that's merely cross-linked more prominently from the farm page. These have different routing/IA consequences for the frontend.

**Recommendation:** This is the most concretely scoped item in the whole revision — batches-by-farm already exists as a backend query capability (`GET /api/v1/batches/?farm_id=...`), so the farm-detail redesign is primarily a frontend composition change once the IA question is settled, not a new backend capability.

---

## 3. Archive Strategy

**Current state:** Does not exist in any form. SF-24 (Historical archiving, 7-year retention) was explicitly placed in "Future Release (Phase 3+)" by ADR-003 (`project_memory.md` §23, §27) and has zero implementation — no archive table, no archive flag on any entity, no UI, no API.

**Implication:** With quarantine removed and only ACTIVE/COMPLETED remaining, a COMPLETED batch presumably still needs to be retained (BRD constraint: minimum 7-year retention, BR-019/BR-024 — audit trail and closed records must not be deleted) but should likely no longer clutter active operational views (dashboards, farm detail batch lists). This is effectively asking: what happens to a batch (and its buildings/sections, if decommissioned) after COMPLETED, from a *visibility* standpoint, separate from data retention (which is a non-negotiable BRD constraint already, retention ≠ archival UI).

**Risk:** Conflating "archive" (a UI/workflow concept — moving something out of the active view) with "delete" or with "data retention" (a compliance/backend concept — must never delete) would violate BR-019/BR-024/BRD §8 constraint 4–5. Any archive strategy must be additive (a filter/flag), never a deletion path.

**Recommendation:** This needs a business decision, not an engineering one, on: (a) what triggers archiving (time since COMPLETED? manual action? farm-level archiving of a whole inactive farm?), (b) who can un-archive, (c) whether archived batches are still searchable/reportable (BRD's audit-readiness goal VG-02 implies yes). Recorded as a backlog item requiring requirements, not a ready-to-build feature.

---

## 4. Batch Naming Strategy

**Current state:** `Batch.batch_code` is an **optional**, free-text `String(50)` field. No auto-generation logic exists anywhere in `create_batch.py`. Frontend placeholder suggests a convention (`"B-2026-001"`) but does not enforce or generate it. If left blank, the UI falls back to displaying `batch.id.slice(0,8)` (a UUID fragment) as the batch's effective name — which is not human-meaningful and is purely an accident of implementation, not a designed identifier scheme.

**Implication:** A "batch naming strategy" requirement is a fair signal that the current accidental-UUID-fallback identification is inadequate for daily operational use by farm workers (who, per BRD's persona definitions, have low digital literacy and need simple, memorable identifiers — not UUID fragments).

**Recommendation:** Needs a concrete convention decided by the business owner — common patterns worth presenting as options (not decided here): farm-prefixed sequential (`FARM01-2026-003`), building/section-prefixed, or pure date+sequence. Whatever is chosen, `batch_code` should likely become **required** (not optional) and **server-generated or server-validated for uniqueness per farm** (today `create_batch.py` only checks for duplicates if a code is actually supplied — an empty code currently bypasses the duplicate check entirely since multiple batches can have a null `batch_code`).

---

## 5. Inventory Separation

**Current state:** Already fully separate at every layer (own DB schema, own top-level nav, own page, farm-scoped only via a loosely-coupled `farm_id`). See Gap Analysis §2.4.

**Recommendation:** No action needed. This is a confirmation, not a change request. Flag explicitly in the backlog as "verified compatible, no work item."

---

## 6. Daily Feed Workflow

**Current state:** Fully implemented (`record_feed.py`, `RecordFeedRequest`), gated to `ACTIVE`-status batches, UI form exists inside `BatchDetailPage.tsx` (date, quantity_kg, water_liters, feed_type, optional inventory item link).

**Implication of new principles:** Functionally unaffected by quarantine removal except the gating condition's *label* changes (still "must be the in-progress status," just renamed/restructured from `ACTIVE only, not QUARANTINE/CLOSED` to `ACTIVE only, not COMPLETED` — net simplification since there's one fewer state to exclude). The "daily operations become core workflow" principle is more about *prominence in the IA* than changing this form's fields or logic.

**Recommendation:** No functional/schema change required beyond the mechanical status-set update that falls out of 2.1. If "core workflow" implies a more prominent entry point (e.g., reachable directly from a farm or a "today's tasks" dashboard widget — see OQ-REV-04), that's a navigation/composition change, not a change to this workflow's own logic.

---

## 7. Daily Mortality Workflow

**Current state:** Fully implemented (`record_mortality.py`), gated to `ACTIVE`, additionally validates quantity does not exceed `current_count`, atomically decrements `current_count`. UI form exists, no status-disable beyond the section-hide-if-not-active pattern shared by all daily forms.

**Recommendation:** Same conclusion as §6 — no functional change required beyond the status-set update.

---

## 8. Daily Weight Workflow

**Current state:** Fully implemented (`record_weight_sampling.py`), gated to `ACTIVE`, computes average weight and age_days server-side. UI form exists.

**Recommendation:** Same conclusion as §6/§7 — no functional change required beyond the status-set update.

**Cross-cutting note for §6–8:** The vaccination use case (`record_vaccination.py`) was found to have **no** status gate at all — it can be recorded against a batch in any status today, unlike feed/mortality/weight. This is a pre-existing inconsistency, not introduced by this revision, but worth flagging since "daily operations become core workflow" may be a good occasion to decide whether vaccination should be gated the same way as the other three (likely yes, for consistency) — recorded as a backlog candidate, not assumed.

---

## 9. User Management Workflow

**Current state:** `UsersPage.tsx` lets a logged-in user (implicitly farm-owner-scoped) create/edit users for their **single** farm. Backend supports hybrid RBAC (role templates ∪ individual per-module-per-action grants), matching SRS §4.1/§11.2/BR-021/BR-026/BR-027 closely. No multi-farm-per-user assignment exists in the UI (`farm_id` is set implicitly from the creator, not selectable).

**Implication:** None of the six new business principles directly mention changing RBAC/permission logic — "user management workflow" is listed under "Requirements to Analyze," which this report reads as "confirm it still fits," not "it must change." The one place it intersects the new principles is structural: if a quarantine-free, farm-primary IA changes which farm(s) a manager-level user needs visibility into (e.g. if "account hierarchy" — see §10 — introduces multi-farm ownership), user management would need a corresponding multi-farm assignment capability it doesn't have today.

**Recommendation:** No change needed on its own. Revisit once OQ-REV-05 (account hierarchy) is answered, since that answer may force a multi-farm-per-user capability that doesn't exist today.

---

## 10. Account Hierarchy Workflow

**Current state:** **Does not exist.** Confirmed by direct code search: no `Account`/`Organization`/tenant entity anywhere in `app/identity` or elsewhere. The only "account" hits in the codebase are about login-lockout ("account is locked after 5 failed attempts"), unrelated to organizational hierarchy. Today: one `User` → at most one `Farm` (via `User.farm_id`); one `Farm` → one owner (`Farm.owner_user_id`, a bare column, not modeled as a relationship with cardinality beyond 1:1 implied). There is no `reports_to`/`manager_id` field anywhere, and no entity that sits above `Farm` (e.g. a company/group owning multiple farms).

**Implication:** This is the largest unknown in the entire revision. BRD §5 already describes a Farm Owner persona who can "create users and assign flexible permissions" across what's implicitly a single farm's staff — multi-farm ownership under one account was never part of the original BRD/SRS scope (SG-02 talks about the *platform* supporting ≥5 farms, not one *owner account* owning ≥5 farms — these are different claims). If "account hierarchy" means a Farm Owner should be able to operate multiple farms under one login (one `Account`, many `Farm`s), this is a genuinely new entity and a non-trivial structural addition: a new `Account`/`Organization` table, a `Farm.account_id` FK, and revisiting whether `User.farm_id` (singular) becomes `User` ↔ `Farm` (many-to-many, scoped within an account).

**Recommendation:** Do not scope backlog work for this until the business owner defines what "account hierarchy" concretely means (see OQ-REV-05 options in Gap Analysis §4.5). This is flagged as the report's top blocking open question.

---

## 11. Factory/Building Hierarchy Workflow

**Current state:** Farm → Building → Section is implemented and FK-enforced for Building→Farm and Section→Building. Two looseness points exist today (informational, not necessarily defects): `Section.farm_id` is a denormalized bare UUID (not FK-enforced) alongside the FK-enforced `building_id`, and `Batch.section_id` is also a bare UUID with no FK constraint at all (cross-module/cross-schema reference, consistent with this being a modular monolith where cross-schema FKs were inconsistently applied during the M5 migration).

**Implication of new principles:** "Factory/building hierarchy workflow" is listed as an analysis item; combined with principle 2.5 ("Building details are operational entities only"), the read here is that the hierarchy itself (Farm→Building→Section) is sound and matches the SRS's entity model (§7.1/§7.2), and the actual work is in the *typing* of the lowest level (`SectionType`), which is entangled with quarantine removal (2.1/2.5) — not a structural hierarchy change.

**Recommendation:** No structural change to the Farm→Building→Section hierarchy itself is implied. The `SectionType` enum's contents are the only piece in scope here, and that's already covered under principle 2.1/2.5 in the Gap Analysis. Separately — not because the new business principles ask for it, but because it surfaced during this review — the unenforced `Section.farm_id` and `Batch.section_id` FKs are a latent data-integrity gap worth a footnote in the backlog as a non-urgent hardening item, independent of this business revision.

---

## 12. Cross-Cutting Risk Summary

| Risk | Source | Mitigation Path |
|---|---|---|
| Building work before IA questions (OQ-REV-01/02/03/04/05/06/07) are answered by the business owner | Every section above | Sequence: clarify open questions → re-scope backlog → then implement |
| Conflating "archive" with "delete," violating 7-year retention (BR-019) | §3 | Treat archive as an additive visibility flag only, never a deletion path |
| Quarantine removal silently breaking seed/demo data and any out-of-band tooling that still expects 3 statuses | Gap Analysis §2.1 | Update `scripts/seed/*` in the same change as the status-enum change, not after |
| Vaccination's missing status gate being mistaken for a regression introduced by this revision | §6–8 cross-cutting note | Already documented here as pre-existing, not new |
| Multi-farm/account-hierarchy scope creep if OQ-REV-05 is answered ambitiously | §10 | Keep the smallest viable answer in mind; this is the single largest structural item in the whole revision if scoped broadly |

---

*Business Revision Report — AgroVision Business Model Revision Initiative — 2026-06-18*
*No implementation performed. All recommendations are framed as analysis pending business-owner clarification of the open questions listed in `gap_analysis.md` §4.*

# AgroVision — Backlog Revision Plan

**Date:** 2026-06-18
**Status:** PLAN ONLY — no backlog document has been edited, no code touched.
**Companion documents:** `gap_analysis.md`, `business_revision_report.md`, `updated_execution_strategy.md`

This document answers three questions for the existing roadmap/backlog (`master_roadmap.md`, `development_backlog.md`, `phase_status.md`, `project_state.md`'s Phase Verification Records): **Can it be reused? Can phases be updated? Must phases be replaced?** — and produces a recommendation.

---

## 1. What the Existing Backlog Actually Is

`master_roadmap.md` and `development_backlog.md` are phase/epic/feature/task breakdowns for **P-00 through P-17**, all of which are marked VERIFIED_COMPLETE (P-15 partially) in `project_state.md`. They were written against ADR-002 (8 microservices) and have since been architecturally superseded by the M0–M8 monolith migration (CL-021 through CL-031) — the roadmap's task descriptions still say things like "Create Alembic initial migration for `users` table" per-service, which no longer matches the consolidated monolith's actual structure. In other words: **this backlog already describes a completed and partially obsolete body of work**, independent of the current business-model revision. It is a historical record, not a forward-looking plan, even before considering the quarantine/dashboard/farm changes.

---

## 2. Can the Existing Backlog Be Reused?

**As a traceability record: yes, keep it.** It correctly documents what was built, when, and against which BRD/SRS sections (P-00–P-17 phase verification records in `project_state.md` are detailed and accurate as a historical log) — do not delete or rewrite history per `project_state.md`'s own stated rule ("Never delete or overwrite history").

**As a source of forward-looking tasks: no, mostly not.** Nearly every task in `master_roadmap.md`/`development_backlog.md` is either (a) already done, (b) written against the now-deleted 8-service architecture (e.g. per-service Alembic migrations — Alembic isn't even wired up for the monolith today, per `migration_decisions.md` MD-008), or (c) silent on the new business principles entirely (quarantine is a *required*, not optional, concept throughout the old backlog's BP-03/BR-004 framing).

**Conclusion: Reuse the document as an append-only historical log (P-00–P-17 stays exactly as-is). Do not retrofit new business-model tasks into it.** A new phase series should be created instead (see §4).

---

## 3. Can Phases Be Updated (In Place)?

Two phases are still technically open and touch areas this revision affects directly:

- **P-15 (MVP Stabilization)** — `project_state.md` marks this `PARTIALLY_COMPLETE` with several remaining checklist items (security review, mobile responsiveness, audit trail verification, backup/restore test, user guide, deployment guide, UAT script) that are **orthogonal to the business-model revision** — they don't reference quarantine, dashboards, or farm hierarchy. These can continue to be tracked and closed independently; no need to fold them into the revision's new phases.
- **P-16/P-17** were Farm Management CRUD and User Management UI — both already VERIFIED_COMPLETE (`CL-018`, `CL-019`). They are not "open" but they are the most recent precedent for *how* a new phase should be scoped/documented in this repo's governance style, and the farm-detail and user-management work implied by this revision is a natural continuation of exactly these two phases' subject matter.

**Conclusion:** Nothing in P-00–P-17 should be reopened or edited. They are closed, verified, and (per governance rule) immutable history. The business-model revision's work is new work, not a continuation of an open phase.

---

## 4. Must Phases Be Replaced? — Recommendation: New Phase Series, Not a Replacement

Recommend a **new phase series, numbered independently from P-00–P-17** (e.g. `BR-01`, `BR-02`, ... — "Business Revision" prefix — to avoid colliding with the `P-` numbering or implying continuity with the now-closed microservices-era roadmap), tracked in a new file (or new section) rather than inserted into `master_roadmap.md`. Rationale:

1. The old `master_roadmap.md` is architecturally tied to the 8-service design in its task-level detail (per-service Alembic migrations, per-service test layout) — reusing its format would require stripping nearly every task anyway.
2. The current system is a modular monolith (`app/<module>/`) — a fresh phase series can be written directly against that real structure instead of carrying forward stale per-service framing.
3. Several of the new principles (account hierarchy, archive strategy, batch naming) have **no existing backlog precedent at all** — they are net-new epics, not modifications of old ones.
4. Keeping P-00–P-17 untouched preserves the audit trail the governance system is built around (`project_state.md`'s explicit "never delete or overwrite history" rule, and the same rule applied throughout the M0–M8 migration's CL-0xx entries).

### Proposed new phase series (naming/sequencing only — scope details belong in `updated_execution_strategy.md`, not here):

| Phase | Name | Depends on business-owner answering | Backlog Source |
|---|---|---|---|
| BR-00 | Business Revision Discovery & Sign-off | N/A — this is the phase that produces the answers | OQ-REV-01 through OQ-REV-07 (this revision's open questions) |
| BR-01 | Batch Status Model Simplification (ACTIVE/COMPLETED) | OQ-REV-01, OQ-REV-02 | `app/poultry` `BatchStatus`/state machine, `app/farm` `SectionType`, seed scripts, 5+ frontend files |
| BR-02 | Farm-Primary Information Architecture | OQ-REV-03 | `FarmDetailPage.tsx`, Sidebar/routing, possibly Dashboard's role as landing page |
| BR-03 | Analytics Dashboard | OQ-REV-03 (sequencing only) | New `app/reporting` aggregation endpoints + dashboard frontend rebuild |
| BR-04 | Batch Naming Convention | OQ-REV-06 | `create_batch.py`, `batch_code` validation, `NewBatchPage.tsx` |
| BR-05 | Daily Operations Workflow Consolidation | OQ-REV-04 (and the vaccination-gating inconsistency noted in the Business Revision Report §6–8) | `app/poultry` daily-ops use cases, `BatchDetailPage.tsx` composition |
| BR-06 | Archive Strategy | OQ-REV-07 | Net-new — no current backlog precedent (SF-24 was Future-Release-deferred, never built) |
| BR-07 | Account Hierarchy (conditional — scope unknown until OQ-REV-05 answered) | OQ-REV-05 | Possibly net-new `Account`/`Organization` entity; could be a no-op if the answer is "no change needed" |
| BR-08 | User Management Multi-Farm Support (conditional on BR-07's outcome) | OQ-REV-05 | `app/identity`, `UsersPage.tsx` |

This table is a **sequencing skeleton**, not an authorization to begin any of BR-01 through BR-08. **BR-00 must complete (i.e., the business owner must answer OQ-REV-01–07) before any other phase is scoped into actual tasks**, exactly as the existing governance system requires architectural decisions to be recorded (as ADRs/MDs) before implementation begins.

---

## 5. Items Explicitly Confirmed as Requiring No Backlog Entry

Per the Gap Analysis and Business Revision Report, these are **closed with no action**, recorded here so they aren't mistakenly re-opened later:

- Inventory separation (already correct, both layers)
- Farm→Building→Section structural hierarchy (already correct; only the leaf-level `SectionType` *values* are in scope, under BR-01)
- Daily feed/mortality/weight workflows' core logic (already correct; only the status-set they check against changes, under BR-01/BR-05)

---

## 6. Governance Process Note

Per this repository's established pattern (see `project_state.md`'s "HOW TO USE THIS FILE" protocol and the monolith migration's MD-0xx decision log), recommend that BR-00's sign-off be recorded as a new decision log (e.g. `business_revision_decisions.md`, mirroring `migration_decisions.md`'s format) once the business owner answers the open questions — at that point `updated_execution_strategy.md` (this directory) should be revised from "strategy pending answers" to "strategy with scoped tasks," and only then should new tasks be added to a real backlog file.

---

*Backlog Revision Plan — AgroVision Business Model Revision Initiative — 2026-06-18*
*No backlog files were modified. No implementation performed.*

# AgroVision — Master Roadmap v2 (Business Model Revision)

**Status:** PLANNING ONLY — no implementation authorized by this document.
**Date:** 2026-06-18
**Supersedes (for forward planning purposes only):** `.project-governance/execution/master_roadmap.md` (P-00–P-17), which remains in place as an immutable historical record of the original microservices-era MVP build. Nothing in that file is edited or deleted.
**Built on:** `business-revision/gap_analysis.md`, `business-revision/business_revision_report.md`, `business-revision/backlog_revision_plan.md`, `execution-v2/decision_log.md` (BMD-001 through BMD-008).
**Companion documents (this directory):** `execution_phases.md`, `phase_dependencies.md`, `verification_checklists.md`, `backlog_items.md`.

---

## 1. Why a v2 Roadmap

The original roadmap (P-00–P-17) was built against ADR-002 (8 microservices) and a business model that required quarantine, individual-animal tracking, RFID, and slaughter workflows as first-class concepts. The architecture has since moved to a modular monolith (M0–M8, complete), and the business model itself has now changed (per `business-revision/` and `decision_log.md`). Rather than retrofit the old roadmap, this v2 roadmap is a clean planning artifact scoped directly against:
- the **real poultry workflow priority chain** specified by the business owner, and
- the **11 named requirements** specified by the business owner, and
- the **explicit removals** specified by the business owner.

No old phase (P-00–P-17) is reopened. This roadmap only adds new phases, prefixed `EX-` ("Execution v2") to avoid numbering collisions.

---

## 2. The Real Poultry Workflow (Priority Chain)

This is the backbone of the entire v2 roadmap — every phase exists to either build, simplify, or align with one link in this chain:

```
Account
  └─► Farm
        └─► Building
              └─► Batch
                    ├─► Daily Feed
                    ├─► Daily Mortality
                    ├─► Daily Weight
                    └─► Medication
                          └─► Inventory (feed/medicine stock backing the above)
                                └─► Finance (cost derived from feed/medicine/labor)
                                      └─► Reports (analytics over the full chain)
```

**Reading this chain:** Account is the ownership/tenancy root. A Farm belongs to an Account. A Building belongs to a Farm. A Batch is placed in a Building/Section. Daily Feed, Daily Mortality, Daily Weight, and Medication are recurring events against an active Batch. Inventory supplies the physical stock consumed by Feed/Medication. Finance derives batch cost from Inventory consumption (plus other expenses) and sale revenue. Reports aggregate across the whole chain for decision-making.

This chain is also the **build and verification order** — each link should be structurally sound before the next link is built on top of it, mirroring how the original P-00–P-17 roadmap and the M0–M8 migration both required verifying each phase before starting the next.

---

## 3. Explicit Removals (apply across all phases, not a separate phase)

These are not a phase with deliverables — they are constraints that every phase below must respect. Any phase whose work would touch one of these areas must remove/simplify it, not preserve or extend it.

| Removed Concept | Current Footprint (per Gap Analysis / Business Revision Report) | Decision Reference |
|---|---|---|
| Quarantine workflows | `BatchStatus.QUARANTINE`, `SectionType.QUARANTINE`, `quarantine_end_date`, `QUARANTINE_MINIMUM_7_DAYS` rule, 5+ frontend label/badge maps, seed data ("Karantin bloki") | BMD-002 |
| Slaughter workflows | `BatchCloseReason.slaughter`, any slaughter-specific UI/labels, BP-14 traceability framing | BMD-003 |
| RFID workflows | RFID/tag-number fields tied to the dormant `_Animal_FutureRelease` model; SRS §3.2 RFID hardware-interface references (informational only, SRS itself is not edited) | BMD-004 |
| Individual bird workflows | `_Animal_FutureRelease` model, `AnimalStatus` enum, per-bird weight/health concepts | BMD-004 |

---

## 4. Phase List (Overview)

Full detail for each phase is in `execution_phases.md`; dependency ordering is in `phase_dependencies.md`; per-phase checklists are in `verification_checklists.md`; flat tasks are in `backlog_items.md`. This table is the index.

| Phase | Name | Priority-Chain Link | Requirement # | Removal Applied |
|---|---|---|---|---|
| EX-01 | Account Foundation | Account | — (new, enables #5) | — |
| EX-02 | Farm Management Revision | Farm | #2 Farm Management CRUD | — |
| EX-03 | Building & Section Simplification | Building | — (supports #3) | Quarantine (section type) |
| EX-04 | Batch Lifecycle Simplification | Batch | — (supports #4, #9) | Quarantine, Slaughter, RFID, Individual bird |
| EX-05 | Batch Auto Naming | Batch | #4 Batch Auto Naming | — |
| EX-06 | Daily Feed Tracking Revision | Daily Feed | #6 Daily Feed Tracking | Quarantine (status gate) |
| EX-07 | Daily Mortality Tracking Revision | Daily Mortality | #7 Daily Mortality Tracking | Quarantine (status gate) |
| EX-08 | Daily Weight Tracking Revision | Daily Weight | #8 Daily Weight Tracking | Quarantine (status gate) |
| EX-09 | Medication Workflow Alignment | Medication | — (consistency fix, supports chain) | Quarantine (status gate) |
| EX-10 | Inventory Linkage Hardening | Inventory | — (confirmed compatible, hardening only) | — |
| EX-11 | Finance Improvements | Finance | #10 Finance Improvements | Slaughter-related cost/sale framing |
| EX-12 | Reporting Improvements | Reports | #11 Reporting Improvements | Quarantine/slaughter KPI removal |
| EX-13 | Farm Detail View Redesign | Farm + Batch (cross-cutting) | #3 Farm Detail View | Quarantine labels |
| EX-14 | Dashboard Redesign | All (cross-cutting) | #1 Dashboard Redesign | Quarantine KPI cards |
| EX-15 | User Management Revision | Account + Farm (cross-cutting) | #5 User Management | — |
| EX-16 | Archive System | Batch (terminal state) | #9 Archive System | — |

**16 execution phases total**, plus the already-complete `EX-00` (Discovery & Sign-off, satisfied by `decision_log.md` — see §5).

---

## 5. EX-00 Is Already Satisfied

`business-revision/updated_execution_strategy.md` defined a discovery phase (BR-00 in that document's draft numbering) gating all further work on seven open questions. The user's instruction that produced this roadmap answered all seven (recorded as BMD-001 through BMD-008 in `decision_log.md`). **EX-00 is therefore CLOSED as of this roadmap's creation** — it is listed here only for traceability, not as upcoming work.

---

## 6. What This Roadmap Does Not Yet Authorize

Per the explicit instruction governing this work: **no code, schema, or frontend implementation is authorized by this roadmap.** This roadmap, and its companion documents, are planning artifacts only. Execution of EX-01 onward requires a separate, explicit go-ahead, exactly as every prior phase in this repository's history (P-00–P-17, M0–M8) required an explicit trigger ("Execute Next," "Continue Migration," etc.) before work began.

---

## 7. Versioning

| Version | Date | Change |
|---|---|---|
| 2.0 | 2026-06-18 | Initial v2 roadmap created from Business Revision Report + Decision Log |

---

*Master Roadmap v2 — AgroVision Business Model Revision Initiative — 2026-06-18*
*Planning only. No implementation performed or authorized.*

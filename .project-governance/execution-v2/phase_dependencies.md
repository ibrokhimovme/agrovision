# AgroVision — Phase Dependencies v2

**Status:** PLANNING ONLY — no implementation authorized.
**Date:** 2026-06-18
**Companion documents:** `master_roadmap.md`, `execution_phases.md`, `verification_checklists.md`, `backlog_items.md`

---

## 1. Dependency Graph

```
EX-01 Account Foundation
   │
   ▼
EX-02 Farm Management Revision
   │
   ├──────────────────────────────────────┐
   ▼                                       ▼
EX-03 Building & Section          EX-15 User Management
   Simplification                     Revision
   │
   ▼
EX-04 Batch Lifecycle Simplification
   │  (gates almost everything below — see §2)
   │
   ├────────────┬────────────┬────────────┬────────────┬────────────┐
   ▼            ▼            ▼            ▼            ▼            ▼
EX-05        EX-06        EX-07        EX-08        EX-09       EX-16
Batch Auto   Daily Feed   Daily        Daily        Medication  Archive
Naming       Tracking     Mortality    Weight       Workflow    System
                          Tracking     Tracking     Alignment
   │            │            │            │            │
   └────────────┴─────┬──────┴────────────┴────────────┘
                       ▼
              EX-10 Inventory Linkage Hardening
                       │
                       ▼
              EX-11 Finance Improvements
                       │
                       ▼
              EX-12 Reporting Improvements
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
EX-13 Farm Detail View         EX-14 Dashboard
   Redesign                       Redesign
```

---

## 2. Dependency Table (explicit, machine-checkable form)

| Phase | Depends On | Reason |
|---|---|---|
| EX-01 | — | Root of the priority chain; no prerequisite |
| EX-02 | EX-01 | Farm must become account-scoped; Account must exist first |
| EX-03 | EX-02 (soft) | Building/Section belong to Farm; not strictly blocked by EX-02's account-scoping, but should not land before Farm's shape is stable. **Recommended to run in parallel with EX-04** (see `master_roadmap.md`'s sequencing note about resolving quarantine consistently across both batch status and section type at the same time). |
| EX-04 | EX-03 (soft, paired) | Batch lifecycle and Section typing both encode "quarantine" today; resolving them together avoids a half-migrated state where a batch has no quarantine status but is still placed in a section labeled quarantine. |
| EX-05 | EX-04 | Naming convention work should start once the lifecycle model (ACTIVE/COMPLETED, no quarantine stage) is final — a new batch's identity shouldn't be designed against a state machine that's about to change. Not a hard technical blocker, but recommended sequencing. |
| EX-06 | EX-04 | Feed's status gate directly reads `BatchStatus`; cannot finalize the gate wording until EX-04's enum is final. |
| EX-07 | EX-04 | Same reasoning as EX-06, for mortality. |
| EX-08 | EX-04 | Same reasoning as EX-06, for weight. |
| EX-09 | EX-04 | Same reasoning as EX-06, for medication (if a gate is added). |
| EX-10 | EX-04, EX-06 | Inventory FK-hardening touches `FeedConsumption.feed_inventory_item_id`, which is poultry-module-owned; sequence after the poultry module's own EX-04/EX-06 changes to avoid two migrations touching the same table back-to-back. |
| EX-11 | EX-04 | Batch close-reason simplification (slaughter removed) affects what "cost summary at batch completion" means for Finance. |
| EX-12 | EX-04, EX-11 (soft) | Reporting's batch performance card reads batch status/close-reason; also likely shares new aggregation backend work with EX-14, so should be scoped near EX-11 once Finance's shape is known. |
| EX-13 | EX-02, EX-03, EX-04, EX-05 | Farm Detail View composes Farm (account-aware), Section (simplified types), Batch (new lifecycle), and Batch naming (new convention) — all four must be settled first since this phase displays all of them together. |
| EX-14 | EX-04, EX-12 (soft) | Dashboard's quarantine-card removal depends on EX-04; its new analytics content likely reuses whatever aggregation capability EX-12 builds. |
| EX-15 | EX-01, EX-02 | User management's multi-farm-within-account capability requires both Account (EX-01) and account-scoped Farm (EX-02) to exist first. |
| EX-16 | EX-04 | Archiving applies to the `COMPLETED` state, which EX-04 defines. |

**Legend:** "soft" dependencies are recommended sequencing for consistency/risk-reduction, not strict technical blockers — they may be relaxed if the business owner prioritizes differently once execution begins.

---

## 3. Critical Path

The longest unavoidable dependency chain is:

```
EX-01 → EX-02 → EX-04 → EX-13
```
(Account → Farm → Batch Lifecycle → Farm Detail View, with EX-03/EX-05 feeding into EX-13 as well)

and separately:

```
EX-01 → EX-02 → EX-04 → EX-11 → EX-12 → EX-14
```
(Account → Farm → Batch Lifecycle → Finance → Reporting → Dashboard)

**EX-01, EX-02, and EX-04 are on every critical path** — they should be treated as the highest-priority, earliest-scheduled phases regardless of which requirement the business owner cares about most, since every other phase either directly or transitively depends on them. This matches the user's own stated priority chain (Account → Farm → Building → Batch first).

---

## 4. Phases With No Outgoing Dependents (safe to defer without blocking other work)

- EX-09 (Medication Workflow Alignment) — only EX-04 depends on it being scoped after, nothing depends on EX-09 finishing.
- EX-10 (Inventory Linkage Hardening) — a hardening-only phase; nothing downstream requires it.
- EX-15 (User Management Revision) — depends on EX-01/EX-02 but nothing else depends on it.
- EX-16 (Archive System) — depends on EX-04 but nothing else depends on it.

These four can be scheduled flexibly (in parallel with the critical path, or deferred later) without risking a blocked phase elsewhere.

---

## 5. Phases Requiring Business-Owner Clarification Before Detailed Tasks Can Be Written

Per `execution_phases.md`, two phases could not be fully scoped into tasks until clarified, because their headline requirement names ("Finance Improvements," "Reporting Improvements") were given without specifying the improvement itself:

- **EX-11 (Finance Improvements)** — **RESOLVED 2026-06-18.** Business owner provided exact scope directly (supplier debt, customer debt, partial payments, outstanding balances, debtor/creditor summary; explicitly excluding budgeting/forecasting/advanced accounting) — see `decision_log.md` BMD-015. Implemented and VERIFIED_COMPLETE; see `backlog_items.md` EX-11 section.
- **EX-12 (Reporting Improvements)** — **RESOLVED 2026-06-18.** Business owner specified Cross-Farm and Cross-Batch Trend Reporting directly (batch performance comparison, mortality/weight/feed/revenue-profit trends, farm-to-farm comparison; explicitly excluding scheduled/email/Telegram delivery and advanced forecasting) — see `decision_log.md` BMD-016. Implemented and VERIFIED_COMPLETE; see `backlog_items.md` EX-12 section.

Both phases' implementations stayed within their fixed dependency position in the graph (EX-04/EX-11 → EX-12 → EX-14) — see `master_roadmap.md` for the unchanged dependency chain.

---

*Phase Dependencies v2 — AgroVision Business Model Revision Initiative — 2026-06-18*
*Planning only. No implementation performed or authorized.*

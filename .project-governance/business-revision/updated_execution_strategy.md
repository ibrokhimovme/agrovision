# AgroVision — Updated Execution Strategy (Business Model Revision)

**Date:** 2026-06-18
**Status:** STRATEGY PENDING BUSINESS-OWNER SIGN-OFF — no implementation authorized by this document.
**Companion documents:** `gap_analysis.md`, `business_revision_report.md`, `backlog_revision_plan.md`

This document is the forward-looking execution strategy for the new business principles. It does **not** authorize implementation — per the explicit instruction governing this entire initiative, no code/database/frontend work has been or should be done until this strategy is reviewed and the open questions below are answered by the business owner.

---

## 1. Guiding Principle

Mirror the discipline already used successfully in this repository for the microservices→monolith migration (`monolith-migration/migration_master_plan.md`'s phase gating, `migration_decisions.md`'s MD-0xx decision log): **no phase begins until its preconditions are explicitly resolved and recorded**, and **every phase is verified before the next starts**. The same anti-destruction posture applies here — quarantine-related code/data should be deprecated and verified-unused before removal, not deleted outright, consistent with how `services/*` was handled in M7.

---

## 2. Phase BR-00 — Discovery & Sign-off (must complete first)

**Goal:** Get explicit, written answers to the seven open questions raised in `gap_analysis.md` §4, so that BR-01 onward can be scoped into real, estimable tasks instead of speculative ones.

| ID | Question | Why it blocks downstream work |
|---|---|---|
| OQ-REV-01 | Is `COMPLETED` a rename of `CLOSED`, or a new semantic? | Determines whether `BatchCloseReason` and close-flow UI need to change beyond a label swap |
| OQ-REV-02 | Does removing quarantine as a batch status also remove it as a section/place type? | Determines `SectionType` enum scope (BR-01) |
| OQ-REV-03 | Does Farms replace Dashboard as the landing page, or just gain nested batch visibility while Dashboard stays the landing page? | Determines BR-02/BR-03 sequencing and routing structure |
| OQ-REV-04 | Is a new cross-batch "daily tasks" view required, or do per-batch forms suffice once more reachable? | Determines whether BR-05 needs a new aggregate endpoint/page or just navigation changes |
| OQ-REV-05 | What does "account hierarchy" concretely mean? (multi-farm-per-owner / reporting-line / other) | Determines whether BR-07/BR-08 are needed at all, and if so their size — potentially the largest item in the whole revision |
| OQ-REV-06 | What batch naming convention is desired? | Determines BR-04's exact validation/generation logic |
| OQ-REV-07 | What should trigger archiving, who can un-archive, and must archived data stay reportable? | Determines BR-06's scope; must not conflict with the 7-year retention constraint (BR-019) |

**Deliverable of BR-00:** a `business_revision_decisions.md` file (new, modeled on `migration_decisions.md`'s format) recording each answer as a numbered decision (BRD-001, BRD-002, ... — to avoid colliding with "BRD" as the document-type abbreviation, consider prefixing decisions as `BMD-001` for "Business Model Decision"). **This document does not exist yet and should be created only once real answers are obtained — not speculatively.**

**Exit criteria:** all seven questions answered and recorded. No BR-01+ task should be added to any backlog file until this exit criterion is met.

---

## 3. Phase Sequencing Rationale (post BR-00)

Once BR-00 is closed, the recommended order — not yet authorized for execution — is:

1. **BR-01 (Batch Status Model Simplification)** first, because it's the one item every other phase either depends on or is entangled with (dashboard KPIs, section types, daily-ops gating all reference batch status). Doing it first avoids other phases building against a 3-status model that's about to change underneath them.
2. **BR-04 (Batch Naming)** can run in parallel with BR-01 — it touches `create_batch.py` and `NewBatchPage.tsx`, which are adjacent to but not blocked by the status-enum change.
3. **BR-02 (Farm-Primary IA)** next, since BR-03 (Analytics Dashboard) and BR-05 (Daily Ops Consolidation)'s navigation questions depend on where farms sit in the IA.
4. **BR-03 (Analytics Dashboard)** and **BR-05 (Daily Ops Consolidation)** can likely run in parallel once BR-02's IA decision is fixed.
5. **BR-06 (Archive Strategy)** is independent of the above and can be scoped any time after BR-00, but should not start implementation until BR-01 defines what "COMPLETED" means (archiving logically applies to COMPLETED batches).
6. **BR-07/BR-08 (Account Hierarchy + its User Management consequences)** last, and only if OQ-REV-05's answer requires any work at all — this could turn out to be a no-op.

This is a dependency ordering, not a time estimate — no effort sizing is offered here since none of BR-01–BR-08 has been scoped into tasks yet (that happens after BR-00, per the Backlog Revision Plan).

---

## 4. What This Strategy Deliberately Does Not Do

- It does not estimate effort/story points — premature before BR-00.
- It does not write Alembic migrations, SQL, or any schema-change script — premature before BR-00, and in any case the monolith currently has no Alembic wiring at all (a pre-existing, separately tracked gap — `migration_decisions.md` MD-008), so any future schema change (e.g. dropping the `quarantine` enum value) needs its own migration-strategy decision, out of scope for this document.
- It does not modify `master_roadmap.md`, `development_backlog.md`, `phase_status.md`, or `project_state.md`. Per the Backlog Revision Plan, those remain an immutable historical record of P-00–P-17.
- It does not assume any specific answer to the seven open questions — every downstream phase description above is conditional language ("if," "depends on") precisely because the answers aren't in yet.

---

## 5. Recommended Immediate Next Action

Present `gap_analysis.md` §4 and this document's §2 table (the seven open questions) to the business owner (Farm Owner / project sponsor) for explicit answers, following this repository's existing Feature Scope Change Protocol (`project_memory.md` §16: "Any feature request... must receive explicit approval from the project sponsor... recorded in Change History before implementation begins"). Only after that sign-off should:
- a `business_revision_decisions.md` be created,
- new BR-0x tasks be added to a real backlog,
- and any code/schema/frontend implementation begin.

---

*Updated Execution Strategy — AgroVision Business Model Revision Initiative — 2026-06-18*
*No implementation authorized. This document defines sequencing and preconditions only.*

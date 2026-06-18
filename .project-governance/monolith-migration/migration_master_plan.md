# AgroVision — Monolith Migration Master Plan

**Initiative:** Controlled migration from microservices architecture to modular monolith architecture.
**Status:** Framework established. Migration execution has NOT started (M0 audit complete, M1 design complete; M2 onward not started).
**Reversibility:** Fully reversible through M6. Irreversible steps (deleting old service directories, dropping RabbitMQ/old DBs) only happen in M7, and only after verification gates in M8-style checks pass for the relevant phase.

---

## Objective

Migrate from:
- 8 independently deployable FastAPI services + api-gateway + RabbitMQ + 7 Postgres databases

to:
- 1 FastAPI application, internally modularized (Identity, Farm, Poultry, Inventory, Finance, Reporting, Notifications, Shared), single Postgres database (schema-per-module), no RabbitMQ requirement (decision pending, see `migration_decisions.md`)

while preserving:
- All existing business functionality (every BRD/SRS-traceable feature currently implemented, per `.project-governance/project_state.md` phase records P-00–P-17)
- All existing code (moved/refactored, not rewritten from scratch, in early phases)
- All existing documentation and governance (this initiative is additive; it does not supersede `.project-governance/project_memory.md`, `execution/master_roadmap.md`, etc. — those remain the record of *what was built*; this directory is the record of *how the architecture is being reshaped*)
- All existing requirements traceability

## Governing Rules (apply to every phase, no exceptions)

1. **No migration starts before the framework (this directory) is established.** Established 2026-06-18.
2. **No merging services, deleting services, deleting RabbitMQ, or deleting infrastructure happens before the relevant phase is reached and verified.** See Anti-Destruction Rule below.
3. **Verify repository state before every step — do not trust documentation alone.** See `migration_verification.md`.
4. **"Continue Migration" execution protocol:** when instructed to continue, (1) read `migration_status.md`, (2) verify repository state against it, (3) determine the next unfinished phase, (4) execute only that phase, (5) update all migration documents, (6) re-verify results. Never skip ahead to a later phase, never execute multiple phases in one pass without explicit instruction.
5. **Anti-Destruction Rule:** code is marked deprecated (e.g. moved to a clearly-labeled location, or annotated, or left running in parallel) before it is deleted. Deletion requires three things to all be true and recorded in `migration_verification.md`: migration verification passed, dependency verification passed (nothing still calls the old path), replacement verification passed (the new path is proven equivalent). Until then, old services/infrastructure may run alongside new code.

## Migration Phases

| Phase | Name | Objective | Reversible? |
|---|---|---|---|
| M0 | Audit | Document current state factually (services, DB, RabbitMQ, contracts, frontend deps) | N/A (read-only) |
| M1 | Target Architecture | Design target module map, DB strategy, inter-module communication, auth — no code | N/A (design-only) |
| M2 | Module Consolidation | Create the monolith skeleton app; copy each service's `api/application/domain/infrastructure` code into its corresponding module **unchanged**, behind module boundaries; old services keep running untouched | Fully reversible — old services untouched |
| M3 | Event Simplification | Decide and implement: in-process event bus (using existing schemas) vs. dropping event infra entirely. Since RabbitMQ is currently 100% unused (audit §3), this phase carries low risk either way | Fully reversible |
| M4 | Database Consolidation | Consolidate 7 Postgres DBs into 1 DB with schema-per-module; resolve `farms_ref` duplication; migrate Alembic histories | Reversible via DB backup/restore until cutover is confirmed |
| M5 | API Consolidation | Replace gateway's reverse-proxy ROUTE_MAP with direct in-app routing to modules; replace reporting-service's two HTTP clients with in-process calls | Reversible — gateway proxy can be restored from git history |
| M6 | Runtime Simplification | Single Docker image/container for the app; update docker-compose to remove redundant service containers (old ones marked deprecated, not deleted yet); enforce module-boundary import rules | Reversible until old containers are removed in M7 |
| M7 | Cleanup | Delete deprecated service directories, RabbitMQ container, and per-service Postgres databases — **only after M8 verification passes for everything being deleted** | **Irreversible** — this is the only destructive phase |
| M8 | Verification | Final end-to-end verification: all BRD/SRS-traced functionality works, all E2E tests pass against the monolith, performance is acceptable, governance docs updated | N/A (verification phase, but gates M7) |

Note: M7 (Cleanup) is listed after M6 per the anti-destruction rule, even though the prompt's example ordering lists Cleanup before Verification — destructive cleanup must never precede its own verification. Each phase also has its own internal "verify before delete" gate (see `migration_verification.md`), so M8 is both a final phase and a recurring discipline applied throughout M2–M7.

## Current Status

See `migration_status.md` for the live tracker. As of 2026-06-18: M0 and M1 complete (this plan + the audit + target architecture design). M2 not started — no service code has been moved, no service has been merged, no database has been touched, RabbitMQ and all infrastructure remain exactly as they are today.

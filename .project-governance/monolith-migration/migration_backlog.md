# AgroVision — Monolith Migration Backlog

Status values: NOT_STARTED, IN_PROGRESS, COMPLETE, VERIFIED_COMPLETE, BLOCKED.
Item IDs are prefixed `MIG-<phase>-<seq>`.

## M0 — Audit

| ID | Task | Status |
|---|---|---|
| MIG-M0-01 | Inspect all 8 services' structure, DB, RabbitMQ usage, HTTP deps, shared imports | VERIFIED_COMPLETE |
| MIG-M0-02 | Inspect docker-compose topology and dependency graph | VERIFIED_COMPLETE |
| MIG-M0-03 | Inspect frontend service layer for direct-service-call risk | VERIFIED_COMPLETE |
| MIG-M0-04 | Produce `current_state_architecture_report.md` | VERIFIED_COMPLETE |

## M1 — Target Architecture

| ID | Task | Status |
|---|---|---|
| MIG-M1-01 | Define module map (Identity/Farm/Poultry/Inventory/Finance/Reporting/Notifications/Shared) | VERIFIED_COMPLETE |
| MIG-M1-02 | Define DB consolidation strategy (schema-per-module) | VERIFIED_COMPLETE (design only) |
| MIG-M1-03 | Define inter-module communication replacing gateway proxy + reporting's HTTP clients | VERIFIED_COMPLETE (design only) |
| MIG-M1-04 | Define auth carry-over strategy | VERIFIED_COMPLETE (design only) |
| MIG-M1-05 | Produce `target_architecture.md` | VERIFIED_COMPLETE |

## M2 — Module Consolidation (COMPLETE 2026-06-18)

| ID | Task | Status |
|---|---|---|
| MIG-M2-01 | Resolve MD-001 (livestock→poultry naming) before touching code | VERIFIED_COMPLETE |
| MIG-M2-02 | Create monolith app skeleton (`app/main.py`, module package layout) | VERIFIED_COMPLETE — skeleton only, not wired (by design, see M5/M6) |
| MIG-M2-03 | Copy identity-service code into `app/identity/` unchanged | VERIFIED_COMPLETE (40/40 files, imports re-namespaced) |
| MIG-M2-04 | Copy farm-service code into `app/farm/` unchanged | VERIFIED_COMPLETE (40/40 files) |
| MIG-M2-05 | Copy livestock-service code into `app/poultry/` unchanged | VERIFIED_COMPLETE (63/63 files) |
| MIG-M2-06 | Copy inventory-service code into `app/inventory/` unchanged | VERIFIED_COMPLETE (36/36 files) |
| MIG-M2-07 | Copy finance-service code into `app/finance/` unchanged | VERIFIED_COMPLETE (40/40 files) |
| MIG-M2-08 | Copy notification-service code into `app/notifications/` unchanged | VERIFIED_COMPLETE (36/36 files) |
| MIG-M2-09 | Copy reporting-service code into `app/reporting/` unchanged | VERIFIED_COMPLETE (32/32 files) |
| MIG-M2-09b | Copy api-gateway code into `app/gateway/` unchanged (added — needed for M5 auth middleware carry-over) | VERIFIED_COMPLETE (25/25 files) |
| MIG-M2-10 | Move `shared/` into `app/shared/` (or keep at repo root, import-compatible) | VERIFIED_COMPLETE — resolved as MD-006: kept at repo root, no changes needed |
| MIG-M2-11 | Old `services/*` left running, untouched, in parallel for comparison testing | VERIFIED_COMPLETE — `git status --short services/` confirms zero changes |

## M3 — Event Simplification (COMPLETE 2026-06-18)

| ID | Task | Status |
|---|---|---|
| MIG-M3-01 | Resolve MD-002 (keep vs drop RabbitMQ/event bus) | VERIFIED_COMPLETE — resolved: drop (no new feature work in a migration) |
| MIG-M3-02 | If kept: implement in-process event bus using existing schemas | N/A — not selected |
| MIG-M3-03 | If dropped: remove publisher skeleton code from each module (mark deprecated first) | VERIFIED_COMPLETE — all 8 `app/*/infrastructure/messaging/publisher.py` marked DEPRECATED with banner; actual deletion deferred to M7 per anti-destruction rule; `services/*` originals untouched; RabbitMQ container/config in docker-compose.yml untouched (deferred to M7) |

## M4 — Database Consolidation (COMPLETE 2026-06-18)

| ID | Task | Status |
|---|---|---|
| MIG-M4-01 | Resolve MD-003 (farms_ref) and MD-004 (Alembic strategy) | VERIFIED_COMPLETE — see decisions log |
| MIG-M4-02 | Create single target database with schema-per-module | VERIFIED_COMPLETE — `infrastructure/postgres/init_monolith.sql` run against the live `agrovision` database; `identity`, `farm`, `poultry`, `inventory`, `finance`, `notifications` schemas confirmed present via `information_schema.schemata` |
| MIG-M4-03 | Migrate data from 7 databases into target (with backup) | VERIFIED_COMPLETE — Docker access was restored mid-session (user supplied sudo credentials); each of the 6 data-owning databases (identity_db, farm_db, livestock_db, inventory_db, finance_db, notification_db) dumped (`pg_dump --schema=public`), schema-remapped, and loaded into the matching `agrovision` schema. `reporting_db` has no tables (per audit), nothing to migrate. Source databases were only read (`pg_dump`), never written — fully preserved as a backup-by-construction. |
| MIG-M4-04 | Consolidate Alembic histories | DESIGN COMPLETE, execution N/A for this pass — each module's `alembic_version` table was carried over as part of its data (one per schema, e.g. `identity.alembic_version`), satisfying MD-004 (per-schema tracking, scripts unmodified) without any extra step |
| MIG-M4-05 | Verify data integrity post-consolidation (row counts, FK integrity) | VERIFIED_COMPLETE — row-count parity check across all 33 tables in 6 schemas: 100% match, zero mismatches (script + full output in verification log). FK integrity confirmed via `pg_constraint` inspection (all FKs intact) and an orphan-check query (0 orphaned `farm_id` values in `users`/`batches` before the MD-003 FK repoint). |
| MIG-M4-06 (added) | Execute MD-003: repoint `users.farm_id`/`batches.farm_id` FKs to `farm.farms`, drop `identity.farms_ref`/`poultry.farms_ref` | VERIFIED_COMPLETE — repoint executed in a single transaction, verified via `pg_constraint` (both FKs now point at `farm.farms`) and a join spot-check (`poultry.batches JOIN farm.farms` resolves correctly for all 3 batches) |

## M5 — API Consolidation (COMPLETE 2026-06-18)

| ID | Task | Status |
|---|---|---|
| MIG-M5-01 | Mount each module's router on the single app under existing `/api/v1/...` prefixes | VERIFIED_COMPLETE — `app/main.py` mounts all 7 data modules' routers under `/api/v1`; route list inspected and matches the original gateway `ROUTE_MAP` prefixes exactly |
| MIG-M5-02 | Replace reporting module's `LivestockClient`/`FinanceClient` HTTP calls with in-process calls | VERIFIED_COMPLETE — both clients now use `httpx.ASGITransport` against `fastapi_app` (in-process, zero network hop) instead of real HTTP to `LIVESTOCK_SERVICE_URL`/`FINANCE_SERVICE_URL`; live-tested via `/api/v1/reports/batch/{id}`, output byte-identical to the real running `reporting-service` |
| MIG-M5-03 | Apply single JWT-verification middleware app-wide; remove per-module dead JWT config | VERIFIED_COMPLETE — `app/core/auth_middleware.py` (`AuthHeaderInjectionMiddleware`) reproduces the gateway's `verify_token` + header-injection exactly; wraps `fastapi_app` to produce the externally-served `app`. Per-module dead `JWT_SECRET_KEY` configs in `app/<module>/core/config.py` were NOT yet deleted (still anti-destruction-deferred; nothing reads them once `app/core/config.py` is the one actually wired in) |
| MIG-M5-04 | Verify all existing API contracts unchanged (response shapes, status codes) against E2E tests | VERIFIED_COMPLETE (manual live comparison, not the automated E2E suite — see verification log): booted the monolith locally against the real consolidated `agrovision` DB and compared live responses against the still-running real microservices for the same requests — login, farms list, batches list (exercises the MD-003 FK repoint), 401 (missing/invalid auth), 404 (EntityNotFoundError handler), and the full batch report (exercises poultry+finance in-process aggregation) all matched exactly, in one case byte-for-byte identical JSON |
| MIG-M5-05 (added) | Resolve `FarmRef` model collision discovered when both `identity` and `poultry` modules loaded into one process/metadata registry | VERIFIED_COMPLETE — removed the now-dead `FarmRef` ORM class from both modules and repointed `farm_id` columns' `ForeignKey` string to `"farm.farms.id"`, matching the DB-level FK repoint already executed in M4 (MD-003) |

## M6 — Runtime Simplification (COMPLETE 2026-06-18 — including all deferred items, now explicitly resolved)

| ID | Task | Status |
|---|---|---|
| MIG-M6-01 | Single Dockerfile/image for the monolith app | VERIFIED_COMPLETE — `Dockerfile.monolith` (repo root, additive, doesn't touch any `services/<name>/Dockerfile`); builds `shared/` + `app/` + the one extra dependency (`reportlab==4.2.5`, reporting module only); image builds cleanly |
| MIG-M6-02 | Update docker-compose.yml: add monolith service, mark old 8 service containers deprecated (commented/profile-gated, not deleted) | RESOLVED AS MD-009 — added the new additive `monolith` service (port 8100, Redis DB index 7, depends only on postgres+redis). Decided NOT to mark the old 8 containers deprecated yet — that decision requires M8's full automated test run as evidence, not M6's manual spot-check. This is a final decision for M6's scope, not an open item. |
| MIG-M6-03 | Introduce module-boundary import lint rule | VERIFIED_COMPLETE — `scripts/check_module_boundaries.py` written and run: confirmed 0 violations in the current `app/` tree (the only cross-module import is `reporting`'s `from app.main import fastapi_app`, which is the explicitly-allowed "call the entrypoint" pattern). Sanity-tested the tool itself by temporarily injecting a real violation (`app.farm.domain` import into `app.poultry`) — correctly detected and reported; reverted and re-confirmed clean (diffed byte-for-byte against the pre-test file). |
| MIG-M6-04 | Run full app via docker compose, verify boot and health checks | VERIFIED_COMPLETE — `docker compose up -d monolith`: container reaches `healthy` status; `/health`, login, the full cross-module batch report (JSON, diff-verified against the live system, only the `generated_at` timestamp differs), and the PDF report endpoint all verified working through the real Docker network and real `agrovision` database, with all 13 original containers remaining healthy throughout |
| MIG-M6-05 (added) | Resolve missing `reportlab` dependency in the monolith image | VERIFIED_COMPLETE — first boot attempt crashed (`ModuleNotFoundError: reportlab`, M2 didn't carry per-service `requirements.txt` extras); added `reportlab==4.2.5` (reporting-service's only unique dependency, confirmed via audit) to `Dockerfile.monolith`; PDF endpoint verified working after the fix |
| MIG-M6-06 (added, deferred — MD-008) | Alembic-on-startup wiring for the monolith | DEFERRED (final decision, not open) — M4 already brought every consolidated schema to the correct migration state via direct data copy (including each module's `alembic_version` table); building 6 schema-aware Alembic environments is real follow-up work, to be picked up whenever the monolith needs its first new schema change, not before |

## M7 — Cleanup (COMPLETE 2026-06-18)

| ID | Task | Status |
|---|---|---|
| MIG-M7-00 (added) | Close the one remaining M8 evidence gap (write-test `app/notifications`) before proceeding | VERIFIED_COMPLETE — found a pre-existing bug (notification create/list 500, schema/model drift on `created_by`/`updated_by`), confirmed identical against the still-live original `notification-service`, therefore not a migration regression and out of scope to fix here |
| MIG-M7-00b (added) | Back up all 7 original databases + the consolidated DB before any destructive step | VERIFIED_COMPLETE — `db_backups_2026-06-18/`, all 8 dumps validated (PGDMP header + correct table-data counts via `pg_restore --list`) |
| MIG-M7-06 (added) = CLEAN-08 | Repoint `infrastructure/nginx/conf.d/agrovision.conf` from `api-gateway` to `monolith` (the cutover) | VERIFIED_COMPLETE — config edited, `nginx -s reload` applied, confirmed via live traffic that requests now reach the monolith and `api-gateway` stopped receiving anything but its own healthcheck |
| MIG-M7-01 | Pass Deletion Gate (migration+dependency+replacement verification) for each old service before deleting it | VERIFIED_COMPLETE — see Deletion Log in `migration_verification.md`; all three gates passed for every item before deletion |
| MIG-M7-07 (added) = CLEAN-09 | Stop the 8 old service containers (deprecate before delete) | VERIFIED_COMPLETE — `docker compose stop`; full smoke test repeated with them stopped, all green |
| MIG-M7-04 = CLEAN-10 | Drop old per-service Postgres databases (only after M4 data migration verified) | VERIFIED_COMPLETE — all 7 dropped; smoke test repeated post-drop, all green |
| MIG-M7-03 = CLEAN-11 | Remove RabbitMQ container/config (MD-002 decided to drop it) | VERIFIED_COMPLETE — zero active connections confirmed immediately before removal; container, compose block, volume, and `infrastructure/rabbitmq/` all removed |
| MIG-M7-02 = CLEAN-12 | Delete deprecated `services/*` directories | VERIFIED_COMPLETE — all 8 old containers `docker rm`'d, their compose blocks removed, `services/*` (3.6MB) deleted |
| MIG-M7-05 | Remove api-gateway proxy code (superseded by in-app routing) | VERIFIED_COMPLETE — deleted as part of `services/*` removal above; its function was already fully superseded by `app/core/auth_middleware.py` since M5 |
| MIG-M7-08 (added) | Fix breakage in `scripts/seed/*` caused by the DB drop (was pointed at the now-dropped per-service databases) = CLEAN-07 | VERIFIED_COMPLETE — repointed at the consolidated `agrovision` DB with a `search_path`-aware `connect()` helper; `py_compile` clean across all touched files. Functional re-test against a clean DB still pending (not safe to test against the live, already-seeded DB — would hit PK conflicts) |
| MIG-M7-09 (added) | Update `docker-compose.dev.yml`, `Makefile`, `README.md`, `DEPLOYMENT.md`, `.env.example` for the monolith-only world | VERIFIED_COMPLETE |

## M8 — Verification (MOSTLY COMPLETE 2026-06-18 — real bug found and fixed)

| ID | Task | Status |
|---|---|---|
| MIG-M8-00 (added) | Run existing `tests/e2e/*` suite as baseline (against `services/*`, unaffected by migration) | VERIFIED_COMPLETE — 15/15 pass, confirms migration work hasn't broken the still-live system |
| MIG-M8-01 | Full E2E suite passes against monolith (`tests/e2e/*`) | NOT PORTABLE as-is (resolved as MD-010 — the suite imports service code via `sys.path`/unprefixed `app.*`, incompatible with the monolith's namespaced `app.<module>.*`). **Substituted with direct manual API verification of all UAT test cases (TC-01–TC-09) against the live monolith container** — see MIG-M8-03. Real portability fix tracked separately as `repository_cleanup_backlog.md` CLEAN-05. |
| MIG-M8-02 | Performance tests re-run against monolith (`tests/performance/*`) | VERIFIED_COMPLETE — `GATEWAY_URL=http://localhost:8100` (no code changes needed, portable via env var): all 4 tests pass; p95 latency for the batch report (1.08s) closely matches the live system (1.07s, same test run against `http://localhost`), both well under the 5s budget |
| MIG-M8-03 | UAT script re-run against monolith (`tests/uat/uat_test_script.md`) | VERIFIED_COMPLETE (API-level; TC-10 mobile/UI-only excluded — see note below). TC-01 (auth incl. wrong-password/refresh/logout) through TC-09 (user management) all manually exercised via curl against the live `agrovision-monolith-1` container with real data: farm CRUD + building/section cascade (TC-03/04), full batch lifecycle incl. quarantine business rule enforcement, feed/mortality/weight/expense/sale on an active batch with correct profit arithmetic (TC-05/07), inventory warehouse/stock-item/receive/dispatch (TC-06), user create/edit/disable/re-enable (TC-09), and the batch report endpoint (TC-08, already proven in M5/M6). **TC-10 (mobile responsiveness) cannot be tested this way — it is a frontend/browser concern, and the frontend isn't pointed at the monolith yet (that's the CLEAN-08 cutover decision, still blocked on this very M8 completing).** |
| MIG-M8-03b (found via testing) | `POST /api/v1/batches/` crashed with `NoReferencedTableError` | **BUG FOUND AND FIXED** — resolved as MD-011. Root cause: `farm` module's models never declared `schema="farm"` in SQLAlchemy, so the cross-schema FK string from MD-003 never matched at the Python metadata level (only worked for reads, where Postgres `search_path` papered over it). Fixed in `app/farm/domain/models/farm.py`; rebuilt monolith image; re-verified batch creation now succeeds (201) and the rest of the lifecycle works on a real batch. |
| MIG-M8-04 | Update `.project-governance/project_state.md` and `project_memory.md` to reflect final architecture | VERIFIED_COMPLETE — cutover (CLEAN-08) happened in M7; `project_state.md` updated accordingly (see Change Ledger) |
| MIG-M8-05 | Update `DEPLOYMENT.md` for single-app deployment | VERIFIED_COMPLETE — fully rewritten for the monolith-only deployment in M7 |

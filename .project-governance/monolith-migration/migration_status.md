# AgroVision — Monolith Migration Status (Live Tracker)

**This is the authoritative record of migration progress. Read this file first whenever told "Continue Migration."**

```
Initiative started:     2026-06-18
Current phase:          M7 COMPLETE. M0–M8 all complete. Migration finished.
Next phase to execute:  None — the migration is done. Remaining open items are
                         follow-up engineering work tracked in migration_backlog.md
                         and repository_cleanup_backlog.md (CLEAN-05 test portability,
                         CLEAN-03 new ADR, CLEAN-07 seed script — now actually fixed,
                         see below), not migration phases.
Repository state:       `services/*` DELETED (8 directories, all source code —
                         backed up nowhere separately since the same code lives on in
                         app/<module>, and git history retains it regardless).
                         `infrastructure/rabbitmq/` DELETED. RabbitMQ container and
                         compose service DELETED. The 7 original per-service Postgres
                         databases DROPPED (full pg_dump backups taken and verified
                         first — see db_backups_2026-06-18/). nginx now routes all
                         real traffic to the monolith (CLEAN-08 cutover complete).
                         docker-compose.yml, docker-compose.dev.yml, Makefile, README.md,
                         DEPLOYMENT.md, .env.example all updated to reflect the
                         monolith-only world. scripts/seed/config.py fixed (was broken
                         by the DB drop — repointed at the consolidated `agrovision`
                         DB with per-module search_path; CLEAN-07 resolved).
Unchanged / still live:  `app/` (the monolith) is now THE application — no longer
                         "additive". `agrovision` consolidated database, postgres,
                         redis, frontend, nginx all running normally.
Reversibility:           NO LONGER FULLY REVERSIBLE. services/* and the 7 original
                         databases are gone from the live system (recoverable from
                         git history + the verified pg_dump backups in
                         db_backups_2026-06-18/, but this is now a real restore
                         operation, not a no-op revert).
```

## Phase Status

| Phase | Status | Date | Evidence |
|---|---|---|---|
| M0 — Audit | COMPLETE | 2026-06-18 | `current_state_architecture_report.md` |
| M1 — Target Architecture | COMPLETE | 2026-06-18 | `target_architecture.md` |
| M2 — Module Consolidation | COMPLETE | 2026-06-18 | All 8 modules copied, file-count parity, `services/*` untouched (at the time) |
| M3 — Event Simplification | COMPLETE | 2026-06-18 | MD-002 (drop RabbitMQ usage), publishers marked DEPRECATED |
| M4 — Database Consolidation | COMPLETE | 2026-06-18 | 6 schemas, 100% row-count parity, MD-003 (farms_ref → farm.farms FK) executed |
| M5 — API Consolidation | COMPLETE | 2026-06-18 | Routers mounted, DB wired, auth trust-boundary split (MD-007), reporting clients in-process |
| M6 — Runtime Simplification | COMPLETE | 2026-06-18 | Dockerfile + additive docker-compose service, lint rule, MD-008/MD-009 decisions recorded |
| M7 — Cleanup | **COMPLETE** | 2026-06-18 | See Deletion Log in `migration_verification.md`. Cutover (CLEAN-08), old container removal (CLEAN-09), DB drop (CLEAN-10), RabbitMQ removal (CLEAN-11), services/* deletion (CLEAN-12) — all executed with backups taken first and full-system verification after each step. |
| M8 — Verification | COMPLETE | 2026-06-18 | Baseline E2E (15/15, against the now-deleted services — historical), performance tests (4/4), full manual UAT pass (TC-01–TC-09) — found and fixed a real cross-schema FK bug (MD-011). Post-cutover re-verification (new, M7-adjacent): full smoke test repeated with all 8 old containers stopped, then again after DB drop, then again after RabbitMQ/services deletion — passed every time. |

## Verification Log (M7 session, 2026-06-18)

| Action | Result |
|---|---|
| Write-tested `app/notifications` (the one module never write-tested in M8) | Found a 500 on notification create/list — reproduced the *identical* error against the still-live original `notification-service` via the real gateway, confirming this is a pre-existing schema/model drift bug (`Notification.created_by`/`updated_by` columns expected by the ORM but never present in the actual table), not a migration regression. Out of scope to fix as part of this migration; left as-is, documented. |
| Backed up all 7 original databases + the consolidated `agrovision` DB (`pg_dump -Fc`) to `db_backups_2026-06-18/` | All 8 dump files verified valid (PGDMP magic header, correct per-table data-entry counts via `pg_restore --list` after `docker cp`) before any destructive step |
| CLEAN-08: repointed `infrastructure/nginx/conf.d/agrovision.conf` upstream from `api-gateway:8000` to `monolith:8100`; updated nginx's `depends_on` in docker-compose.yml | `nginx -s reload` applied; confirmed via live curl through `http://localhost` that real traffic now reaches the monolith; confirmed via `api-gateway` logs that it stopped receiving anything but its own healthcheck pings |
| Full smoke test through the real public entry point post-cutover | frontend 200, login 200, farms 200, batches 200, report 200, report-pdf 200, health 200 |
| CLEAN-09: stopped (not yet deleted) all 8 original service containers | Full smoke test repeated with old containers stopped — all green, confirming zero dependency on them |
| CLEAN-10: dropped all 7 original per-service databases | `\l` confirms only `agrovision`/`postgres`/`template0`/`template1` remain; full smoke test repeated post-drop — all green |
| CLEAN-11: removed RabbitMQ (confirmed zero active connections immediately before stopping it) — container, compose service block, volume, `infrastructure/rabbitmq/` | System verified still functional afterward |
| CLEAN-12: removed the 8 old containers entirely (`docker rm`), removed their docker-compose.yml service blocks, deleted `services/*` (3.6MB, all 8 directories) | Compose config re-validated clean; full smoke test repeated post-deletion — all green |
| Updated `docker-compose.dev.yml`, `Makefile`, `README.md`, `DEPLOYMENT.md`, `.env.example` for the monolith-only world | All reflect current reality, no dangling references to removed services/RabbitMQ outside of intentional historical comments |
| Found and fixed a real, M7-caused breakage: `scripts/seed/config.py` pointed at the 7 now-dropped databases | Repointed all 6 keys at the consolidated `agrovision` DSN, added a `SCHEMAS` map and a `connect(key)` helper that sets `search_path` per module; updated all 6 seed scripts + `verify.py` to use it; `py_compile` clean across all 9 files (CLEAN-07 resolved) |
| Final full-system verification | 5 containers running (monolith, frontend, nginx, postgres, redis — down from 14); login, farms, batches, warehouses, users, report, report-pdf, health all 200 |

## Next Action

The migration is complete. Remaining work is tracked, scoped follow-up engineering, not migration phases:
- **CLEAN-05** — make `tests/e2e/*` portable to `app/<module>` (currently still written against the deleted `services/*` layout and will not run at all anymore; this was already a known gap, now more urgent since there's no fallback `services/*` to test against).
- **CLEAN-03** — write a new ADR documenting the monolith architecture (ADR-002 described microservices; it's now historical).
- Functional re-test of the fixed `scripts/seed/*` against a **fresh** `agrovision` database (not the live one, which already has this exact seed data with the same hardcoded UUIDs — re-running the seed against it would hit primary-key conflicts. This needs a clean DB or a teardown/rebuild cycle to actually exercise, which wasn't done here to avoid disrupting the live verified system).
- A consolidated, schema-aware Alembic setup (deferred per MD-008, still deferred).

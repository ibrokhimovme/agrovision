# AgroVision — Repository Cleanup Backlog

Generated from `repository_cleanup_audit.md` (2026-06-18). Ordered by risk, lowest first.
**No item in this backlog has been executed yet.** Per the deprecation rule: mark DEPRECATED → re-verify → remove. Nothing skips straight to removal.

Status values: NOT_STARTED, DEPRECATED, VERIFIED_FOR_REMOVAL, REMOVED.

---

## Risk Tier 1 — Low risk (self-contained, zero external references found)

### CLEAN-01 — Remove `app/gateway/` (dead code inside the monolith) — REMOVED 2026-06-18
- **What:** the gateway module copied into `app/` during M2 (MIG-M2-09b), never imported by `app/main.py` or any other module — M5 wrote new auth middleware (`app/core/auth_middleware.py`) instead of reusing it.
- **Evidence:** `grep -rln "app\.gateway" app/ --include=*.py` only matched files inside `app/gateway/` itself. Not referenced by `Dockerfile.monolith`'s `CMD`, not imported by `app/main.py`.
- **Risk:** LOW — confirmed correct. Removing it did not affect `services/api-gateway` (a completely separate directory, untouched) or any running container.
- **Execution (2026-06-18):** re-verified the grep finding immediately before removal (still 0 external references), then `rm -rf app/gateway`. Post-removal verification: `python3 -c "from app.main import app"` succeeded; `python3 -m py_compile` on the entire remaining `app/` tree succeeded; rebuilt and restarted the live `agrovision-monolith-1` container (`docker compose build monolith && docker compose up -d monolith`) — reached `healthy`; re-ran the full functional smoke test (`/health` → 200, login → valid JWT, `/api/v1/reports/batch/{id}` → 200) against the rebuilt container; confirmed all 14 containers (13 original + monolith) remained healthy and `git status --short services/` stayed empty throughout.
- **Status:** REMOVED. Verified working post-removal.

### CLEAN-02 — Decide the fate of `infrastructure/postgres/init_monolith.sql` once it's no longer needed standalone
- **What:** this script has already done its one job (created the 6 consolidated schemas in the live `agrovision` DB, M4). It isn't wired into any container's automatic init flow, so it won't re-run on its own.
- **Risk:** LOW (it's inert once already applied; not currently doing any harm by existing).
- **Recommended action:** not a removal candidate yet — KEEP until the monolith's runtime story (M6 follow-up: Alembic wiring, MD-008) is resolved, since this script may need to be re-run or formalized into that flow. Listed here only to track it, not to act on it.
- **Status:** NOT_STARTED (tracking only, no action expected soon).

---

## Risk Tier 2 — Medium risk (requires a small amount of follow-up work before being truly low-risk)

### CLEAN-03 — Update `docs/architecture/overview.md` and related ADRs to reflect the modular-monolith initiative
- **What:** `docs/architecture/overview.md` currently states it "Supersedes: ADR-001 (monolith baseline)" and describes the microservices architecture as the approved, current state — with zero mention that a migration back toward a modular monolith is underway.
- **Risk:** MEDIUM in the sense that leaving it stale risks confusing a future reader (this is a documentation accuracy risk, not a deletion risk — nothing here is being removed).
- **Recommended action:** write a new ADR (e.g. ADR-004) documenting the modular-monolith migration decision, once the migration reaches a real decision point (M7/M8, not before — writing it now would describe an undecided future). Not a deletion task.
- **Status:** NOT_STARTED.

### CLEAN-04 — Make `tests/performance/test_report_latency.py` runnable against the monolith
- **What:** already portable in principle (`GATEWAY_URL` env var, defaults to `http://localhost:8000`) — running it with `GATEWAY_URL=http://localhost:8100` against the live `agrovision-monolith-1` container requires zero code changes, just a documented invocation.
- **Risk:** LOW-MEDIUM (no deletion involved at all — this is an *enablement* task, included here because it directly feeds M8 evidence, which gates the real removal decisions in Tier 3/4).
- **Recommended action:** run it (not a code change) as part of M8. Document the result in `migration_verification.md`.
- **Status:** DONE (M8) — ran with `GATEWAY_URL=http://localhost:8100`: 4/4 pass, p95 1.08s. Result recorded in `migration_verification.md`.

### CLEAN-05 — Port `tests/e2e/{finance,livestock,reporting}` to also run against `app.<module>` (or replace with HTTP-based E2E)
- **What:** these tests currently only work against `services/<name>-service`'s unprefixed `app.domain...` imports (via sys.path manipulation in each `conftest.py`). They cannot currently validate the monolith's `app/finance`, `app/poultry`, `app/reporting` modules at all.
- **Risk:** MEDIUM — this is real engineering work (either parametrize the conftest fixtures to optionally point at `app/<module>` instead of `services/<name>-service`, or rewrite as HTTP tests that can hit either `:8000` or `:8100`). Not a deletion task, but it's the single biggest gap preventing M8 from being comprehensive.
- **Recommended action:** treat as its own implementation task before claiming "M8 complete" — manual spot-checks (already done in M5/M6) are not a substitute for this for a real deprecation decision (MD-009).
- **Status:** STILL NOT_STARTED, now more urgent — `services/*` was deleted in M7, so these tests no longer run against *anything*; this is the single biggest remaining gap in the project's automated test coverage.

### CLEAN-06 — Add a `monolith` override block to `docker-compose.dev.yml` and monolith-aware targets to `Makefile`
- **What:** both files currently only know about the 8 original services. Not broken, just incomplete relative to the new `app/` tree.
- **Risk:** LOW (additive, no deletion).
- **Recommended action:** add `monolith` to `docker-compose.dev.yml` (volume-mount `app/` + `shared/`, `--reload`) and a `migrate-monolith`/`shell-monolith`/`lint-monolith` style target to `Makefile`, whenever active development on `app/` resumes.
- **Status:** DONE (M7) — `docker-compose.dev.yml` now has a single `monolith` override block; `Makefile` rewritten with `lint`/`format`/`shell` targets pointed at the `monolith` service (the per-service loop targets no longer apply since `services/*` is gone).

### CLEAN-07 — Give `scripts/seed/` a consolidated-schema variant (or make it dual-target)
- **What:** `scripts/seed/config.py`'s `DATABASES` dict hardcodes the 7 old per-service DB names (`identity_db`, `farm_db`, ...). This only matters once/if the old databases are ever dropped (M7) — until then it works exactly as today.
- **Risk:** MEDIUM, but **not urgent** — purely a forward-looking dependency, not a current problem.
- **Recommended action:** do not touch until M7 planning actually targets dropping the old databases; flagged here so it isn't forgotten when that day comes.
- **Status:** DONE (M7) — the old databases were in fact dropped in M7, which would have silently broken every seed script. Fixed: `config.py` now points all 6 `DATABASES` keys at the consolidated `agrovision` DSN, with a new `SCHEMAS` map and `connect(key)` helper that sets `search_path` per module; all 6 seed scripts + `verify.py` updated to use it. `py_compile` clean. Functional re-test against a live/clean DB still pending (the current live DB already has this exact seed data with the same hardcoded UUIDs, so re-running would hit PK conflicts — needs a fresh DB to actually exercise).

---

## Risk Tier 3 — High risk (deployment cutover — requires a real decision, not just code changes)

### CLEAN-08 — Repoint `infrastructure/nginx/conf.d/agrovision.conf` from `api-gateway` to `monolith`
- **What:** the single change that would actually make the monolith the live system instead of an additive side-container.
- **Risk:** HIGH — this is a real production cutover. It should only happen after: (a) CLEAN-05's test gap is closed, (b) the full E2E+UAT suite (M8) passes against the monolith, (c) `app/inventory` and `app/notifications` get the same level of live-traffic verification that `app/identity`, `app/farm`, `app/poultry`, `app/finance`, `app/reporting` already received in M5/M6 (per the audit's per-service table, those two modules are "PARTIALLY VERIFIED" — copied and proven to import/compile, but never exercised by a live request in this session).
- **Recommended action:** do NOT execute until M8 is complete and explicitly approved. This is the actual trigger for MD-009's "deprecation decision."
- **Status:** DONE (2026-06-18) — executed under explicit user instruction ("Complete M7 also") that overrode the MD-009/CLEAN-05 preconditions (see `migration_decisions.md` MD-012). `app/inventory`'s write paths had already been verified in M8 (TC-06); `app/notifications` was write-tested immediately before this step and found to have a pre-existing (non-regression) bug, documented rather than blocking on. CLEAN-05's test-portability gap remains genuinely open, not closed — the user's instruction was treated as accepting that residual risk explicitly, not as evidence the gap stopped existing. Config repointed, nginx reloaded, full smoke test passed.

---

## Risk Tier 4 — Irreversible (genuine deletions of live infrastructure — furthest out, gated hardest)

### CLEAN-09 — Deprecate (not yet delete) the 8 `services/*` containers in docker-compose
- **Precondition:** CLEAN-08 has happened and been stable for a meaningful observation period.
- **Risk:** HIGH. Per the architecture migration's own anti-destruction rule, this is a "mark deprecated" step, not a deletion — keep the containers defined (e.g. profile-gated) for some time after cutover in case of rollback need.
- **Status:** DONE (2026-06-18) — stopped via `docker compose stop` immediately after the cutover, with a full smoke test passing while they were stopped (proving zero dependency) before proceeding to delete them in CLEAN-12. The "meaningful observation period" precondition was explicitly shortened per the user's direct instruction to complete M7 in this same session — observation was a single smoke-test pass, not an extended wall-clock window.

### CLEAN-10 — Drop the 7 original per-service databases
- **Precondition:** CLEAN-09 has happened, a full backup exists, and CLEAN-07 (seed script update) is done so dev/demo workflows don't silently break.
- **Risk:** IRREVERSIBLE once executed (data loss if no backup). Requires the full Deletion Gate (migration verification + dependency verification + replacement verification) per `migration_verification.md`.
- **Status:** DONE (2026-06-18) — full `pg_dump -Fc` backup of all 7 databases (plus the consolidated `agrovision` DB) taken and validated *before* dropping anything (`db_backups_2026-06-18/`). Note: CLEAN-07 was actually fixed *after* this step, once the breakage it predicted was confirmed real — sequencing differed slightly from this backlog's original plan but the backup-first safety property was preserved regardless.

### CLEAN-11 — Remove the RabbitMQ container and `infrastructure/rabbitmq/`
- **Precondition:** confirmed (already true today, per M3/MD-002) that nothing publishes or consumes events; re-verify this is still true immediately before removal, since new code could theoretically have been added between now and then.
- **Risk:** MEDIUM-HIGH (the capability has been unused throughout this entire migration, but it's still infrastructure other engineers might expect to exist — verify no out-of-band tooling depends on the RabbitMQ management UI/API before removing).
- **Status:** DONE (2026-06-18) — re-verified zero active connections (`rabbitmqctl list_connections`, empty) immediately before stopping/removing the container; removed the compose service block, the `rabbitmq-data` volume, and `infrastructure/rabbitmq/`.

### CLEAN-12 — Delete `services/*` (expanded from the original "just api-gateway" scope to all 8 directories, matching `migration_backlog.md` MIG-M7-02's broader scope)
- **Precondition:** CLEAN-08 (nginx repointed) AND confirmation that no other tooling (Makefile lint/format targets currently include `api-gateway`) still references it.
- **Risk:** IRREVERSIBLE, HIGH — this is the component nginx and every developer's `make up` currently depends on for all real traffic.
- **Status:** DONE (2026-06-18) — all 8 old containers `docker rm`'d, their compose blocks removed, `services/*` (3.6MB) deleted entirely (not just `api-gateway`, since none of the other 7 had any remaining purpose either once their data and code were both already migrated). `Makefile` and `docker-compose.dev.yml` updated to no longer reference any of them. Compose config re-validated clean; full smoke test passed post-deletion.

---

## Execution Rule Reminder

Per the user's stated process: when told **"Cleanup Next"**, the next action is to (1) read this backlog and the audit, (2) re-verify repository state (don't trust this document's age), (3) select the next item that is genuinely SAFE_TO_REMOVE *right now* (today, that's only CLEAN-01 — everything else in Tier 2+ has an unresolved precondition), (4) re-verify that specific item one more time, (5) remove it, (6) update `repository_cleanup_audit.md`/`repository_cleanup_backlog.md` and the relevant migration documents, (7) record the change in `project_state.md`'s Change Ledger.

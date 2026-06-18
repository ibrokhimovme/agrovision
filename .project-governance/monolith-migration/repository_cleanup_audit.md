# AgroVision — Repository Cleanup Audit

**Audit date:** 2026-06-18
**Method:** Static inspection (`grep`/`find` across the full repo) + direct verification of every claim — no assumption made from a directory's name alone. Cross-referenced against `current_state_architecture_report.md` (M0), `migration_status.md` (M0–M6), and live `docker ps`/`docker compose config` output.
**Context:** the monolith (`app/`) exists, passed M0–M6, and runs as an additive 14th container (`agrovision-monolith-1`) — but **nginx still routes 100% of real traffic to `api-gateway`, not the monolith** (confirmed: `infrastructure/nginx/conf.d/agrovision.conf` has zero references to `monolith` or port 8100). The microservices are still the live, deployed system. Nothing in this audit changes that.

**Status legend:** USED / PARTIALLY USED / LEGACY / DEPRECATED / SAFE TO REMOVE / REQUIRES MIGRATION FIRST.
**Recommended-action legend:** KEEP / DEPRECATE / REMOVE_LATER / SAFE_TO_REMOVE (matches the categories requested for the cleanup backlog).

---

## Top-Level Directories

### `services/`
- **Purpose:** the 8 original microservices (api-gateway + 7 domain services).
- **Current usage:** all 8 are built and run by `docker-compose.yml` (`context: .`, `dockerfile: services/<name>/Dockerfile`), serve all real traffic via nginx → api-gateway → the other 7, and are the only thing `Makefile`'s `migrate`/`test`/`lint`/`format`/`shell-%` targets operate on.
- **References found:** `docker-compose.yml` (8 build blocks), `docker-compose.dev.yml` (8 volume/command overrides), `Makefile` (`SERVICES` list + api-gateway), `DEPLOYMENT.md` (seed command examples), and — critically — **`tests/e2e/{finance,livestock,reporting}/conftest.py` directly inserts `services/<name>-service` onto `sys.path` and imports `app.domain...`/`app.application...` unprefixed.** These are not HTTP E2E tests; they are in-process tests against each service's own `app` package. This means 3 of the 7 domain services are a genuine **test-time runtime dependency**, not just a deployment artifact.
- **Status:** USED (all 8). Not legacy, not deprecated, not migrated-away-from yet.
- **Recommended action:** KEEP. Do not deprecate any service in `services/` until (a) nginx is repointed at the monolith and (b) `tests/e2e/*` is either ported to import from `app.<module>` or replaced by HTTP-based tests that can target either system. Both are real engineering work, not yet started.

### `app/`
- **Purpose:** the modular monolith (M2–M6 of the architecture migration).
- **Current usage:** runs as `agrovision-monolith-1`, additive, not in the live serving path (see above). Verified working for a manually-tested subset of endpoints (M5/M6 verification logs).
- **References found:** `Dockerfile.monolith`, `docker-compose.yml`'s `monolith` service block, `scripts/check_module_boundaries.py` (lints it).
- **Status:** PARTIALLY USED (used by its own container; not used by anything else yet — not the frontend, not nginx, not tests).
- **Recommended action:** KEEP. This is the migration target, obviously not removable.
- **Sub-finding — `app/gateway/` was dead code, REMOVED 2026-06-18:** had been copied from `services/api-gateway` in M2 (MIG-M2-09b) anticipating reuse for the M5 auth middleware, but M5 actually wrote new code in `app/core/auth_middleware.py` instead and never imported `app.gateway` from anywhere. Removed per `repository_cleanup_backlog.md` CLEAN-01 — re-verified zero references immediately before removal, then verified the monolith still imports, compiles, and runs correctly (rebuilt + restarted the live `agrovision-monolith-1` container, re-ran the full functional smoke test) after removal.

### `shared/`
- **Purpose:** common base models, exceptions, API contracts, event schemas — used by every service and module.
- **Current usage:** imported by 69 files under `app/` and 89 files under `services/`. Zero imports from `tests/` or `scripts/` (they don't need it).
- **References found:** `from shared.*`/`import shared.*` across both `app/` and `services/`; `COPY shared/` in every `Dockerfile` (8 services + `Dockerfile.monolith`).
- **Status:** USED — by both architectures simultaneously. This is expected and correct: `shared/` is meant to outlive the migration (per `target_architecture.md` §2, it's planned to remain `app/shared`-equivalent, currently kept at repo root per MD-006).
- **Recommended action:** KEEP. Not a cleanup candidate at any point in this migration — removing it would break both systems.

### `infrastructure/`
- **Purpose:** nginx, RabbitMQ, Postgres bootstrap config.
- **Current usage:**
  - `infrastructure/nginx/` — actively serving all real traffic (frontend + API proxy to api-gateway only).
  - `infrastructure/postgres/init.sql` — actively used; creates the 7 per-service databases on first container start.
  - `infrastructure/postgres/init_monolith.sql` — written in M4, additive; already executed once manually against the live `agrovision` DB (schemas exist). Not wired into any container's init flow (not referenced by docker-compose `volumes:` for the postgres init dir — confirmed by inspection) — it's a one-time script that has already done its job for the current consolidated schemas, but would need re-running if the DB were ever recreated from scratch.
  - `infrastructure/rabbitmq/` — actively used by `rabbitmq` container (mounted config + definitions) and by all 7 domain services' `RABBITMQ_URL` env var. **However**, per M3 (MD-002), RabbitMQ pub/sub is 100% dead code at the application level — nothing publishes or consumes a single event. The container itself is "used" only in the sense that services connect to it and declare an exchange; no actual messaging traffic flows.
- **Status:** nginx/postgres init = USED. RabbitMQ infra = USED (container is live, services connect) but the *capability* it provides is unused (consistent with M0/M3 findings).
- **Recommended action:** nginx/postgres init: KEEP. RabbitMQ infra: KEEP for now (REMOVE_LATER) — removal is explicitly M7 scope in the architecture migration and requires the Deletion Gate; do not remove ahead of that, and do not remove before the monolith (if it ever takes over) also confirms it doesn't need messaging.

### `frontend/`
- **Purpose:** React/TypeScript UI, only talks to one base URL (the gateway, via nginx).
- **Current usage:** actively served container, only API dependency is `/api/v1/...` via nginx → api-gateway. Zero hardcoded service ports (confirmed in the original M0 audit).
- **Status:** USED.
- **Recommended action:** KEEP. Not a cleanup candidate. (Relevant migration fact, not a cleanup fact: because of this single-base-URL design, repointing nginx at the monolith instead of api-gateway would require zero frontend changes — but that repoint hasn't happened.)

### `tests/`
- **Purpose:** `e2e/` (in-process tests against 3 specific services' `app` packages via sys.path swap — see `services/` section above), `performance/` (real HTTP against `GATEWAY_URL`, defaults to `http://localhost:8000`), `uat/` (manual test script, markdown only).
- **Current usage:** `pytest.ini` sets `testpaths = tests`; `Makefile`'s `test` target runs tests *inside each service container* (`docker compose exec $$svc pytest tests/ -v`) — that's each service's own internal `tests/unit`/`tests/integration`, not the root `tests/` directory. The root `tests/e2e` suite is run manually (per `DEPLOYMENT.md`/session history), not wired into any Makefile target or CI.
- **References found:** `pytest.ini`, `tests/e2e/*/conftest.py` (services/ coupling, see above), `tests/performance/test_report_latency.py` (`GATEWAY_URL` env var — portable to the monolith without code changes, just point the env var at `http://localhost:8100`).
- **Status:** USED, but with an important nuance for the migration: `tests/e2e/*` is **not currently portable** to the monolith without rework (it imports `app.domain...` unprefixed, which only resolves against a single `services/<name>` `sys.path` entry, not the namespaced `app.<module>.domain...` the monolith uses). `tests/performance/*` **is** portable (HTTP-based, env-var-configurable).
- **Recommended action:** KEEP everything. No removal candidate here — this is a "requires migration first" finding (the M8 phase of the architecture migration needs this fixed before it can claim full E2E coverage of the monolith), not a cleanup finding.

### `scripts/`
- **Purpose:** `seed/` (idempotent dev/demo data loader, connects directly to the 7 per-service databases by name — `identity_db`, `farm_db`, etc., per `scripts/seed/config.py`), `check_module_boundaries.py` (M6 lint tool, new).
- **Current usage:** `scripts/seed/run_all.py` is the documented way to populate dev data (`DEPLOYMENT.md`); it is in fact how every batch of data this entire migration session has been testing against got there.
- **Status:** USED.
- **Recommended action:** KEEP. **Requires migration first** if the 7 per-service databases are ever dropped (M7) — `scripts/seed/config.py`'s `DATABASES` dict hardcodes the 7 old DB names; it would need a consolidated-schema variant to keep working post-M7. Not a removal candidate now.

### `docs/`
- **Purpose:** architecture/ADR documentation (`overview.md`, `bounded-contexts.md`, `service-ownership.md`, `mvp-scope.md`), API standards, event schema docs, dev conventions.
- **Current usage:** reference documentation, not executed code.
- **Status:** USED as documentation, but **stale relative to the new direction**: `docs/architecture/overview.md` states "Status: Approved (ADR-002)... Supersedes: ADR-001 (monolith baseline)" — i.e. it documents the microservices decision that this very migration is now reversing. It does not yet mention the modular-monolith initiative at all.
- **Recommended action:** KEEP (do not delete — these are real historical ADR records and current onboarding docs for the still-live system). REQUIRES UPDATE (not a deletion task) once the migration reaches a decision point: a new ADR superseding ADR-002 should be written when/if the monolith becomes the deployed system. Tracked as a backlog item, not a removal.

### `.project-governance/`
- **Purpose:** all governance: `project_state.md`, `project_memory.md`, `execution/`, and this session's `monolith-migration/` subdirectory.
- **Current usage:** actively maintained every session, authoritative source of truth per its own stated rules.
- **Status:** USED.
- **Recommended action:** KEEP. Not a cleanup candidate.

### `.github/`
- **Purpose:** presumably CI/CD + issue templates.
- **Current usage:** contains only an **empty** `ISSUE_TEMPLATE/` directory (zero files) and nothing else — no workflows, no CI/CD pipeline exists in this repo at all.
- **Status:** LEGACY/placeholder — not legacy in the "leftover from old architecture" sense, just never populated. Not a microservices-vs-monolith artifact at all.
- **Recommended action:** KEEP (empty directories are harmless; this is outside the scope of the architecture migration). Not added to the cleanup backlog.

### `.claude/`
- **Purpose:** Claude Code harness state (worktrees, settings).
- **Current usage:** contains a worktree directory (`.claude/worktrees/agent-a1ab531791e4d358a/`) — a leftover from a prior agent session's isolated worktree. Already fully gitignored (`.gitignore:84`).
- **Status:** harness-internal, not part of the application or its architecture.
- **Recommended action:** OUT OF SCOPE for this audit — this is not a microservices/monolith artifact, it's tooling state. Flagging its existence for your awareness only; not adding it to the cleanup backlog since removing harness state isn't this initiative's concern and it's already excluded from version control.

### Root-level files (`Dockerfile.monolith`, `docker-compose.yml`, `docker-compose.dev.yml`, `Makefile`, `start.sh`/`stop.sh`/`restart.sh`, `.env`/`.env.example`, `pytest.ini`, `.dockerignore`, `.gitignore`, `README.md`, `DEPLOYMENT.md`)
- **`Dockerfile.monolith`:** USED (builds the monolith container). KEEP.
- **`docker-compose.yml`:** USED — defines all 9 backend containers (8 services + monolith) + infra + frontend + nginx. KEEP.
- **`docker-compose.dev.yml`:** USED for hot-reload dev workflow, but **only overrides the 8 original services** — has no `monolith` override block yet. PARTIALLY USED / REQUIRES UPDATE if monolith-based dev workflow is wanted; not a removal candidate.
- **`Makefile`:** USED, but its `SERVICES` variable and all targets (`migrate`, `test`, `lint`, `format`, `shell-%`) only know about the 8 original services — no monolith targets exist yet. PARTIALLY USED / REQUIRES UPDATE, not a removal candidate.
- **`start.sh`/`stop.sh`/`restart.sh`:** thin wrappers around `docker compose up/down --build`, which now also builds/starts the monolith (additive) since it's in `docker-compose.yml`. USED, no change needed.
- **`.env`/`.env.example`:** USED by every container (services + monolith) via `env_file: .env`. KEEP.
- **Everything else listed:** USED, standard project files, not cleanup candidates.

---

## Services Directory — Per-Service Detail

| Service | Still referenced? | Migrated into monolith? | Status | Recommended Action |
|---|---|---|---|---|
| `services/api-gateway` | Yes — nginx routes 100% of real traffic through it; only auth-verification point currently live | Code copied into `app/gateway` in M2, but **not actually used** by the monolith (M5 wrote new auth middleware instead) | USED (live) | KEEP. Cannot deprecate until nginx is repointed at the monolith — a decision not yet made (MD-009 blocks any deprecation decision on M8 evidence) |
| `services/identity-service` | Yes — live container, issues all real JWTs today | Code copied into `app/identity`, verified working (M5/M6) | USED (live) | KEEP |
| `services/farm-service` | Yes — live container | Code copied into `app/farm`, verified working | USED (live) | KEEP |
| `services/livestock-service` | Yes — live container; **also a direct test-time dependency** (`tests/e2e/livestock/conftest.py` sys.path-imports it) | Code copied into `app/poultry` (renamed per MD-001), verified working, including the `farms_ref` FK fix (MD-003) | USED (live + test) | KEEP |
| `services/inventory-service` | Yes — live container | Code copied into `app/inventory`, not yet exercised in live testing (no M5/M6 test hit this module specifically) | USED (live), PARTIALLY VERIFIED in monolith form | KEEP |
| `services/finance-service` | Yes — live container; **also a direct test-time dependency** (`tests/e2e/finance/conftest.py`) | Code copied into `app/finance`, verified working (exercised via the batch report test) | USED (live + test) | KEEP |
| `services/notification-service` | Yes — live container | Code copied into `app/notifications`, not yet exercised in live testing | USED (live), PARTIALLY VERIFIED in monolith form | KEEP |
| `services/reporting-service` | Yes — live container; **also a direct test-time dependency** (`tests/e2e/reporting/conftest.py`) | Code copied into `app/reporting`, verified working (the batch report test exercised this directly, both JSON and PDF) | USED (live + test) | KEEP |

**None of the 8 services qualify as "Completely unused" or "Safe to remove" today.** All 8 are live, deployed, and serving real traffic; 3 are additionally required by the test suite at the source level. "Migrated into monolith" is true for the *code*, but the *deployment* has not switched over — both copies are simultaneously real right now.

---

## Cross-Cutting Finding: the Monolith Has Its Own Internal Dead Weight

Independent of the services-vs-monolith question, one concrete, low-risk cleanup candidate was found **inside `app/` itself**: `app/gateway/` (8 files, copied in M2, never imported by `app/main.py` or any other module after M5 took a different approach). This is the only item in this audit that is both (a) verified-unused by grep, and (b) has zero references from any deployment, test, or doc artifact. See the backlog for its risk classification.

---

## Summary Table

| Directory | Status | Recommended Action |
|---|---|---|
| `services/*` (all 8) | USED (live + partially test-coupled) | KEEP |
| `app/*` (7 data modules + core + main) | PARTIALLY USED (own container only) | KEEP |
| `app/gateway` | UNUSED (dead code within the monolith) | REMOVE_LATER (low risk — see backlog) |
| `shared/` | USED (both architectures) | KEEP |
| `infrastructure/nginx`, `infrastructure/postgres/init.sql` | USED | KEEP |
| `infrastructure/postgres/init_monolith.sql` | USED (already executed once) | KEEP |
| `infrastructure/rabbitmq` | USED (container live; capability unused) | KEEP for now / REMOVE_LATER (M7-gated) |
| `frontend/` | USED | KEEP |
| `tests/e2e/*` | USED, but NOT portable to monolith without rework | KEEP / REQUIRES MIGRATION FIRST |
| `tests/performance/*` | USED, portable to monolith via env var | KEEP |
| `tests/uat/*` | USED (manual) | KEEP |
| `scripts/seed/*` | USED | KEEP / REQUIRES MIGRATION FIRST (if M7 drops old DBs) |
| `scripts/check_module_boundaries.py` | USED | KEEP |
| `docs/*` | USED, content stale re: new direction | KEEP / docs-update backlog (not a removal) |
| `.project-governance/*` | USED | KEEP |
| `.github/*` | Empty/placeholder, unrelated to migration | KEEP, out of scope |
| `.claude/*` | Harness-internal, gitignored | Out of scope for this audit |
| Root config/scripts | USED (some PARTIALLY — don't yet know about the monolith) | KEEP / minor update backlog |

**Bottom line: nothing in this repository is currently SAFE_TO_REMOVE today.** The only REMOVE_LATER candidate identified is `app/gateway/` (low risk, self-contained, zero external references) — and even that should go through the deprecation step before deletion per the anti-destruction rule. Everything else (RabbitMQ infra, all 8 services, the old per-service databases) is still load-bearing for the live system and is correctly gated behind M8 evidence (MD-009) before any deprecation decision, per the architecture migration's own rules.

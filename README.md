# AgroVision — Poultry Production Management Platform

A production-grade platform for managing poultry batch operations for small and medium farms in Uzbekistan. See [ADR-003](docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md) for MVP scope.

**Architecture note (2026-06-18):** AgroVision was originally built as 8 microservices (ADR-002) and has since been migrated to a modular monolith (`app/`). The migration's full audit trail, decisions, and verification evidence live in `.project-governance/monolith-migration/`. A new ADR documenting this is pending (see `repository_cleanup_backlog.md` CLEAN-03).

---

## What Changed — Microservices → Modular Monolith (2026-06-18)

AgroVision moved from **8 independent FastAPI microservices + RabbitMQ + 7 separate Postgres databases** to **one FastAPI application (`app/`) backed by a single consolidated database**. Nothing about the platform's business functionality changed — every API path, request/response shape, status code, and business rule was verified identical before and after the migration. This section is the human-readable summary; the full step-by-step record (every decision, every piece of verification evidence, every bug found and fixed) lives in `.project-governance/monolith-migration/`.

### Before → After

| | Before | After |
|---|---|---|
| Backend processes | 8 separate services (`api-gateway`, `identity-service`, `farm-service`, `livestock-service`, `inventory-service`, `finance-service`, `notification-service`, `reporting-service`) | 1 process (`app/`, the modular monolith), with the same 7 business domains as internal modules (`identity`, `farm`, `poultry`, `inventory`, `finance`, `notifications`, `reporting`) |
| Inter-service calls | Real HTTP calls through the gateway, plus direct service-to-service HTTP (e.g. reporting → livestock/finance) | In-process Python calls (ASGI transport for the one case that needed it) — no network hop |
| Databases | 7 separate Postgres databases, one per service | 1 database (`agrovision`), one Postgres **schema** per module (`identity`, `farm`, `poultry`, `inventory`, `finance`, `notifications`) |
| Message broker | RabbitMQ (confirmed, via audit, to be 100% unused — no service ever actually published or consumed an event despite the scaffolding existing) | Removed entirely |
| Auth | JWT verified once at `api-gateway`, trusted downstream by every service | JWT verified once by a single app-wide middleware (`app/core/auth_middleware.py`), same trust model preserved for internal calls |
| Containers running | 14 (8 services + gateway + RabbitMQ + Postgres + Redis + frontend + nginx) | 5 (monolith + Postgres + Redis + frontend + nginx) |
| Routing | nginx → api-gateway → individual service, by `ROUTE_MAP` | nginx → monolith directly, same `/api/v1/...` paths, frontend required zero changes |

### Why

Eight services for a platform of this size added operational overhead (8 containers, 7 databases, a message broker) without giving anything back — the audit that kicked off this work found RabbitMQ was wired into every service but never actually used by any of them, and the services talked to each other constantly over plain HTTP for things that didn't need network isolation. Consolidating into one process with module boundaries (enforced by `scripts/check_module_boundaries.py`, a lint rule that fails if one module reaches into another's internals instead of its public entrypoint) keeps the same separation of concerns without the infrastructure cost.

### How it was done (8 phases, each verified before the next started)

1. **Audit** — inspected every service's code, database, and dependency graph; confirmed RabbitMQ was unused; mapped the gateway's full routing table.
2. **Target design** — defined the module map, the schema-per-module database strategy, and how reporting's external HTTP calls would become in-process calls.
3. **Module consolidation** — copied each service's code into `app/<module>/` unchanged (only import paths were renamed to be namespaced), with the original `services/*` left running untouched throughout for live comparison.
4. **Event simplification** — decided not to build a new event bus (that would have been a new feature, not a migration); the dead publisher code was marked deprecated, not silently deleted.
5. **Database consolidation** — created the 6 schemas inside one `agrovision` database, migrated all data from the 7 original databases with a 100% row-count parity check across 33 tables, then repointed a stale denormalized FK (`farms_ref`) at the real `farm.farms` table.
6. **API consolidation** — mounted every module's router on one FastAPI app under the same `/api/v1/...` paths the frontend already used; found and fixed two real bugs in the process (a duplicate ORM class collision, and an internal auth-boundary regression).
7. **Runtime simplification** — built one Docker image and one additive `monolith` container; added the module-boundary lint rule; proved the containerized app produces byte-identical output to the live system for the same requests.
8. **Verification, then cleanup** — ran the existing automated test suite as a baseline, ran performance tests, and manually exercised every user-facing workflow (auth, farms, batches, feed/mortality/weight tracking, inventory, finance/profit, user management, reports) against the running monolith — which is how a real bug (a cross-schema foreign key that worked for reads but crashed on writes) was caught and fixed before anything was cut over. Only after all of that did the actual cutover happen: nginx was repointed at the monolith, the 8 old containers were stopped then removed, the 7 old databases were dropped (after taking and validating full backups), RabbitMQ was removed, and `services/*` was deleted.

### What stayed exactly the same

- Every REST API path and response shape (`/api/v1/auth/...`, `/api/v1/farms/...`, `/api/v1/batches/...`, etc.) — the frontend needed zero code changes.
- Every business rule (quarantine periods, active-batch-only restrictions on feed/mortality/weight records, profit calculation arithmetic, RBAC permission checks).
- All historical data — migrated with a verified 100% row-count match, not regenerated.
- Default credentials, JWT behavior, and session handling.

### What a developer needs to do differently now

- Run `docker compose up --build` exactly as before — it now starts the monolith instead of 8 services, same one command.
- Backend code lives in `app/<module>/` instead of `services/<name>-service/app/`.
- There's one container to read logs from (`docker compose logs monolith`) instead of eight.
- `make migrate` no longer exists — Alembic-on-startup isn't wired up yet for the monolith (tracked as follow-up work); the database is already at the correct schema version from the one-time migration.
- See [Database Migrations](#database-migrations), [Troubleshooting](#troubleshooting), and [Repository Structure](#repository-structure) below for specifics.

---

## Quick Start

```bash
# Start the stack (infrastructure + the monolith + frontend)
docker compose up --build
```

The `.env` file with development defaults is included. No additional setup is required.

---

## Service URLs

After `docker compose up --build`:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost | React SPA (served by Nginx) |
| API (via Nginx) | http://localhost/api/v1/... | All backend traffic, routed to the monolith |
| Monolith (direct) | http://localhost:8100/docs | Swagger UI — identity, farm, poultry, inventory, finance, notifications, reporting all in one app |
| PostgreSQL | localhost:5432 | User: `agrovision` / `agrovision_dev`, single DB: `agrovision` (schema per module) |
| Redis | localhost:6379 | Password: `redis_dev` |

---

## Verify Services

```bash
# Check all container health status
docker compose ps

# Check the monolith's health endpoint
curl http://localhost:8100/health

# Verify PostgreSQL connectivity
docker compose exec postgres psql -U agrovision -d agrovision -c "\dn"
# Expected schemas: identity, farm, poultry, inventory, finance, notifications

# Verify Redis
docker compose exec redis redis-cli ping
```

---

## Convenience Scripts

```bash
./start.sh          # docker compose up --build
./stop.sh           # docker compose down
./restart.sh        # docker compose down && docker compose up --build
```

---

## Development with Hot-Reload

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Changes to `app/` and `shared/` are reflected immediately without rebuild.

---

## Database Migrations

**Not currently wired up for the monolith.** The consolidated `agrovision` database's schemas were brought to their current state via a one-time manual migration during the M4 phase of the architecture migration (data copied from the original 7 per-service databases, which have since been dropped — see `.project-governance/monolith-migration/migration_decisions.md` MD-004/MD-008). A proper consolidated Alembic setup (per-module migration directories, schema-aware `env.py`) is tracked as follow-up work, not yet built.

---

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript (Vite) |
| Backend | FastAPI (Python 3.12), modular monolith — one process, modules: identity, farm, poultry, inventory, finance, notifications, reporting |
| Primary Database | PostgreSQL 16 — single `agrovision` database, one schema per module |
| Cache | Redis 7 |
| Reverse Proxy | Nginx 1.25 |
| Auth | JWT (access 30min, refresh 7d), single app-wide verification middleware |
| ORM | SQLAlchemy 2.x (async) |
| Containerization | Docker + Docker Compose |

See [Architecture Overview](docs/architecture/overview.md) and [ADR records](docs/decisions/) for the original microservices design, and `.project-governance/monolith-migration/target_architecture.md` for the current modular-monolith design (those docs are pending a refresh per CLEAN-03).

---

## Modules (formerly separate services)

| Module | Path | Domain |
|--------|------|--------|
| identity | `app/identity` | Auth, users, roles, permissions |
| farm | `app/farm` | Farms, buildings, sections |
| poultry | `app/poultry` | Poultry batches, health, growth |
| inventory | `app/inventory` | Warehouses, feed, medicine, equipment |
| finance | `app/finance` | Expenses, sales, batch profit |
| notifications | `app/notifications` | Alerts, in-app notifications |
| reporting | `app/reporting` | Batch performance cards, PDF |

All mounted under `/api/v1/...` on a single FastAPI app (`app/main.py`) — the same paths the old API gateway used to proxy to, so the frontend required no changes.

---

## Repository Structure

```
/
├── frontend/                  React + TypeScript SPA
├── app/                       Modular monolith (the application)
│   ├── identity/               Auth, RBAC, users
│   ├── farm/                   Farm catalog
│   ├── poultry/                Poultry batches, health, growth (MVP)
│   ├── inventory/               Warehouse & stock (FIFO/FEFO)
│   ├── finance/                 Expenses, sales, batch profit
│   ├── notifications/           Alerts
│   ├── reporting/               Reports & analytics
│   ├── core/                    Consolidated settings, app-wide auth middleware
│   └── main.py                  Single FastAPI app, mounts every module
├── shared/
│   ├── contracts/              API response schemas (APIResponse, ErrorResponse)
│   ├── events/                 Domain event schemas (currently unused — see MD-002)
│   ├── models/                 SQLAlchemy base models (UUIDPrimaryKeyMixin, etc.)
│   ├── utils/                  Shared utilities
│   └── exceptions/             Domain exception hierarchy
├── infrastructure/
│   ├── nginx/                  Reverse proxy config (routes to the monolith)
│   └── postgres/               DB init scripts (single `agrovision` database + schema bootstrap)
├── scripts/
│   ├── seed/                   Dev/demo data loader (NOTE: targets the old per-service DB names —
│   │                            needs updating post-M7, see repository_cleanup_backlog.md CLEAN-07)
│   └── check_module_boundaries.py  Lint rule: modules may only call each other's public entrypoint
├── docs/
│   ├── architecture/           Architecture overview, bounded contexts, MVP scope (pre-migration)
│   ├── api/                    REST + event standards
│   ├── development/            Coding, git, commit standards
│   └── decisions/               ADR-001, ADR-002, ADR-003
└── .project-governance/        Project memory, BRD/SRS traceability, and the full
                                 monolith-migration audit trail (monolith-migration/)
```

---

## Troubleshooting

**Monolith fails to start:**
```bash
docker compose ps postgres redis
docker compose logs monolith --tail 50
docker compose logs --tail 30
```

**PostgreSQL connection refused:**
```bash
docker compose exec postgres psql -U agrovision -c "\l"
# Expected: a single `agrovision` database (the 7 old per-service databases were dropped in M7)
```

**Build fails due to `shared` package not found:**
Build context is the repository root. Do not change `context: .` in docker-compose.yml.

**Port conflicts:**
If ports 80, 8100, 5432, or 6379 are in use:
```bash
lsof -i :8100
# Then stop docker compose and kill the conflicting process
```

---

## Documentation

- [Architecture Overview](docs/architecture/overview.md) (pre-migration; describes the original microservices design)
- [MVP Scope](docs/architecture/mvp-scope.md)
- [Bounded Contexts](docs/architecture/bounded-contexts.md)
- [Service Ownership Matrix](docs/architecture/service-ownership.md) (now module ownership)
- [ADR-003: MVP Realignment](docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md)
- [API Standards](docs/api/standards.md)
- [Event Standards](docs/api/events.md) (events currently unused — see migration_decisions.md MD-002)
- [Development Standards](docs/development/standards.md)
- [Monolith Migration: full audit trail](.project-governance/monolith-migration/) — `current_state_architecture_report.md`, `target_architecture.md`, `migration_status.md`, `migration_decisions.md`, `migration_verification.md`, `repository_cleanup_audit.md`, `repository_cleanup_backlog.md`

---

## Source Documents

- `1. BRD_AgroVision_Farm_Management_qism1.docx` — Business Requirements Document (Part 1)
- `2. SRS_AgroVision_Farm_Management_v1.1.docx` — Software Requirements Specification v1.1

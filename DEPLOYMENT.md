# AgroVision — Deployment Guide
**Version:** 2.0 | **Date:** 2026-06-18
**Architecture:** Modular monolith (migrated from 8 microservices — see `.project-governance/monolith-migration/` for the full migration record)

---

## Prerequisites

- Docker ≥ 24 and Docker Compose v2
- Git
- 2 GB RAM minimum (one application container instead of eight)
- Ports 80 and 8100 free on the host

---

## Environment Configuration

Copy the example env file and fill in all required secrets before starting:

```bash
cp .env.example .env
```

**Required variables in `.env`:**

```dotenv
# Must be changed from "changeme" for staging/production
JWT_SECRET_KEY=<generate: openssl rand -hex 32>

# Database password
POSTGRES_PASSWORD=<strong-password>

# Redis
REDIS_PASSWORD=<strong-password>

# Environment label — the app validates JWT_SECRET_KEY in non-development
ENVIRONMENT=production
```

Generate a secure JWT secret:
```bash
openssl rand -hex 32
```

**Note:** RabbitMQ variables are no longer used — RabbitMQ was removed in the M7 cleanup phase (it was confirmed unused by any service throughout the project's history; see `migration_decisions.md` MD-002).

---

## Development (local)

```bash
# Start the stack (postgres, redis, the monolith, frontend, nginx)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Frontend (hot reload, separate from the container)
cd frontend && npm install && npm run dev
```

Available at:
- Frontend: http://localhost
- API (via Nginx): http://localhost/api/v1/...
- Monolith direct + API docs: http://localhost:8100/docs

Default admin: `admin@agrovision.uz` / `Admin123!`

---

## Production

```bash
# 1. Set ENVIRONMENT=production in .env (triggers JWT secret validation at startup)
# 2. Start stack
docker compose up -d --build

# 3. Verify all containers healthy
docker compose ps
```

**Database migrations:** not currently automated for the monolith (see "Database Migrations" below) — the consolidated database was brought to its current schema state via a one-time manual migration during the architecture migration's M4 phase. There is no seed-data step needed for a fresh production deploy; seeding (`scripts/seed/`) is a dev/demo-only convenience and currently targets the old per-service database names (needs updating — tracked as `repository_cleanup_backlog.md` CLEAN-07).

---

## Database Migrations

**Not currently wired up.** The monolith does not run Alembic on startup (deferred — see `migration_decisions.md` MD-008). The single `agrovision` database has 6 schemas (`identity`, `farm`, `poultry`, `inventory`, `finance`, `notifications`), each still tracking its own `alembic_version` (carried over from the original per-service databases during the M4 consolidation). If you need to make a schema change:

1. Write a new Alembic revision under the relevant module (a proper per-module migration directory structure for `app/<module>` is not yet built — this is real follow-up work).
2. Until that exists, apply schema changes manually against `agrovision`, target schema via `SET search_path` or schema-qualified DDL, and update that schema's `alembic_version` table to match.

---

## Backup and Restore

**Backup the database:**

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

docker compose exec -T postgres pg_dump -U agrovision -Fc agrovision > "$BACKUP_DIR/agrovision.dump"
echo "Backup complete: $BACKUP_DIR/agrovision.dump"
```

**Restore:**

```bash
cat backups/20260618_120000/agrovision.dump \
  | docker compose exec -T postgres pg_restore -U agrovision -d agrovision --clean --if-exists
```

(A historical pre-cutover backup of the original 7 per-service databases, taken immediately before they were dropped in M7, is kept at `.project-governance/monolith-migration/db_backups_2026-06-18/` for reference/rollback purposes only — not part of routine backup procedure.)

---

## Health Checks

```bash
# Via Nginx (public entry point)
curl http://localhost/health

# Monolith directly
curl http://localhost:8100/health
```

---

## Logs

```bash
# Everything
docker compose logs -f

# The monolith only
docker compose logs -f monolith

# Last 100 lines
docker compose logs --tail=100 monolith
```

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `JWT_SECRET_KEY must be set` on startup | `ENVIRONMENT=production` with default secret | Set `JWT_SECRET_KEY` in `.env` |
| `Connection refused` from Nginx | Monolith not yet healthy | Wait 10–20s after `docker compose up`; check `docker compose ps` |
| Frontend shows a loading/error state for data | Monolith not reachable | Verify `docker compose logs monolith`; confirm Nginx's `conf.d/agrovision.conf` upstream points at `monolith:8100` |
| `relation "X" does not exist` after a fresh `agrovision` database | Schemas not bootstrapped | Run `infrastructure/postgres/init_monolith.sql` against the `agrovision` database, then restore/apply data as needed |

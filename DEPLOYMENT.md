# AgroVision — Deployment Guide
**Version:** 1.0 | **Date:** 2026-06-17

---

## Prerequisites

- Docker ≥ 24 and Docker Compose v2
- Git
- 4 GB RAM minimum (8 GB recommended)
- Ports 3000 and 8000 free on the host

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

# Database passwords
POSTGRES_PASSWORD=<strong-password>

# RabbitMQ
RABBITMQ_DEFAULT_PASS=<strong-password>

# Redis
REDIS_PASSWORD=<strong-password>

# Environment label — services validate JWT_SECRET_KEY in non-development
ENVIRONMENT=production
```

Generate a secure JWT secret:
```bash
openssl rand -hex 32
```

---

## Development (local)

```bash
# Start all services + databases
docker compose -f docker-compose.dev.yml up --build

# In a second terminal — seed roles and admin user
docker compose -f docker-compose.dev.yml exec identity-service python seeds/seed_roles.py

# Frontend (hot reload)
cd frontend && npm install && npm run dev
```

Services available at:
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs

Default admin: `admin@agrovision.uz` / `Admin@123`

---

## Production

```bash
# 1. Set ENVIRONMENT=production in .env (triggers JWT secret validation at startup)
# 2. Start stack
docker compose up -d --build

# 3. Run database migrations (first deploy only)
for svc in farm-service identity-service livestock-service inventory-service finance-service notification-service reporting-service; do
  docker compose exec $svc alembic upgrade head
done

# 4. Seed initial data
docker compose exec identity-service python seeds/seed_roles.py

# 5. Verify all containers healthy
docker compose ps
```

---

## Database Migrations

Each service manages its own schema via Alembic.

```bash
# Apply pending migrations for one service
docker compose exec <service-name> alembic upgrade head

# Rollback last migration
docker compose exec <service-name> alembic downgrade -1

# View migration history
docker compose exec <service-name> alembic history
```

---

## Backup and Restore

**Backup all PostgreSQL databases:**

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

for db in farm_db identity_db livestock_db inventory_db finance_db notification_db reporting_db; do
  docker compose exec -T postgres pg_dump -U agrovision "$db" \
    | gzip > "$BACKUP_DIR/${db}.sql.gz"
  echo "Backed up $db"
done
echo "Backup complete: $BACKUP_DIR"
```

**Restore a database:**

```bash
gunzip -c backups/20260617_120000/farm_db.sql.gz \
  | docker compose exec -T postgres psql -U agrovision farm_db
```

---

## Health Checks

```bash
# API Gateway
curl http://localhost:8000/health

# Individual services (internal ports)
curl http://localhost:8002/health   # farm-service
curl http://localhost:8003/health   # livestock-service
```

---

## Logs

```bash
# All services
docker compose logs -f

# Single service
docker compose logs -f api-gateway

# Last 100 lines
docker compose logs --tail=100 livestock-service
```

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `JWT_SECRET_KEY must be set` on startup | ENVIRONMENT=production with default secret | Set `JWT_SECRET_KEY` in `.env` |
| `Connection refused` to downstream service | Service not yet healthy | Wait 10–20s after `docker compose up`; check `docker compose ps` |
| `alembic: command not found` | Running outside container | Use `docker compose exec <svc> alembic ...` |
| Frontend shows "Fermalar yuklanmadi" | API Gateway not reachable | Verify `VITE_API_BASE_URL` points to gateway |

# AgroVision — Poultry Production Management Platform

A production-grade microservices platform for managing poultry batch operations for small and medium farms in Uzbekistan. See [ADR-003](docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md) for MVP scope.

---

## Quick Start

```bash
# Start all services (infrastructure + all 8 microservices + frontend)
docker compose up --build
```

The `.env` file with development defaults is included. No additional setup is required.

---

## Service URLs

After `docker compose up --build` all services are available:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost | React SPA (served by Nginx) |
| API Gateway | http://localhost:8000 | Entry point; JWT verification |
| API Gateway Docs | http://localhost:8000/docs | Swagger UI |
| Identity Service | http://localhost:8001/docs | Auth, users, RBAC |
| Farm Service | http://localhost:8002/docs | Farm catalog |
| Livestock Service | http://localhost:8003/docs | Batch management |
| Inventory Service | http://localhost:8004/docs | Feed, medicine, stock |
| Finance Service | http://localhost:8005/docs | Expenses, sales, profit |
| Notification Service | http://localhost:8006/docs | Alerts, WebSocket |
| Reporting Service | http://localhost:8007/docs | Batch performance reports |
| RabbitMQ Management | http://localhost:15672 | User: `agrovision` / `rabbitmq_dev` |
| PostgreSQL | localhost:5432 | User: `agrovision` / `agrovision_dev` |
| Redis | localhost:6379 | Password: `redis_dev` |

---

## Verify Services

After startup, verify all services are healthy:

```bash
# Check all container health status
docker compose ps

# Check API Gateway health
curl http://localhost:8000/health

# Check all service health endpoints
for port in 8000 8001 8002 8003 8004 8005 8006 8007; do
  echo -n "Port $port: " && curl -sf http://localhost:$port/health || echo "UNHEALTHY"
done

# Verify RabbitMQ management UI
curl -u agrovision:rabbitmq_dev http://localhost:15672/api/overview | python3 -m json.tool

# Verify PostgreSQL connectivity
docker compose exec postgres psql -U agrovision -c "\l"

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

For development with live code reload on every service:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Changes to `services/<name>/app/` and `shared/` are reflected immediately without rebuild.

---

## Database Migrations

Run Alembic migrations per service after first startup:

```bash
# Run migrations for a specific service
docker compose exec identity-service alembic upgrade head
docker compose exec farm-service alembic upgrade head
docker compose exec livestock-service alembic upgrade head
docker compose exec inventory-service alembic upgrade head
docker compose exec finance-service alembic upgrade head
docker compose exec notification-service alembic upgrade head
docker compose exec reporting-service alembic upgrade head

# Or run migrations for all services at once
for svc in identity-service farm-service livestock-service inventory-service finance-service notification-service reporting-service; do
  echo "Migrating $svc..."
  docker compose exec $svc alembic upgrade head
done
```

---

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript (Vite) |
| API Gateway | FastAPI (Python 3.12) |
| Backend Services | FastAPI × 7 microservices |
| Primary Database | PostgreSQL 16 (one DB per service) |
| Cache | Redis 7 |
| Message Broker | RabbitMQ 3.13 (topic exchange) |
| Reverse Proxy | Nginx 1.25 |
| Real-time | WebSocket |
| Auth | JWT (access 30min, refresh 7d) |
| Migrations | Alembic per service |
| ORM | SQLAlchemy 2.x (async) |
| Containerization | Docker + Docker Compose |

See [Architecture Overview](docs/architecture/overview.md) and [ADR records](docs/decisions/) for full details.

---

## Services

| Service | Port | Domain |
|---------|------|--------|
| api-gateway | 8000 | Routing, JWT verification |
| identity-service | 8001 | Auth, users, roles, permissions |
| farm-service | 8002 | Farms, buildings, sections |
| livestock-service | 8003 | Poultry batches, health, growth |
| inventory-service | 8004 | Warehouses, feed, medicine, equipment |
| finance-service | 8005 | Expenses, sales, batch profit |
| notification-service | 8006 | Alerts, WebSocket delivery |
| reporting-service | 8007 | Batch performance cards, PDF |

---

## Repository Structure

```
/
├── frontend/                  React + TypeScript SPA
├── services/
│   ├── api-gateway/           JWT verification, reverse proxy
│   ├── identity-service/      Auth, RBAC, users
│   ├── farm-service/          Farm catalog
│   ├── livestock-service/     Poultry batches, health, growth (MVP)
│   ├── inventory-service/     Warehouse & stock (FIFO/FEFO)
│   ├── finance-service/       Expenses, sales, batch profit
│   ├── notification-service/  Alerts & WebSocket
│   └── reporting-service/     Reports & analytics
├── shared/
│   ├── contracts/             API response schemas (APIResponse, ErrorResponse)
│   ├── events/                Domain event schemas (RabbitMQ topic exchange)
│   ├── models/                SQLAlchemy base models (UUIDPrimaryKeyMixin, etc.)
│   ├── utils/                 Shared utilities
│   └── exceptions/            Domain exception hierarchy
├── infrastructure/
│   ├── nginx/                 Reverse proxy config
│   ├── postgres/              DB init scripts (creates all 7 service databases)
│   └── rabbitmq/              Exchange/queue definitions (agrovision.events)
├── docs/
│   ├── architecture/          Architecture overview, bounded contexts, MVP scope
│   ├── api/                   REST + event standards
│   ├── development/           Coding, git, commit standards
│   └── decisions/             ADR-001, ADR-002, ADR-003
└── .project-governance/       Project memory, BRD/SRS traceability
```

---

## Troubleshooting

**Services fail to start:**
```bash
# Check infrastructure health first
docker compose ps postgres redis rabbitmq

# View logs for a specific service
docker compose logs identity-service --tail 50

# View all logs
docker compose logs --tail 30
```

**PostgreSQL connection refused:**
```bash
# Check if databases were created
docker compose exec postgres psql -U agrovision -c "\l"
# Expected: identity_db, farm_db, livestock_db, inventory_db, finance_db, notification_db, reporting_db
```

**RabbitMQ connection refused:**
```bash
# Check RabbitMQ status
docker compose exec rabbitmq rabbitmq-diagnostics ping

# Check vhost exists
curl -s -u agrovision:rabbitmq_dev http://localhost:15672/api/vhosts | python3 -m json.tool
```

**Build fails due to `shared` package not found:**
Build context is the repository root. Do not change `context: .` in docker-compose.yml.

**Port conflicts:**
If ports 80, 8000-8007, 5432, 6379, 5672, or 15672 are in use:
```bash
# Find what's using a port
lsof -i :8000
# Then stop docker compose and kill the conflicting process
```

---

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [MVP Scope](docs/architecture/mvp-scope.md)
- [Bounded Contexts](docs/architecture/bounded-contexts.md)
- [Service Ownership Matrix](docs/architecture/service-ownership.md)
- [ADR-001: Initial Monolith](docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md)
- [ADR-002: Microservices](docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md)
- [ADR-003: MVP Realignment](docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md)
- [API Standards](docs/api/standards.md)
- [Event Standards](docs/api/events.md)
- [Development Standards](docs/development/standards.md)

---

## Source Documents

- `1. BRD_AgroVision_Farm_Management_qism1.docx` — Business Requirements Document (Part 1)
- `2. SRS_AgroVision_Farm_Management_v1.1.docx` — Software Requirements Specification v1.1

# AgroVision — Architecture Overview

**Status:** Approved (ADR-002)
**Date:** 2026-06-16
**Supersedes:** ADR-001 (monolith baseline)

---

## System Overview

AgroVision is a microservices-based Farm Management Platform designed to support poultry, livestock, dairy, and mixed farm operations across multiple farms and warehouses.

The system serves the following primary user groups (BRD §5):
- Farm Owner, Farm Director, Farm Manager
- Veterinarian, Accountant, Warehouse Manager
- Sales Personnel, Farm Workers, Government Inspectors, Auditors

---

## Architecture Style

**Pattern:** Microservices with event-driven integration via RabbitMQ
**API Style:** REST (versioned: `/api/v1/...`)
**Real-time:** WebSocket (notification delivery, KPI dashboard updates)
**Communication:** Synchronous (HTTP via API Gateway) + Asynchronous (AMQP events)

---

## Service Map

```
Internet
    │
[Nginx]          ← TLS termination, rate limiting, static frontend serving
    │
[API Gateway]    ← JWT verification, routing, header injection
    │
    ├── [Identity Service]      :8001  — Auth, users, roles, permissions
    ├── [Farm Service]          :8002  — Farms, buildings, sections
    ├── [Livestock Service]     :8003  — Animals, batches, health, growth
    ├── [Inventory Service]     :8004  — Warehouses, feed, medicine, equipment
    ├── [Finance Service]       :8005  — Revenue, expenses, sales, customers
    ├── [Notification Service]  :8006  — Alerts, WebSocket delivery, reminders
    └── [Reporting Service]     :8007  — Reports, KPIs, PDF/Excel/CSV export

Shared Infrastructure:
  [PostgreSQL]   ← One database per service (isolated schemas)
  [Redis]        ← Caching, session data, rate limiting
  [RabbitMQ]     ← Async event bus (exchange: agrovision.events, type: topic)
```

---

## Data Flow

### Synchronous (Client → Server)
```
Client → Nginx → API Gateway (JWT verify) → Service → PostgreSQL/Redis → Response
```

### Asynchronous (Event-driven)
```
Service A publishes event → RabbitMQ (agrovision.events exchange, topic routing)
     → Queue: notification.events → Notification Service
     → Queue: reporting.events   → Reporting Service
     → Queue: finance.events     → Finance Service (livestock.# events)
     → Queue: inventory.events   → Inventory Service (inventory.# events)
```

---

## Authentication Flow

1. Client POSTs credentials to `/api/v1/auth/login` (bypasses JWT check)
2. API Gateway forwards to Identity Service
3. Identity Service validates, issues JWT access token (30 min) + refresh token (7 days)
4. Client stores tokens; subsequent requests carry `Authorization: Bearer <token>`
5. API Gateway verifies signature; injects `X-User-Id`, `X-User-Roles`, `X-Farm-Id` headers
6. Downstream services trust these headers — no re-verification

**Security references:** SRS §11 (2FA, lockout after 5 attempts, bcrypt, TLS 1.2+)

---

## Service Database Isolation

Each service has its own PostgreSQL database. Services never query another service's database. Cross-service data needs are satisfied by:
1. Events (async, eventual consistency)
2. Read-model projections stored in the consuming service's own DB
3. HTTP calls to the owning service's API (sync, avoid for heavy reads)

| Service | Database |
|---------|----------|
| Identity | identity_db |
| Farm | farm_db |
| Livestock | livestock_db |
| Inventory | inventory_db |
| Finance | finance_db |
| Notification | notification_db |
| Reporting | reporting_db |

---

## Non-Functional Architecture Decisions

| NFR | Architectural Solution |
|-----|----------------------|
| 99.5% uptime | Docker health checks, `unless-stopped` restart policy, PostgreSQL connection pooling |
| <5s report load | Redis caching for aggregations, async pre-computation in Reporting Service |
| Critical notifications <1min | WebSocket push from Notification Service; RabbitMQ priority queue |
| 7-year audit retention | Immutable audit log table in each service; archive tier planned Phase 2 |
| OWASP Top 10 | Rate limiting (Nginx), JWT expiry, bcrypt, TLS, parameterised SQL via SQLAlchemy ORM |
| Inventory variance ≤2% | FIFO/FEFO enforced at domain layer; stock reconciliation use case |

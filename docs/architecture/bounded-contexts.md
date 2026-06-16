# AgroVision — Bounded Context Definitions

Each microservice is a bounded context. The service owns all data, logic, and APIs for its domain.
No service may directly read or write another service's database.

> **ADR-003 (2026-06-16):** MVP scope narrowed to Uzbekistan Poultry Production Platform.
> Livestock context is batch-centric for MVP. Individual animal tracking and non-poultry species
> are marked FUTURE RELEASE. All routing keys updated from `livestock.#` to `batch.#` for MVP events.

---

## 1. Identity Context (identity-service)

**Owns:** Users, Roles, Permissions, JWT lifecycle, Farm-user associations
**BRD ref:** §5 (Stakeholders), **SRS ref:** §5.1, §5.2, §5.26, §11
**MVP Classification: Core MVP**

**Invariants:**
- Passwords stored as bcrypt hash only
- Account locked after 5 failed attempts (15-min lockout)
- Hybrid RBAC: effective permissions = union(role permissions ∪ individual grants)
- Farm Owner can assign permissions without system admin — SRS §5.2

**MVP scope:** Auth, users, 3–5 predefined system roles, farm-user binding. Advanced role builder → Phase 2.

**Events published:** (none — identity events TBD)
**Events consumed:** `farm.farm.created` → creates FarmRef projection

---

## 2. Farm Context (farm-service)

**Owns:** Farms, Buildings, Sections, Farm catalog
**BRD ref:** §6.1 items 1, 3; **SRS ref:** §5.3, SF-02
**MVP Classification: Core MVP**

**Invariants:**
- A section's type determines what can be placed in it (quarantine vs production)
- Buildings belong to exactly one farm
- Farm deactivation does not delete data

**MVP scope:** Poultry-compatible farm structures. Mixed/livestock farms → Phase 3.

**Events published:** `farm.farm.created`, `farm.farm.updated`
**Events consumed:** (none at MVP)

---

## 3. Livestock Context (livestock-service)

**Owns (MVP):** Batches, WeightSamplings, MortalityRecords, VaccinationRecords,
MedicationRecords, DailyHealthLogs, FeedConsumption, WaterConsumption
**BRD ref:** §6.1 items 2, 4-9, 15-16; **SRS ref:** §5.3-§5.10, §5.18-§5.21
**MVP Classification: Core MVP (narrowed — batch-centric poultry only)**

**Invariants:**
- Batch status: quarantine → active → closed only. No skip.
- Quarantine minimum: 7–14 days poultry — BP-03
- Expired vaccines cannot be used — BP-07
- Every mortality logged within 24h — BP-15

**MVP Events published (batch.* routing prefix):**
- `batch.batch.opened` / `batch.batch.closed`
- `batch.feed.consumed` / `batch.water.consumed`
- `batch.mortality.recorded`
- `batch.vaccination.completed`
- `batch.medication.recorded`
- `batch.weight.sampled`

**Events consumed:**
- `farm.farm.created` → FarmRef projection
- `inventory.stock.dispatched` → links feed/medicine dispatch to batch

**FUTURE RELEASE (ADR-003):**
- `livestock.animal.created/updated/deceased/transferred` — individual tracking (Phase 3)
- `livestock.slaughter.recorded` — slaughter module (Phase 2); use `batch.batch.closed` + reason in MVP
- `livestock.disease.incident_created` — formal case management (Phase 2); use `batch.medication.recorded` in MVP
- Individual Animal model, RFID, ear tags, genealogy (Phase 3)
- Cattle, sheep, goat species (Phase 3)

---

## 4. Inventory Context (inventory-service)

**Owns:** Warehouses, Stock Items, Stock Batches (FIFO/FEFO lots), Stock Movements
**BRD ref:** §6.1 items 10-11; **SRS ref:** §5.12-§5.13, SF-12-SF-13
**MVP Classification: Core MVP**

**Invariants:**
- Expired stock items cannot be dispatched — BP-07, BP-09
- FIFO/FEFO dispatch order enforced at domain layer
- Inventory variance target ≤2% — OG-03
- Minimum stock alerts trigger LowStockAlertEvent

**Events published:**
- `inventory.stock.received` / `inventory.stock.dispatched` / `inventory.stock.updated`
- `inventory.alert.low_stock` / `inventory.alert.expiry`

**Events consumed:**
- `batch.feed.consumed` → auto-dispatch feed quantity from warehouse
- `batch.vaccination.completed` → records vaccine consumption
- `batch.medication.recorded` → records medicine consumption

---

## 5. Finance Context (finance-service)

**Owns (MVP):** Expenses, SalesRecords, BatchCostSummaries
**BRD ref:** §6.1 items 12-13; **SRS ref:** §5.15-§5.18, SF-14 to SF-17
**MVP Classification: Core MVP (narrowed)**

**Invariants:**
- Every transaction requires a primary document reference — BP-11
- Currency: UZS (Uzbek Sum) — ADR-003 Uzbekistan market constraint

**MVP scope:** Batch expense tracking (auto-created from batch events), simple sales record per batch,
profit per batch calculation, basic payment status (paid/pending).

**MVP Events published:**
- `finance.expense.created`
- `finance.sale.recorded`

**Events consumed:**
- `batch.batch.opened` → initializes batch cost ledger
- `batch.batch.closed` → triggers final batch profit calculation
- `batch.feed.consumed` → auto-creates feed expense record
- `batch.medication.recorded` → auto-creates medicine expense record
- `batch.vaccination.completed` → auto-creates vaccine expense record
- `inventory.stock.dispatched` → cost allocation to batch expense

**FUTURE RELEASE (ADR-003):**
- `finance.revenue.recorded` / `finance.payment.received` — advanced AR/AP with debtor tracking (Phase 2)
- `sales.order.created` / `sales.order.fulfilled` — full multi-line sales order workflow (Phase 2)
- Budget management, director approval workflow for large sales, credit limit enforcement (Phase 2)

---

## 6. Notification Context (notification-service)

**Owns:** Notifications, Alert rules, WebSocket connections, Delivery log
**BRD ref:** §6.1 item 20; **SRS ref:** §5.22-§5.23, SF-22
**MVP Classification: Supporting MVP**

**Invariants:**
- Critical notifications delivered within 1 minute — SRS §6 NFR
- MVP channel: WebSocket in-app only
- All events from agrovision.events exchange are consumed for alerting

**MVP scope:** In-app alerts for vaccination overdue, low stock, mortality threshold exceeded.

**Events published:** (delivery confirmations — internal)
**Events consumed:** ALL events via `#` binding — notification-service is a fan-out consumer

**FUTURE RELEASE (ADR-003):** Email and SMS notification delivery (Phase 2).

---

## 7. Reporting Context (reporting-service)

**Owns:** Report definitions, Generated reports, KPI aggregations, Export files
**BRD ref:** §6.1 item 18; **SRS ref:** §5.22, SF-21
**MVP Classification: Supporting MVP (minimal)**

**MVP scope:** On-demand batch performance card (FCR, mortality rate, feed cost, profit per batch).
Export: PDF only in MVP.

**Invariants:**
- Standard report load time <5s — SRS §6 Performance NFR

**Events published:** (none)
**Events consumed:**
- ALL events via `#` binding — builds read-model projections for fast reporting
- Maintains denormalized aggregation tables for KPI dashboards

**FUTURE RELEASE (ADR-003):** Scheduled report delivery, Excel/CSV export, cross-farm analytics (Phase 2).

---

## Cross-Context Communication Rules

| Scenario | Preferred Pattern |
|----------|-----------------|
| Service A needs to read Service B's data in real-time | HTTP call to Service B's API |
| Service A needs to react to Service B's state changes | Subscribe to Service B's events |
| Service A needs Service B's reference data (names, IDs) | Maintain a local projection updated via events |
| Reporting needs data from many services | Consume all events; build denormalized read models |

---

## MVP Routing Key Reference

| Domain | Routing Pattern | Consumer Queues |
|--------|----------------|-----------------|
| `farm.#` | Farm lifecycle | notification, reporting |
| `batch.#` | Poultry batch operations | finance, notification, reporting |
| `inventory.#` | Stock movements & alerts | finance, notification, reporting |
| `finance.#` | Expenses & sales | notification, reporting |
| `livestock.#` | **FUTURE RELEASE only** — not consumed in MVP | — |
| `sales.#` | **FUTURE RELEASE only** | — |

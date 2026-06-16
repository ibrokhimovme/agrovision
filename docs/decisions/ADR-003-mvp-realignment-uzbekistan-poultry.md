# ADR-003 — MVP Realignment: Uzbekistan Poultry Production Platform

| Field | Value |
|-------|-------|
| **Status** | APPROVED |
| **Decision Date** | 2026-06-16 |
| **Recorded By** | Engineering Steward |
| **Supersedes** | Scope assumptions in ADR-001, ADR-002 |
| **Does NOT supersede** | ADR-002 architecture stack (microservices, RabbitMQ, etc. remain) |

---

## Context

ADR-001 and ADR-002 established the technical architecture for a generic, multi-species "enterprise agriculture platform" covering poultry, cattle, sheep, goat, dairy, and mixed farms — with enterprise-grade features like IoT integration, advanced compliance, individual animal tracking with RFID, genealogy, and government inspection workflows.

This scope was derived from a literal reading of BRD Part 1 (§1–§9) and SRS v1.1, which describe a maximum-ambition vision for a future-state platform.

**The problem:** That scope optimizes for an imaginary large-scale enterprise farm, not for the actual target customer: a small or medium poultry farm in Uzbekistan.

**Observed reality of target farms (BRD §2, AS-IS analysis):**
- Primarily broiler and/or layer production
- Paper-based records, Excel files, verbal communication
- 1–5 farm locations, not 50+
- Limited IT infrastructure and digital literacy
- Core operational pain: knowing daily mortality, feed consumed, batch cost, and profit per cycle
- Veterinary work is batch-level, not per-bird
- No RFID infrastructure
- No IoT sensors
- No genealogy or breeding analytics
- No government inspection digital integration yet

**The primary workflow that drives 90% of the business value is:**

```
Batch Arrival (chick placement)
  → Daily Feed Consumption
  → Daily Water Consumption
  → Medication Events
  → Vaccination Events (scheduled by age)
  → Daily Mortality Count
  → Periodic Weight Sampling
  → Batch Close (sale or slaughter)
  → Cost + Profit Analysis per Batch
```

Everything outside this workflow must justify its inclusion in MVP.

---

## Decision

### 1. Product Focus Realignment

**FROM:** Generic multi-species enterprise agriculture platform  
**TO:** Poultry Production Management Platform for Uzbekistan small/medium farms

The product name remains AgroVision. The MVP scope is narrowed to serve the primary workflow above.

### 2. Batch-First Principle (Mandatory)

All poultry domain models, events, and API endpoints must be batch-centric.

- **Accepted:** Batch, FeedConsumption, WaterConsumption, MortalityRecord, VaccinationEvent, MedicationEvent, WeightSampling, SalesRecord
- **Deferred:** Individual bird tracking, RFID, ear tags, per-animal health records, individual bird transfer workflows, genealogy

Rationale: In Uzbekistan poultry operations, birds are managed as groups (partiya). Individual bird traceability is not a current operational requirement and would add unacceptable UI complexity for farm workers.

### 3. Species Scope

**MVP species:** `broiler`, `layer` (egg-laying hens)  
**Deferred species:** `cattle`, `sheep`, `goat`, `dairy`

The `Animal` model (individual livestock tracking) is preserved in the codebase as a future-release skeleton but is **not activated for MVP**. The livestock-service is focused on poultry batch management for MVP.

### 4. Service Classification

All 8 services remain in the architecture (ADR-002 is not modified). MVP scope within each service is narrowed:

| Service | MVP Classification | MVP Scope (narrowed) |
|---------|-------------------|----------------------|
| api-gateway | **Core MVP** | JWT verification, routing — no change |
| identity-service | **Core MVP** | Auth, users, simplified RBAC (3–5 system roles), farm-user binding |
| farm-service | **Core MVP** | Farm + House/Section catalog. Narrowed to poultry-compatible structures |
| livestock-service | **Core MVP (narrowed)** | Poultry batches only. Full batch lifecycle. No individual Animal tracking in MVP |
| inventory-service | **Core MVP** | Feed, vaccine, medicine stock. FIFO/FEFO. Low-stock alerts |
| finance-service | **Core MVP (narrowed)** | Batch expense tracking, simple sales record, profit per batch. Advanced budget → deferred |
| notification-service | **Supporting MVP** | In-app alerts for vaccination overdue, low stock, mortality threshold. Email/SMS → Phase 2 |
| reporting-service | **Supporting MVP (minimal)** | Batch performance card (FCR, mortality rate, cost, profit). Full scheduled reports → Phase 2 |

### 5. Deferred Features (Full List)

**Moved to Phase 2:**
- Email and SMS notification delivery (notification-service delivers in-app WebSocket only in MVP)
- Scheduled report delivery (reporting-service delivers on-demand only in MVP)
- Advanced sales management (debtor tracking beyond simple payment status)
- Transport management (BP-13, SF-19)
- Slaughter management as a distinct module (SF-20) — batch sale/close covers MVP need
- Water consumption monitoring as a separate module (SF-11) — track as daily log field in feed record
- Workforce scheduling and shift management
- Customer registry beyond basic name + phone

**Moved to Future Release (Phase 3+):**
- Individual animal tracking (Animal model, RFID, ear tags)
- Cattle, sheep, goat management (SF-04)
- Animal registration module (SF-05 — individual registration)
- Dairy operations and milk quality monitoring
- Government inspection and compliance workflows (BP-17 advanced)
- Full audit trail UI (audit log stored, but no dedicated UI in MVP)
- Historical archiving module (SF-24) — data retained per NFR; archiving API deferred
- Advanced genetics/breeding analytics
- IoT sensor integration
- Multi-language support beyond Uzbek
- SSO / enterprise identity integration
- PDF/Excel scheduled report delivery
- Multi-database replication / horizontal scaling

### 6. Event Contracts Narrowing

MVP events (kept active):
- `farm.farm.created`, `farm.farm.updated`
- `batch.batch.opened`, `batch.batch.closed`
- `batch.feed.consumed`
- `batch.mortality.recorded`
- `batch.vaccination.completed`
- `batch.medication.recorded`
- `batch.weight.sampled`
- `inventory.stock.received`, `inventory.stock.dispatched`
- `inventory.alert.low_stock`, `inventory.alert.expiry`
- `finance.expense.created`, `finance.sale.recorded`

Deferred events (defined in schemas, not consumed in MVP):
- `livestock.animal.created/updated/deceased/transferred` — individual tracking, Future Release
- `livestock.slaughter.recorded` — use batch.batch.closed with reason instead
- `livestock.disease.incident_created` (simplified: disease tracking is a field on medication event)
- `sales.order.created/fulfilled` — simplified to finance.sale.recorded in MVP
- `finance.revenue.recorded`, `finance.payment.received` — advanced AR tracking, Phase 2

### 7. Uzbekistan Market Constraints

These constraints shape MVP feature selection:

1. **Digital literacy:** UI must use Uzbek, simple navigation, large touch targets. Zero learning curve.
2. **Connectivity:** Intermittent 3G/4G at farm sites. Critical operations (daily mortality, feed log) must be fast, low-bandwidth, and retry-safe.
3. **Device profile:** Mobile phones (Android) and basic office PCs. No tablets assumed.
4. **Currency:** Uzbek Sum (UZS). All financial amounts in UZS.
5. **No existing digital tools:** Users are coming from paper. The system must feel like a digital replacement for their notebook, not an ERP system.
6. **Regulatory:** No formal government digital integration required in MVP. Export to PDF for inspectors is sufficient.
7. **Team size:** 1–3 office staff per farm. Not multiple departments.

### 8. What This Decision Does NOT Change

- ADR-002 architecture stack (microservices, RabbitMQ, PostgreSQL, FastAPI, etc.)
- Service boundaries and database isolation
- Event envelope format and routing key convention
- API standards (REST, versioning, response envelopes)
- Development standards and git workflow
- The `Animal` domain model (preserved in codebase, marked as future)
- The full event schema file (deferred events preserved, marked clearly)

---

## Consequences

**Positive:**
- Dramatically reduces MVP scope and time-to-market
- Feature set is deliverable by a small team in weeks, not months
- UI complexity is manageable for low-digital-literacy users
- Performance targets are achievable with the existing infrastructure
- Architecture investment (ADR-002) is fully preserved for future scale

**Risks:**
- BRD Part 1 described a broader scope — stakeholder expectations must be managed
- Some BRD sections (§10–§20, not yet delivered) may contain requirements that conflict with MVP narrowing
- If cattle/sheep management is required sooner than Phase 3, the individual animal tracking infrastructure will need faster activation

**Mitigation:**
- Record this decision in project_memory.md and present to project sponsor before implementation begins
- Keep deferred features in codebase as clearly marked skeletons, not deleted code
- Track deferred features in the Future Release Roadmap (project_memory.md §20)

---

## Governance Rule Added

> Any feature proposed for MVP implementation that falls outside the primary poultry batch workflow must produce a written business justification referencing the BRD and demonstrating that the feature is required before first production deployment. Justification must be reviewed before sprint inclusion.

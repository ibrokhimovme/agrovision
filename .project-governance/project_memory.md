# AgroVision — Project Governance Memory

**Authority:** This document is the authoritative project memory for the AgroVision platform.
**Superseded by:** BRD and SRS take precedence over this file whenever conflict exists.
**Maintained by:** Engineering steward — update after every completed task.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Business Objectives](#2-business-objectives)
3. [Approved Scope](#3-approved-scope)
4. [Out-of-Scope Items](#4-out-of-scope-items)
5. [Stakeholders](#5-stakeholders)
6. [Functional Requirements Summary](#6-functional-requirements-summary)
7. [Non-Functional Requirements Summary](#7-non-functional-requirements-summary)
8. [Constraints](#8-constraints)
9. [Assumptions](#9-assumptions)
10. [Acceptance Criteria](#10-acceptance-criteria)
11. [Domain Terminology](#11-domain-terminology)
12. [Architectural Decisions Already Made](#12-architectural-decisions-already-made)
13. [Open Questions](#13-open-questions)
14. [Risks](#14-risks)
15. [Requirements Traceability Matrix](#15-requirements-traceability-matrix)
16. [Scope Boundary](#16-scope-boundary)
17. [Technical Decisions Log](#17-technical-decisions-log)
18. [Development Journal](#18-development-journal)
19. [Development Progress](#19-development-progress)
20. [Change History](#20-change-history)
21. [MVP Definition (ADR-003)](#21-mvp-definition-adr-003)
22. [Product Focus — Uzbekistan Poultry Platform](#22-product-focus--uzbekistan-poultry-platform)
23. [Deferred Features](#23-deferred-features)
24. [Uzbekistan Market Constraints](#24-uzbekistan-market-constraints)
25. [Simplification Decisions](#25-simplification-decisions)
26. [Architecture Realignment Summary](#26-architecture-realignment-summary)
27. [Future Release Roadmap](#27-future-release-roadmap)

---

## 1. Project Overview

**Product Name:** AgroVision  
**Description:** A unified enterprise-scale farm management platform for poultry farms, livestock farms, dairy farms, and mixed/integrated agricultural operations.  
**Primary Language:** Uzbek (UI); documents authored in Uzbek.  
**Source Documents:**
- `1. BRD_AgroVision_Farm_Management_qism1.docx` — Business Requirements Document (Part 1, §1–§9)
- `2. SRS_AgroVision_Farm_Management_v1.1.docx` — Software Requirements Specification v1.1 (IEEE 830)

**BRD Note:** The BRD covers §1–§9. Sections §10–§20 (Business Rules, Functional Business Requirements, Non-Functional Requirements, Reports, Compliance, Risks, Assumptions, KPIs, Expected Business Benefits, Acceptance Criteria, Conclusion) are declared as belonging to a second part not yet delivered. **These missing sections must be obtained before implementing any feature that depends on them.**

**Platform Context:** Replaces paper journals, disconnected Excel files, and verbal information flows used by Uzbekistan and regional farms. Targets farms managing hundreds of batches, thousands of animals, tens of employees, and continuous feed/product flows.

---

## 2. Business Objectives

All objectives are sourced from BRD §3. Each has a success criterion.

### 2.1 Strategic Goals

| ID | Goal | Success Criterion |
|----|------|-------------------|
| SG-01 | Digital transformation of farm operations | ≥90% of farm operations run on platform; paper fallback only in exceptions |
| SG-02 | Multi-farm management under single platform | System manages ≥5 farms and 10 warehouses under one panel |
| SG-03 | Data-driven management decisions | ≥80% of board meeting data sourced directly from platform reports |

### 2.2 Operational Goals

| ID | Goal | Success Criterion |
|----|------|-------------------|
| OG-01 | Full lifecycle tracking of animals and batches | All events per batch (acquisition → slaughter/sale) stored completely |
| OG-02 | Veterinary and prophylactic measures on schedule | ≥95% of planned vet events executed on time |
| OG-03 | Inventory accuracy and transparency | Physical vs. book variance ≤2% |

### 2.3 Financial Goals

| ID | Goal | Success Criterion |
|----|------|-------------------|
| FG-01 | Precise cost calculation per batch | Accurate cost and margin report for every closed batch |
| FG-02 | Transparent cash flow and receivables management | 30- and 60-day overdue debt maintained below defined threshold |

### 2.4 Productivity Goals

| ID | Goal | Success Criterion |
|----|------|-------------------|
| PG-01 | Improve Feed Conversion Ratio (FCR) | Average FCR improves ≥5% over baseline |
| PG-02 | Reduce mortality rate | Average mortality rate decreases ≥20% from initial level |

### 2.5 Visibility Goals

| ID | Goal | Success Criterion |
|----|------|-------------------|
| VG-01 | Real-time dashboards with top 10 KPIs | Top 10 KPIs visible daily with ≤24h data lag |
| VG-02 | Audit readiness and audit trail | Audit-requested data deliverable within 1 business day |

### 2.6 Decision-Making Goals

| ID | Goal | Success Criterion |
|----|------|-------------------|
| DG-01 | Faster and evidence-based decisions | Average management decision time reduced ≥50% from baseline |

---

## 3. Approved Scope

**Source:** BRD §6.1

The following business domains and capabilities are within platform scope for Version 1:

1. Multi-farm and multi-warehouse centralized management
2. Full lifecycle tracking — poultry batches (broiler and egg) and livestock (cattle, sheep/goat)
3. Dairy operations and milk quality monitoring
4. Animal and batch identification and registry
5. Acquisition, quarantine, placement, and provenance documentation
6. Daily feeding operations, water consumption, and basic microclimate metrics
7. Health monitoring, veterinary visit records, and treatment history
8. Vaccination schedule and prophylactic event management
9. Growth and productivity metrics (weight, FCR, ADG, HDP, etc.)
10. Inventory management: feed, vaccines, medicines, equipment, and packaging materials
11. Workforce management: shift scheduling, task assignment, time tracking
12. Financial operations: revenue, expenses, debtor/creditor, batch-level cost calculation
13. Sales operations, customer registry, and order management
14. Transport and logistics operations
15. Slaughter, packaging, and output (chiqim) reporting
16. Mortality and disposal event records with detailed logging
17. Compliance management and audit trails; internal review visibility
18. Management dashboards: daily, weekly, monthly reports
19. User and role management, permissions matrix
20. Automated notifications and reminders (vaccination deadlines, expiries, etc.)

---

## 4. Out-of-Scope Items

**Source:** BRD §6.2

The following areas are explicitly **excluded** from AgroVision v1:

| # | Excluded Area | Notes |
|---|---------------|-------|
| 1 | Horticulture/crop operations, field work, irrigation systems | Separate initiative |
| 2 | Fishery and aquaculture operations | Separate initiative |
| 3 | Internal lab processes and test equipment management | Third-party system |
| 4 | Full IoT sensor/microcontroller integration | Future scope (§6.3) |
| 5 | Full accounting/bank/tax system integration | v1 is export-only; full integration is future scope |
| 6 | Marketing and e-commerce (B2C) platform | Separate initiative |
| 7 | Internal credit/microfinance operations | Separate initiative |
| 8 | Employee LMS (Learning Management System) | Separate initiative |
| 9 | Deep genetic/breeding scientific analysis modules | Future scope (§6.3) |

---

## 5. Stakeholders

**Source:** BRD §5

| Role | Responsibilities | Impact Level | Key Concerns |
|------|-----------------|--------------|--------------|
| Farm Owner (Ferma egasi) | Strategic decisions, capital, profit distribution, user creation and permission assignment | **High** | Losses, internal fraud, regulatory liability |
| Farm Director (Ferma direktori) | Operational/management decisions, budget, KPIs, external relations | **High** | Data latency delaying decisions, unreliable reports |
| Farm Manager (Ferma boshqaruvchisi) | Daily operations, shift planning, task assignment, batch monitoring | **High** | Employee accountability, data hiding, incorrect entries |
| Veterinarian | Animal health, disease diagnosis/treatment, vaccination schedules, biosecurity | **High** | Delayed prophylaxis, expired medicines, epidemic events |
| Accountant (Hisobchi) | Bookkeeping, tax, cash/bank operations, debtor/creditor, financial reports | **Medium-High** | Lost documents, data unreliability, report deadlines |
| Warehouse Manager (Ombor menejeri) | Feed, vaccines, medicines, equipment: receipt, dispatch, stock, physical inventory | **Medium-High** | Inaccurate stock, theft risk, expired product losses |
| Sales Personnel (Sotuv xodimi) | Customer relations, order intake, delivery tracking, debt collection | **Medium** | Incorrect stock display, pricing inconsistencies, debtors |
| Farm Workers (Ferma xodimlari) | Daily feeding, watering, cleaning, anomaly reporting | **Low (mass adoption critical)** | Over-documentation burden, language barrier, complex UI |
| Government Inspector | Compliance checks (veterinary, sanitary, tax, environmental) | **Medium** | Falsified reports, data manipulation, fragmented records |
| External Auditor | Financial/operational audit, internal controls assessment | **Medium** | Absence of logs, inconsistent reports |
| Investors / Banks | Capital provision, lending | **Medium-High** | Data reliability, profitability, financial transparency |

---

## 6. Functional Requirements Summary

**Source:** SRS §4 (24 System Features) and §5 (225 Functional Requirements across 26 sub-sections)

### 6.1 System Features (24 total)

| SF# | Feature | Priority |
|-----|---------|----------|
| SF-01 | Authentication and flexible permissions (hybrid RBAC + individual access) | Critical |
| SF-02 | Farm management (multi-farm, buildings, sections catalog) | High |
| SF-03 | Poultry batch management (lifecycle, daily records, KPI computation) | Critical |
| SF-04 | Livestock management (individual and group, cattle/sheep/goat) | Critical |
| SF-05 | Animal registration (intake, provenance, quarantine assignment) | High |
| SF-06 | Weight monitoring (periodic weighing, ADG/FCR, anomaly detection) | High |
| SF-07 | Vaccination management (auto-schedule, reminders, execution logging) | Critical |
| SF-08 | Disease management (incident logging, treatment protocols, isolation, biosecurity) | Critical |
| SF-09 | Veterinary records (full health history, vet visit logs, e-signature) | High |
| SF-10 | Feed management (recipes, daily norm, consumption, FCR tracking) | Critical |
| SF-11 | Water consumption monitoring (daily intake, quality, anomaly alerts) | Medium-High |
| SF-12 | Inventory management (receipt, dispatch, balance, FIFO/FEFO, min-stock alerts) | Critical |
| SF-13 | Warehouse operations (warehouse catalog, inter-warehouse transfers, documents) | High |
| SF-14 | Financial tracking (revenue/expense logging, debtor/creditor, budget vs. actual) | High |
| SF-15 | Cost management (per-batch/per-sector cost allocation, cost driver mapping) | High |
| SF-16 | Revenue management (sales revenue, payment status, revenue analysis) | High |
| SF-17 | Sales management (order intake, fulfillment, shipment, payment tracking) | Critical |
| SF-18 | Mortality tracking (incident logging, cause analysis, utilization planning) | Critical |
| SF-19 | Transport management (trip planning, load/health docs, route logging) | Medium-High |
| SF-20 | Slaughter management (batch selection, live-to-carcass ratio, product receipt) | High |
| SF-21 | Reports (standard and parametric, PDF/Excel/CSV export, scheduled delivery) | High |
| SF-22 | Notifications (in-app, email, SMS for critical events and reminders) | Medium |
| SF-23 | Audit log (immutable, who/when/what, old and new value capture) | Critical |
| SF-24 | Historical archiving (lifecycle-based archiving, 7-year retention, retrieval) | Medium |

### 6.2 Functional Requirements Modules (SRS §5)

The SRS declares 225 functional requirements distributed across 26 sub-sections (FR-001 – FR-225 approx.). The individual FR table rows are not included in the delivered SRS text — only section headers are visible. The detailed FR IDs require the complete FR table to be obtained from the document owner.

**Sub-sections:**
5.1 Authentication and authorization
5.2 Users and permissions (flexible model)
5.3 Farm management
5.4 Poultry batch management
5.5 Livestock management
5.6 Animal registration
5.7 Weight monitoring
5.8 Vaccination management
5.9 Disease management
5.10 Veterinary records
5.11 Feed management
5.12 Water consumption monitoring
5.13 Inventory management
5.14 Warehouse operations
5.15 Financial tracking
5.16 Cost management
5.17 Revenue management
5.18 Sales management
5.19 Mortality tracking
5.20 Transport management
5.21 Slaughter management
5.22 Reports
5.23 Notifications
5.24 Audit log
5.25 Historical archiving
5.26 Flexible permissions (supplementary requirements FR-216 – FR-223)

### 6.3 Business Processes (BRD §9)

| ID | Process | Key Business Rule |
|----|---------|-------------------|
| BP-01 | Animal/Poultry Acquisition | Only certified supplier; every batch must have unique ID |
| BP-02 | Arrival Management | Every arrival formalized with acceptance act; no batch to main section without vet approval |
| BP-03 | Quarantine Management | Poultry: 7–14 days min; cattle: ≥21 days; no transfer to main section without health conclusion |
| BP-04 | Feeding Operations | Feed matched to batch age/type; expired feed not used; FCR computed daily/weekly |
| BP-05 | Water Management | Supply interruption ≤1 hour; water quality must meet standards |
| BP-06 | Health Monitoring | Every anomaly reviewed within 24h; isolated animal not returned without authorized approval |
| BP-07 | Vaccination Operations | Expired vaccines blocked; every record saved with full details; 95% on-time execution |
| BP-08 | Growth Monitoring | Measurements per defined schedule; below-baseline batches analyzed within 7 days |
| BP-09 | Inventory Management | FIFO/FEFO rules; expired items blocked; variance ≤2% |
| BP-10 | Workforce Operations | Tasks must name responsible person; unfinished tasks escalated; 95% completion per shift |
| BP-11 | Financial Operations | Every transaction backed by primary document; approval authorities respected |
| BP-12 | Sales Operations | Sales above threshold require director approval; sales to over-limit debtors blocked |
| BP-13 | Transport Operations | Live animal transport blocked without vet documents; losses ≤1% |
| BP-14 | Slaughter Operations | Slaughter blocked without vet clearance; sanitary regulations mandatory |
| BP-15 | Mortality Management | Every death logged within 24h; cause unidentified ≤5% |
| BP-16 | Disposal Management | Sanitary regulations fully complied with |
| BP-17 | Compliance Management | Every inspection formally documented; audit response ≤1 business day |

### 6.4 Use Cases (SRS §9)

| ID | Use Case | Actors |
|----|----------|--------|
| UC-01 | System login | All roles |
| UC-02 | Open new poultry batch | Manager, Director |
| UC-03 | Execute vaccination | Veterinarian |
| UC-04 | Record daily mortality | Manager, Shift Supervisor |
| UC-05 | Execute feed dispatch act | Warehouse Manager, Manager |
| UC-06 | Accept sales order | Sales Manager |
| UC-07 | Generate monthly financial report | Accountant, Director |
| UC-08 | Respond to audit request | Auditor, Director |
| UC-09 | Farm owner creates user and assigns flexible permissions | Farm Owner |
| UC-10 | Close a batch | Manager, Director |
| UC-11 | Conduct inventory | Warehouse Manager, Director |
| UC-12 | Manage disease outbreak | Veterinarian, Director, Manager |

---

## 7. Non-Functional Requirements Summary

**Source:** SRS §6 (categories) and §11 (security)

| Category | Key Requirements |
|----------|-----------------|
| **Performance** | Standard reports: <5 seconds load time |
| **Reliability** | Data integrity maintained; no data loss |
| **Availability** | 99.5% monthly uptime (measured during UAT) |
| **Scalability** | Must support ≥5 farms, ≥10 warehouses simultaneously |
| **Security — Auth** | 2FA support for admin/critical roles; account locked after 5 failed attempts (15-minute lockout); password complexity enforced (≥8 chars, digit+letter+special); bcrypt password hashing |
| **Security — Session** | 30-minute inactivity timeout; unique secure tokens; immediate session invalidation on logout |
| **Security — Transport** | TLS 1.2+ mandatory for all connections |
| **Security — Data at Rest** | Personal and financial data encrypted at rest; backups encrypted and stored separately |
| **Security — AppSec** | OWASP Top 10 protections required |
| **Audit** | Immutable audit logs; all critical actions logged with old/new values; 7-year retention |
| **Data Integrity** | Inventory variance ≤2% |
| **Localization** | UI in Uzbek language; English technical terms may accompany |
| **Notifications** | Critical notifications delivered within 1 minute |
| **Reports** | PDF, Excel, CSV export formats supported; scheduled delivery capability |
| **Data Retention** | Historical data stored minimum 7 years; archive deletion only after 7 years with admin approval |
| **Usability** | Interface must be simple and minimum-step; designed for users with basic digital literacy |
| **Maintainability** | Documented in SRS §6.5 (details in full FR table not delivered) |
| **Backup & Recovery** | Backup and restore tests must pass before acceptance (SRS §13) |
| **Privacy** | Collect only necessary personal data; comply with Uzbekistan Personal Data law; support data export and deletion requests |

---

## 8. Constraints

**Source:** SRS §2.5

1. **Language:** User interface must be in Uzbek. English technical terms may accompany where needed.
2. **Simplicity:** Interface must be simple and minimum-step — designed for users with basic digital literacy who are new to digital tools.
3. **Document formats:** Government and veterinary authorities require PDF and Excel format support for all output documents.
4. **Data retention:** Historical data must be stored for a minimum of 7 years (audit requirements).
5. **Immutability:** Audit trail and critical data must be stored immutably — no modification or deletion permitted.
6. **Multi-tenancy:** Platform must support multiple farms and multiple warehouses concurrently under a single instance.
7. **Implementation independence:** SRS is intentionally technology-neutral. Technology stack, database schema, frameworks, deployment model, and infrastructure decisions are deferred to Architecture Design and ADR documents (not yet produced).
8. **Connectivity:** System must tolerate short-duration internet outages (farm connectivity may be unstable). Critical modules must remain operable during brief disconnection.

---

## 9. Assumptions

**Source:** SRS §2.6

1. Users possess basic digital literacy skills, or they will undergo dedicated training before platform use.
2. Farm locations have at minimum mobile internet connectivity.
3. Users have browser-capable devices (personal or farm-provided).
4. Sufficient infrastructure resources are allocated for data storage and protection.
5. Initial data loading contracts (batches, warehouses, product catalog) are in place before go-live.

---

## 10. Acceptance Criteria

**Source:** SRS §13

The project is considered successfully delivered only when **all** of the following are met:

| # | Criterion |
|---|-----------|
| AC-01 | 100% of functional requirements implemented and test-verified |
| AC-02 | 100% of NFRs measured and within defined limits |
| AC-03 | 100% of business rules enforced by the system |
| AC-04 | 99.5% monthly uptime demonstrated during UAT |
| AC-05 | UAT conducted; ≥90% of scenarios passed |
| AC-06 | Security audit conducted; no critical vulnerabilities found |
| AC-07 | Audit trail and backup restore tests passed |
| AC-08 | Project documentation delivered: BRD, SRS, User Manual, Admin Manual |
| AC-09 | User training conducted and training report delivered |
| AC-10 | 7-year data retention strategy tested and verified |
| AC-11 | Uzbek localization complete and terminology approved |

---

## 11. Domain Terminology

**Sources:** BRD §4, SRS §1.3 and §14.1

| Term | Definition |
|------|-----------|
| FCR | Feed Conversion Ratio (yem konversiya nisbati) — kg feed consumed per kg weight gained |
| ADG | Average Daily Gain (o'rtacha sutkalik o'sish) — average weight gained per day per animal |
| HDP | Hen Day Production (tuxum berish koeffitsienti) — egg production efficiency per hen per day |
| FIFO | First In First Out — inventory dispatch method: oldest stock leaves first |
| FEFO | First Expired First Out — inventory dispatch method: nearest expiry leaves first |
| Batch (Partiya) | A group of poultry placed together in a section, managed as a unit through their lifecycle |
| Lifecycle (Hayot davri) | Full tracking from acquisition/quarantine through growth to slaughter/sale/death |
| FCR Baseline | Reference FCR value against which batch performance is measured |
| Mortality Rate | Percentage of animals dying within a batch during its lifecycle |
| Biosecurity (Biokavfsizlik) | Protocols to prevent disease entry and spread between batches/farms |
| Karantin (Quarantine) | Mandatory isolation period for newly arrived animals before placement in main section |
| RBAC | Role-Based Access Control — permission model where users are assigned roles |
| Hybrid Permission Model | AgroVision extension of RBAC: role templates + individual module-level access grants, combined as union |
| Role Template (Rol shabloni) | Predefined role (e.g., Farm Manager, Veterinarian) with standard access set |
| Individual Access (Individual dostup) | Per-module, per-action (read/create/update/delete/approve) access granted individually |
| KPI | Key Performance Indicator — quantitative metric for monitoring business performance |
| UAT | User Acceptance Testing |
| SOP | Standard Operating Procedure |
| AS-IS | Current-state analysis of farm operations before platform |
| TO-BE | Future-state vision of farm operations with platform |
| P&L | Profit and Loss statement |
| 2FA | Two-Factor Authentication |
| Audit Trail (Audit izi) | Immutable log of every critical action: who, when, what changed |
| Variance | Difference between physical stock count and book-recorded stock count |
| HACCP | Hazard Analysis and Critical Control Points (food safety standard — future scope) |
| OIE | World Organisation for Animal Health |
| Drill-down | UI action to navigate from summary view into detailed sub-data |
| Cost Driver (Qaynoq manba) | The operational activity or input driving a specific cost item |
| Debitor | Customer with outstanding receivable (money owed to the farm) |
| Kreditor | Supplier with outstanding payable (money owed by the farm) |
| Traceability (Izlanish) | Ability to trace any data record back to its source event and responsible actor |
| Compliance | Adherence to government, veterinary, sanitary, and international regulations |

---

## 12. Architectural Decisions Already Made

**Source:** SRS §2.1, §2.4, §3.3, §3.4

The following decisions are documented in the SRS and the approved architecture baseline (ADR-001).

| Decision | Detail |
|----------|--------|
| Technology neutrality (SRS baseline) | SRS is implementation-independent. Stack, DB schema, frameworks, and deployment model were deferred to Architecture Design + ADR documents. **Resolved by ADR-001 below.** |
| Web-first access | Users access via web browser on workstations, office computers, and mobile devices. |
| Permission model | Hybrid RBAC: standard role templates + individual module-action-level access. Union of all assigned roles and individual grants = effective permissions. Farm Owner can assign permissions without involving a system administrator. |
| Connectivity resilience | Critical modules must remain operable during brief internet outages. |
| Document output formats | PDF, Excel (XLSX), CSV must be supported for all exports. |
| Communication channels | Email and SMS for notifications; HTTPS for all web traffic; REST or equivalent for API integrations. |
| Hardware interfaces | RFID readers, barcode/QR scanners, electronic scales, printers, mobile terminals are in scope as future hardware interface points. |
| Software integrations (v1) | Accounting system integration: export-only in v1. Government portals: export in standard format. Email and SMS services for notifications. File storage service for document attachments. SSO: future scope. |
| Data retention policy | Minimum 7 years for all audit-relevant data; archival deletion only after 7 years with admin approval. |

---

### ADR-001 — Initial MVP Architecture Baseline

| Field | Value |
|-------|-------|
| **Status** | **APPROVED — Current Baseline** |
| **Decision Date** | 2026-06-16 |
| **Recorded By** | Engineering Steward |
| **Source Authority** | BRD §3, §6.1; SRS §4, §6 |

#### Context

The project is in MVP stage. The primary objective is to rapidly deliver a production-ready Farm Management System while minimizing architectural complexity, development overhead, infrastructure cost, and operational burden.

The system must support: poultry management, livestock management, veterinary workflows, inventory management, financial tracking, reporting, notifications, and real-time dashboard updates.

**Current scale assumptions:**
- Limited number of farms
- Moderate data volume
- Limited concurrent users
- No large-scale IoT ingestion requirements yet
- No high-volume event streaming requirements yet

#### Approved Architecture Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React + TypeScript |
| **Backend** | FastAPI |
| **Primary Database** | PostgreSQL |
| **Caching Layer** | Redis |
| **Containerization** | Docker + Docker Compose |
| **Reverse Proxy** | Nginx |
| **Real-Time Communication** | WebSocket |
| **Authentication** | JWT-based authentication |
| **Database Migration** | Alembic |
| **ORM** | SQLAlchemy |

#### Decision Rationale

1. FastAPI provides rapid development and strong performance.
2. PostgreSQL satisfies current transactional requirements.
3. Redis provides caching and future extensibility.
4. Docker simplifies deployment and environment consistency.
5. WebSockets satisfy current real-time requirements without additional infrastructure.
6. Architecture remains simple enough for MVP delivery.
7. Team productivity is prioritized over premature optimization.
8. Infrastructure cost is minimized.
9. Operational complexity is minimized.
10. Future scaling paths remain available without committing to them now.

#### Explicitly Rejected For MVP

| Rejected Technology / Pattern | Reason |
|-------------------------------|--------|
| Microservice architecture | Current business requirements documented in BRD and SRS do not justify the complexity, maintenance cost, operational burden, or development effort. |
| Event sourcing | Same as above. |
| CQRS | Same as above. |
| Apache Kafka | No measurable high-volume event streaming requirement exists at current scale. |
| Complex distributed systems | Same rationale as microservices. |
| Service mesh | Premature; no service-to-service communication complexity exists yet. |
| Multi-database architecture | PostgreSQL satisfies all current transactional requirements. |
| Premature horizontal scaling | Current scale assumptions do not justify it. |
| RabbitMQ / other message brokers | No demonstrated asynchronous event processing requirement yet. |

#### Future Evolution Path

| Phase | Actions |
|-------|---------|
| **Phase 1 (Current)** | FastAPI + React + PostgreSQL + Redis + Docker + WebSocket |
| **Phase 2** | Add background job processing if justified by measurable requirements. |
| **Phase 3** | Add message broker only when measurable business requirements require asynchronous event processing. |
| **Phase 4** | Evaluate event-driven architecture only when scale, throughput, or integration demands justify it. |

#### Governance Rules (Architecture)

1. Future architectural changes must be recorded as a new ADR **before** implementation begins.
2. Any proposal to introduce Kafka, CQRS, event sourcing, or similar technologies must include documented justification referencing BRD and SRS requirements.
3. Architectural additions must solve a **demonstrated** problem, not an anticipated one.
4. Simplicity is preferred unless business requirements prove otherwise.

---

### ADR-002 — Production Microservices Architecture Baseline

| Field | Value |
|-------|-------|
| **Status** | **APPROVED — Supersedes ADR-001** |
| **Decision Date** | 2026-06-16 |
| **Recorded By** | Engineering Steward |
| **Supersedes** | ADR-001 (Initial MVP Architecture Baseline) |
| **Source Authority** | Engineering directive — long-term platform architecture decision |

#### Context

ADR-001 established a simple monolithic architecture suitable for MVP delivery.

Subsequent engineering direction establishes this system as a **long-term Farm Management Platform** requiring:
- Independent deployability of each business domain
- Domain-driven boundaries with loose coupling
- Event-driven integration between bounded contexts
- Ability for multiple agents/teams to work on separate services independently
- Scale paths for individual services without full-system redeployment

The business system spans 8 clearly separated domains (Identity, Farm, Livestock, Inventory, Finance, Notifications, Reporting, API Gateway), each with independent data ownership requirements.

#### Approved Architecture Stack (Supersedes ADR-001)

| Layer | Technology | Change from ADR-001 |
|-------|-----------|-------------------|
| **Frontend** | React + TypeScript | Same |
| **Backend** | FastAPI × 8 microservices | Was single FastAPI app |
| **Primary Database** | PostgreSQL (one DB per service) | Was single DB |
| **Caching Layer** | Redis | Same |
| **Message Broker** | RabbitMQ (topic exchange) | New — was not present |
| **Containerization** | Docker + Docker Compose | Same |
| **Reverse Proxy** | Nginx | Same |
| **Real-Time Communication** | WebSocket | Same |
| **Authentication** | JWT (verified at API Gateway only) | Same mechanism, gateway pattern added |
| **Database Migration** | Alembic (per service) | Was single migration set |
| **ORM** | SQLAlchemy | Same |
| **Architecture Style** | Microservices | Was monolith |
| **API Style** | REST | Same |

#### Service Inventory

| Service | Port | Domain | BRD Ref | SRS Ref |
|---------|------|--------|---------|---------|
| api-gateway | 8000 | Routing, JWT verification | BRD §3 | SRS §11 |
| identity-service | 8001 | Auth, users, roles, permissions | BRD §5 | SRS §5.1, §5.2, §5.26 |
| farm-service | 8002 | Farms, buildings, sections | BRD §6.1 items 1, 3 | SRS §5.3 |
| livestock-service | 8003 | Animals, batches, health, growth | BRD §6.1 items 2, 4-9, 15-16 | SRS §5.3-§5.10, §5.18-§5.21 |
| inventory-service | 8004 | Warehouses, feed, medicine, equipment | BRD §6.1 items 10-11 | SRS §5.12-§5.13 |
| finance-service | 8005 | Revenue, expenses, sales, customers | BRD §6.1 items 12-13 | SRS §5.15-§5.18 |
| notification-service | 8006 | Alerts, WebSocket delivery, reminders | BRD §6.1 item 20 | SRS §5.22-§5.23 |
| reporting-service | 8007 | Reports, KPIs, export | BRD §6.1 item 18 | SRS §5.22, SF-21 |

#### Architectural Principles Applied

1. **Domain-driven boundaries** — each service is a bounded context
2. **Loose coupling** — services communicate via REST API or async events only
3. **High cohesion** — each service owns all logic for its domain
4. **Independent deployability** — each service has its own Dockerfile and database
5. **Event-driven integration** — RabbitMQ topic exchange for async domain events
6. **API-first design** — all inter-service communication via documented REST APIs
7. **Service ownership** — one service owns each entity; no cross-DB queries
8. **Traceability** — every service maps to BRD and SRS sections

#### RabbitMQ Event Architecture

- Exchange: `agrovision.events` (topic type, durable)
- Routing key pattern: `{domain}.{entity}.{action}`
- Dead-letter exchange: `agrovision.dlx`
- Consumer queues: `notification.events`, `reporting.events`, `finance.events`, `inventory.events`
- Full event catalogue: `docs/api/events.md`
- Event schemas: `shared/events/schemas.py`

#### Repository Structure Established

```
/frontend          React + TypeScript SPA
/services          8 independent FastAPI microservices
/shared            Contracts, events, models, utils, exceptions
/infrastructure    Nginx, PostgreSQL init, RabbitMQ definitions
/docs              Architecture, API, development documentation
/.project-governance  This file
```

#### What Changed from ADR-001

- Monolith → 8 microservices
- Single database → 8 isolated databases (one per service)
- No message broker → RabbitMQ with topic routing
- No inter-service boundaries → domain-driven bounded contexts
- RabbitMQ and microservices were previously rejected in ADR-001; this decision explicitly overrides that rejection with engineering directive authority

#### Governance Rules (ADR-002)

1. Every bounded context (service) must maintain its own database. No cross-service DB queries.
2. Cross-context communication: REST API (sync) or domain events via RabbitMQ (async).
3. New microservices may only be added via a new ADR with domain boundary justification.
4. Event schema changes that are breaking require a version bump and migration strategy.
5. The API Gateway is the sole JWT verification point. Services trust injected headers only.

---

### ADR-003 — MVP Realignment: Uzbekistan Poultry Production Platform

| Field | Value |
|-------|-------|
| **Status** | **APPROVED** |
| **Decision Date** | 2026-06-16 |
| **Recorded By** | Engineering Steward |
| **Supersedes** | Scope assumptions in ADR-001 and ADR-002 (BRD literal reading as generic enterprise platform) |
| **Does NOT supersede** | ADR-002 architecture stack (microservices, RabbitMQ, etc. remain unchanged) |
| **Full document** | `docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md` |

#### Summary

Realigned product scope from "generic multi-species enterprise agriculture platform" to "Poultry Production Management Platform for small/medium farms in Uzbekistan."

**Batch-First Principle mandated:** All poultry domain models, events, and endpoints must be batch-centric. No individual bird tracking in MVP.

**MVP Species:** broiler, layer only. Cattle/sheep/goat → Phase 3+.

**Primary workflow:** Batch Arrival → Feed → Water → Medication → Vaccination → Mortality → Weight → Close → Profit Analysis.

**All 8 services remain.** MVP scope within each service narrowed (see §21 MVP Definition).

#### MVP Governance Rule (Added by ADR-003)

> Any feature proposed for MVP implementation that falls outside the primary poultry batch workflow must produce a written business justification referencing the BRD and demonstrating that the feature is required before first production deployment.

---

## 13. Open Questions

| # | Question | Source | Status |
|---|----------|--------|--------|
| OQ-01 | BRD §10–§20 (Business Rules, Full Functional Requirements, NFRs, Reports, Compliance, Risks, Assumptions, KPIs, Business Benefits, Acceptance Criteria, Conclusion) are declared in the BRD as a "second part" but not yet provided. Many implementation decisions depend on these sections. | BRD cover note | **OPEN — second BRD part needed** |
| OQ-02 | SRS §5 states 225 functional requirements (FR-001 – FR-225) but the detailed FR table rows are not visible in the delivered document. Only section headers are present. Are the individual FRs in a separate file or a later version? | SRS §5 | **OPEN — full FR list needed** |
| OQ-03 | SRS §6 lists NFR categories (Performance, Reliability, Availability, Scalability, Maintainability, Security, Usability, Accessibility, Auditability, Backup and Recovery, Data Integrity, Localization, Reporting Performance) but specific measurable values per category are not fully visible (except those confirmed in §11 for security and §13 for acceptance). Full NFR table needed. | SRS §6 | **OPEN — full NFR table needed** |
| OQ-04 | SRS §8 declares a business rules section with unique identifiers (BR-XXX) but the rules themselves are not visible in the delivered text. Full business rules list needed. | SRS §8 | **OPEN — full BR list needed** |
| OQ-05 | SRS §12 declares a traceability matrix linking business goals → system features → functional requirements but the matrix content is not included in the delivered text. | SRS §12 | **OPEN — full traceability matrix needed** |
| OQ-06 | Technology stack, database schema, framework, and deployment model have not been chosen. Are there any pre-existing technology preferences, existing infrastructure, or budget constraints that should guide the ADR process? | Architecture phase | **RESOLVED — See ADR-001 (2026-06-16)** |
| OQ-07 | The SRS §1.3 references a glossary section but states it will be updated as new terms appear. Is there a separate, more complete terminology document? | SRS §1.3 | **OPEN — confirm if separate glossary exists** |
| OQ-08 | Offline mode for field workers is listed as future scope (BRD §6.3), but SRS §2.4 requires critical modules to handle brief internet outages. Exact definition of "brief outage" and scope of offline capability for v1 is ambiguous. | BRD §6.3 / SRS §2.4 | **OPEN — clarification needed** |
| OQ-09 | The permission model allows a user to hold multiple roles simultaneously. What happens when two roles grant conflicting permissions (e.g., one role allows and another denies)? SRS §11.2 states union (most permissive) — but §4.1 mentions an alert if configured accesses conflict. Clarify conflict resolution. | SRS §4.1, §11.2 | **OPEN — conflict resolution rule needs formal definition** |

---

## 14. Risks

**Source:** BRD §7 (AS-IS pain points), BRD §2 (business problems), governance analysis

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R-01 | BRD Part 2 missing — development may proceed without complete business rules, KPIs, and compliance requirements | High | High | Do not implement features dependent on missing sections until Part 2 is received |
| R-02 | 225 functional requirements table not visible — implementation may miss specific FRs | High | High | Request full SRS with complete FR rows before sprint planning |
| R-03 | User adoption risk — farm workers (largest user group) may resist digital tools | Medium | High | Platform must enforce simplicity (minimum steps, Uzbek UI); training mandatory before go-live |
| R-04 | Internet connectivity instability at farm sites may cause data loss or sync conflicts | Medium | Medium | Architecture must address offline/sync strategy; define v1 scope for offline operation |
| R-05 | Scope creep from stakeholder requests for features from Future Scope (§6.3) | Medium | Medium | Enforce BRD §6.2 and §6.3 boundaries; any addition requires formal change approval |
| R-06 | Data migration risk — transitioning from paper/Excel records to platform | Low-Medium | Medium | Initial data loading contracts are an assumption; migration strategy must be defined |
| R-07 | Compliance gaps — veterinary, sanitary, tax regulations not fully documented | Medium | High | Await BRD Part 2 §14 (Compliance); do not implement compliance modules until requirements confirmed |
| R-08 | Permission model complexity — hybrid RBAC + individual access may produce unintended access if misconfigured | Low | High | Conflict detection (OQ-09) must be resolved; thorough UAT of permission scenarios required |

---

## 15. Requirements Traceability Matrix

**Source:** SRS §12 (matrix content not delivered — reconstructed from BRD §3 goals and SRS §4 features)

> **Note:** The official traceability matrix (SRS §12) content was not visible in the delivered document. The mapping below is derived from explicit goal→feature linkages in BRD §3 and SRS §4. It must be replaced with the official matrix when SRS §12 content is obtained.

| Business Goal | BRD Section | System Feature(s) | SRS §4 Reference |
|--------------|-------------|-------------------|-----------------|
| SG-01: Digital transformation | BRD §3.1 | All 24 features | SF-01 through SF-24 |
| SG-02: Multi-farm management | BRD §3.1 | Farm management | SF-02 |
| SG-03: Data-driven decisions | BRD §3.1 | Reports, Dashboards | SF-21 |
| OG-01: Lifecycle tracking | BRD §3.2 | Poultry batch, Livestock, Animal registration, Slaughter | SF-03, SF-04, SF-05, SF-20 |
| OG-02: Vet scheduling | BRD §3.2 | Vaccination, Disease, Vet records, Notifications | SF-07, SF-08, SF-09, SF-22 |
| OG-03: Inventory accuracy | BRD §3.2 | Inventory management, Warehouse ops | SF-12, SF-13 |
| FG-01: Batch cost calculation | BRD §3.3 | Cost management, Financial tracking | SF-15, SF-14 |
| FG-02: Cash flow / receivables | BRD §3.3 | Revenue mgmt, Sales mgmt, Financial tracking | SF-16, SF-17, SF-14 |
| PG-01: FCR improvement | BRD §3.4 | Feed management, Weight monitoring, Reports | SF-10, SF-06, SF-21 |
| PG-02: Mortality reduction | BRD §3.4 | Mortality tracking, Health monitoring, Vaccination | SF-18, SF-07 |
| VG-01: Real-time visibility | BRD §3.5 | Reports, Notifications, Dashboards | SF-21, SF-22 |
| VG-02: Audit readiness | BRD §3.5 | Audit log, Historical archiving, Reports | SF-23, SF-24, SF-21 |
| DG-01: Faster decisions | BRD §3.6 | Dashboards, Reports, Notifications | SF-21, SF-22 |

### Business Process → Feature Traceability

| Business Process | BRD §9 | Primary System Features |
|-----------------|--------|------------------------|
| BP-01 Acquisition | BRD §9.1 | SF-05, SF-12 |
| BP-02 Arrival Management | BRD §9.2 | SF-03, SF-04, SF-05 |
| BP-03 Quarantine | BRD §9.3 | SF-03, SF-04, SF-07, SF-08 |
| BP-04 Feeding | BRD §9.4 | SF-10, SF-12 |
| BP-05 Water Management | BRD §9.5 | SF-11 |
| BP-06 Health Monitoring | BRD §9.6 | SF-08, SF-09, SF-22 |
| BP-07 Vaccination | BRD §9.7 | SF-07, SF-09, SF-12, SF-22 |
| BP-08 Growth Monitoring | BRD §9.8 | SF-06, SF-21 |
| BP-09 Inventory | BRD §9.9 | SF-12, SF-13 |
| BP-10 Workforce | BRD §9.10 | SF-01, SF-02 |
| BP-11 Financial | BRD §9.11 | SF-14, SF-15, SF-16 |
| BP-12 Sales | BRD §9.12 | SF-17, SF-14 |
| BP-13 Transport | BRD §9.13 | SF-19 |
| BP-14 Slaughter | BRD §9.14 | SF-20, SF-09 |
| BP-15 Mortality | BRD §9.15 | SF-18, SF-08, SF-09 |
| BP-16 Disposal | BRD §9.16 | SF-18, SF-23 |
| BP-17 Compliance | BRD §9.17 | SF-23, SF-24, SF-21 |

---

## 16. Scope Boundary

### What Is Inside Scope (Summary)
Everything listed in BRD §6.1 and §3 (goals). All 24 system features in SRS §4. All business processes BP-01 through BP-17.

### What Is Outside Scope (Hard Boundary)
Everything in BRD §6.2. Any feature not traceable to a BRD section or SRS feature ID is out of scope by default.

### What Is Future Scope (Not v1)
Everything in BRD §6.3:
- Full IoT sensor integration
- RFID/biometric auto-tracking
- Advanced genetics/breeding module
- B2B e-commerce and customer portal
- Automated export/certification document generation
- Enhanced bank/tax/government platform integration
- HACCP food safety specialized module
- AI-based disease detection and intervention
- Multi-language support (Uzbek + Russian + English)
- Offline mode for field workers (note: v1 must tolerate brief outages but not full offline operation)

### Architectural Scope Boundary (Added 2026-06-16 — ADR-001)

The following architectural patterns and technologies are **outside the approved MVP architecture boundary**. Any proposal to introduce them must follow the Architecture Change Protocol below:

- Microservice architecture
- Event sourcing
- CQRS
- Apache Kafka, RabbitMQ, or any message broker
- Complex distributed systems
- Service mesh
- Multi-database architecture
- Premature horizontal scaling infrastructure

### Architecture Change Protocol
Any proposal to expand the technology stack beyond ADR-001 must:
1. Be documented as a new ADR before any implementation
2. Reference the specific BRD or SRS requirement that cannot be met by the existing stack
3. Include a cost/complexity impact assessment
4. Receive explicit approval before implementation begins
5. Be recorded in Change History

### Feature Scope Change Protocol
Any feature request that falls outside BRD §6.1 must:
1. Be documented as a proposed change
2. Reference which BRD/SRS section it would modify
3. Receive explicit approval from the project sponsor (Farm Owner / Loyiha homiysi)
4. Be recorded in Change History with impact assessment before implementation begins

---

## 17. Technical Decisions Log

The production microservices architecture baseline has been approved via ADR-002 (2026-06-16), superseding ADR-001.

### Technical Decisions

| # | Decision Area | Status | Detail |
|---|--------------|--------|--------|
| TDL-01 | Frontend framework and language | **DECIDED — ADR-002** | React + TypeScript |
| TDL-02 | Backend framework and language | **DECIDED — ADR-002** | FastAPI (Python 3.12) |
| TDL-03 | Primary database | **DECIDED — ADR-002** | PostgreSQL 16 (one database per service) |
| TDL-04 | Caching layer | **DECIDED — ADR-002** | Redis 7 |
| TDL-05 | Containerization and orchestration | **DECIDED — ADR-002** | Docker + Docker Compose |
| TDL-06 | Reverse proxy | **DECIDED — ADR-002** | Nginx 1.25 |
| TDL-07 | Real-time communication | **DECIDED — ADR-002** | WebSocket (in notification-service via WebSocketManager) |
| TDL-08 | Authentication mechanism | **DECIDED — ADR-002** | JWT — verified at API Gateway only; downstream services trust X-User-Id headers |
| TDL-09 | Database migration tool | **DECIDED — ADR-002** | Alembic (per service, independent migration sets) |
| TDL-10 | ORM | **DECIDED — ADR-002** | SQLAlchemy 2.x (async with asyncpg driver) |
| TDL-11 | Architecture style | **DECIDED — ADR-002** | Microservices (8 services, domain-driven boundaries) |
| TDL-12 | Message broker | **DECIDED — ADR-002** | RabbitMQ 3.13 (topic exchange: agrovision.events) |
| TDL-13 | API style | **DECIDED — ADR-002** | REST, versioned at /api/v1/ |
| TDL-14 | Inter-service communication | **DECIDED — ADR-002** | Synchronous: HTTP via API Gateway. Asynchronous: RabbitMQ events |
| TDL-15 | Repository pattern | **DECIDED — ADR-002** | Abstract repository interface in domain layer; concrete implementation in infrastructure layer |
| TDL-16 | Shared package strategy | **DECIDED — ADR-002** | shared/ package for contracts, events, models, utils, exceptions |
| TDL-17 | Offline/sync strategy for unstable connectivity | **OPEN** | Not decided — depends on OQ-08 resolution |
| TDL-18 | File/document storage service | **OPEN** | Not decided |
| TDL-19 | SMS/notification gateway provider | **OPEN** | Not decided |
| TDL-20 | Archiving strategy and archive storage tier | **OPEN** | Not decided — Reporting Service owns archiving API skeleton |
| TDL-21 | Report generation engine (PDF/Excel) | **OPEN** | Not decided — Reporting Service skeleton ready for engine selection |

---

## 18. Development Journal

### Entry DJ-001 — 2026-06-16
**Event:** Project governance system established.
**Context:** No code exists yet. BRD (Part 1, §1–§9) and SRS v1.1 have been read and analyzed. Both documents are in Uzbek. The governance directory and project_memory.md have been created as the authoritative project baseline.
**Key finding:** BRD Part 2 (§10–§20) is explicitly declared as not yet delivered. SRS §5 individual FR rows (225 FRs) and §8 business rules (BR-XXX) are declared but their content was not visible in the delivered document. These gaps must be resolved before implementation begins.
**Next step:** Obtain BRD Part 2 and the full SRS FR/BR tables before any feature development.

### Entry DJ-002 — 2026-06-16
**Event:** MVP architecture baseline approved and recorded (ADR-001).
**Context:** BRD and SRS were re-read to confirm current scale assumptions and system requirements. The approved stack (React + TypeScript, FastAPI, PostgreSQL, Redis, Docker, Nginx, WebSocket, JWT, Alembic, SQLAlchemy) is documented as ADR-001 in Section 12. Microservices, Kafka, CQRS, event sourcing, and related patterns are explicitly rejected for MVP.
**Key finding:** Current scale assumptions (limited farms, moderate data volume, limited concurrent users, no large-scale IoT or event streaming) do not justify architectural complexity beyond the approved baseline.
**Next step:** All development must conform to ADR-001. Any future proposal to alter the stack must produce a new ADR referencing BRD/SRS requirements before implementation.

### Entry DJ-003 — 2026-06-16
**Event:** Production-grade microservices architecture foundation established (ADR-002).
**Context:** Engineering directive established the system as a long-term platform requiring domain-driven microservices. ADR-002 supersedes ADR-001. Full repository foundation created: 8 microservices, shared packages, infrastructure configuration, domain model skeletons, event contracts, API standards, documentation, CI pipeline.
**Key decisions made:**
- Architecture: microservices with RabbitMQ event bus
- 8 bounded contexts established with full BRD/SRS traceability
- Domain layer separation enforced (no infrastructure in domain models)
- Event schemas defined for all cross-service domain events
- Repository pattern established (abstract interfaces in domain, concrete in infrastructure)
- JWT verification centralized at API Gateway
**Files created:** 80+ files across frontend, 8 services, shared packages, infrastructure, docs, CI
**Key finding:** All 24 SRS system features (SF-01 to SF-24) and 17 business processes (BP-01 to BP-17) are mapped to owning services. Domain models created for livestock, farm, inventory, finance, and identity domains.
**Next step:** Feature implementation agents can now begin working on individual services. Start with identity-service authentication endpoints (SRS §5.1) then farm-service (SRS §5.3).

### Entry DJ-004 — 2026-06-16
**Event:** Strategic MVP Realignment — ADR-003 approved and implemented.
**Context:** Domain models, event contracts, and architecture documents were reviewed against the business reality of target customers: small/medium poultry farms in Uzbekistan. The original generic enterprise scope was narrowed to a focused Poultry Production Management Platform.
**Key decisions made:**
- Product focus: poultry batches (broiler, layer) only for MVP
- Batch-First Principle enforced: batch_id is required (not optional) on all health, mortality, vaccination, medication records
- Individual Animal model preserved as `_Animal_FutureRelease` skeleton — not activated in MVP
- WeightRecord renamed to WeightSampling; reflects sampling approach not per-bird measurement
- New MVP health models: MedicationRecord + DailyHealthLog (replace formal DiseaseIncident)
- Event routing keys changed from `livestock.*` prefix to `batch.*` prefix for all MVP events
- New MVP events added: MortalityRecordedEvent, MedicationRecordedEvent, WeightSampledEvent, SaleRecordedEvent
- Old FUTURE RELEASE events prefixed with underscore (e.g., `_SlaughterRecordedEvent_FutureRelease`)
- RabbitMQ bindings updated: finance.events now binds `batch.#` + `finance.#` (was `livestock.#`)
- Bounded contexts doc rewritten with MVP/Future Release classification and new routing key table
- Service ownership matrix updated with MVP Release column for all SF and BP entries
**Files modified:** livestock/domain/models/animal.py, livestock/domain/models/health.py, shared/events/schemas.py, shared/events/__init__.py, infrastructure/rabbitmq/definitions.json, docs/architecture/bounded-contexts.md, docs/architecture/service-ownership.md, docs/decisions/ADR-003-*.md (created), project_memory.md (this file)
**Next step:** Begin MVP feature implementation. Start with identity-service auth → farm-service → livestock-service batch CRUD endpoints.

---

## 19. Development Progress

| Module | Status | BRD Reference | SRS Reference | Notes |
|--------|--------|--------------|--------------|-------|
| Governance baseline | **Complete** | BRD §1-§9 | SRS all | CH-001 |
| Architecture baseline (ADR-001) | **Superseded** | BRD §3, §6.1 | SRS §4, §6 | Superseded by ADR-002 |
| Architecture baseline (ADR-002) | **Complete** | BRD §3, §6.1 | SRS §4, §6 | Microservices + RabbitMQ + all service skeletons established |
| Repository structure | **Complete** | All | All | 8 service directories, shared packages, infrastructure, docs, CI |
| API Gateway skeleton | **Complete** | All | SRS §11 | JWT middleware, reverse proxy routing |
| Identity Service skeleton | **Complete** | BRD §5 | SRS §5.1, §5.2, §5.26 | User/Role/Permission models, authenticate use case |
| Farm Service skeleton | **Complete** | BRD §6.1 items 1,3 | SRS §5.3 | Farm/Building/Section models |
| Livestock Service skeleton | **Complete** | BRD §6.1 items 2,4-9,15-16 | SRS §5.3-§5.10, §5.18-§5.21 | Batch/Animal/WeightRecord/Mortality/Vaccination/Disease/Treatment models |
| Inventory Service skeleton | **Complete** | BRD §6.1 items 10-11 | SRS §5.12-§5.13 | Warehouse/StockItem/StockBatch/StockMovement models |
| Finance Service skeleton | **Complete** | BRD §6.1 items 12-13 | SRS §5.15-§5.18 | Expense/SalesOrder/Payment/Customer models |
| Notification Service skeleton | **Complete** | BRD §6.1 item 20 | SRS §5.22-§5.23 | Notification model, WebSocketManager |
| Reporting Service skeleton | **Complete** | BRD §6.1 item 18 | SRS §5.22, SF-21 | Skeleton only — no report engines yet |
| Shared event schemas | **Updated (ADR-003)** | All | SRS §5.23-§5.24 | MVP batch.* events + Future Release skeletons separated; SaleRecordedEvent added |
| Shared contracts | **Complete** | All | SRS §6 (API NFRs) | APIResponse, PaginatedResponse, ErrorResponse |
| Shared exceptions | **Complete** | All | All | Domain exception hierarchy |
| Domain models (all services) | **Updated (ADR-003)** | Per service | Per service | Livestock models batch-centric; Animal→FutureRelease; WeightSampling; MedicationRecord; DailyHealthLog |
| MVP Realignment (ADR-003) | **Complete** | BRD §2, §6.1 | SRS §5.3-§5.10 | Scope narrowed to poultry batch platform; events/docs/models updated; see CH-004 |
| Business feature implementation | **Not started** | BRD §6.1 | SRS §5 (225 FRs) | Awaiting feature agents |
| Authentication endpoints | **Not started** | BRD §5 | SRS §5.1 | Implement login, refresh, logout in identity-service |
| Farm CRUD endpoints | **Not started** | BRD §6.1 item 1 | SRS §5.3 | Implement in farm-service |

---

## 20. Change History

All entries are permanent. Mark superseded entries as `[SUPERSEDED by CH-XXX]` but never delete.

---

### CH-001
- **Date:** 2026-06-16
- **Task performed:** Establishment of project governance system — initial baseline creation
- **Files created:**
  - `.project-governance/project_memory.md` (this file)
- **Files read:**
  - `1. BRD_AgroVision_Farm_Management_qism1.docx` — full content extracted (§1–§9)
  - `2. SRS_AgroVision_Farm_Management_v1.1.docx` — full content extracted (all 14 sections, noting content gaps)
- **Requirements affected:** All — this is the initial baseline
- **Reason for change:** No governance system existed. Project memory must be established before any implementation begins, per engineering stewardship mandate.
- **Impact assessment:** Zero code impact. This change establishes the governance framework that all future work must align with. Identified 9 open questions and 8 risks, most critically that BRD Part 2 and the full SRS FR/BR tables are not yet available.

---

### CH-002
- **Date:** 2026-06-16
- **Task performed:** Recording of Initial MVP Architecture Baseline as approved architectural decision (ADR-001)
- **Files modified:**
  - `.project-governance/project_memory.md` — Sections 12, 13, 16, 17, 18, 19, 20 updated
- **Files read:**
  - `1. BRD_AgroVision_Farm_Management_qism1.docx` — re-read to confirm scope and scale assumptions
  - `2. SRS_AgroVision_Farm_Management_v1.1.docx` — re-read to confirm NFRs and system feature requirements
- **Decisions recorded:**
  - ADR-001: Approved stack — React + TypeScript (frontend), FastAPI (backend), PostgreSQL (primary DB), Redis (cache), Docker + Docker Compose (containerization), Nginx (reverse proxy), WebSocket (real-time), JWT (auth), Alembic (migrations), SQLAlchemy (ORM)
  - Explicitly rejected for MVP: microservices, event sourcing, CQRS, Kafka, RabbitMQ, distributed systems, service mesh, multi-database architecture, premature horizontal scaling
- **Open questions resolved:** OQ-06 (technology stack) — marked RESOLVED
- **Technical decisions updated:** TDL-01 through TDL-10 marked DECIDED; TDL-11 through TDL-17 remain OPEN
- **Scope Boundary updated:** Architectural scope boundary section added with Architecture Change Protocol
- **Requirements affected:** None — governance documentation only. No application code modified.
- **Reason for change:** Engineering steward mandate requires all architectural decisions to be recorded before implementation begins. ADR-001 establishes the approved baseline that all subsequent development must conform to.
- **Impact assessment:** Zero code impact. This establishes the architectural framework. All future stack proposals must reference ADR-001 and follow the Architecture Change Protocol.

---

### CH-003
- **Date:** 2026-06-16
- **Task performed:** Establishment of production-grade microservices architecture foundation
- **ADR recorded:** ADR-002 (supersedes ADR-001)
- **Files created (count):** 80+ files
- **Key files created:**
  - `.gitignore`, `.env.example`, `README.md`, `Makefile`
  - `docker-compose.yml`, `docker-compose.dev.yml`
  - `infrastructure/nginx/nginx.conf`, `infrastructure/nginx/conf.d/agrovision.conf`
  - `infrastructure/postgres/init.sql`
  - `infrastructure/rabbitmq/rabbitmq.conf`, `infrastructure/rabbitmq/definitions.json`
  - `shared/events/schemas.py` (24 domain event classes)
  - `shared/contracts/api_standards.py` (response envelopes, error codes, pagination)
  - `shared/models/base.py` (SQLAlchemy base mixins)
  - `shared/exceptions/__init__.py` (domain exception hierarchy)
  - For each of 8 services: `Dockerfile`, `requirements.txt`, `pyproject.toml`, `alembic.ini`
  - For each of 8 services: `app/main.py`, `app/core/config.py`, `app/core/exceptions.py`
  - For each of 8 services: `app/api/v1/router.py`, `app/infrastructure/database/session.py`
  - For each of 8 services: `app/infrastructure/messaging/publisher.py`, `migrations/env.py`, `tests/conftest.py`
  - `services/api-gateway/app/middleware/auth.py` (JWT verification)
  - `services/api-gateway/app/api/v1/router.py` (reverse proxy)
  - `services/identity-service/app/domain/models/user.py` (User, Role, Permission models)
  - `services/identity-service/app/domain/repositories/user_repository.py`
  - `services/identity-service/app/application/use_cases/authenticate.py`
  - `services/identity-service/app/api/dependencies.py`
  - `services/farm-service/app/domain/models/farm.py` (Farm, Building, Section models)
  - `services/livestock-service/app/domain/models/animal.py` (Batch, Animal, WeightRecord, MortalityRecord)
  - `services/livestock-service/app/domain/models/health.py` (Vaccination, DiseaseIncident, Treatment)
  - `services/inventory-service/app/domain/models/inventory.py` (Warehouse, StockItem, StockBatch, StockMovement)
  - `services/finance-service/app/domain/models/finance.py` (Expense, SalesOrder, Payment, Customer)
  - `services/notification-service/app/domain/models/notification.py`
  - `services/notification-service/app/infrastructure/websocket/manager.py`
  - `frontend/` (package.json, tsconfig.json, vite.config.ts, Dockerfile, src/main.tsx, App.tsx, types/index.ts, services/api.ts, store/*)
  - `docs/architecture/overview.md`, `bounded-contexts.md`, `service-ownership.md`
  - `docs/api/standards.md`, `events.md`
  - `docs/development/standards.md`, `git-workflow.md`, `commit-conventions.md`
  - `.github/workflows/ci.yml`
- **Requirements affected:** Architecture baseline for all modules
- **Reason for change:** Engineering directive to establish long-term microservices platform foundation before any feature implementation begins.
- **Impact assessment:**
  - Zero business logic implemented
  - All 24 SRS features (SF-01 to SF-24) mapped to owning services
  - All 17 business processes (BP-01 to BP-17) mapped to services
  - Domain models created covering BRD §6.1 items 1-13, 15-16, 18, 20
  - Repository is immediately committable to GitHub
  - Future feature agents can begin implementation without restructuring

---

### CH-004
- **Date:** 2026-06-16
- **Task performed:** Strategic MVP Realignment — ADR-003 implementation
- **ADR recorded:** ADR-003 (MVP Realignment: Uzbekistan Poultry Production Platform)
- **Files created:**
  - `docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md`
- **Files modified:**
  - `services/livestock-service/app/domain/models/animal.py` — Batch-first refactor; Animal→_Animal_FutureRelease; WeightRecord→WeightSampling; batch_id required on MortalityRecord
  - `services/livestock-service/app/domain/models/health.py` — VaccinationRecord batch-scoped; DiseaseIncident→_FutureRelease; MedicationRecord + DailyHealthLog added; duplicate VaccinationStatus fixed
  - `shared/events/schemas.py` — MVP section (batch.* routing keys); Future Release section (old livestock.* events marked with underscore prefix); SaleRecordedEvent added
  - `shared/events/__init__.py` — Exports updated to MVP event set; old individual-animal events re-exported as FutureRelease names
  - `infrastructure/rabbitmq/definitions.json` — finance.events binding updated from `livestock.#` to `batch.#` + `finance.#`
  - `docs/architecture/bounded-contexts.md` — Full rewrite with MVP/Future Release classification and routing key reference table
  - `docs/architecture/service-ownership.md` — MVP Release column added to all SF and BP tables
  - `.project-governance/project_memory.md` — ADR-003 added to §12; §§21-27 added; DJ-004, CH-004 recorded
- **Requirements affected:** livestock-service (SF-03, SF-06, SF-07, SF-08, SF-18), finance-service (SF-17), all event consumers
- **Reason for change:** The original codebase modeled a generic enterprise platform not matching actual target customers. This realignment aligns implementation with real Uzbekistan small poultry farm operations.
- **Impact assessment:**
  - No API endpoints broken (no endpoints implemented yet — skeleton phase)
  - Domain models narrowed but not deleted — future release skeletons preserved
  - Event routing key changes required only infrastructure/rabbitmq/definitions.json update
  - All deferred features preserved in codebase as clearly marked skeletons
  - ADR-002 architecture stack (microservices, RabbitMQ) unchanged

---

## 21. MVP Definition (ADR-003)

**Status:** APPROVED (2026-06-16) | **Full document:** `docs/decisions/ADR-003-mvp-realignment-uzbekistan-poultry.md`

The MVP is a **Poultry Production Management Platform** delivering the following primary workflow end-to-end:

```
Batch Arrival (chick placement)
  → Daily Feed Consumption recording
  → Daily Water Consumption recording
  → Medication event recording (when administered)
  → Vaccination event recording (scheduled by bird age)
  → Daily Mortality Count
  → Periodic Weight Sampling (for FCR / ADG computation)
  → Batch Close (sale or slaughter)
  → Cost + Profit Analysis per Batch
```

### MVP Service Scope Summary

| Service | MVP Scope |
|---------|-----------|
| api-gateway | JWT verification, routing — full MVP |
| identity-service | Auth, users, 3–5 system roles, farm-user binding |
| farm-service | Farm + House/Section catalog (poultry-compatible structures) |
| livestock-service | Poultry batch lifecycle (all batch operations above); no individual animal tracking |
| inventory-service | Feed, vaccine, medicine stock with FIFO/FEFO; low-stock + expiry alerts |
| finance-service | Auto-created batch expenses; simple sale record; profit per batch |
| notification-service | In-app WebSocket alerts (vaccination overdue, low stock, mortality threshold) |
| reporting-service | On-demand batch performance card (FCR, mortality rate, cost, profit) |

---

## 22. Product Focus — Uzbekistan Poultry Platform

**Platform identity:** AgroVision MVP is a digital replacement for the paper notebook and Excel file used by a poultry farm operator in Uzbekistan to track daily batch operations.

**Primary user persona:** Farm Manager / Shift Supervisor — needs to log daily feed, water, mortality, and vaccination records quickly on a mobile phone, with minimal training.

**Secondary persona:** Farm Owner / Director — needs to see profit per batch, FCR trend, and mortality rate dashboard at a glance.

**Core value proposition:**
- Every batch's cost is automatically computed from feed + medicine + vaccine records
- Profit per batch = sale revenue − total batch cost (shown immediately after batch close)
- Vaccination schedule is auto-generated from breed and age; overdue alerts fire automatically
- Mortality trend visible daily — early warning when above-baseline mortality occurs

**What the MVP is NOT:**
- Not an ERP system
- Not a multi-species livestock management platform (MVP)
- Not a compliance/government reporting platform (MVP)
- Not an individual animal tracking system (MVP)

---

## 23. Deferred Features

### Phase 2 (Post-MVP — next release)

| Feature | Reason Deferred |
|---------|----------------|
| Email and SMS notifications | Requires provider integration; in-app WebSocket sufficient for MVP |
| Scheduled report delivery (PDF/Excel) | On-demand sufficient for MVP; delivery pipeline adds complexity |
| Debtor/creditor management (advanced AR) | Simple payment status on SaleRecord covers MVP cash flow visibility |
| Transport management (SF-19, BP-13) | Not in primary batch workflow; adds UI complexity |
| Slaughter module (SF-20) | `batch.batch.closed` with close_reason=slaughter covers MVP need |
| Water consumption as standalone module (SF-11) | Recorded as daily field in feed record for MVP |
| Workforce scheduling and shift management | Not in primary batch workflow |
| Full sales order workflow with multi-line items | Simple SaleRecord covers MVP |
| Formal DiseaseIncident case management (SF-08) | DailyHealthLog + MedicationRecord sufficient for MVP |
| Customer registry beyond name + phone | Simple customer_name on SaleRecord sufficient for MVP |
| Government compliance workflow (BP-17 advanced) | PDF export of batch records sufficient for inspector visits |

### Future Release (Phase 3+)

| Feature | Reason Deferred |
|---------|----------------|
| Individual animal tracking (Animal model, RFID, ear tags) | No RFID infrastructure; batch management meets all MVP needs |
| Cattle, sheep, goat management (SF-04) | Out of poultry focus for MVP |
| Animal registration module (SF-05 individual) | Linked to individual tracking — Phase 3 |
| Dairy operations and milk quality monitoring | Separate product domain |
| Government inspection and compliance workflows | Requires regulatory API specifications not yet available |
| Full audit trail UI (dedicated audit log viewer) | Logs stored; UI deferred |
| Historical archiving module (SF-24) | Data retained per NFR; archive API deferred |
| Advanced genetics/breeding analytics | Phase 3+ |
| IoT sensor integration (microclimate, scales) | BRD §6.3 future scope |
| Multi-language support (Russian, English) | Uzbek only for MVP |
| SSO / enterprise identity integration | Phase 3 |
| Multi-database replication / horizontal scaling | Current scale does not justify |

---

## 24. Uzbekistan Market Constraints

These constraints are non-negotiable design requirements for MVP (ADR-003):

| Constraint | Implication for Implementation |
|-----------|-------------------------------|
| **UI in Uzbek language** | All labels, messages, and error text must be in Uzbek. No fallback to Russian or English in UI. |
| **Intermittent 3G/4G connectivity** | Daily operation forms (feed, water, mortality) must be fast-loading and low-bandwidth. Critical writes should queue and retry on reconnect. |
| **Android mobile phones** | Touch targets must be large; no hover-only interactions; test on 360px width minimum. |
| **Uzbek Sum (UZS) currency** | All financial amounts in UZS. No multi-currency in MVP. Currency symbol: `so'm` or `UZS`. |
| **Low digital literacy** | UI must be minimum-step. Each daily task should complete in ≤3 taps/clicks. No jargon. |
| **No existing digital tools** | Users come from paper. The system must feel like a digital notebook, not an ERP. |
| **1–3 office staff per farm** | No complex multi-department approval workflows in MVP. |
| **PDF for inspectors** | Government and veterinary inspectors require PDF. PDF export of batch summary is MVP requirement. |

---

## 25. Simplification Decisions

Specific simplifications made during ADR-003 realignment vs. original architecture:

| Original Model/Design | MVP Simplification | Rationale |
|----------------------|-------------------|-----------|
| `Animal` model as primary livestock entity | Replaced by `Batch` as sole primary entity; Animal marked `_Animal_FutureRelease` | Uzbekistan farms don't track individual birds |
| `WeightRecord` with optional `animal_id` | `WeightSampling` with required `batch_id`; no per-bird weight | Poultry weight is always measured by batch sample |
| `DiseaseIncident` + `TreatmentRecord` formal case | `MedicationRecord` + `DailyHealthLog` — simplified health tracking | Case management overhead unjustified for MVP farm |
| `VaccinationRecord.veterinarian_id` | Renamed to `performed_by` — veterinarian not required in MVP | Small farms often self-administer vaccines |
| `VaccinationSchedule.batch_id` | Removed — schedule is a template per species, not per-batch | Same schedule applies to all broiler/layer batches |
| `SalesOrder` + `SalesOrderLine` + `Customer` entities | `SaleRecord` — simple batch-level sale with customer_name field | No customer registry needed for MVP |
| `livestock.*` event routing prefix | `batch.*` for MVP events | Routing key reflects what is actually tracked |
| `RevenueRecordedEvent`, `PaymentReceivedEvent` | Moved to Future Release; `SaleRecordedEvent.payment_status` field covers MVP | Complex AR tracking deferred |
| `finance.events` binding: `livestock.#` | Changed to `batch.#` + `finance.#` | Matches actual MVP event routing keys |
| Species enum: BROILER, LAYER, CATTLE, SHEEP, GOAT | `PoultrySpecies` enum (MVP): BROILER, LAYER only | MVP scope is poultry only |

---

## 26. Architecture Realignment Summary

ADR-003 did NOT change the ADR-002 architecture stack. What changed at the **implementation scope** level:

| Dimension | Before ADR-003 | After ADR-003 |
|-----------|---------------|---------------|
| Product focus | Generic multi-species enterprise farm platform | Poultry batch management for Uzbekistan SME farms |
| Primary aggregate | Animal (individual) + Batch | **Batch only** in MVP |
| Livestock domain scope | All species, individual tracking, RFID | Broiler + layer batches only |
| Health tracking | Formal DiseaseIncident case management | DailyHealthLog + MedicationRecord (simplified) |
| Event routing prefix | `livestock.*` | `batch.*` for all MVP events |
| Finance domain | Full AR/AP, sales orders, customer registry | Expense auto-creation + simple SaleRecord |
| Notifications | Email + SMS + WebSocket | WebSocket in-app only (MVP) |
| Reporting | Full scheduled multi-format delivery | On-demand batch card + PDF (MVP) |
| RabbitMQ finance binding | `livestock.#` | `batch.#` + `finance.#` |
| Deferred feature handling | Not classified | All deferred features preserved as `_*_FutureRelease` skeletons |

---

## 27. Future Release Roadmap

### Phase 2 (post-MVP, estimated 3–6 months after production)

- Email and SMS notification delivery (notification-service)
- Scheduled report delivery with PDF/Excel/CSV (reporting-service)
- Advanced sales order workflow with customer registry and debtor tracking (finance-service)
- Formal DiseaseIncident case management with isolation workflow (livestock-service)
- Transport management (SF-19, BP-13) — livestock-service
- Slaughter module (SF-20) — livestock-service
- Workforce scheduling and shift management (identity-service extension)
- Water consumption standalone module (SF-11 full)
- Government compliance PDF generation with inspection workflow
- Basic budget vs. actual tracking (finance-service)

### Phase 3+ (Future Release — 12+ months)

- Individual animal tracking (Animal model activation, RFID integration)
- Cattle, sheep, goat management (livestock-service extension)
- Dairy operations and milk quality monitoring (new service or livestock extension)
- IoT sensor integration (microclimate, automated scales)
- Advanced genetics/breeding analytics
- Multi-language support (Russian, English)
- SSO / enterprise identity federation
- Multi-region database replication
- Government API integration (veterinary, tax, sanitary)
- Full audit trail UI with search
- Historical archiving API (SF-24)

---

### CH-005
- **Date:** 2026-06-16
- **Task performed:** Runtime readiness review and `docker compose up --build` validation
- **Files created:**
  - `.env` — development environment file (from `.env.example`; safe dev credentials)
  - `shared/__init__.py` — makes `shared/` a proper Python package (`from shared.xxx import` now works)
  - `frontend/nginx.conf` — nginx config for the SPA container (React router fallback to index.html)
  - `.dockerignore` — prevents `.git`, `node_modules`, `__pycache__`, `*.pyc` from entering build context
  - `start.sh`, `stop.sh`, `restart.sh` — convenience scripts for single-command operations
- **Files modified:**
  - `services/*/Dockerfile` (all 8) — Build context changed to repo root; `shared/` package copied; `PYTHONPATH=/app` set; `curl` installed; `HEALTHCHECK` directive added
  - `docker-compose.yml` — Full rewrite: all build contexts set to `.` (repo root) with explicit Dockerfile paths; Redis health check fixed (`REDISCLI_AUTH` env var); all FastAPI services get `healthcheck:` blocks; all app service `depends_on:` have `condition: service_healthy`; nginx `depends_on:` api-gateway and frontend with health conditions; all infrastructure+service ports exposed; `start_period` added for health checks
  - `docker-compose.dev.yml` — Removed now-redundant port/infrastructure overrides (ports already in base); added `./shared:/app/shared` volume mounts for all 8 services so shared code hot-reloads too
  - `shared/requirements-base.txt` — Removed duplicate `httpx==0.27.0`; commented out pytest/ruff (should be installed separately in CI, not baked into production images)
  - `README.md` — Complete rewrite with Quick Start, Service URLs, Verify Services commands, hot-reload instructions, migration commands, Troubleshooting section
- **Issues fixed:**
  1. `shared/` package unavailable in Docker builds (root cause: service build context didn't include parent dir) → all Dockerfiles now build from repo root context
  2. `from shared.xxx import` would fail at container startup → `shared/__init__.py` created + `PYTHONPATH=/app` set
  3. No `.env` file → `docker compose up` would fail on first line → `.env` created
  4. Redis health check `redis-cli ping` fails with password authentication → `REDISCLI_AUTH` env var added to redis service
  5. No HEALTHCHECK on any FastAPI service → `depends_on: condition: service_healthy` couldn't work → added to all 8 Dockerfiles and compose
  6. Nginx depends_on api-gateway without health condition → nginx could start before api-gateway was ready → fixed with condition
  7. `frontend/nginx.conf` missing → frontend Docker build would COPY fail → created
  8. Dev hot-reload volumes didn't mount `shared/` → edits to shared code required full rebuild → fixed in docker-compose.dev.yml
  9. `httpx` listed twice in requirements → pip warning on every install → fixed
  10. pytest/ruff baked into runtime image → unnecessary image bloat → moved to CI-only comments
- **Startup sequence after fix:**
  1. postgres, redis, rabbitmq start (parallel)
  2. Once all three are healthy: all 8 FastAPI services start (parallel)
  3. Once api-gateway and frontend are healthy: nginx starts
  4. Total expected time to full healthy: ~2-3 minutes
- **Developer experience after fix:**
  - `docker compose up --build` → single command, no manual steps
  - All service Swagger UIs accessible at localhost:8001-8007/docs
  - API Gateway at localhost:8000
  - RabbitMQ management at localhost:15672
  - `./start.sh`, `./stop.sh`, `./restart.sh` convenience scripts

---

*End of project_memory.md — Last updated: 2026-06-16 (CH-005)*

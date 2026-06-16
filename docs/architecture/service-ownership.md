# AgroVision — Service Ownership Matrix

Maps each service to: BRD sections, SRS features, business processes, and owning domain.

> **ADR-003 (2026-06-16):** Added MVP Release column. Features marked **MVP** are in scope for
> initial production release. **Phase 2** features follow MVP launch. **Future Release** features
> are preserved in codebase as skeletons but not activated. See ADR-003 for full rationale.

| Service | BRD Business Goals | SRS Features | Business Processes | Domain | MVP Classification |
|---------|-------------------|--------------|--------------------|--------|--------------------|
| api-gateway | All (routing) | All (access point) | All | Infrastructure | **Core MVP** |
| identity-service | SG-01, SG-02 | SF-01 | BP-10 | Identity & Access | **Core MVP** |
| farm-service | SG-01, SG-02 | SF-02 | — | Farm & Structure | **Core MVP** |
| livestock-service | OG-01, OG-02, PG-01, PG-02 | SF-03 (MVP), SF-06-SF-08 (MVP simplified), SF-10-SF-11 (MVP), SF-18 (MVP) | BP-01 to BP-09, BP-15 | Animal & Health | **Core MVP (batch-centric poultry only)** |
| inventory-service | OG-03 | SF-12, SF-13 | BP-09 | Warehouse & Stock | **Core MVP** |
| finance-service | FG-01, FG-02 | SF-14, SF-15 (MVP), SF-16-SF-17 (Phase 2) | BP-11 (MVP), BP-12 (Phase 2) | Finance & Sales | **Core MVP (narrowed)** |
| notification-service | VG-01, OG-02 | SF-22 | BP-07, BP-06 | Alerts & Delivery | **Supporting MVP** |
| reporting-service | SG-03, VG-01, VG-02, DG-01 | SF-21 (minimal), SF-23-SF-24 (Future) | BP-17 (partial) | Reporting & Analytics | **Supporting MVP (minimal)** |

---

## SRS Feature → Service Mapping (Full)

| SF# | Feature | Owning Service | MVP Release |
|-----|---------|----------------|-------------|
| SF-01 | Authentication and flexible permissions | identity-service | **MVP** — simplified RBAC (3–5 system roles); advanced role builder → Phase 2 |
| SF-02 | Farm management | farm-service | **MVP** — poultry farms; mixed/livestock farms → Phase 3 |
| SF-03 | Poultry batch management | livestock-service | **MVP** — full batch lifecycle (arrival → feed/water/vaccination/mortality → close) |
| SF-04 | Livestock management (cattle/sheep/goat) | livestock-service | **Future Release** — species not in MVP (ADR-003) |
| SF-05 | Animal registration (individual) | livestock-service | **Future Release** — individual tracking deferred (ADR-003) |
| SF-06 | Weight monitoring | livestock-service | **MVP** — batch-level weight sampling (WeightSampling model) |
| SF-07 | Vaccination management | livestock-service | **MVP** — batch-level; schedule templates by species age |
| SF-08 | Disease management (formal case) | livestock-service | **Phase 2** — MVP uses DailyHealthLog + MedicationRecord (simplified) |
| SF-09 | Veterinary records | livestock-service | **Phase 2** — linked to formal DiseaseIncident case management |
| SF-10 | Feed management | livestock-service (consumption) + inventory-service (stock) | **MVP** |
| SF-11 | Water consumption monitoring | livestock-service | **MVP** — recorded as daily field; standalone water module → Phase 2 |
| SF-12 | Inventory management | inventory-service | **MVP** — feed, vaccine, medicine stock with FIFO/FEFO |
| SF-13 | Warehouse operations | inventory-service | **MVP** |
| SF-14 | Financial tracking (expense) | finance-service | **MVP** — batch expenses, auto-created from batch events |
| SF-15 | Cost management | finance-service | **MVP** — profit per batch calculation |
| SF-16 | Revenue management | finance-service | **Phase 2** — advanced AR/revenue; MVP has SaleRecordedEvent |
| SF-17 | Sales management | finance-service | **Phase 2** (full); **MVP**: simple sale record (finance.sale.recorded) |
| SF-18 | Mortality tracking | livestock-service | **MVP** — daily batch mortality count (MortalityRecord) |
| SF-19 | Transport management | livestock-service | **Phase 2** — BP-13 deferred (ADR-003) |
| SF-20 | Slaughter management | livestock-service | **Phase 2** — MVP: use batch.batch.closed with close_reason=slaughter |
| SF-21 | Reports | reporting-service | **MVP (minimal)** — on-demand batch performance card; scheduled delivery → Phase 2 |
| SF-22 | Notifications | notification-service | **MVP** — in-app WebSocket; email/SMS → Phase 2 |
| SF-23 | Audit log | All services (each maintains own audit trail) | **MVP** — stored; audit trail UI → Future Release |
| SF-24 | Historical archiving | reporting-service (archive API) | **Future Release** — data retained per NFR; archiving API deferred |

---

## Business Process → Service Responsibility

| BP | Process | Primary Service | Supporting Services | MVP Release |
|----|---------|----------------|---------------------|-------------|
| BP-01 | Animal/Batch Acquisition | livestock-service | inventory-service, finance-service | **MVP** (batch arrival) |
| BP-02 | Arrival Management | livestock-service | farm-service | **MVP** |
| BP-03 | Quarantine | livestock-service | notification-service | **MVP** |
| BP-04 | Feeding Operations | livestock-service | inventory-service | **MVP** |
| BP-05 | Water Management | livestock-service | — | **MVP** (daily field) |
| BP-06 | Health Monitoring | livestock-service | notification-service | **MVP** (simplified — DailyHealthLog) |
| BP-07 | Vaccination Operations | livestock-service | inventory-service, notification-service | **MVP** |
| BP-08 | Growth Monitoring | livestock-service | reporting-service | **MVP** (weight sampling + batch card) |
| BP-09 | Inventory Management | inventory-service | notification-service | **MVP** |
| BP-10 | Workforce Operations | identity-service | — | **MVP** (user management); scheduling → Phase 2 |
| BP-11 | Financial Operations | finance-service | — | **MVP** (expense tracking + batch profit) |
| BP-12 | Sales Operations | finance-service | notification-service | **Phase 2** (full); **MVP**: simple sale record |
| BP-13 | Transport Operations | livestock-service | — | **Phase 2** — ADR-003 deferred |
| BP-14 | Slaughter Operations | livestock-service | finance-service | **Phase 2** — use batch close in MVP |
| BP-15 | Mortality Management | livestock-service | notification-service, reporting-service | **MVP** |
| BP-16 | Disposal Management | livestock-service | — | **Phase 2** |
| BP-17 | Compliance Management | reporting-service | All (audit logs) | **Phase 2** (basic PDF export MVP) |

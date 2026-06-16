# AgroVision MVP Scope

**Approved:** 2026-06-16 | **Authority:** ADR-003 | **Product:** Poultry Production Management Platform

---

## MVP Primary Workflow

```
Batch Arrival (chick placement)
  → Daily Feed Consumption
  → Daily Water Consumption
  → Medication Events (when administered)
  → Vaccination Events (auto-scheduled by bird age)
  → Daily Mortality Count
  → Periodic Weight Sampling
  → Batch Close (sale or slaughter)
  → Cost + Profit Analysis per Batch
```

Every feature in MVP exists to support this workflow. Features outside this workflow require written business justification before inclusion (ADR-003 governance rule).

---

## Feature Classification

### MVP — Core (must ship in initial production release)

| Feature | Service | SRS Ref | Notes |
|---------|---------|---------|-------|
| User authentication (login, JWT, logout) | identity-service | SF-01 | Lockout after 5 failures |
| User management + farm-user binding | identity-service | SF-01, §5.2 | Farm Owner creates users |
| Role-based access (3–5 system roles) | identity-service | SF-01 | Farm Owner, Manager, Vet, Warehouse, Accountant |
| Farm + building + section catalog | farm-service | SF-02 | Poultry-compatible structures |
| Open poultry batch (batch arrival) | livestock-service | SF-03 | PoultrySpecies: broiler/layer; quarantine start |
| Quarantine → Active transition | livestock-service | SF-03 | 7–14 day minimum; BP-03 |
| Daily feed consumption recording | livestock-service | SF-10 | Deducts from inventory |
| Daily water consumption recording | livestock-service | SF-11 | Simple daily field |
| Daily mortality count recording | livestock-service | SF-18 | Batch-level; cause category |
| Vaccination schedule templates | livestock-service | SF-07 | By species + day-of-age |
| Vaccination event recording | livestock-service | SF-07 | Links to schedule; deducts vaccine inventory |
| Medication event recording | livestock-service | SF-08 (simplified) | MedicationRecord; deducts medicine inventory |
| Daily health observation log | livestock-service | SF-08 (simplified) | DailyHealthLog; flags abnormalities |
| Periodic weight sampling | livestock-service | SF-06 | Sample-based; FCR computation |
| Close batch (sale or slaughter) | livestock-service | SF-03 | BatchCloseReason; triggers profit calc |
| Feed/vaccine/medicine inventory stock | inventory-service | SF-12 | FIFO/FEFO dispatch |
| Warehouse management | inventory-service | SF-13 | Receipt + dispatch acts |
| Low-stock alerts | inventory-service | SF-12 | Triggers notification |
| Expiry alerts | inventory-service | SF-12 | FEFO; expired stock blocked |
| Batch expense auto-creation | finance-service | SF-14, SF-15 | From feed/medication/vaccination events |
| Simple sale record | finance-service | SF-17 (simplified) | Per batch; customer name; payment status |
| Profit per batch calculation | finance-service | SF-15 | Revenue − total expenses |
| In-app notifications (WebSocket) | notification-service | SF-22 | Vaccination overdue; low stock; mortality alert |
| Batch performance report (on-demand) | reporting-service | SF-21 (minimal) | FCR, mortality rate, cost, profit; PDF export |
| Audit log (write) | All services | SF-23 | Stored; no UI in MVP |

### MVP — Supporting (required, but secondary)

| Feature | Service | Notes |
|---------|---------|-------|
| Password complexity + lockout | identity-service | SRS §11 NFR |
| JWT refresh tokens | identity-service | 30-min access / 7-day refresh |
| TLS enforcement | api-gateway / Nginx | SRS §6 Security NFR |
| Data backup | PostgreSQL / ops | SRS §13 AC-07 |
| Uzbek UI | frontend | ADR-003 market constraint |
| UZS currency formatting | frontend + finance | ADR-003 market constraint |

---

### Phase 2 — Not in MVP

| Feature | SRS Ref | Reason Deferred |
|---------|---------|----------------|
| Email notifications | SF-22 | Provider integration; WebSocket sufficient for MVP |
| SMS notifications | SF-22 | Provider integration; adds dependency |
| Scheduled report delivery | SF-21 | On-demand covers MVP; scheduled delivery adds complexity |
| Debtor/creditor management | SF-16, SF-17 | payment_status field on SaleRecord covers MVP |
| Transport management | SF-19 | Outside primary batch workflow (BP-13) |
| Slaughter module | SF-20 | batch.batch.closed with reason=slaughter covers MVP |
| DiseaseIncident case management | SF-08 (full) | MedicationRecord + DailyHealthLog sufficient |
| Customer registry | SF-17 | customer_name field on SaleRecord sufficient |
| Workforce scheduling | SF-01 extension | Not in primary batch workflow |
| Government compliance workflow | BP-17 | PDF export of batch summary covers inspector visits |
| Advanced role builder UI | SF-01 | System roles sufficient for MVP team sizes |
| Budget vs. actual tracking | SF-14, SF-15 | Phase 2 financial enhancement |
| Water consumption standalone module | SF-11 (full) | Daily field in feed record sufficient |

---

### Future Release — Phase 3+

| Feature | SRS Ref | Reason |
|---------|---------|--------|
| Individual animal tracking | SF-05 | No RFID infrastructure; batch model meets all MVP needs |
| RFID / ear tag scanning | BRD §6.3 | Hardware not present at target farms |
| Cattle, sheep, goat management | SF-04 | Outside poultry focus |
| Dairy operations / milk quality | — | Separate product domain |
| IoT sensor integration | BRD §6.3 | Future hardware integration |
| Advanced genetics / breeding | BRD §6.3 | Scientific module |
| Multi-language support | SRS §6 | Uzbek only for MVP |
| SSO / enterprise identity | SRS §7 | Phase 3 enterprise customers |
| Government API integration | SF-23, BP-17 | Regulatory API specs not yet available |
| Full audit trail UI | SF-23 | Logs stored; dedicated viewer Phase 3 |
| Historical archiving API | SF-24 | Data retained per NFR; archiving deferred |

---

## Batch-First Principle (Mandatory — ADR-003)

All livestock domain models, events, and API endpoints must be batch-centric.

**Required:** Every health, mortality, vaccination, medication, feed, water, and weight record must carry a `batch_id` as a required (non-nullable) field.

**Prohibited in MVP:** Any endpoint or model that accepts `animal_id` without a corresponding `batch_id`. Per-bird tracking endpoints are Future Release only.

**Rationale:** Uzbekistan poultry operations manage birds as groups (partiya). Individual bird traceability is not an operational requirement and would add unacceptable UI complexity for farm workers.

---

## MVP Acceptance Checklist

- [ ] Farm can be created with poultry-type buildings and sections
- [ ] Batch opened with species, count, supplier, placement date
- [ ] Quarantine period tracked; batch transitions to Active after 7 days minimum
- [ ] Daily feed consumption recorded; feed inventory deducted
- [ ] Daily mortality recorded; batch current_count updated
- [ ] Vaccination executed; vaccine inventory deducted; notification fired for overdue
- [ ] Medication recorded; medicine inventory deducted
- [ ] Weight sampled; FCR computed
- [ ] Low-stock alert fires when feed drops below minimum threshold
- [ ] Batch closed; total cost = sum of all expenses; profit = revenue − cost
- [ ] Batch performance report (PDF) shows FCR, mortality rate, cost, profit
- [ ] All UI labels in Uzbek; all financial values in UZS

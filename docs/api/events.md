# AgroVision — Event Standards

All domain events published to RabbitMQ must follow these standards.

---

## Event Bus Configuration

- **Exchange:** `agrovision.events`
- **Exchange type:** `topic` (routing-key-based fan-out)
- **Dead-letter exchange:** `agrovision.dlx` (undeliverable messages)
- **Message TTL:** 24 hours (configurable per queue)

---

## Routing Key Convention

```
{domain}.{entity}.{action}
```

| Domain | Entities | Actions |
|--------|----------|---------|
| `farm` | `farm`, `building`, `section` | `created`, `updated`, `deleted` |
| `livestock` | `animal`, `batch`, `vaccination`, `disease`, `treatment`, `feed`, `slaughter` | `created`, `updated`, `deceased`, `transferred`, `opened`, `closed`, `completed`, `recorded` |
| `inventory` | `stock` | `received`, `dispatched`, `updated` |
| `inventory` | `alert` | `low_stock`, `expiry` |
| `finance` | `expense`, `revenue`, `payment` | `created`, `recorded`, `received` |
| `sales` | `order` | `created`, `fulfilled` |

**Wildcard subscriptions:**
- `#` — all events (Notification Service, Reporting Service)
- `livestock.#` — all livestock events (Finance Service cost tracking)
- `inventory.#` — all inventory events (Inventory Service internal)

---

## Event Envelope

Every event carries this metadata envelope:

```json
{
  "metadata": {
    "event_id": "uuid-v4",
    "correlation_id": "uuid-v4",
    "causation_id": "uuid-v4-or-null",
    "occurred_at": "2026-06-16T10:30:00Z",
    "version": 1,
    "producer_service": "livestock-service"
  },
  "...domain-specific fields..."
}
```

---

## Versioning Events

- `version: 1` is the initial version
- Breaking changes to event schema require `version: 2`
- Consumers must handle version detection and schema migration
- Old event versions are kept in `shared/events/schemas_v{N}.py`
- Never silently change an existing event contract

---

## Event Catalogue

### Farm Events
| Event Class | Routing Key | Producer |
|------------|------------|---------|
| FarmCreatedEvent | `farm.farm.created` | farm-service |
| FarmUpdatedEvent | `farm.farm.updated` | farm-service |

### Livestock Events
| Event Class | Routing Key | Producer |
|------------|------------|---------|
| AnimalCreatedEvent | `livestock.animal.created` | livestock-service |
| AnimalUpdatedEvent | `livestock.animal.updated` | livestock-service |
| AnimalDeceasedEvent | `livestock.animal.deceased` | livestock-service |
| AnimalTransferredEvent | `livestock.animal.transferred` | livestock-service |
| BatchOpenedEvent | `livestock.batch.opened` | livestock-service |
| BatchClosedEvent | `livestock.batch.closed` | livestock-service |
| VaccinationCompletedEvent | `livestock.vaccination.completed` | livestock-service |
| DiseaseIncidentCreatedEvent | `livestock.disease.incident_created` | livestock-service |
| TreatmentRecordedEvent | `livestock.treatment.recorded` | livestock-service |
| FeedConsumedEvent | `livestock.feed.consumed` | livestock-service |
| WaterConsumedEvent | `livestock.water.consumed` | livestock-service |
| SlaughterRecordedEvent | `livestock.slaughter.recorded` | livestock-service |

### Inventory Events
| Event Class | Routing Key | Producer |
|------------|------------|---------|
| InventoryReceivedEvent | `inventory.stock.received` | inventory-service |
| InventoryDispatchedEvent | `inventory.stock.dispatched` | inventory-service |
| InventoryUpdatedEvent | `inventory.stock.updated` | inventory-service |
| LowStockAlertEvent | `inventory.alert.low_stock` | inventory-service |
| ExpiryAlertEvent | `inventory.alert.expiry` | inventory-service |

### Finance Events
| Event Class | Routing Key | Producer |
|------------|------------|---------|
| ExpenseCreatedEvent | `finance.expense.created` | finance-service |
| RevenueRecordedEvent | `finance.revenue.recorded` | finance-service |
| PaymentReceivedEvent | `finance.payment.received` | finance-service |
| SalesOrderCreatedEvent | `sales.order.created` | finance-service |
| SalesOrderFulfilledEvent | `sales.order.fulfilled` | finance-service |

---

## Consumer Queue Bindings

| Queue | Binding (routing key) | Consumer Service |
|-------|----------------------|----------------|
| `notification.events` | `#` | notification-service |
| `reporting.events` | `#` | reporting-service |
| `finance.events` | `livestock.#` | finance-service |
| `inventory.events` | `inventory.#` | inventory-service |

from .schemas import (
    BaseEvent,
    EventMetadata,
    # Farm (MVP)
    FarmCreatedEvent,
    FarmUpdatedEvent,
    # Batch (MVP)
    BatchOpenedEvent,
    BatchClosedEvent,
    # Batch daily operations (MVP)
    FeedConsumedEvent,
    WaterConsumedEvent,
    MortalityRecordedEvent,
    VaccinationCompletedEvent,
    MedicationRecordedEvent,
    WeightSampledEvent,
    # Inventory (MVP)
    InventoryReceivedEvent,
    InventoryDispatchedEvent,
    InventoryUpdatedEvent,
    LowStockAlertEvent,
    ExpiryAlertEvent,
    # Finance (MVP)
    ExpenseCreatedEvent,
    SaleRecordedEvent,
    # Future Release — imported for forward-compatibility only; not consumed in MVP
    _AnimalCreatedEvent_FutureRelease,
    _AnimalUpdatedEvent_FutureRelease,
    _AnimalDeceasedEvent_FutureRelease,
    _AnimalTransferredEvent_FutureRelease,
    _SlaughterRecordedEvent_FutureRelease,
    _DiseaseIncidentCreatedEvent_FutureRelease,
    _TreatmentRecordedEvent_FutureRelease,
    _RevenueRecordedEvent_FutureRelease,
    _PaymentReceivedEvent_FutureRelease,
    _SalesOrderCreatedEvent_FutureRelease,
    _SalesOrderFulfilledEvent_FutureRelease,
)

__all__ = [
    # Core envelope
    "BaseEvent",
    "EventMetadata",
    # Farm (MVP)
    "FarmCreatedEvent",
    "FarmUpdatedEvent",
    # Batch lifecycle (MVP)
    "BatchOpenedEvent",
    "BatchClosedEvent",
    # Batch daily operations (MVP)
    "FeedConsumedEvent",
    "WaterConsumedEvent",
    "MortalityRecordedEvent",
    "VaccinationCompletedEvent",
    "MedicationRecordedEvent",
    "WeightSampledEvent",
    # Inventory (MVP)
    "InventoryReceivedEvent",
    "InventoryDispatchedEvent",
    "InventoryUpdatedEvent",
    "LowStockAlertEvent",
    "ExpiryAlertEvent",
    # Finance (MVP)
    "ExpenseCreatedEvent",
    "SaleRecordedEvent",
    # Future Release skeletons
    "_AnimalCreatedEvent_FutureRelease",
    "_AnimalUpdatedEvent_FutureRelease",
    "_AnimalDeceasedEvent_FutureRelease",
    "_AnimalTransferredEvent_FutureRelease",
    "_SlaughterRecordedEvent_FutureRelease",
    "_DiseaseIncidentCreatedEvent_FutureRelease",
    "_TreatmentRecordedEvent_FutureRelease",
    "_RevenueRecordedEvent_FutureRelease",
    "_PaymentReceivedEvent_FutureRelease",
    "_SalesOrderCreatedEvent_FutureRelease",
    "_SalesOrderFulfilledEvent_FutureRelease",
]

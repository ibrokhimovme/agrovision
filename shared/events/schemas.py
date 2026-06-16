"""
AgroVision — Domain Event Schemas
==================================
ADR-003: This file is divided into two sections:
  1. MVP EVENTS — published and consumed in production MVP
  2. FUTURE RELEASE EVENTS — defined for forward compatibility, not consumed in MVP

Routing key convention: <domain>.<entity>.<action>
Exchange: agrovision.events (topic type)

MVP event routing keys in use:
  farm.farm.created / farm.farm.updated
  batch.batch.opened / batch.batch.closed
  batch.feed.consumed / batch.water.consumed
  batch.mortality.recorded
  batch.vaccination.completed
  batch.medication.recorded
  batch.weight.sampled
  inventory.stock.received / inventory.stock.dispatched / inventory.stock.updated
  inventory.alert.low_stock / inventory.alert.expiry
  finance.expense.created / finance.sale.recorded

FUTURE RELEASE routing keys (defined, not consumed in MVP):
  livestock.animal.created / updated / deceased / transferred  — individual tracking
  livestock.slaughter.recorded                                 — slaughter module
  livestock.disease.incident_created                           — formal case management
  livestock.treatment.recorded                                 — formal treatment records
  finance.revenue.recorded / finance.payment.received          — advanced AR/AP
  sales.order.created / sales.order.fulfilled                  — advanced sales workflow

All events:
  - Are immutable value objects (frozen Pydantic models).
  - Carry a metadata envelope (correlation_id, causation_id, timestamp, version).
  - Are versioned. Breaking changes require version bump, never silent field change.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ── Metadata Envelope ────────────────────────────────────────────────────────

class EventMetadata(BaseModel):
    event_id: UUID = Field(default_factory=uuid.uuid4)
    correlation_id: UUID = Field(default_factory=uuid.uuid4)
    causation_id: Optional[UUID] = None
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    producer_service: str

    class Config:
        frozen = True


class BaseEvent(BaseModel):
    metadata: EventMetadata

    class Config:
        frozen = True

    @property
    def routing_key(self) -> str:
        raise NotImplementedError


# ==============================================================================
# MVP EVENTS — Published and consumed in production MVP (ADR-003)
# ==============================================================================

# ── Farm Events (MVP) ─────────────────────────────────────────────────────────

class FarmCreatedEvent(BaseEvent):
    farm_id: UUID
    name: str
    farm_type: str  # poultry | mixed (MVP: poultry farms only)

    @property
    def routing_key(self) -> str:
        return "farm.farm.created"


class FarmUpdatedEvent(BaseEvent):
    farm_id: UUID
    changed_fields: list[str]

    @property
    def routing_key(self) -> str:
        return "farm.farm.updated"


# ── Batch Events (MVP) ────────────────────────────────────────────────────────

class BatchOpenedEvent(BaseEvent):
    """Replaces AnimalCreatedEvent for poultry MVP. Batch is the unit, not the bird."""
    batch_id: UUID
    farm_id: UUID
    section_id: UUID
    species: str  # broiler | layer
    initial_count: int
    placement_date: datetime
    supplier_name: Optional[str] = None

    @property
    def routing_key(self) -> str:
        return "batch.batch.opened"


class BatchClosedEvent(BaseEvent):
    batch_id: UUID
    farm_id: UUID
    close_reason: str  # sale | slaughter | transfer | disease | other
    final_count: int
    total_mortality: int
    closed_at: datetime
    fcr: Optional[Decimal] = None

    @property
    def routing_key(self) -> str:
        return "batch.batch.closed"


# ── Batch Daily Operations (MVP) ──────────────────────────────────────────────

class FeedConsumedEvent(BaseEvent):
    record_id: UUID
    batch_id: UUID
    farm_id: UUID
    feed_inventory_item_id: UUID
    quantity_kg: Decimal
    recorded_at: datetime

    @property
    def routing_key(self) -> str:
        return "batch.feed.consumed"


class WaterConsumedEvent(BaseEvent):
    record_id: UUID
    batch_id: UUID
    farm_id: UUID
    quantity_liters: Decimal
    recorded_at: datetime

    @property
    def routing_key(self) -> str:
        return "batch.water.consumed"


class MortalityRecordedEvent(BaseEvent):
    """Batch-level daily mortality count. Not individual bird events."""
    record_id: UUID
    batch_id: UUID
    farm_id: UUID
    quantity: int
    cause_category: Optional[str] = None
    deceased_at: datetime

    @property
    def routing_key(self) -> str:
        return "batch.mortality.recorded"


class VaccinationCompletedEvent(BaseEvent):
    vaccination_id: UUID
    batch_id: UUID
    farm_id: UUID
    vaccine_name: str
    vaccine_inventory_item_id: UUID
    quantity_used: Decimal
    vaccinated_at: datetime
    performed_by: Optional[UUID] = None

    @property
    def routing_key(self) -> str:
        return "batch.vaccination.completed"


class MedicationRecordedEvent(BaseEvent):
    """MVP simplified health event. Replaces DiseaseIncident for MVP."""
    record_id: UUID
    batch_id: UUID
    farm_id: UUID
    medicine_name: str
    medicine_inventory_item_id: UUID
    quantity_used: Decimal
    reason: Optional[str] = None
    administered_at: datetime

    @property
    def routing_key(self) -> str:
        return "batch.medication.recorded"


class WeightSampledEvent(BaseEvent):
    sampling_id: UUID
    batch_id: UUID
    farm_id: UUID
    sample_size: int
    average_weight_kg: Decimal
    age_days: Optional[int] = None
    measured_at: datetime

    @property
    def routing_key(self) -> str:
        return "batch.weight.sampled"


# ── Inventory Events (MVP) ────────────────────────────────────────────────────


class InventoryReceivedEvent(BaseEvent):
    movement_id: UUID
    warehouse_id: UUID
    item_id: UUID
    item_type: str     # feed | vaccine | medicine | equipment | packaging
    quantity: Decimal
    unit: str
    supplier_id: Optional[UUID] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    received_at: datetime

    @property
    def routing_key(self) -> str:
        return "inventory.stock.received"


class InventoryDispatchedEvent(BaseEvent):
    movement_id: UUID
    warehouse_id: UUID
    item_id: UUID
    quantity: Decimal
    unit: str
    purpose: str     # feed_batch | vaccination | treatment | sale | transfer
    reference_id: Optional[UUID] = None
    dispatched_at: datetime

    @property
    def routing_key(self) -> str:
        return "inventory.stock.dispatched"


class InventoryUpdatedEvent(BaseEvent):
    item_id: UUID
    warehouse_id: UUID
    previous_quantity: Decimal
    new_quantity: Decimal
    unit: str
    updated_at: datetime

    @property
    def routing_key(self) -> str:
        return "inventory.stock.updated"


class LowStockAlertEvent(BaseEvent):
    item_id: UUID
    warehouse_id: UUID
    item_name: str
    current_quantity: Decimal
    minimum_quantity: Decimal
    unit: str

    @property
    def routing_key(self) -> str:
        return "inventory.alert.low_stock"


class ExpiryAlertEvent(BaseEvent):
    item_id: UUID
    warehouse_id: UUID
    item_name: str
    expiry_date: datetime
    days_until_expiry: int
    quantity: Decimal

    @property
    def routing_key(self) -> str:
        return "inventory.alert.expiry"


# ── Finance Events ────────────────────────────────────────────────────────────

class ExpenseCreatedEvent(BaseEvent):
    expense_id: UUID
    farm_id: UUID
    category: str   # feed | veterinary | labor | transport | equipment | other
    amount: Decimal
    currency: str = "UZS"
    reference_id: Optional[UUID] = None   # batch_id, order_id, etc.
    created_at: datetime

    @property
    def routing_key(self) -> str:
        return "finance.expense.created"


class SaleRecordedEvent(BaseEvent):
    """MVP simple batch sale record. Replaces SalesOrderCreatedEvent for MVP."""
    sale_id: UUID
    batch_id: UUID
    farm_id: UUID
    customer_name: Optional[str] = None
    head_count: int
    total_weight_kg: Optional[Decimal] = None
    price_per_kg: Optional[Decimal] = None
    total_amount: Decimal
    currency: str = "UZS"
    payment_status: str = "pending"  # pending | received
    sold_at: datetime

    @property
    def routing_key(self) -> str:
        return "finance.sale.recorded"


# ==============================================================================
# FUTURE RELEASE EVENTS — Defined for forward compatibility. NOT consumed in MVP.
# See ADR-003 for rationale. Activate in Phase 2 / Phase 3 as noted.
# ==============================================================================

# ── Individual Animal Events — FUTURE RELEASE (Phase 3, ADR-003) ──────────────
# Individual bird/animal tracking requires RFID infrastructure and per-animal
# health records. Not applicable in Uzbekistan small poultry farms at MVP.

class _AnimalCreatedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 3. Individual animal registration (SF-05)."""
    animal_id: UUID
    farm_id: UUID
    species: str
    tag_number: Optional[str] = None

    @property
    def routing_key(self) -> str:
        return "livestock.animal.created"


class _AnimalUpdatedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 3."""
    animal_id: UUID
    farm_id: UUID
    changed_fields: list[str]

    @property
    def routing_key(self) -> str:
        return "livestock.animal.updated"


class _AnimalDeceasedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 3. Individual mortality (use batch.mortality.recorded in MVP)."""
    animal_id: UUID
    farm_id: UUID
    cause: Optional[str] = None
    deceased_at: datetime

    @property
    def routing_key(self) -> str:
        return "livestock.animal.deceased"


class _AnimalTransferredEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 3. Individual animal transfer."""
    animal_id: UUID
    from_section_id: UUID
    to_section_id: UUID
    farm_id: UUID
    reason: Optional[str] = None

    @property
    def routing_key(self) -> str:
        return "livestock.animal.transferred"


# ── Slaughter Module — FUTURE RELEASE (Phase 2, ADR-003) ─────────────────────
# Slaughter as a distinct module with veterinarian clearance, weight yield
# tracking, and carcass grading deferred to Phase 2. In MVP, use
# batch.batch.closed with close_reason=slaughter/sale.

class _SlaughterRecordedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 2 slaughter module (SF-20)."""
    slaughter_id: UUID
    batch_id: UUID
    farm_id: UUID
    head_count: int
    live_weight_kg: Decimal
    carcass_weight_kg: Decimal
    slaughtered_at: datetime
    veterinarian_clearance_id: Optional[UUID] = None

    @property
    def routing_key(self) -> str:
        return "livestock.slaughter.recorded"


# ── Disease Case Events — FUTURE RELEASE (Phase 2, ADR-003) ──────────────────
# Formal disease case management with isolation workflow and treatment plans.
# In MVP, use batch.medication.recorded for health observations.

class _DiseaseIncidentCreatedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 2. Formal disease case (SF-08 full)."""
    incident_id: UUID
    farm_id: UUID
    batch_id: Optional[UUID] = None
    diagnosis: Optional[str] = None
    severity: str
    detected_at: datetime

    @property
    def routing_key(self) -> str:
        return "livestock.disease.incident_created"


class _TreatmentRecordedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 2. Linked to DiseaseIncident."""
    treatment_id: UUID
    incident_id: UUID
    farm_id: UUID
    medicine_inventory_item_id: UUID
    quantity_used: Decimal
    administered_by: UUID
    treated_at: datetime

    @property
    def routing_key(self) -> str:
        return "livestock.treatment.recorded"


# ── Advanced Finance Events — FUTURE RELEASE (Phase 2, ADR-003) ──────────────
# Advanced AR/AP tracking with debtor management. In MVP use SaleRecordedEvent
# with payment_status field for simple cash/debt tracking.

class _RevenueRecordedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 2. Advanced revenue/subsidy tracking."""
    revenue_id: UUID
    farm_id: UUID
    source: str
    amount: Decimal
    currency: str = "UZS"
    reference_id: Optional[UUID] = None
    recorded_at: datetime

    @property
    def routing_key(self) -> str:
        return "finance.revenue.recorded"


class _PaymentReceivedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 2. Linked to SalesOrder debtor tracking."""
    payment_id: UUID
    customer_id: UUID
    order_id: UUID
    amount: Decimal
    currency: str = "UZS"
    payment_method: str
    received_at: datetime

    @property
    def routing_key(self) -> str:
        return "finance.payment.received"


# ── Advanced Sales Events — FUTURE RELEASE (Phase 2, ADR-003) ────────────────
# Full sales order workflow with multi-line items, customer registry, delivery
# tracking. Deferred to Phase 2. In MVP use SaleRecordedEvent (finance.sale.recorded).

class _SalesOrderCreatedEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 2. Full sales order (replaces SaleRecordedEvent)."""
    order_id: UUID
    farm_id: UUID
    customer_id: UUID
    total_amount: Decimal
    currency: str = "UZS"
    created_at: datetime

    @property
    def routing_key(self) -> str:
        return "sales.order.created"


class _SalesOrderFulfilledEvent_FutureRelease(BaseEvent):
    """FUTURE RELEASE — Phase 2."""
    order_id: UUID
    farm_id: UUID
    customer_id: UUID
    fulfilled_at: datetime

    @property
    def routing_key(self) -> str:
        return "sales.order.fulfilled"

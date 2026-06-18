"""
DTOs for inventory service. SF-12, SF-13, BP-09.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.inventory.domain.models.inventory import ItemType, MovementType


# ── Warehouse ─────────────────────────────────────────────────────────────────

class CreateWarehouseRequest(BaseModel):
    farm_id: UUID
    name: str
    location: Optional[str] = None
    notes: Optional[str] = None


class WarehouseResponse(BaseModel):
    id: UUID
    farm_id: UUID
    name: str
    location: Optional[str]
    is_active: bool
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Stock Item ────────────────────────────────────────────────────────────────

class CreateStockItemRequest(BaseModel):
    warehouse_id: UUID
    name: str
    item_type: ItemType
    unit: str
    minimum_quantity: Decimal = Decimal("0")
    unit_cost: Optional[Decimal] = None
    sku: Optional[str] = None


class StockItemResponse(BaseModel):
    id: UUID
    warehouse_id: UUID
    name: str
    item_type: ItemType
    unit: str
    current_quantity: Decimal
    minimum_quantity: Decimal
    unit_cost: Optional[Decimal]
    sku: Optional[str]
    is_active: bool
    is_below_minimum: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Receive Stock ─────────────────────────────────────────────────────────────

class ReceiveStockRequest(BaseModel):
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    supplier_id: Optional[UUID] = None
    notes: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class StockBatchResponse(BaseModel):
    id: UUID
    stock_item_id: UUID
    batch_number: Optional[str]
    quantity: Decimal
    remaining_quantity: Decimal
    unit_cost: Optional[Decimal]
    received_at: datetime
    expiry_date: Optional[datetime]
    is_expired: bool

    model_config = {"from_attributes": True}


# ── Dispatch Stock ────────────────────────────────────────────────────────────

class DispatchStockRequest(BaseModel):
    quantity: Decimal
    purpose: Optional[str] = None
    reference_id: Optional[UUID] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None
    use_fefo: bool = False

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class DispatchResultResponse(BaseModel):
    dispatched_quantity: Decimal
    stock_item_id: UUID
    remaining_stock: Decimal
    movements_created: int


# ── Stock Movement ────────────────────────────────────────────────────────────

class StockMovementResponse(BaseModel):
    id: UUID
    stock_item_id: UUID
    warehouse_id: UUID
    movement_type: MovementType
    quantity: Decimal
    unit: str
    unit_cost: Optional[Decimal]
    purpose: Optional[str]
    reference_id: Optional[UUID]
    reference_type: Optional[str]
    notes: Optional[str]
    moved_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}

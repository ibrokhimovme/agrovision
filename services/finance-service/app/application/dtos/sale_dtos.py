"""
DTOs for sales management. SF-17, BP-12.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.domain.models.finance import SalePaymentStatus


class RecordSaleRequest(BaseModel):
    farm_id: UUID
    customer_name: str
    customer_phone: Optional[str] = None
    head_count: int
    quantity_kg: Decimal
    price_per_kg_uzs: Decimal
    payment_status: SalePaymentStatus = SalePaymentStatus.PENDING
    sold_at: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("quantity_kg", "price_per_kg_uzs")
    @classmethod
    def must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("must be positive")
        return v

    @field_validator("head_count")
    @classmethod
    def head_count_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("must be positive")
        return v


class SaleRecordResponse(BaseModel):
    id: UUID
    batch_id: UUID
    farm_id: UUID
    customer_name: str
    customer_phone: Optional[str]
    head_count: int
    quantity_kg: Decimal
    price_per_kg_uzs: Decimal
    total_revenue_uzs: Decimal
    payment_status: SalePaymentStatus
    sold_at: datetime
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchSalesSummaryResponse(BaseModel):
    batch_id: UUID
    total_revenue_uzs: Decimal
    sale_count: int

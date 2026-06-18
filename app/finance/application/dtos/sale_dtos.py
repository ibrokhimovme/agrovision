"""
DTOs for sales management. SF-17, BP-12.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.finance.domain.models.finance import SalePaymentStatus


class RecordSaleRequest(BaseModel):
    farm_id: UUID
    customer_name: str
    customer_phone: Optional[str] = None
    head_count: int
    quantity_kg: Decimal
    price_per_kg_uzs: Decimal
    payment_status: SalePaymentStatus = SalePaymentStatus.PENDING
    # EX-11 (execution-v2): optional exact paid amount, for partial-payment
    # tracking. If omitted, derived from payment_status for backward
    # compatibility (PAID -> full amount, PENDING/PARTIAL -> 0).
    amount_paid: Optional[Decimal] = None
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


class RecordSalePaymentRequest(BaseModel):
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be positive")
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
    amount_paid: Decimal
    outstanding_amount: Decimal
    payment_status: SalePaymentStatus
    sold_at: datetime
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchSalesSummaryResponse(BaseModel):
    batch_id: UUID
    total_revenue_uzs: Decimal
    sale_count: int

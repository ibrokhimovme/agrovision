"""
DTOs for expense and cost tracking. SF-14, SF-15, FG-01.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.finance.domain.models.finance import BatchExpenseType, ExpenseCategory


class RecordManualExpenseRequest(BaseModel):
    farm_id: UUID
    batch_id: Optional[UUID] = None
    category: ExpenseCategory
    expense_type: Optional[BatchExpenseType] = None
    description: str
    amount: Decimal
    currency: str = "UZS"
    # EX-11 (execution-v2): supplier debt and partial-payment tracking, per
    # decision_log.md BMD-015. amount_paid defaults to the full amount
    # (already settled) if omitted, so existing callers are unaffected.
    supplier_id: Optional[UUID] = None
    amount_paid: Optional[Decimal] = None
    expense_date: Optional[datetime] = None
    reference_document: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v


class RecordExpensePaymentRequest(BaseModel):
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v


class ExpenseResponse(BaseModel):
    id: UUID
    farm_id: UUID
    batch_id: Optional[UUID]
    category: ExpenseCategory
    expense_type: Optional[BatchExpenseType]
    description: str
    amount: Decimal
    currency: str
    supplier_id: Optional[UUID]
    amount_paid: Decimal
    outstanding_amount: Decimal
    payment_status: str
    source_event_id: Optional[UUID]
    expense_date: datetime
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchCostSummaryResponse(BaseModel):
    batch_id: UUID
    total_uzs: Decimal
    breakdown: dict[str, Decimal]
    expense_count: int

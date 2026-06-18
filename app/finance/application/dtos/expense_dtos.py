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
    expense_date: Optional[datetime] = None
    reference_document: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
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

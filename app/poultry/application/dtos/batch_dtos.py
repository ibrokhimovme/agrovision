from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.poultry.domain.models.animal import PoultrySpecies, BatchStatus, BatchCloseReason


class CreateBatchRequest(BaseModel):
    farm_id: UUID
    section_id: UUID
    species: PoultrySpecies
    initial_count: int = Field(gt=0)
    placement_date: datetime
    batch_code: Optional[str] = None
    supplier_name: Optional[str] = None
    chick_price_per_head: Optional[Decimal] = None
    notes: Optional[str] = None
    quarantine_end_date: Optional[datetime] = None


class UpdateBatchRequest(BaseModel):
    batch_code: Optional[str] = None
    supplier_name: Optional[str] = None
    chick_price_per_head: Optional[Decimal] = None
    notes: Optional[str] = None
    quarantine_end_date: Optional[datetime] = None


class CloseBatchRequest(BaseModel):
    close_reason: BatchCloseReason
    notes: Optional[str] = None


class BatchResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    farm_id: UUID
    section_id: UUID
    species: PoultrySpecies
    status: BatchStatus
    batch_code: Optional[str]
    initial_count: int
    current_count: int
    placement_date: datetime
    quarantine_end_date: Optional[datetime]
    closed_at: Optional[datetime]
    close_reason: Optional[BatchCloseReason]
    supplier_name: Optional[str]
    chick_price_per_head: Optional[Decimal]
    notes: Optional[str]
    total_mortality: int
    survival_rate: Decimal
    created_at: datetime
    updated_at: datetime

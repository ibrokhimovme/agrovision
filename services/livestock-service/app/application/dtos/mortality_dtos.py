from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RecordMortalityRequest(BaseModel):
    farm_id: UUID
    quantity: int = Field(gt=0)
    deceased_at: datetime
    cause_category: Optional[str] = None
    cause_description: Optional[str] = None
    disposal_method: Optional[str] = None


class MortalityRecordResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    batch_id: UUID
    farm_id: UUID
    quantity: int
    cause_category: Optional[str]
    cause_description: Optional[str]
    disposal_method: Optional[str]
    deceased_at: datetime


class MortalitySummaryResponse(BaseModel):
    batch_id: UUID
    total_deaths: int
    initial_count: int
    current_count: int
    mortality_rate: Decimal
    cause_breakdown: dict[str, int]

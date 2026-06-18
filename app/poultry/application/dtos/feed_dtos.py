from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RecordFeedRequest(BaseModel):
    farm_id: UUID
    feed_date: date
    quantity_kg: Decimal = Field(gt=0)
    water_liters: Optional[Decimal] = Field(default=None, gt=0)
    feed_type: Optional[str] = None
    age_days: Optional[int] = Field(default=None, ge=0)
    feed_inventory_item_id: Optional[UUID] = None
    notes: Optional[str] = None


class FeedRecordResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    batch_id: UUID
    farm_id: UUID
    feed_date: date
    feed_type: Optional[str]
    quantity_kg: Decimal
    water_liters: Optional[Decimal]
    age_days: Optional[int]
    feed_inventory_item_id: Optional[UUID]
    notes: Optional[str]


class FeedSummaryResponse(BaseModel):
    batch_id: UUID
    total_feed_kg: Decimal
    total_water_liters: Optional[Decimal]
    record_count: int
    fcr: Optional[Decimal]

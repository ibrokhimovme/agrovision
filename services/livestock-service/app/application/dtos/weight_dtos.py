from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class RecordWeightRequest(BaseModel):
    farm_id: UUID
    sample_size: int
    total_sample_weight_kg: Decimal
    measured_at: Optional[datetime] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_positive(self) -> "RecordWeightRequest":
        if self.sample_size <= 0:
            raise ValueError("sample_size must be > 0")
        if self.total_sample_weight_kg <= 0:
            raise ValueError("total_sample_weight_kg must be > 0")
        return self


class WeightSamplingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    batch_id: UUID
    farm_id: UUID
    sample_size: int
    average_weight_kg: Decimal
    total_sample_weight_kg: Optional[Decimal] = None
    age_days: Optional[int] = None
    measured_at: datetime
    notes: Optional[str] = None


class GrowthMetricsResponse(BaseModel):
    batch_id: UUID
    sampling_count: int
    latest_avg_weight_kg: Optional[Decimal] = None
    age_days: Optional[int] = None
    adg_kg: Optional[Decimal] = None
    total_feed_kg: Optional[Decimal] = None
    fcr: Optional[Decimal] = None

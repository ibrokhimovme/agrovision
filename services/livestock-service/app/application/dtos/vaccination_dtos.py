from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateScheduleRequest(BaseModel):
    farm_id: UUID
    species: str
    vaccine_name: str
    day_of_age: int
    is_mandatory: bool = True
    notes: Optional[str] = None


class VaccinationScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    species: str
    vaccine_name: str
    day_of_age: int
    is_mandatory: bool
    notes: Optional[str] = None


class RecordVaccinationRequest(BaseModel):
    vaccinated_at: Optional[datetime] = None
    quantity_used: Optional[Decimal] = None
    unit: Optional[str] = None
    vaccine_inventory_item_id: Optional[UUID] = None
    notes: Optional[str] = None


class VaccinationRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    batch_id: UUID
    farm_id: UUID
    schedule_id: Optional[UUID] = None
    vaccine_name: str
    status: str
    scheduled_at: Optional[datetime] = None
    vaccinated_at: Optional[datetime] = None
    quantity_used: Optional[Decimal] = None
    unit: Optional[str] = None
    vaccine_inventory_item_id: Optional[UUID] = None
    notes: Optional[str] = None

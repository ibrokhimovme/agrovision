from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RecordMedicationRequest(BaseModel):
    farm_id: UUID
    medicine_name: str
    medicine_inventory_item_id: UUID
    quantity_used: Decimal = Field(gt=0)
    unit: str
    reason: Optional[str] = None
    dosage_notes: Optional[str] = None
    administered_at: Optional[datetime] = None
    notes: Optional[str] = None


class MedicationRecordResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    batch_id: UUID
    farm_id: UUID
    medicine_name: str
    medicine_inventory_item_id: UUID
    quantity_used: Decimal
    unit: str
    reason: Optional[str]
    dosage_notes: Optional[str]
    administered_at: datetime
    notes: Optional[str]

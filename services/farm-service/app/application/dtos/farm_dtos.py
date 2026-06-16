from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.domain.models.farm import FarmType


class CreateFarmRequest(BaseModel):
    name: str
    farm_type: FarmType
    address: Optional[str] = None
    region: Optional[str] = None
    notes: Optional[str] = None


class FarmResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    farm_type: FarmType
    address: Optional[str]
    region: Optional[str]
    owner_user_id: UUID
    is_active: bool
    notes: Optional[str]
    created_at: datetime

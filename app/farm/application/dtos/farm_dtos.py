from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.farm.domain.models.farm import FarmType, SectionType


class CreateFarmRequest(BaseModel):
    name: str
    farm_type: FarmType
    address: Optional[str] = None
    region: Optional[str] = None
    notes: Optional[str] = None


class UpdateFarmRequest(BaseModel):
    name: Optional[str] = None
    farm_type: Optional[FarmType] = None
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


class CreateBuildingRequest(BaseModel):
    name: str
    capacity: Optional[int] = None
    notes: Optional[str] = None


class BuildingResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    farm_id: UUID
    name: str
    capacity: Optional[int]
    notes: Optional[str]
    created_at: datetime


class CreateSectionRequest(BaseModel):
    name: str
    section_type: SectionType
    capacity: Optional[int] = None


class SectionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    building_id: UUID
    farm_id: UUID
    name: str
    section_type: SectionType
    capacity: Optional[int]
    is_active: bool

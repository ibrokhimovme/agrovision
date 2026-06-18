"""
DTOs for supplier registry. EX-11 (Finance Improvements, execution-v2).
"""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateSupplierRequest(BaseModel):
    farm_id: UUID
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None


class SupplierResponse(BaseModel):
    id: UUID
    farm_id: UUID
    name: str
    phone: Optional[str]
    address: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}

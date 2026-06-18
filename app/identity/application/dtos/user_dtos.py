from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class RoleResponse(BaseModel):
    id: UUID
    name: str
    display_name: str

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    phone: Optional[str]
    is_active: bool
    is_superuser: bool
    farm_id: Optional[UUID]
    account_id: Optional[UUID]
    roles: list[RoleResponse]

    model_config = {"from_attributes": True}


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role_name: str
    farm_id: Optional[UUID] = None
    phone: Optional[str] = None


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

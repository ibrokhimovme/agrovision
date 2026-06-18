"""
Roles endpoint. SRS §5.2.
GET /roles/ — list available system roles
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.application.dtos.user_dtos import RoleResponse
from app.identity.domain.models.user import Role
from app.identity.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=APIResponse[list[RoleResponse]])
async def list_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Role).order_by(Role.name))
    roles = result.scalars().all()
    return APIResponse(data=[RoleResponse.model_validate(r) for r in roles])

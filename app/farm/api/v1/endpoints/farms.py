"""
Farm management endpoints. SRS §5.3, SF-02.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.farm.application.dtos.farm_dtos import (
    CreateFarmRequest,
    UpdateFarmRequest,
    FarmResponse,
    CreateBuildingRequest,
    BuildingResponse,
)
from app.farm.application.use_cases.create_farm import CreateFarmUseCase
from app.farm.application.use_cases.get_farm import GetFarmUseCase
from app.farm.application.use_cases.list_farms import ListFarmsUseCase
from app.farm.application.use_cases.update_farm import UpdateFarmUseCase
from app.farm.application.use_cases.delete_farm import DeleteFarmUseCase
from app.farm.application.use_cases.list_buildings import ListBuildingsUseCase
from app.farm.application.use_cases.create_building import CreateBuildingUseCase
from app.farm.infrastructure.database.repositories.farm_repository_impl import SQLAlchemyFarmRepository
from app.farm.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/farms", tags=["Farms"])


def _is_superuser(x_user_roles: str) -> bool:
    """EX-02 (execution-v2): the bypass condition for account scoping must
    be the actual super_admin role, not "account_id is absent" — live
    verification during this phase found a real super-admin account that
    legitimately owns an Account too, so the two are not equivalent."""
    return "super_admin" in [r.strip() for r in x_user_roles.split(",") if r.strip()]


@router.post("/", response_model=APIResponse[FarmResponse], status_code=201)
async def create_farm(
    body: CreateFarmRequest,
    x_user_id: str = Header(..., alias="X-User-Id", description="Owner user ID from api-gateway"),
    x_account_id: str = Header(default="", alias="X-Account-Id", description="Caller's Account ID (EX-02, execution-v2); empty for an account-less caller"),
    db: AsyncSession = Depends(get_db),
):
    owner_user_id = UUID(x_user_id)
    account_id = UUID(x_account_id) if x_account_id else None
    repo = SQLAlchemyFarmRepository(db)
    use_case = CreateFarmUseCase(repo)
    farm = await use_case.execute(body, owner_user_id, account_id)
    return APIResponse(data=FarmResponse.model_validate(farm))


@router.get("/", response_model=PaginatedResponse[FarmResponse])
async def list_farms(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    x_account_id: str = Header(default="", alias="X-Account-Id", description="Caller's Account ID (EX-02, execution-v2); empty for an account-less caller"),
    x_user_roles: str = Header(default="", alias="X-User-Roles"),
    db: AsyncSession = Depends(get_db),
):
    account_id = UUID(x_account_id) if x_account_id else None
    repo = SQLAlchemyFarmRepository(db)
    use_case = ListFarmsUseCase(repo)
    farms, total = await use_case.execute(page, page_size, account_id, _is_superuser(x_user_roles))

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
    return PaginatedResponse(
        data=[FarmResponse.model_validate(f) for f in farms],
        pagination=pagination,
    )


@router.get("/{farm_id}", response_model=APIResponse[FarmResponse])
async def get_farm(
    farm_id: UUID,
    x_account_id: str = Header(default="", alias="X-Account-Id", description="Caller's Account ID (EX-02, execution-v2); empty for an account-less caller"),
    x_user_roles: str = Header(default="", alias="X-User-Roles"),
    db: AsyncSession = Depends(get_db),
):
    account_id = UUID(x_account_id) if x_account_id else None
    repo = SQLAlchemyFarmRepository(db)
    use_case = GetFarmUseCase(repo)
    farm = await use_case.execute(farm_id, account_id, _is_superuser(x_user_roles))
    return APIResponse(data=FarmResponse.model_validate(farm))


@router.patch("/{farm_id}", response_model=APIResponse[FarmResponse])
async def update_farm(
    farm_id: UUID,
    body: UpdateFarmRequest,
    x_account_id: str = Header(default="", alias="X-Account-Id", description="Caller's Account ID (EX-02, execution-v2); empty for an account-less caller"),
    x_user_roles: str = Header(default="", alias="X-User-Roles"),
    db: AsyncSession = Depends(get_db),
):
    account_id = UUID(x_account_id) if x_account_id else None
    repo = SQLAlchemyFarmRepository(db)
    use_case = UpdateFarmUseCase(repo)
    farm = await use_case.execute(farm_id, body, account_id, _is_superuser(x_user_roles))
    return APIResponse(data=FarmResponse.model_validate(farm))


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(
    farm_id: UUID,
    x_account_id: str = Header(default="", alias="X-Account-Id", description="Caller's Account ID (EX-02, execution-v2); empty for an account-less caller"),
    x_user_roles: str = Header(default="", alias="X-User-Roles"),
    db: AsyncSession = Depends(get_db),
):
    account_id = UUID(x_account_id) if x_account_id else None
    repo = SQLAlchemyFarmRepository(db)
    use_case = DeleteFarmUseCase(repo)
    await use_case.execute(farm_id, account_id, _is_superuser(x_user_roles))


@router.get("/{farm_id}/buildings", response_model=APIResponse[list[BuildingResponse]])
async def list_buildings(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyFarmRepository(db)
    use_case = ListBuildingsUseCase(repo)
    buildings = await use_case.execute(farm_id)
    return APIResponse(data=[BuildingResponse.model_validate(b) for b in buildings])


@router.post("/{farm_id}/buildings", response_model=APIResponse[BuildingResponse], status_code=201)
async def create_building(
    farm_id: UUID,
    body: CreateBuildingRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyFarmRepository(db)
    use_case = CreateBuildingUseCase(repo)
    building = await use_case.execute(farm_id, body)
    return APIResponse(data=BuildingResponse.model_validate(building))

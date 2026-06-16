"""
Farm management endpoints. SRS §5.3, SF-02.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.farm_dtos import CreateFarmRequest, FarmResponse
from app.application.use_cases.create_farm import CreateFarmUseCase
from app.application.use_cases.get_farm import GetFarmUseCase
from app.application.use_cases.list_farms import ListFarmsUseCase
from app.infrastructure.database.repositories.farm_repository_impl import SQLAlchemyFarmRepository
from app.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post("/", response_model=APIResponse[FarmResponse], status_code=201)
async def create_farm(
    body: CreateFarmRequest,
    x_user_id: str = Header(..., alias="X-User-Id", description="Owner user ID from api-gateway"),
    db: AsyncSession = Depends(get_db),
):
    owner_user_id = UUID(x_user_id)
    repo = SQLAlchemyFarmRepository(db)
    use_case = CreateFarmUseCase(repo)
    farm = await use_case.execute(body, owner_user_id)
    return APIResponse(data=FarmResponse.model_validate(farm))


@router.get("/", response_model=PaginatedResponse[FarmResponse])
async def list_farms(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyFarmRepository(db)
    use_case = ListFarmsUseCase(repo)
    farms, total = await use_case.execute(page, page_size)

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
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyFarmRepository(db)
    use_case = GetFarmUseCase(repo)
    farm = await use_case.execute(farm_id)
    return APIResponse(data=FarmResponse.model_validate(farm))

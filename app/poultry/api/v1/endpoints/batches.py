"""
Batch management endpoints. SRS §5.3, SF-03.
"""
from __future__ import annotations

import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.poultry.application.dtos.batch_dtos import (
    BatchResponse,
    CloseBatchRequest,
    CreateBatchRequest,
    UpdateBatchRequest,
)
from app.poultry.application.use_cases.archive_batch import ArchiveBatchUseCase
from app.poultry.application.use_cases.close_batch import CloseBatchUseCase
from app.poultry.application.use_cases.create_batch import CreateBatchUseCase
from app.poultry.application.use_cases.get_batch import GetBatchUseCase
from app.poultry.application.use_cases.list_batches import ListBatchesUseCase
from app.poultry.application.use_cases.unarchive_batch import UnarchiveBatchUseCase
from app.poultry.application.use_cases.update_batch import UpdateBatchUseCase
from app.poultry.domain.models.animal import BatchStatus
from app.poultry.infrastructure.database.repositories.batch_repository_impl import SQLAlchemyBatchRepository
from app.poultry.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/batches", tags=["Batches"])


def _can_archive(x_user_roles: str) -> bool:
    """EX-16 (execution-v2): archive/un-archive authority is restricted to
    "Account Owner" and "Farm Director" per the business owner's policy
    (decision_log.md BMD-018). The RBAC catalog has no roles by those exact
    names (and adding them would be RBAC redesign, out of scope per EX-15) —
    this maps onto the existing `farm_owner` role, the only seeded role at
    that authority level, plus the usual `super_admin` bypass."""
    roles = [r.strip() for r in x_user_roles.split(",") if r.strip()]
    return "super_admin" in roles or "farm_owner" in roles


@router.post("/", response_model=APIResponse[BatchResponse], status_code=201)
async def create_batch(
    body: CreateBatchRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyBatchRepository(db)
    use_case = CreateBatchUseCase(repo)
    batch = await use_case.execute(body)
    return APIResponse(data=BatchResponse.model_validate(batch))


@router.get("/", response_model=PaginatedResponse[BatchResponse])
async def list_batches(
    farm_id: UUID = Query(..., description="Farm ID to filter batches"),
    status: Optional[BatchStatus] = Query(None, description="Filter by batch status"),
    archived: str = Query(
        "false",
        pattern="^(true|false|all)$",
        description="EX-16 (execution-v2): 'false' (default, active views) excludes archived batches; "
                    "'true' returns only archived batches (Archive view); 'all' returns both (Reports).",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    archived_filter: Optional[bool] = {"true": True, "false": False, "all": None}[archived]
    repo = SQLAlchemyBatchRepository(db)
    use_case = ListBatchesUseCase(repo)
    batches, total = await use_case.execute(farm_id, status, page, page_size, archived_filter)

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
        data=[BatchResponse.model_validate(b) for b in batches],
        pagination=pagination,
    )


@router.get("/{batch_id}", response_model=APIResponse[BatchResponse])
async def get_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyBatchRepository(db)
    use_case = GetBatchUseCase(repo)
    batch = await use_case.execute(batch_id)
    return APIResponse(data=BatchResponse.model_validate(batch))


@router.patch("/{batch_id}", response_model=APIResponse[BatchResponse])
async def update_batch(
    batch_id: UUID,
    body: UpdateBatchRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyBatchRepository(db)
    use_case = UpdateBatchUseCase(repo)
    batch = await use_case.execute(batch_id, body)
    return APIResponse(data=BatchResponse.model_validate(batch))


@router.post("/{batch_id}/close", response_model=APIResponse[BatchResponse])
async def close_batch(
    batch_id: UUID,
    body: CloseBatchRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyBatchRepository(db)
    use_case = CloseBatchUseCase(repo)
    batch = await use_case.execute(batch_id, body)
    return APIResponse(data=BatchResponse.model_validate(batch))


@router.post("/{batch_id}/archive", response_model=APIResponse[BatchResponse])
async def archive_batch(
    batch_id: UUID,
    x_user_id: str = Header(default="", alias="X-User-Id"),
    x_user_roles: str = Header(default="", alias="X-User-Roles"),
    db: AsyncSession = Depends(get_db),
):
    if not _can_archive(x_user_roles):
        raise HTTPException(status_code=403, detail="Only the Account Owner or Farm Director may archive a batch")
    repo = SQLAlchemyBatchRepository(db)
    use_case = ArchiveBatchUseCase(repo)
    batch = await use_case.execute(batch_id, UUID(x_user_id))
    return APIResponse(data=BatchResponse.model_validate(batch))


@router.post("/{batch_id}/unarchive", response_model=APIResponse[BatchResponse])
async def unarchive_batch(
    batch_id: UUID,
    x_user_roles: str = Header(default="", alias="X-User-Roles"),
    db: AsyncSession = Depends(get_db),
):
    if not _can_archive(x_user_roles):
        raise HTTPException(status_code=403, detail="Only the Account Owner or Farm Director may unarchive a batch")
    repo = SQLAlchemyBatchRepository(db)
    use_case = UnarchiveBatchUseCase(repo)
    batch = await use_case.execute(batch_id)
    return APIResponse(data=BatchResponse.model_validate(batch))

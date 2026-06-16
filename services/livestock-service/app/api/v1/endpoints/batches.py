"""
Batch management endpoints. SRS §5.3, SF-03.
"""
from __future__ import annotations

import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.batch_dtos import (
    BatchResponse,
    CloseBatchRequest,
    CreateBatchRequest,
    UpdateBatchRequest,
)
from app.application.use_cases.activate_batch import ActivateBatchUseCase
from app.application.use_cases.close_batch import CloseBatchUseCase
from app.application.use_cases.create_batch import CreateBatchUseCase
from app.application.use_cases.get_batch import GetBatchUseCase
from app.application.use_cases.list_batches import ListBatchesUseCase
from app.application.use_cases.update_batch import UpdateBatchUseCase
from app.domain.models.animal import BatchStatus
from app.infrastructure.database.repositories.batch_repository_impl import SQLAlchemyBatchRepository
from app.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/batches", tags=["Batches"])


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
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyBatchRepository(db)
    use_case = ListBatchesUseCase(repo)
    batches, total = await use_case.execute(farm_id, status, page, page_size)

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


@router.post("/{batch_id}/activate", response_model=APIResponse[BatchResponse])
async def activate_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyBatchRepository(db)
    use_case = ActivateBatchUseCase(repo)
    batch = await use_case.execute(batch_id)
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

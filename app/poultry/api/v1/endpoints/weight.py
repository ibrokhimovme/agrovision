"""
Weight sampling endpoints. SRS §5.6 (SF-06), BP-08.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.poultry.application.dtos.weight_dtos import (
    GrowthMetricsResponse,
    RecordWeightRequest,
    WeightSamplingResponse,
)
from app.poultry.application.use_cases.get_weight_history import GetGrowthMetricsUseCase, GetWeightHistoryUseCase
from app.poultry.application.use_cases.record_weight_sampling import RecordWeightSamplingUseCase
from app.poultry.infrastructure.database.repositories.batch_repository_impl import SQLAlchemyBatchRepository
from app.poultry.infrastructure.database.repositories.feed_repository_impl import SQLAlchemyFeedRepository
from app.poultry.infrastructure.database.repositories.weight_repository_impl import SQLAlchemyWeightRepository
from app.poultry.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/batches/{batch_id}/weight/",
    response_model=APIResponse[WeightSamplingResponse],
    status_code=201,
    tags=["Weight"],
)
async def record_weight(
    batch_id: UUID,
    body: RecordWeightRequest,
    db: AsyncSession = Depends(get_db),
):
    batch_repo = SQLAlchemyBatchRepository(db)
    weight_repo = SQLAlchemyWeightRepository(db)
    sampling = await RecordWeightSamplingUseCase(batch_repo, weight_repo).execute(batch_id, body)
    return APIResponse(data=WeightSamplingResponse.model_validate(sampling))


@router.get(
    "/batches/{batch_id}/weight/",
    response_model=PaginatedResponse[WeightSamplingResponse],
    tags=["Weight"],
)
async def list_weight(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    weight_repo = SQLAlchemyWeightRepository(db)
    samplings, total = await GetWeightHistoryUseCase(weight_repo).execute(batch_id, page, page_size)

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
        data=[WeightSamplingResponse.model_validate(s) for s in samplings],
        pagination=pagination,
    )


@router.get(
    "/batches/{batch_id}/weight/metrics",
    response_model=APIResponse[GrowthMetricsResponse],
    tags=["Weight"],
)
async def weight_metrics(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    weight_repo = SQLAlchemyWeightRepository(db)
    feed_repo = SQLAlchemyFeedRepository(db)
    metrics = await GetGrowthMetricsUseCase(weight_repo, feed_repo).execute(batch_id)
    return APIResponse(data=metrics)

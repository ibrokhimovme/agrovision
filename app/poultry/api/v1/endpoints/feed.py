"""
Feed consumption endpoints. SRS §5.10 (SF-10), BP-04.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.poultry.application.dtos.feed_dtos import (
    FeedRecordResponse,
    FeedSummaryResponse,
    RecordFeedRequest,
)
from app.poultry.application.use_cases.get_feed_history import GetBatchFeedHistoryUseCase, GetFeedSummaryUseCase
from app.poultry.application.use_cases.record_feed import RecordFeedConsumptionUseCase
from app.poultry.infrastructure.database.repositories.batch_repository_impl import SQLAlchemyBatchRepository
from app.poultry.infrastructure.database.repositories.feed_repository_impl import SQLAlchemyFeedRepository
from app.poultry.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/batches/{batch_id}/feed",
    response_model=APIResponse[FeedRecordResponse],
    status_code=201,
    tags=["Feed"],
)
async def record_feed(
    batch_id: UUID,
    body: RecordFeedRequest,
    db: AsyncSession = Depends(get_db),
):
    batch_repo = SQLAlchemyBatchRepository(db)
    feed_repo = SQLAlchemyFeedRepository(db)
    use_case = RecordFeedConsumptionUseCase(batch_repo, feed_repo)
    record = await use_case.execute(batch_id, body)
    return APIResponse(data=FeedRecordResponse.model_validate(record))


@router.get(
    "/batches/{batch_id}/feed",
    response_model=PaginatedResponse[FeedRecordResponse],
    tags=["Feed"],
)
async def list_feed(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    feed_repo = SQLAlchemyFeedRepository(db)
    use_case = GetBatchFeedHistoryUseCase(feed_repo)
    records, total = await use_case.execute(batch_id, page, page_size)

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
        data=[FeedRecordResponse.model_validate(r) for r in records],
        pagination=pagination,
    )


@router.get(
    "/batches/{batch_id}/feed/summary",
    response_model=APIResponse[FeedSummaryResponse],
    tags=["Feed"],
)
async def feed_summary(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    batch_repo = SQLAlchemyBatchRepository(db)
    feed_repo = SQLAlchemyFeedRepository(db)
    use_case = GetFeedSummaryUseCase(batch_repo, feed_repo)
    summary = await use_case.execute(batch_id)
    return APIResponse(data=summary)

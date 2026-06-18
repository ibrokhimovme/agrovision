"""
Mortality tracking endpoints. SRS §5.18 (SF-18), BP-15, UC-04.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.poultry.application.dtos.mortality_dtos import (
    MortalityRecordResponse,
    MortalitySummaryResponse,
    RecordMortalityRequest,
)
from app.poultry.application.use_cases.get_mortality_history import (
    GetMortalityHistoryUseCase,
    GetMortalitySummaryUseCase,
)
from app.poultry.application.use_cases.record_mortality import RecordMortalityUseCase
from app.poultry.infrastructure.database.repositories.batch_repository_impl import SQLAlchemyBatchRepository
from app.poultry.infrastructure.database.repositories.mortality_repository_impl import SQLAlchemyMortalityRepository
from app.poultry.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/batches/{batch_id}/mortality",
    response_model=APIResponse[MortalityRecordResponse],
    status_code=201,
    tags=["Mortality"],
)
async def record_mortality(
    batch_id: UUID,
    body: RecordMortalityRequest,
    db: AsyncSession = Depends(get_db),
):
    batch_repo = SQLAlchemyBatchRepository(db)
    mortality_repo = SQLAlchemyMortalityRepository(db)
    use_case = RecordMortalityUseCase(batch_repo, mortality_repo)
    record = await use_case.execute(batch_id, body)
    return APIResponse(data=MortalityRecordResponse.model_validate(record))


@router.get(
    "/batches/{batch_id}/mortality",
    response_model=PaginatedResponse[MortalityRecordResponse],
    tags=["Mortality"],
)
async def list_mortality(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    mortality_repo = SQLAlchemyMortalityRepository(db)
    use_case = GetMortalityHistoryUseCase(mortality_repo)
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
        data=[MortalityRecordResponse.model_validate(r) for r in records],
        pagination=pagination,
    )


@router.get(
    "/batches/{batch_id}/mortality/summary",
    response_model=APIResponse[MortalitySummaryResponse],
    tags=["Mortality"],
)
async def mortality_summary(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    batch_repo = SQLAlchemyBatchRepository(db)
    mortality_repo = SQLAlchemyMortalityRepository(db)
    use_case = GetMortalitySummaryUseCase(batch_repo, mortality_repo)
    summary = await use_case.execute(batch_id)
    return APIResponse(data=summary)

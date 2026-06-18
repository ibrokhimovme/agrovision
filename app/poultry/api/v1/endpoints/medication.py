"""
Medication tracking endpoints. SRS §5.8, §5.9 (MVP simplification). BP-06.
EX-09 (Medication Workflow Alignment, execution-v2): first live write path
for MedicationRecord — previously a dormant model populated only by seed
data (decision_log.md BMD-013).
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.poultry.application.dtos.medication_dtos import (
    MedicationRecordResponse,
    RecordMedicationRequest,
)
from app.poultry.application.use_cases.get_medication_history import GetMedicationHistoryUseCase
from app.poultry.application.use_cases.record_medication import RecordMedicationUseCase
from app.poultry.infrastructure.database.repositories.batch_repository_impl import SQLAlchemyBatchRepository
from app.poultry.infrastructure.database.repositories.medication_repository_impl import (
    SQLAlchemyMedicationRepository,
)
from app.poultry.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/batches/{batch_id}/medication",
    response_model=APIResponse[MedicationRecordResponse],
    status_code=201,
    tags=["Medication"],
)
async def record_medication(
    batch_id: UUID,
    body: RecordMedicationRequest,
    db: AsyncSession = Depends(get_db),
):
    batch_repo = SQLAlchemyBatchRepository(db)
    medication_repo = SQLAlchemyMedicationRepository(db)
    use_case = RecordMedicationUseCase(batch_repo, medication_repo)
    record = await use_case.execute(batch_id, body)
    return APIResponse(data=MedicationRecordResponse.model_validate(record))


@router.get(
    "/batches/{batch_id}/medication",
    response_model=PaginatedResponse[MedicationRecordResponse],
    tags=["Medication"],
)
async def list_medication(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    medication_repo = SQLAlchemyMedicationRepository(db)
    use_case = GetMedicationHistoryUseCase(medication_repo)
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
        data=[MedicationRecordResponse.model_validate(r) for r in records],
        pagination=pagination,
    )

"""
Vaccination schedule and execution endpoints. SRS §5.7 (SF-07), BP-07, UC-03.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.poultry.application.dtos.vaccination_dtos import (
    CreateScheduleRequest,
    RecordVaccinationRequest,
    VaccinationRecordResponse,
    VaccinationScheduleResponse,
)
from app.poultry.application.use_cases.create_vaccination_schedule import CreateVaccinationScheduleUseCase
from app.poultry.application.use_cases.generate_batch_vaccination_plan import GenerateBatchVaccinationPlanUseCase
from app.poultry.application.use_cases.get_batch_vaccinations import GetBatchVaccinationsUseCase
from app.poultry.application.use_cases.record_vaccination import RecordVaccinationUseCase
from app.poultry.infrastructure.database.repositories.batch_repository_impl import SQLAlchemyBatchRepository
from app.poultry.infrastructure.database.repositories.vaccination_repository_impl import (
    SQLAlchemyVaccinationRepository,
    SQLAlchemyVaccinationScheduleRepository,
)
from app.poultry.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/vaccination-schedules/",
    response_model=APIResponse[VaccinationScheduleResponse],
    status_code=201,
    tags=["Vaccination"],
)
async def create_schedule(
    body: CreateScheduleRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyVaccinationScheduleRepository(db)
    schedule = await CreateVaccinationScheduleUseCase(repo).execute(body)
    return APIResponse(data=VaccinationScheduleResponse.model_validate(schedule))


@router.get(
    "/vaccination-schedules/",
    response_model=APIResponse[list[VaccinationScheduleResponse]],
    tags=["Vaccination"],
)
async def list_schedules(
    farm_id: UUID = Query(...),
    species: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    repo = SQLAlchemyVaccinationScheduleRepository(db)
    if species:
        schedules = await repo.list_by_farm_species(farm_id, species)
    else:
        schedules = await repo.list_by_farm(farm_id)
    return APIResponse(data=[VaccinationScheduleResponse.model_validate(s) for s in schedules])


@router.post(
    "/batches/{batch_id}/vaccinations/generate",
    response_model=APIResponse[list[VaccinationRecordResponse]],
    status_code=201,
    tags=["Vaccination"],
)
async def generate_vaccination_plan(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    batch_repo = SQLAlchemyBatchRepository(db)
    schedule_repo = SQLAlchemyVaccinationScheduleRepository(db)
    vacc_repo = SQLAlchemyVaccinationRepository(db)
    use_case = GenerateBatchVaccinationPlanUseCase(batch_repo, schedule_repo, vacc_repo)
    records = await use_case.execute(batch_id)
    return APIResponse(data=[VaccinationRecordResponse.model_validate(r) for r in records])


@router.get(
    "/batches/{batch_id}/vaccinations/",
    response_model=PaginatedResponse[VaccinationRecordResponse],
    tags=["Vaccination"],
)
async def list_batch_vaccinations(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    vacc_repo = SQLAlchemyVaccinationRepository(db)
    use_case = GetBatchVaccinationsUseCase(vacc_repo)
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
        data=[VaccinationRecordResponse.model_validate(r) for r in records],
        pagination=pagination,
    )


@router.patch(
    "/vaccinations/{record_id}/complete",
    response_model=APIResponse[VaccinationRecordResponse],
    tags=["Vaccination"],
)
async def complete_vaccination(
    record_id: UUID,
    body: RecordVaccinationRequest,
    db: AsyncSession = Depends(get_db),
):
    vacc_repo = SQLAlchemyVaccinationRepository(db)
    use_case = RecordVaccinationUseCase(vacc_repo)
    record = await use_case.execute(record_id, body)
    return APIResponse(data=VaccinationRecordResponse.model_validate(record))

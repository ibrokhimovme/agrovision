"""
Unit tests for vaccination use cases. SF-07, BP-07, UC-03.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos.vaccination_dtos import RecordVaccinationRequest
from app.application.use_cases.generate_batch_vaccination_plan import GenerateBatchVaccinationPlanUseCase
from app.application.use_cases.get_batch_vaccinations import GetBatchVaccinationsUseCase
from app.application.use_cases.record_vaccination import RecordVaccinationUseCase
from app.domain.models.animal import Batch, BatchStatus
from app.domain.models.health import VaccinationRecord, VaccinationSchedule, VaccinationStatus
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


def _make_batch(species: str = "broiler") -> Batch:
    b = Batch()
    b.id = uuid4()
    b.farm_id = uuid4()
    b.species = species
    b.status = BatchStatus.QUARANTINE
    b.placement_date = datetime.now(timezone.utc)
    return b


def _make_schedule(farm_id, species: str = "broiler", day: int = 7) -> VaccinationSchedule:
    s = VaccinationSchedule()
    s.id = uuid4()
    s.farm_id = farm_id
    s.species = species
    s.vaccine_name = "Newcastle"
    s.day_of_age = day
    s.is_mandatory = True
    return s


def _make_record(status: VaccinationStatus = VaccinationStatus.PLANNED) -> VaccinationRecord:
    r = VaccinationRecord()
    r.id = uuid4()
    r.batch_id = uuid4()
    r.farm_id = uuid4()
    r.vaccine_name = "Newcastle"
    r.status = status
    r.scheduled_at = datetime.now(timezone.utc) + timedelta(days=3)
    return r


# ── GenerateBatchVaccinationPlanUseCase ───────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_plan_creates_planned_records():
    batch = _make_batch()
    schedule = _make_schedule(batch.farm_id)

    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    schedule_repo = AsyncMock()
    schedule_repo.list_by_farm_species = AsyncMock(return_value=[schedule])
    vacc_repo = AsyncMock()
    vacc_repo.bulk_create_records = AsyncMock(side_effect=lambda r: r)

    result = await GenerateBatchVaccinationPlanUseCase(
        batch_repo, schedule_repo, vacc_repo
    ).execute(batch.id)

    assert len(result) == 1
    assert result[0].status == VaccinationStatus.PLANNED
    assert result[0].vaccine_name == "Newcastle"
    assert result[0].batch_id == batch.id


@pytest.mark.asyncio
async def test_generate_plan_no_schedules_returns_empty():
    batch = _make_batch()
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    schedule_repo = AsyncMock()
    schedule_repo.list_by_farm_species = AsyncMock(return_value=[])
    vacc_repo = AsyncMock()

    result = await GenerateBatchVaccinationPlanUseCase(
        batch_repo, schedule_repo, vacc_repo
    ).execute(batch.id)

    assert result == []
    vacc_repo.bulk_create_records.assert_not_called()


@pytest.mark.asyncio
async def test_generate_plan_batch_not_found_raises():
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(EntityNotFoundError):
        await GenerateBatchVaccinationPlanUseCase(
            batch_repo, AsyncMock(), AsyncMock()
        ).execute(uuid4())


# ── RecordVaccinationUseCase ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_record_vaccination_planned_ok():
    record = _make_record(VaccinationStatus.PLANNED)
    vacc_repo = AsyncMock()
    vacc_repo.get_record_by_id = AsyncMock(return_value=record)
    vacc_repo.update_record = AsyncMock(side_effect=lambda r: r)

    req = RecordVaccinationRequest()
    result = await RecordVaccinationUseCase(vacc_repo).execute(record.id, req)

    assert result.status == VaccinationStatus.COMPLETED
    assert result.vaccinated_at is not None


@pytest.mark.asyncio
async def test_record_vaccination_overdue_ok():
    record = _make_record(VaccinationStatus.OVERDUE)
    vacc_repo = AsyncMock()
    vacc_repo.get_record_by_id = AsyncMock(return_value=record)
    vacc_repo.update_record = AsyncMock(side_effect=lambda r: r)

    result = await RecordVaccinationUseCase(vacc_repo).execute(
        record.id, RecordVaccinationRequest()
    )

    assert result.status == VaccinationStatus.COMPLETED


@pytest.mark.asyncio
async def test_record_vaccination_already_completed_raises():
    record = _make_record(VaccinationStatus.COMPLETED)
    vacc_repo = AsyncMock()
    vacc_repo.get_record_by_id = AsyncMock(return_value=record)

    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await RecordVaccinationUseCase(vacc_repo).execute(
            record.id, RecordVaccinationRequest()
        )

    assert exc_info.value.rule == "VACCINATION_ALREADY_COMPLETED"


@pytest.mark.asyncio
async def test_record_vaccination_not_found_raises():
    vacc_repo = AsyncMock()
    vacc_repo.get_record_by_id = AsyncMock(return_value=None)

    with pytest.raises(EntityNotFoundError):
        await RecordVaccinationUseCase(vacc_repo).execute(
            uuid4(), RecordVaccinationRequest()
        )


# ── GetBatchVaccinationsUseCase ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_vaccinations_marks_overdue():
    record = _make_record(VaccinationStatus.PLANNED)
    record.scheduled_at = datetime.now(timezone.utc) - timedelta(days=1)

    vacc_repo = AsyncMock()
    vacc_repo.list_by_batch = AsyncMock(return_value=([record], 1))
    vacc_repo.update_record = AsyncMock(side_effect=lambda r: r)

    records, total = await GetBatchVaccinationsUseCase(vacc_repo).execute(uuid4(), 1, 50)

    assert records[0].status == VaccinationStatus.OVERDUE
    vacc_repo.update_record.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_vaccinations_future_stays_planned():
    record = _make_record(VaccinationStatus.PLANNED)
    record.scheduled_at = datetime.now(timezone.utc) + timedelta(days=5)

    vacc_repo = AsyncMock()
    vacc_repo.list_by_batch = AsyncMock(return_value=([record], 1))

    records, _ = await GetBatchVaccinationsUseCase(vacc_repo).execute(uuid4(), 1, 50)

    assert records[0].status == VaccinationStatus.PLANNED
    vacc_repo.update_record.assert_not_called()

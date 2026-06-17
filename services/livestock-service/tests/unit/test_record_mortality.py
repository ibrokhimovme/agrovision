"""
Unit tests for RecordMortalityUseCase. SF-18, BP-15, UC-04.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos.mortality_dtos import RecordMortalityRequest
from app.application.use_cases.record_mortality import RecordMortalityUseCase
from app.domain.models.animal import Batch, BatchStatus
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


def _make_batch(status: BatchStatus = BatchStatus.ACTIVE, current_count: int = 1000) -> Batch:
    b = Batch()
    b.id = uuid4()
    b.status = status
    b.initial_count = 1000
    b.current_count = current_count
    b.mortality_records = []
    b.weight_samplings = []
    return b


def _req(quantity: int = 10) -> RecordMortalityRequest:
    return RecordMortalityRequest(
        farm_id=uuid4(),
        quantity=quantity,
        deceased_at=datetime.now(timezone.utc),
        cause_category="disease",
    )


def _repos(batch):
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    batch_repo.update = AsyncMock(side_effect=lambda b: b)
    mortality_repo = AsyncMock()
    mortality_repo.create = AsyncMock(side_effect=lambda r: r)
    return batch_repo, mortality_repo


@pytest.mark.asyncio
async def test_record_mortality_ok_decrements_count():
    batch = _make_batch(current_count=1000)
    batch_repo, mortality_repo = _repos(batch)

    result = await RecordMortalityUseCase(batch_repo, mortality_repo).execute(batch.id, _req(10))

    assert result.quantity == 10
    assert batch.current_count == 990
    batch_repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_record_mortality_exact_remaining_count_ok():
    """Can record all remaining birds as dead."""
    batch = _make_batch(current_count=50)
    batch_repo, mortality_repo = _repos(batch)

    await RecordMortalityUseCase(batch_repo, mortality_repo).execute(batch.id, _req(50))

    assert batch.current_count == 0


@pytest.mark.asyncio
async def test_record_mortality_exceeds_count_raises():
    """Cannot record more deaths than current_count — BP-15."""
    batch = _make_batch(current_count=100)
    batch_repo, mortality_repo = _repos(batch)

    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await RecordMortalityUseCase(batch_repo, mortality_repo).execute(batch.id, _req(101))

    assert exc_info.value.rule == "MORTALITY_EXCEEDS_CURRENT_COUNT"
    batch_repo.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_record_mortality_quarantine_raises():
    batch = _make_batch(BatchStatus.QUARANTINE)
    batch_repo, mortality_repo = _repos(batch)

    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await RecordMortalityUseCase(batch_repo, mortality_repo).execute(batch.id, _req())

    assert exc_info.value.rule == "MORTALITY_BATCH_NOT_ACTIVE"


@pytest.mark.asyncio
async def test_record_mortality_closed_raises():
    batch = _make_batch(BatchStatus.CLOSED)
    batch_repo, mortality_repo = _repos(batch)

    with pytest.raises(BusinessRuleViolationError):
        await RecordMortalityUseCase(batch_repo, mortality_repo).execute(batch.id, _req())


@pytest.mark.asyncio
async def test_record_mortality_not_found_raises():
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=None)
    mortality_repo = AsyncMock()

    with pytest.raises(EntityNotFoundError):
        await RecordMortalityUseCase(batch_repo, mortality_repo).execute(uuid4(), _req())

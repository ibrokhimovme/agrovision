"""
Unit tests for ActivateBatchUseCase — quarantine enforcement (BP-03).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.use_cases.activate_batch import ActivateBatchUseCase
from app.domain.models.animal import Batch, BatchStatus
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


def _make_batch(
    status: BatchStatus = BatchStatus.QUARANTINE,
    quarantine_end_date: Optional[datetime] = None,
) -> Batch:
    b = Batch()
    b.id = uuid4()
    b.status = status
    b.mortality_records = []
    b.weight_samplings = []
    b.initial_count = 1000
    b.current_count = 1000
    b.quarantine_end_date = quarantine_end_date
    return b


def _mock_repo(batch: Optional[Batch]) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=batch)
    repo.update = AsyncMock(side_effect=lambda b: b)
    return repo


@pytest.mark.asyncio
async def test_activate_ok_quarantine_period_elapsed():
    """Batch activates when quarantine_end_date is in the past."""
    past = datetime.now(timezone.utc) - timedelta(days=1)
    batch = _make_batch(quarantine_end_date=past)
    repo = _mock_repo(batch)

    result = await ActivateBatchUseCase(repo).execute(batch.id)

    assert result.status == BatchStatus.ACTIVE


@pytest.mark.asyncio
async def test_activate_ok_no_quarantine_end_date():
    """Batch activates when quarantine_end_date is None (no restriction)."""
    batch = _make_batch(quarantine_end_date=None)
    repo = _mock_repo(batch)

    result = await ActivateBatchUseCase(repo).execute(batch.id)

    assert result.status == BatchStatus.ACTIVE


@pytest.mark.asyncio
async def test_activate_blocked_quarantine_not_elapsed():
    """BP-03: activation blocked when quarantine_end_date is in the future."""
    future = datetime.now(timezone.utc) + timedelta(days=3)
    batch = _make_batch(quarantine_end_date=future)
    repo = _mock_repo(batch)

    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await ActivateBatchUseCase(repo).execute(batch.id)

    assert exc_info.value.rule == "QUARANTINE_MINIMUM_7_DAYS"


@pytest.mark.asyncio
async def test_activate_not_found_raises():
    repo = _mock_repo(None)

    with pytest.raises(EntityNotFoundError):
        await ActivateBatchUseCase(repo).execute(uuid4())

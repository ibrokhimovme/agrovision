"""
Unit tests for RecordFeedConsumptionUseCase. SF-10, BP-04.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos.feed_dtos import RecordFeedRequest
from app.application.use_cases.record_feed import RecordFeedConsumptionUseCase
from app.domain.models.animal import Batch, BatchStatus
from app.domain.models.feed import FeedConsumption
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


def _make_batch(status: BatchStatus = BatchStatus.ACTIVE) -> Batch:
    b = Batch()
    b.id = uuid4()
    b.status = status
    b.mortality_records = []
    b.weight_samplings = []
    b.initial_count = 1000
    b.current_count = 1000
    return b


def _make_request(**kwargs) -> RecordFeedRequest:
    defaults = dict(
        farm_id=uuid4(),
        feed_date=date.today(),
        quantity_kg=Decimal("150.500"),
        water_liters=Decimal("300.0"),
        feed_type="starter",
        age_days=5,
    )
    defaults.update(kwargs)
    return RecordFeedRequest(**defaults)


@pytest.mark.asyncio
async def test_record_feed_ok():
    batch = _make_batch(BatchStatus.ACTIVE)
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    feed_repo = AsyncMock()
    feed_repo.create = AsyncMock(side_effect=lambda r: r)

    result = await RecordFeedConsumptionUseCase(batch_repo, feed_repo).execute(
        batch.id, _make_request()
    )

    assert result.batch_id == batch.id
    assert result.quantity_kg == Decimal("150.500")
    assert result.water_liters == Decimal("300.0")


@pytest.mark.asyncio
async def test_record_feed_quarantine_raises():
    """Cannot record feed for a batch still in quarantine."""
    batch = _make_batch(BatchStatus.QUARANTINE)
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    feed_repo = AsyncMock()

    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await RecordFeedConsumptionUseCase(batch_repo, feed_repo).execute(
            batch.id, _make_request()
        )

    assert exc_info.value.rule == "FEED_BATCH_NOT_ACTIVE"


@pytest.mark.asyncio
async def test_record_feed_closed_raises():
    """Cannot record feed for a closed batch."""
    batch = _make_batch(BatchStatus.CLOSED)
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    feed_repo = AsyncMock()

    with pytest.raises(BusinessRuleViolationError):
        await RecordFeedConsumptionUseCase(batch_repo, feed_repo).execute(
            batch.id, _make_request()
        )


@pytest.mark.asyncio
async def test_record_feed_batch_not_found():
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=None)
    feed_repo = AsyncMock()

    with pytest.raises(EntityNotFoundError):
        await RecordFeedConsumptionUseCase(batch_repo, feed_repo).execute(
            uuid4(), _make_request()
        )

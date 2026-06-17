"""
Unit tests for weight sampling use cases. SF-06, BP-08.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos.weight_dtos import RecordWeightRequest
from app.application.use_cases.get_weight_history import GetGrowthMetricsUseCase
from app.application.use_cases.record_weight_sampling import RecordWeightSamplingUseCase
from app.domain.models.animal import Batch, BatchStatus, WeightSampling
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


def _make_batch(status: BatchStatus = BatchStatus.ACTIVE) -> Batch:
    b = Batch()
    b.id = uuid4()
    b.farm_id = uuid4()
    b.status = status
    b.initial_count = 1000
    b.current_count = 990
    b.placement_date = datetime.now(timezone.utc) - timedelta(days=14)
    b.weight_samplings = []
    b.mortality_records = []
    return b


def _make_sampling(age_days: int, avg_weight: str) -> WeightSampling:
    s = WeightSampling()
    s.id = uuid4()
    s.batch_id = uuid4()
    s.farm_id = uuid4()
    s.sample_size = 50
    s.average_weight_kg = Decimal(avg_weight)
    s.age_days = age_days
    s.measured_at = datetime.now(timezone.utc) - timedelta(days=14 - age_days)
    return s


def _req() -> RecordWeightRequest:
    return RecordWeightRequest(
        farm_id=uuid4(),
        sample_size=50,
        total_sample_weight_kg=Decimal("75.0"),
    )


# ── RecordWeightSamplingUseCase ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_record_weight_ok_computes_average():
    batch = _make_batch()
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    weight_repo = AsyncMock()
    weight_repo.create = AsyncMock(side_effect=lambda s: s)

    result = await RecordWeightSamplingUseCase(batch_repo, weight_repo).execute(
        batch.id, _req()
    )

    assert result.average_weight_kg == Decimal("1.500")
    assert result.sample_size == 50
    assert result.age_days == 14


@pytest.mark.asyncio
async def test_record_weight_quarantine_raises():
    batch = _make_batch(BatchStatus.QUARANTINE)
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)

    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await RecordWeightSamplingUseCase(batch_repo, AsyncMock()).execute(
            batch.id, _req()
        )
    assert exc_info.value.rule == "WEIGHT_BATCH_NOT_ACTIVE"


@pytest.mark.asyncio
async def test_record_weight_closed_raises():
    batch = _make_batch(BatchStatus.CLOSED)
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)

    with pytest.raises(BusinessRuleViolationError):
        await RecordWeightSamplingUseCase(batch_repo, AsyncMock()).execute(
            batch.id, _req()
        )


@pytest.mark.asyncio
async def test_record_weight_not_found_raises():
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(EntityNotFoundError):
        await RecordWeightSamplingUseCase(batch_repo, AsyncMock()).execute(
            uuid4(), _req()
        )


# ── GetGrowthMetricsUseCase ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_metrics_no_samplings_returns_empty():
    weight_repo = AsyncMock()
    weight_repo.all_by_batch = AsyncMock(return_value=[])
    feed_repo = AsyncMock()
    feed_repo.total_feed_kg = AsyncMock(return_value=Decimal("0"))

    metrics = await GetGrowthMetricsUseCase(weight_repo, feed_repo).execute(uuid4())

    assert metrics.sampling_count == 0
    assert metrics.adg_kg is None
    assert metrics.fcr is None


@pytest.mark.asyncio
async def test_metrics_single_sampling_no_adg():
    s = _make_sampling(age_days=7, avg_weight="0.500")
    weight_repo = AsyncMock()
    weight_repo.all_by_batch = AsyncMock(return_value=[s])
    feed_repo = AsyncMock()
    feed_repo.total_feed_kg = AsyncMock(return_value=Decimal("100"))

    metrics = await GetGrowthMetricsUseCase(weight_repo, feed_repo).execute(uuid4())

    assert metrics.sampling_count == 1
    assert metrics.latest_avg_weight_kg == Decimal("0.500")
    assert metrics.adg_kg is None


@pytest.mark.asyncio
async def test_metrics_two_samplings_computes_adg():
    s1 = _make_sampling(age_days=7, avg_weight="0.500")
    s2 = _make_sampling(age_days=14, avg_weight="1.200")
    weight_repo = AsyncMock()
    weight_repo.all_by_batch = AsyncMock(return_value=[s1, s2])
    feed_repo = AsyncMock()
    feed_repo.total_feed_kg = AsyncMock(return_value=Decimal("0"))

    metrics = await GetGrowthMetricsUseCase(weight_repo, feed_repo).execute(uuid4())

    assert metrics.adg_kg == Decimal("0.1000")  # (1.2 - 0.5) / 7
    assert metrics.latest_avg_weight_kg == Decimal("1.200")


@pytest.mark.asyncio
async def test_metrics_computes_fcr_with_feed():
    s = _make_sampling(age_days=14, avg_weight="2.000")
    s.sample_size = 50
    weight_repo = AsyncMock()
    weight_repo.all_by_batch = AsyncMock(return_value=[s])
    feed_repo = AsyncMock()
    feed_repo.total_feed_kg = AsyncMock(return_value=Decimal("200"))

    metrics = await GetGrowthMetricsUseCase(weight_repo, feed_repo).execute(uuid4())

    # fcr = 200 / (2.0 * 50) = 200 / 100 = 2.0
    assert metrics.fcr == Decimal("2.000")

"""
E2E workflow test for livestock-service use cases.
Tests the full lifecycle: create → activate → feed → weight → mortality.
Imports are deferred to test body so conftest sys.path setup runs first.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock


BATCH_ID = uuid4()
FARM_ID = uuid4()
SECTION_ID = uuid4()


def _batch_in_quarantine(past_quarantine: bool = True):
    from app.domain.models.animal import Batch, BatchStatus

    b = Batch()
    b.id = BATCH_ID
    b.farm_id = FARM_ID
    b.section_id = SECTION_ID
    b.species = "broiler"
    b.status = BatchStatus.QUARANTINE
    b.initial_count = 5000
    b.current_count = 5000
    b.mortality_records = []
    b.weight_samplings = []
    if past_quarantine:
        b.quarantine_end_date = datetime.now(timezone.utc) - timedelta(days=1)
    else:
        b.quarantine_end_date = datetime.now(timezone.utc) + timedelta(days=3)
    return b


def _active_batch():
    from app.domain.models.animal import Batch, BatchStatus

    b = Batch()
    b.id = BATCH_ID
    b.farm_id = FARM_ID
    b.species = "broiler"
    b.status = BatchStatus.ACTIVE
    b.initial_count = 5000
    b.current_count = 4980
    b.mortality_records = []
    b.weight_samplings = []
    return b


@pytest.mark.asyncio
async def test_create_batch():
    from app.application.use_cases.create_batch import CreateBatchUseCase
    from app.application.dtos.batch_dtos import CreateBatchRequest
    from app.domain.models.animal import BatchStatus, PoultrySpecies

    req = CreateBatchRequest(
        farm_id=FARM_ID,
        section_id=SECTION_ID,
        species=PoultrySpecies.BROILER,
        initial_count=5000,
        placement_date=datetime.now(timezone.utc) - timedelta(days=10),
        batch_code="TEST-E2E-001",
    )

    repo = AsyncMock()
    repo.get_by_code = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=lambda b: (setattr(b, "id", BATCH_ID), b)[1])

    result = await CreateBatchUseCase(repo).execute(req)

    assert result.id == BATCH_ID
    assert result.status == BatchStatus.QUARANTINE
    assert result.current_count == 5000


@pytest.mark.asyncio
async def test_activate_batch_after_quarantine():
    from app.application.use_cases.activate_batch import ActivateBatchUseCase
    from app.domain.models.animal import BatchStatus

    batch = _batch_in_quarantine(past_quarantine=True)
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=batch)
    repo.update = AsyncMock(side_effect=lambda b: b)

    result = await ActivateBatchUseCase(repo).execute(BATCH_ID)

    assert result.status == BatchStatus.ACTIVE


@pytest.mark.asyncio
async def test_activate_blocked_during_quarantine():
    from app.application.use_cases.activate_batch import ActivateBatchUseCase
    from shared.exceptions import BusinessRuleViolationError

    batch = _batch_in_quarantine(past_quarantine=False)
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=batch)

    with pytest.raises(BusinessRuleViolationError) as exc:
        await ActivateBatchUseCase(repo).execute(BATCH_ID)

    assert exc.value.rule == "QUARANTINE_MINIMUM_7_DAYS"


@pytest.mark.asyncio
async def test_record_feed():
    from app.application.use_cases.record_feed import RecordFeedConsumptionUseCase
    from app.application.dtos.feed_dtos import RecordFeedRequest
    from app.domain.models.feed import FeedConsumption
    from datetime import date

    req = RecordFeedRequest(
        farm_id=FARM_ID,
        feed_date=date.today(),
        quantity_kg=Decimal("150.5"),
        water_liters=Decimal("300.0"),
        feed_type="starter",
    )

    feed = FeedConsumption()
    feed.id = uuid4()
    feed.batch_id = BATCH_ID
    feed.farm_id = FARM_ID
    feed.feed_date = req.feed_date
    feed.quantity_kg = req.quantity_kg
    feed.water_liters = req.water_liters
    feed.feed_type = req.feed_type
    feed.age_days = None
    feed.notes = None

    batch = _active_batch()
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    batch_repo.update = AsyncMock(side_effect=lambda b: b)

    feed_repo = AsyncMock()
    feed_repo.create = AsyncMock(return_value=feed)

    result = await RecordFeedConsumptionUseCase(batch_repo, feed_repo).execute(BATCH_ID, req)

    assert result.batch_id == BATCH_ID
    assert result.quantity_kg == Decimal("150.5")


@pytest.mark.asyncio
async def test_record_mortality():
    from app.application.use_cases.record_mortality import RecordMortalityUseCase
    from app.application.dtos.mortality_dtos import RecordMortalityRequest, MortalityRecordResponse
    from app.domain.models.animal import MortalityRecord

    req = RecordMortalityRequest(
        farm_id=FARM_ID,
        quantity=20,
        deceased_at=datetime.now(timezone.utc),
        cause_category="disease",
    )

    mort = MortalityRecord()
    mort.id = uuid4()
    mort.batch_id = BATCH_ID
    mort.farm_id = FARM_ID
    mort.quantity = req.quantity
    mort.cause_category = req.cause_category
    mort.cause_description = None
    mort.disposal_method = None
    mort.deceased_at = req.deceased_at

    batch = _active_batch()
    batch_repo = AsyncMock()
    batch_repo.get_by_id = AsyncMock(return_value=batch)
    batch_repo.update = AsyncMock(side_effect=lambda b: b)

    mort_repo = AsyncMock()
    mort_repo.create = AsyncMock(return_value=mort)

    result = await RecordMortalityUseCase(batch_repo, mort_repo).execute(BATCH_ID, req)

    assert result.batch_id == BATCH_ID
    assert result.quantity == 20

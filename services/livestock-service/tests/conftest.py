"""
Shared pytest fixtures for livestock-service.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.domain.models.animal import Batch, BatchStatus, PoultrySpecies


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


def make_batch(
    farm_id=None,
    section_id=None,
    species: PoultrySpecies = PoultrySpecies.BROILER,
    status: BatchStatus = BatchStatus.QUARANTINE,
    initial_count: int = 1000,
    current_count: int = 1000,
    batch_code: str | None = None,
) -> Batch:
    batch = Batch()
    batch.id = uuid4()
    batch.farm_id = farm_id or uuid4()
    batch.section_id = section_id or uuid4()
    batch.species = species
    batch.status = status
    batch.batch_code = batch_code
    batch.initial_count = initial_count
    batch.current_count = current_count
    batch.placement_date = datetime.now(timezone.utc)
    batch.quarantine_end_date = None
    batch.closed_at = None
    batch.close_reason = None
    batch.supplier_name = None
    batch.chick_price_per_head = None
    batch.notes = None
    batch.mortality_records = []
    batch.weight_samplings = []
    batch.created_at = datetime.now(timezone.utc)
    batch.updated_at = datetime.now(timezone.utc)
    return batch


@pytest.fixture
def mock_batch_repo():
    return AsyncMock()

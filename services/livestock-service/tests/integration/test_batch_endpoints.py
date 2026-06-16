"""
Integration tests for batch endpoints.
Mocks SQLAlchemyBatchRepository to avoid needing a real DB.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.domain.models.animal import Batch, BatchStatus, BatchCloseReason, PoultrySpecies
from shared.exceptions import DuplicateEntityError, EntityNotFoundError, InvalidStateTransitionError
from tests.conftest import make_batch

FARM_ID = str(uuid4())
SECTION_ID = str(uuid4())


def _batch_create_payload(**overrides) -> dict:
    return {
        "farm_id": FARM_ID,
        "section_id": SECTION_ID,
        "species": "broiler",
        "initial_count": 500,
        "placement_date": datetime.now(timezone.utc).isoformat(),
        **overrides,
    }


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_create_batch_success(client: AsyncClient):
    batch = make_batch(batch_code="B-001")
    with patch(
        "app.api.v1.endpoints.batches.SQLAlchemyBatchRepository"
    ) as MockRepo:
        instance = AsyncMock()
        MockRepo.return_value = instance
        instance.get_by_code.return_value = None
        instance.create.return_value = batch

        resp = await client.post(
            "/api/v1/batches/",
            json=_batch_create_payload(batch_code="B-001"),
        )

    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["batch_code"] == "B-001"


@pytest.mark.asyncio
async def test_create_batch_duplicate_code(client: AsyncClient):
    existing = make_batch(batch_code="B-DUP")
    with patch(
        "app.api.v1.endpoints.batches.SQLAlchemyBatchRepository"
    ) as MockRepo:
        instance = AsyncMock()
        MockRepo.return_value = instance
        instance.get_by_code.return_value = existing

        resp = await client.post(
            "/api/v1/batches/",
            json=_batch_create_payload(batch_code="B-DUP"),
        )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_batches(client: AsyncClient):
    batches = [make_batch(), make_batch()]
    with patch(
        "app.api.v1.endpoints.batches.SQLAlchemyBatchRepository"
    ) as MockRepo:
        instance = AsyncMock()
        MockRepo.return_value = instance
        instance.list_by_farm.return_value = (batches, 2)

        resp = await client.get(f"/api/v1/batches/?farm_id={FARM_ID}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["pagination"]["total_items"] == 2


@pytest.mark.asyncio
async def test_get_batch_found(client: AsyncClient):
    batch = make_batch()
    with patch(
        "app.api.v1.endpoints.batches.SQLAlchemyBatchRepository"
    ) as MockRepo:
        instance = AsyncMock()
        MockRepo.return_value = instance
        instance.get_by_id.return_value = batch

        resp = await client.get(f"/api/v1/batches/{batch.id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["id"] == str(batch.id)


@pytest.mark.asyncio
async def test_get_batch_not_found(client: AsyncClient):
    batch_id = uuid4()
    with patch(
        "app.api.v1.endpoints.batches.SQLAlchemyBatchRepository"
    ) as MockRepo:
        instance = AsyncMock()
        MockRepo.return_value = instance
        instance.get_by_id.return_value = None

        resp = await client.get(f"/api/v1/batches/{batch_id}")

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_activate_batch(client: AsyncClient):
    batch = make_batch(status=BatchStatus.QUARANTINE)
    activated = make_batch(status=BatchStatus.ACTIVE)
    activated.id = batch.id

    with patch(
        "app.api.v1.endpoints.batches.SQLAlchemyBatchRepository"
    ) as MockRepo:
        instance = AsyncMock()
        MockRepo.return_value = instance
        instance.get_by_id.return_value = batch
        instance.update.return_value = activated

        resp = await client.post(f"/api/v1/batches/{batch.id}/activate")

    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_close_batch(client: AsyncClient):
    batch = make_batch(status=BatchStatus.ACTIVE)
    closed = make_batch(status=BatchStatus.CLOSED)
    closed.id = batch.id
    closed.closed_at = datetime.now(timezone.utc)
    closed.close_reason = BatchCloseReason.SALE

    with patch(
        "app.api.v1.endpoints.batches.SQLAlchemyBatchRepository"
    ) as MockRepo:
        instance = AsyncMock()
        MockRepo.return_value = instance
        instance.get_by_id.return_value = batch
        instance.update.return_value = closed

        resp = await client.post(
            f"/api/v1/batches/{batch.id}/close",
            json={"close_reason": "sale"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["status"] == "closed"


@pytest.mark.asyncio
async def test_invalid_close_from_quarantine(client: AsyncClient):
    """Closing a quarantine batch directly is invalid (must activate first)."""
    batch = make_batch(status=BatchStatus.QUARANTINE)

    with patch(
        "app.api.v1.endpoints.batches.SQLAlchemyBatchRepository"
    ) as MockRepo:
        instance = AsyncMock()
        MockRepo.return_value = instance
        instance.get_by_id.return_value = batch
        # update is NOT called since transition raises

        resp = await client.post(
            f"/api/v1/batches/{batch.id}/close",
            json={"close_reason": "sale"},
        )

    assert resp.status_code == 409

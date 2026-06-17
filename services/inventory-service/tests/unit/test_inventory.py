"""
Unit tests for inventory use cases. BP-09, SF-12.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos.inventory_dtos import (
    CreateStockItemRequest,
    CreateWarehouseRequest,
    DispatchStockRequest,
    ReceiveStockRequest,
)
from app.application.use_cases.create_stock_item import CreateStockItemUseCase
from app.application.use_cases.create_warehouse import CreateWarehouseUseCase
from app.application.use_cases.dispatch_stock import DispatchStockUseCase
from app.application.use_cases.receive_stock import ReceiveStockUseCase
from app.domain.models.inventory import ItemType, StockBatch, StockItem, Warehouse
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


def _make_warehouse() -> Warehouse:
    w = Warehouse()
    w.id = uuid4()
    w.farm_id = uuid4()
    w.name = "Test Ombor"
    w.is_active = True
    w.created_at = datetime.now(timezone.utc)
    w.updated_at = datetime.now(timezone.utc)
    return w


def _make_stock_item(qty: str = "100") -> StockItem:
    item = StockItem()
    item.id = uuid4()
    item.warehouse_id = uuid4()
    item.name = "Yem"
    item.item_type = ItemType.FEED
    item.unit = "kg"
    item.current_quantity = Decimal(qty)
    item.minimum_quantity = Decimal("10")
    item.is_active = True
    item.created_at = datetime.now(timezone.utc)
    item.updated_at = datetime.now(timezone.utc)
    return item


def _make_batch(received_days_ago: int, qty: str, expiry_days: int | None = None) -> StockBatch:
    b = StockBatch()
    b.id = uuid4()
    b.stock_item_id = uuid4()
    b.quantity = Decimal(qty)
    b.remaining_quantity = Decimal(qty)
    b.received_at = datetime.now(timezone.utc) - timedelta(days=received_days_ago)
    if expiry_days is not None:
        b.expiry_date = datetime.now(timezone.utc) + timedelta(days=expiry_days)
    else:
        b.expiry_date = None
    b.created_at = datetime.now(timezone.utc)
    b.updated_at = datetime.now(timezone.utc)
    return b


# ── CreateWarehouseUseCase ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_warehouse_ok():
    warehouse_repo = AsyncMock()
    created = _make_warehouse()
    warehouse_repo.create = AsyncMock(side_effect=lambda w: w)

    req = CreateWarehouseRequest(farm_id=uuid4(), name="Asosiy ombor")
    result = await CreateWarehouseUseCase(warehouse_repo).execute(req)

    assert result.name == "Asosiy ombor"
    warehouse_repo.create.assert_called_once()


# ── CreateStockItemUseCase ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_stock_item_ok():
    warehouse_repo = AsyncMock()
    warehouse_repo.get_by_id = AsyncMock(return_value=_make_warehouse())
    stock_item_repo = AsyncMock()
    stock_item_repo.create = AsyncMock(side_effect=lambda i: i)

    req = CreateStockItemRequest(
        warehouse_id=uuid4(),
        name="Yem A",
        item_type=ItemType.FEED,
        unit="kg",
    )
    result = await CreateStockItemUseCase(warehouse_repo, stock_item_repo).execute(req)

    assert result.name == "Yem A"
    assert result.current_quantity == Decimal("0")


@pytest.mark.asyncio
async def test_create_stock_item_warehouse_not_found():
    warehouse_repo = AsyncMock()
    warehouse_repo.get_by_id = AsyncMock(return_value=None)

    req = CreateStockItemRequest(
        warehouse_id=uuid4(),
        name="Yem B",
        item_type=ItemType.FEED,
        unit="kg",
    )
    with pytest.raises(EntityNotFoundError):
        await CreateStockItemUseCase(warehouse_repo, AsyncMock()).execute(req)


# ── ReceiveStockUseCase ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_receive_stock_updates_quantity():
    item = _make_stock_item("50")
    stock_item_repo = AsyncMock()
    stock_item_repo.get_by_id = AsyncMock(return_value=item)
    stock_item_repo.update = AsyncMock(side_effect=lambda i: i)
    stock_batch_repo = AsyncMock()
    stock_batch_repo.create = AsyncMock(side_effect=lambda b: b)
    movement_repo = AsyncMock()
    movement_repo.create = AsyncMock(side_effect=lambda m: m)

    req = ReceiveStockRequest(quantity=Decimal("30"), unit_cost=Decimal("5.00"))
    result = await ReceiveStockUseCase(stock_item_repo, stock_batch_repo, movement_repo).execute(item.id, req)

    assert result.quantity == Decimal("30")
    assert item.current_quantity == Decimal("80")


@pytest.mark.asyncio
async def test_receive_stock_item_not_found():
    stock_item_repo = AsyncMock()
    stock_item_repo.get_by_id = AsyncMock(return_value=None)

    req = ReceiveStockRequest(quantity=Decimal("10"))
    with pytest.raises(EntityNotFoundError):
        await ReceiveStockUseCase(stock_item_repo, AsyncMock(), AsyncMock()).execute(uuid4(), req)


# ── DispatchStockUseCase ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dispatch_fifo_depletes_oldest_first():
    item = _make_stock_item("100")
    batch_old = _make_batch(received_days_ago=10, qty="60")
    batch_new = _make_batch(received_days_ago=2, qty="40")
    batch_old.stock_item_id = item.id
    batch_new.stock_item_id = item.id

    stock_item_repo = AsyncMock()
    stock_item_repo.get_by_id = AsyncMock(return_value=item)
    stock_item_repo.update = AsyncMock(side_effect=lambda i: i)
    stock_batch_repo = AsyncMock()
    stock_batch_repo.list_available_fifo = AsyncMock(return_value=[batch_old, batch_new])
    stock_batch_repo.update = AsyncMock(side_effect=lambda b: b)
    movement_repo = AsyncMock()
    movement_repo.create = AsyncMock(side_effect=lambda m: m)

    req = DispatchStockRequest(quantity=Decimal("70"))
    result = await DispatchStockUseCase(stock_item_repo, stock_batch_repo, movement_repo).execute(item.id, req)

    assert result.dispatched_quantity == Decimal("70")
    assert batch_old.remaining_quantity == Decimal("0")
    assert batch_new.remaining_quantity == Decimal("30")
    assert item.current_quantity == Decimal("30")


@pytest.mark.asyncio
async def test_dispatch_insufficient_stock_raises():
    item = _make_stock_item("10")

    stock_item_repo = AsyncMock()
    stock_item_repo.get_by_id = AsyncMock(return_value=item)

    req = DispatchStockRequest(quantity=Decimal("50"))
    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await DispatchStockUseCase(stock_item_repo, AsyncMock(), AsyncMock()).execute(item.id, req)
    assert exc_info.value.rule == "INSUFFICIENT_STOCK"


@pytest.mark.asyncio
async def test_dispatch_fefo_uses_nearest_expiry():
    item = _make_stock_item("100")
    batch_far = _make_batch(received_days_ago=5, qty="50", expiry_days=30)
    batch_near = _make_batch(received_days_ago=3, qty="50", expiry_days=7)
    batch_far.stock_item_id = item.id
    batch_near.stock_item_id = item.id

    stock_item_repo = AsyncMock()
    stock_item_repo.get_by_id = AsyncMock(return_value=item)
    stock_item_repo.update = AsyncMock(side_effect=lambda i: i)
    stock_batch_repo = AsyncMock()
    # FEFO ordering: batch_near first (closer expiry)
    stock_batch_repo.list_available_fefo = AsyncMock(return_value=[batch_near, batch_far])
    stock_batch_repo.update = AsyncMock(side_effect=lambda b: b)
    movement_repo = AsyncMock()
    movement_repo.create = AsyncMock(side_effect=lambda m: m)

    req = DispatchStockRequest(quantity=Decimal("30"), use_fefo=True)
    result = await DispatchStockUseCase(stock_item_repo, stock_batch_repo, movement_repo).execute(item.id, req)

    assert result.dispatched_quantity == Decimal("30")
    assert batch_near.remaining_quantity == Decimal("20")
    assert batch_far.remaining_quantity == Decimal("50")

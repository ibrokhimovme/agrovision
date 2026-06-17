"""
SQLAlchemy implementations of inventory repositories. BP-09, SF-12.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, asc, select, func, nullslast, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.inventory import StockBatch, StockItem, StockMovement, Warehouse
from app.domain.repositories.stock_repository import (
    AbstractStockBatchRepository,
    AbstractStockItemRepository,
    AbstractStockMovementRepository,
    AbstractWarehouseRepository,
)


class SQLAlchemyWarehouseRepository(AbstractWarehouseRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, warehouse: Warehouse) -> Warehouse:
        self._session.add(warehouse)
        await self._session.commit()
        await self._session.refresh(warehouse)
        return warehouse

    async def get_by_id(self, warehouse_id: UUID) -> Optional[Warehouse]:
        result = await self._session.execute(
            select(Warehouse).where(Warehouse.id == warehouse_id)
        )
        return result.scalar_one_or_none()

    async def list_by_farm(self, farm_id: UUID) -> list[Warehouse]:
        result = await self._session.execute(
            select(Warehouse)
            .where(Warehouse.farm_id == farm_id, Warehouse.is_active == True)
            .order_by(asc(Warehouse.name))
        )
        return list(result.scalars().all())

    async def update(self, warehouse: Warehouse) -> Warehouse:
        await self._session.commit()
        await self._session.refresh(warehouse)
        return warehouse


class SQLAlchemyStockItemRepository(AbstractStockItemRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, item: StockItem) -> StockItem:
        self._session.add(item)
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def get_by_id(self, item_id: UUID) -> Optional[StockItem]:
        result = await self._session.execute(
            select(StockItem).where(StockItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def list_by_warehouse(
        self, warehouse_id: UUID, page: int, page_size: int
    ) -> tuple[list[StockItem], int]:
        count_result = await self._session.execute(
            select(func.count()).where(
                StockItem.warehouse_id == warehouse_id,
                StockItem.is_active == True,
            )
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        rows = await self._session.execute(
            select(StockItem)
            .where(StockItem.warehouse_id == warehouse_id, StockItem.is_active == True)
            .order_by(asc(StockItem.name))
            .offset(offset)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

    async def list_by_farm(
        self, farm_id: UUID, page: int, page_size: int
    ) -> tuple[list[StockItem], int]:
        count_result = await self._session.execute(
            select(func.count())
            .select_from(StockItem)
            .join(Warehouse, StockItem.warehouse_id == Warehouse.id)
            .where(Warehouse.farm_id == farm_id, StockItem.is_active == True)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        rows = await self._session.execute(
            select(StockItem)
            .join(Warehouse, StockItem.warehouse_id == Warehouse.id)
            .where(Warehouse.farm_id == farm_id, StockItem.is_active == True)
            .order_by(asc(StockItem.name))
            .offset(offset)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

    async def update(self, item: StockItem) -> StockItem:
        await self._session.commit()
        await self._session.refresh(item)
        return item

    async def list_below_minimum(self, farm_id: UUID) -> list[StockItem]:
        result = await self._session.execute(
            select(StockItem)
            .join(Warehouse, StockItem.warehouse_id == Warehouse.id)
            .where(
                Warehouse.farm_id == farm_id,
                StockItem.is_active == True,
                StockItem.current_quantity < StockItem.minimum_quantity,
            )
            .order_by(asc(StockItem.name))
        )
        return list(result.scalars().all())


class SQLAlchemyStockBatchRepository(AbstractStockBatchRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, batch: StockBatch) -> StockBatch:
        self._session.add(batch)
        await self._session.commit()
        await self._session.refresh(batch)
        return batch

    async def get_by_id(self, batch_id: UUID) -> Optional[StockBatch]:
        result = await self._session.execute(
            select(StockBatch).where(StockBatch.id == batch_id)
        )
        return result.scalar_one_or_none()

    async def list_available_fifo(self, stock_item_id: UUID) -> list[StockBatch]:
        """FIFO: oldest received_at first, non-zero remaining, non-expired."""
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(StockBatch)
            .where(
                StockBatch.stock_item_id == stock_item_id,
                StockBatch.remaining_quantity > 0,
                (StockBatch.expiry_date == None) | (StockBatch.expiry_date > now),
            )
            .order_by(asc(StockBatch.received_at))
        )
        return list(result.scalars().all())

    async def list_available_fefo(self, stock_item_id: UUID) -> list[StockBatch]:
        """FEFO: nearest expiry_date first (nulls last), non-zero remaining, non-expired."""
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(StockBatch)
            .where(
                StockBatch.stock_item_id == stock_item_id,
                StockBatch.remaining_quantity > 0,
                (StockBatch.expiry_date == None) | (StockBatch.expiry_date > now),
            )
            .order_by(nullslast(asc(StockBatch.expiry_date)))
        )
        return list(result.scalars().all())

    async def update(self, batch: StockBatch) -> StockBatch:
        await self._session.commit()
        await self._session.refresh(batch)
        return batch

    async def list_expiring_soon(self, days: int) -> list[StockBatch]:
        now = datetime.now(timezone.utc)
        threshold = now + timedelta(days=days)
        result = await self._session.execute(
            select(StockBatch)
            .where(
                StockBatch.remaining_quantity > 0,
                StockBatch.expiry_date != None,
                StockBatch.expiry_date > now,
                StockBatch.expiry_date <= threshold,
            )
            .order_by(asc(StockBatch.expiry_date))
        )
        return list(result.scalars().all())


class SQLAlchemyStockMovementRepository(AbstractStockMovementRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, movement: StockMovement) -> StockMovement:
        self._session.add(movement)
        await self._session.commit()
        await self._session.refresh(movement)
        return movement

    async def list_by_item(
        self, stock_item_id: UUID, page: int, page_size: int
    ) -> tuple[list[StockMovement], int]:
        count_result = await self._session.execute(
            select(func.count()).where(StockMovement.stock_item_id == stock_item_id)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        rows = await self._session.execute(
            select(StockMovement)
            .where(StockMovement.stock_item_id == stock_item_id)
            .order_by(desc(StockMovement.moved_at))
            .offset(offset)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

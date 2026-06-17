from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.feed import FeedConsumption
from app.domain.repositories.feed_repository import AbstractFeedRepository


class SQLAlchemyFeedRepository(AbstractFeedRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, record: FeedConsumption) -> FeedConsumption:
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record

    async def get_by_id(self, record_id: UUID) -> Optional[FeedConsumption]:
        result = await self._session.execute(
            select(FeedConsumption).where(FeedConsumption.id == record_id)
        )
        return result.scalar_one_or_none()

    async def list_by_batch(
        self,
        batch_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[FeedConsumption], int]:
        count_result = await self._session.execute(
            select(func.count()).where(FeedConsumption.batch_id == batch_id)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        rows = await self._session.execute(
            select(FeedConsumption)
            .where(FeedConsumption.batch_id == batch_id)
            .order_by(desc(FeedConsumption.feed_date))
            .offset(offset)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

    async def total_feed_kg(self, batch_id: UUID) -> Decimal:
        result = await self._session.execute(
            select(func.coalesce(func.sum(FeedConsumption.quantity_kg), 0))
            .where(FeedConsumption.batch_id == batch_id)
        )
        return Decimal(str(result.scalar_one()))

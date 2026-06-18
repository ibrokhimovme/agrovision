from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.poultry.domain.models.animal import Batch, BatchStatus
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository


class SQLAlchemyBatchRepository(AbstractBatchRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, batch_id: UUID) -> Optional[Batch]:
        result = await self._session.execute(
            select(Batch)
            .options(
                selectinload(Batch.mortality_records),
                selectinload(Batch.weight_samplings),
            )
            .where(Batch.id == batch_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, batch_code: str, farm_id: UUID) -> Optional[Batch]:
        result = await self._session.execute(
            select(Batch).where(
                Batch.batch_code == batch_code,
                Batch.farm_id == farm_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_farm(
        self,
        farm_id: UUID,
        status: Optional[BatchStatus],
        page: int,
        page_size: int,
    ) -> tuple[list[Batch], int]:
        base_query = select(Batch).where(Batch.farm_id == farm_id)
        if status is not None:
            base_query = base_query.where(Batch.status == status)

        total_result = await self._session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self._session.execute(
            base_query
            .options(
                selectinload(Batch.mortality_records),
                selectinload(Batch.weight_samplings),
            )
            .order_by(Batch.placement_date.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create(self, batch: Batch) -> Batch:
        self._session.add(batch)
        await self._session.flush()
        return await self.get_by_id(batch.id)  # type: ignore[return-value]

    async def update(self, batch: Batch) -> Batch:
        await self._session.flush()
        return await self.get_by_id(batch.id)  # type: ignore[return-value]

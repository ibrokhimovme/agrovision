from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.animal import WeightSampling
from app.domain.repositories.weight_repository import AbstractWeightRepository


class SQLAlchemyWeightRepository(AbstractWeightRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, sampling: WeightSampling) -> WeightSampling:
        self._session.add(sampling)
        await self._session.flush()
        return sampling

    async def get_by_id(self, sampling_id: UUID) -> Optional[WeightSampling]:
        result = await self._session.execute(
            select(WeightSampling).where(WeightSampling.id == sampling_id)
        )
        return result.scalar_one_or_none()

    async def list_by_batch(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[WeightSampling], int]:
        total = (
            await self._session.execute(
                select(func.count()).select_from(WeightSampling).where(
                    WeightSampling.batch_id == batch_id
                )
            )
        ).scalar_one()

        rows = await self._session.execute(
            select(WeightSampling)
            .where(WeightSampling.batch_id == batch_id)
            .order_by(WeightSampling.measured_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

    async def all_by_batch(self, batch_id: UUID) -> list[WeightSampling]:
        rows = await self._session.execute(
            select(WeightSampling)
            .where(WeightSampling.batch_id == batch_id)
            .order_by(WeightSampling.measured_at.asc())
        )
        return list(rows.scalars().all())

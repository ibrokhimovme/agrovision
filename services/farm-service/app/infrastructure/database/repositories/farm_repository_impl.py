from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.farm import Farm
from app.domain.repositories.farm_repository import AbstractFarmRepository


class SQLAlchemyFarmRepository(AbstractFarmRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, farm_id: UUID) -> Optional[Farm]:
        result = await self._session.execute(
            select(Farm).where(Farm.id == farm_id)
        )
        return result.scalar_one_or_none()

    async def list_active(self, page: int, page_size: int) -> tuple[list[Farm], int]:
        base_query = select(Farm).where(Farm.is_active == True)  # noqa: E712

        total_result = await self._session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self._session.execute(
            base_query
            .order_by(Farm.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create(self, farm: Farm) -> Farm:
        self._session.add(farm)
        await self._session.flush()
        await self._session.refresh(farm)
        return farm

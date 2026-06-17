from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.farm import Farm, Building, Section
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

    async def update(self, farm: Farm) -> Farm:
        await self._session.flush()
        await self._session.refresh(farm)
        return farm

    async def soft_delete(self, farm_id: UUID) -> Optional[Farm]:
        farm = await self.get_by_id(farm_id)
        if farm is None:
            return None
        farm.is_active = False
        await self._session.flush()
        return farm

    async def list_buildings(self, farm_id: UUID) -> list[Building]:
        result = await self._session.execute(
            select(Building)
            .where(Building.farm_id == farm_id)
            .order_by(Building.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_building_by_id(self, building_id: UUID) -> Optional[Building]:
        result = await self._session.execute(
            select(Building).where(Building.id == building_id)
        )
        return result.scalar_one_or_none()

    async def create_building(self, building: Building) -> Building:
        self._session.add(building)
        await self._session.flush()
        await self._session.refresh(building)
        return building

    async def list_sections(self, building_id: UUID) -> list[Section]:
        result = await self._session.execute(
            select(Section)
            .where(Section.building_id == building_id)
            .order_by(Section.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_section(self, section: Section) -> Section:
        self._session.add(section)
        await self._session.flush()
        await self._session.refresh(section)
        return section

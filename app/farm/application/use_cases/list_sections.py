from __future__ import annotations

from uuid import UUID

from app.farm.domain.models.farm import Section
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class ListSectionsUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, building_id: UUID) -> list[Section]:
        building = await self._repo.get_building_by_id(building_id)
        if building is None:
            raise EntityNotFoundError("Building", str(building_id))
        return await self._repo.list_sections(building_id)

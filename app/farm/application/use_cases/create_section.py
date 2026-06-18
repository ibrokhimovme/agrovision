from __future__ import annotations

from uuid import UUID

from app.farm.application.dtos.farm_dtos import CreateSectionRequest
from app.farm.domain.models.farm import Section
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class CreateSectionUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, building_id: UUID, req: CreateSectionRequest) -> Section:
        building = await self._repo.get_building_by_id(building_id)
        if building is None:
            raise EntityNotFoundError("Building", str(building_id))

        section = Section()
        section.building_id = building_id
        section.farm_id = building.farm_id
        section.name = req.name
        section.section_type = req.section_type
        section.capacity = req.capacity
        section.is_active = True

        return await self._repo.create_section(section)

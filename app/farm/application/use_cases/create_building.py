from __future__ import annotations

from uuid import UUID

from app.farm.application.dtos.farm_dtos import CreateBuildingRequest
from app.farm.domain.models.farm import Building
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class CreateBuildingUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, farm_id: UUID, req: CreateBuildingRequest) -> Building:
        farm = await self._repo.get_by_id(farm_id)
        if farm is None:
            raise EntityNotFoundError("Farm", str(farm_id))

        building = Building()
        building.farm_id = farm_id
        building.name = req.name
        building.capacity = req.capacity
        building.notes = req.notes

        return await self._repo.create_building(building)

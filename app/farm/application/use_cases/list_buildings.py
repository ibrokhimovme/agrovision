from __future__ import annotations

from uuid import UUID

from app.farm.domain.models.farm import Building
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class ListBuildingsUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, farm_id: UUID) -> list[Building]:
        farm = await self._repo.get_by_id(farm_id)
        if farm is None:
            raise EntityNotFoundError("Farm", str(farm_id))
        return await self._repo.list_buildings(farm_id)

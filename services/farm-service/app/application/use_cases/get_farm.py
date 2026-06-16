from __future__ import annotations

from uuid import UUID

from app.domain.models.farm import Farm
from app.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class GetFarmUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, farm_id: UUID) -> Farm:
        farm = await self._repo.get_by_id(farm_id)
        if farm is None:
            raise EntityNotFoundError("Farm", farm_id)
        return farm

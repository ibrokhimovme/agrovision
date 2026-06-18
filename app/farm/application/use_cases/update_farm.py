from __future__ import annotations

from uuid import UUID

from app.farm.application.dtos.farm_dtos import UpdateFarmRequest
from app.farm.domain.models.farm import Farm
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class UpdateFarmUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, farm_id: UUID, req: UpdateFarmRequest) -> Farm:
        farm = await self._repo.get_by_id(farm_id)
        if farm is None:
            raise EntityNotFoundError("Farm", str(farm_id))

        if req.name is not None:
            farm.name = req.name
        if req.farm_type is not None:
            farm.farm_type = req.farm_type
        if req.address is not None:
            farm.address = req.address
        if req.region is not None:
            farm.region = req.region
        if req.notes is not None:
            farm.notes = req.notes

        return await self._repo.update(farm)

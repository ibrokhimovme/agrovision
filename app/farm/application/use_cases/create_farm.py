from __future__ import annotations

from uuid import UUID

from app.farm.application.dtos.farm_dtos import CreateFarmRequest
from app.farm.domain.models.farm import Farm
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository


class CreateFarmUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, req: CreateFarmRequest, owner_user_id: UUID) -> Farm:
        farm = Farm()
        farm.name = req.name
        farm.farm_type = req.farm_type
        farm.address = req.address
        farm.region = req.region
        farm.notes = req.notes
        farm.owner_user_id = owner_user_id
        farm.is_active = True

        return await self._repo.create(farm)

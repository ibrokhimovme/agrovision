from __future__ import annotations

from uuid import UUID

from app.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class DeleteFarmUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, farm_id: UUID) -> None:
        farm = await self._repo.soft_delete(farm_id)
        if farm is None:
            raise EntityNotFoundError("Farm", str(farm_id))

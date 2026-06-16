from __future__ import annotations

from app.domain.models.farm import Farm
from app.domain.repositories.farm_repository import AbstractFarmRepository


class ListFarmsUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(self, page: int, page_size: int) -> tuple[list[Farm], int]:
        return await self._repo.list_active(page, page_size)

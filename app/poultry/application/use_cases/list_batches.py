from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.poultry.domain.models.animal import Batch, BatchStatus
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository


class ListBatchesUseCase:

    def __init__(self, repo: AbstractBatchRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        farm_id: UUID,
        status: Optional[BatchStatus],
        page: int,
        page_size: int,
        archived: Optional[bool] = False,
    ) -> tuple[list[Batch], int]:
        return await self._repo.list_by_farm(farm_id, status, page, page_size, archived)

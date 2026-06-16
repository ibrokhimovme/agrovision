from __future__ import annotations

from uuid import UUID

from app.domain.models.animal import Batch
from app.domain.repositories.batch_repository import AbstractBatchRepository
from shared.exceptions import EntityNotFoundError


class GetBatchUseCase:

    def __init__(self, repo: AbstractBatchRepository) -> None:
        self._repo = repo

    async def execute(self, batch_id: UUID) -> Batch:
        batch = await self._repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)
        return batch

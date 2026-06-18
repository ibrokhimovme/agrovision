"""
ArchiveBatchUseCase: EX-16 (Archive System, execution-v2).
Manual-only archiving of a COMPLETED batch — additive, never deletes data
(decision_log.md BMD-018).
"""
from __future__ import annotations

from uuid import UUID

from app.poultry.domain.models.animal import Batch
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository
from shared.exceptions import EntityNotFoundError


class ArchiveBatchUseCase:

    def __init__(self, repo: AbstractBatchRepository) -> None:
        self._repo = repo

    async def execute(self, batch_id: UUID, archived_by: UUID) -> Batch:
        batch = await self._repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        batch.archive(archived_by)
        return await self._repo.update(batch)

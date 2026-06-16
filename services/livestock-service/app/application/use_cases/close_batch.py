from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.application.dtos.batch_dtos import CloseBatchRequest
from app.domain.models.animal import Batch, BatchStatus
from app.domain.repositories.batch_repository import AbstractBatchRepository
from shared.exceptions import EntityNotFoundError


class CloseBatchUseCase:

    def __init__(self, repo: AbstractBatchRepository) -> None:
        self._repo = repo

    async def execute(self, batch_id: UUID, req: CloseBatchRequest) -> Batch:
        batch = await self._repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        batch.transition_to(BatchStatus.CLOSED)
        batch.closed_at = datetime.now(timezone.utc)
        batch.close_reason = req.close_reason

        if req.notes:
            batch.notes = req.notes

        return await self._repo.update(batch)

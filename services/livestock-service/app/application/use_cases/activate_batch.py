from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.domain.models.animal import Batch, BatchStatus
from app.domain.repositories.batch_repository import AbstractBatchRepository
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class ActivateBatchUseCase:

    def __init__(self, repo: AbstractBatchRepository) -> None:
        self._repo = repo

    async def execute(self, batch_id: UUID) -> Batch:
        batch = await self._repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        # BP-03: minimum 7-day quarantine before activation
        if batch.quarantine_end_date is not None:
            now = datetime.now(timezone.utc)
            end = batch.quarantine_end_date
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            if now < end:
                remaining = (end - now).days + 1
                raise BusinessRuleViolationError(
                    "QUARANTINE_MINIMUM_7_DAYS",
                    f"Karantin davri hali tugamagan. {remaining} kun qoldi.",
                )

        batch.transition_to(BatchStatus.ACTIVE)

        return await self._repo.update(batch)

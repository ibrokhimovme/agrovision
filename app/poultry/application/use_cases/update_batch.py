from __future__ import annotations

from uuid import UUID

from app.poultry.application.dtos.batch_dtos import UpdateBatchRequest
from app.poultry.domain.models.animal import Batch
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository
from shared.exceptions import EntityNotFoundError


class UpdateBatchUseCase:

    def __init__(self, repo: AbstractBatchRepository) -> None:
        self._repo = repo

    async def execute(self, batch_id: UUID, req: UpdateBatchRequest) -> Batch:
        batch = await self._repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        if req.batch_code is not None:
            batch.batch_code = req.batch_code
        if req.supplier_name is not None:
            batch.supplier_name = req.supplier_name
        if req.chick_price_per_head is not None:
            batch.chick_price_per_head = req.chick_price_per_head
        if req.notes is not None:
            batch.notes = req.notes
        if req.quarantine_end_date is not None:
            batch.quarantine_end_date = req.quarantine_end_date

        return await self._repo.update(batch)

from __future__ import annotations

from datetime import timedelta

from app.application.dtos.batch_dtos import CreateBatchRequest
from app.domain.models.animal import Batch, BatchStatus
from app.domain.repositories.batch_repository import AbstractBatchRepository
from shared.exceptions import DuplicateEntityError


class CreateBatchUseCase:

    def __init__(self, repo: AbstractBatchRepository) -> None:
        self._repo = repo

    async def execute(self, req: CreateBatchRequest) -> Batch:
        # Check for duplicate batch_code within the same farm
        if req.batch_code:
            existing = await self._repo.get_by_code(req.batch_code, req.farm_id)
            if existing:
                raise DuplicateEntityError(
                    f"Batch with code '{req.batch_code}' already exists in this farm.",
                    details={"rule": "DUPLICATE_BATCH_CODE"},
                )

        quarantine_end_date = req.quarantine_end_date
        if quarantine_end_date is None:
            quarantine_end_date = req.placement_date + timedelta(days=7)

        batch = Batch()
        batch.farm_id = req.farm_id
        batch.section_id = req.section_id
        batch.species = req.species
        batch.status = BatchStatus.QUARANTINE
        batch.batch_code = req.batch_code
        batch.initial_count = req.initial_count
        batch.current_count = req.initial_count
        batch.placement_date = req.placement_date
        batch.quarantine_end_date = quarantine_end_date
        batch.supplier_name = req.supplier_name
        batch.chick_price_per_head = req.chick_price_per_head
        batch.notes = req.notes

        return await self._repo.create(batch)

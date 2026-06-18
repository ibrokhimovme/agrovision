from __future__ import annotations

from uuid import UUID, uuid4

from app.poultry.application.dtos.mortality_dtos import RecordMortalityRequest
from app.poultry.domain.models.animal import BatchStatus, MortalityRecord
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository
from app.poultry.domain.repositories.mortality_repository import AbstractMortalityRepository
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class RecordMortalityUseCase:

    def __init__(
        self,
        batch_repo: AbstractBatchRepository,
        mortality_repo: AbstractMortalityRepository,
    ) -> None:
        self._batch_repo = batch_repo
        self._mortality_repo = mortality_repo

    async def execute(self, batch_id: UUID, req: RecordMortalityRequest) -> MortalityRecord:
        batch = await self._batch_repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        if batch.status != BatchStatus.ACTIVE:
            raise BusinessRuleViolationError(
                "MORTALITY_BATCH_NOT_ACTIVE",
                "O'lim faqat faol (active) partiyalar uchun kiritiladi.",
            )

        if req.quantity > batch.current_count:
            raise BusinessRuleViolationError(
                "MORTALITY_EXCEEDS_CURRENT_COUNT",
                f"O'lim soni ({req.quantity}) joriy parrandalar sonidan "
                f"({batch.current_count}) oshib ketdi.",
            )

        record = MortalityRecord()
        record.id = uuid4()
        record.batch_id = batch_id
        record.farm_id = req.farm_id
        record.quantity = req.quantity
        record.cause_category = req.cause_category
        record.cause_description = req.cause_description
        record.disposal_method = req.disposal_method
        record.deceased_at = req.deceased_at

        # Atomically decrement current_count
        batch.current_count -= req.quantity
        await self._batch_repo.update(batch)

        return await self._mortality_repo.create(record)

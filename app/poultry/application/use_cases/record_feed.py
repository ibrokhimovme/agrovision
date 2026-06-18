from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

from app.poultry.application.dtos.feed_dtos import RecordFeedRequest
from app.poultry.domain.models.animal import BatchStatus
from app.poultry.domain.models.feed import FeedConsumption
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository
from app.poultry.domain.repositories.feed_repository import AbstractFeedRepository
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class RecordFeedConsumptionUseCase:

    def __init__(
        self,
        batch_repo: AbstractBatchRepository,
        feed_repo: AbstractFeedRepository,
    ) -> None:
        self._batch_repo = batch_repo
        self._feed_repo = feed_repo

    async def execute(self, batch_id: UUID, req: RecordFeedRequest) -> FeedConsumption:
        batch = await self._batch_repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        if batch.status != BatchStatus.ACTIVE:
            raise BusinessRuleViolationError(
                "FEED_BATCH_NOT_ACTIVE",
                "Ozuqlantirish faqat faol (active) partiyalar uchun kiritiladi.",
            )

        record = FeedConsumption()
        record.id = uuid4()
        record.batch_id = batch_id
        record.farm_id = req.farm_id
        record.feed_date = req.feed_date
        record.feed_type = req.feed_type
        record.quantity_kg = req.quantity_kg
        record.water_liters = req.water_liters
        record.age_days = req.age_days
        record.feed_inventory_item_id = req.feed_inventory_item_id
        record.notes = req.notes

        return await self._feed_repo.create(record)

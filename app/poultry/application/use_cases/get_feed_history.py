from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.poultry.application.dtos.feed_dtos import FeedSummaryResponse
from app.poultry.domain.models.feed import FeedConsumption
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository
from app.poultry.domain.repositories.feed_repository import AbstractFeedRepository
from shared.exceptions import EntityNotFoundError


class GetBatchFeedHistoryUseCase:

    def __init__(self, feed_repo: AbstractFeedRepository) -> None:
        self._feed_repo = feed_repo

    async def execute(
        self,
        batch_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[FeedConsumption], int]:
        return await self._feed_repo.list_by_batch(batch_id, page, page_size)


class GetFeedSummaryUseCase:

    def __init__(
        self,
        batch_repo: AbstractBatchRepository,
        feed_repo: AbstractFeedRepository,
    ) -> None:
        self._batch_repo = batch_repo
        self._feed_repo = feed_repo

    async def execute(self, batch_id: UUID) -> FeedSummaryResponse:
        batch = await self._batch_repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        records, total = await self._feed_repo.list_by_batch(batch_id, page=1, page_size=10_000)
        total_feed_kg = sum((r.quantity_kg for r in records), Decimal("0"))
        total_water = sum(
            (r.water_liters for r in records if r.water_liters is not None),
            Decimal("0"),
        )

        # FCR = total_feed_kg / weight_gain_kg
        # weight_gain computed from weight samplings if available
        fcr: Optional[Decimal] = None
        if batch.weight_samplings:
            latest = max(batch.weight_samplings, key=lambda w: w.measured_at)
            weight_gain_kg = latest.average_weight_kg * batch.current_count
            if weight_gain_kg > 0 and total_feed_kg > 0:
                fcr = (total_feed_kg / weight_gain_kg).quantize(Decimal("0.001"))

        return FeedSummaryResponse(
            batch_id=batch_id,
            total_feed_kg=total_feed_kg,
            total_water_liters=total_water if total_water > 0 else None,
            record_count=total,
            fcr=fcr,
        )

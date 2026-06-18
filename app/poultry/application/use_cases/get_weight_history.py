from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.poultry.application.dtos.weight_dtos import GrowthMetricsResponse
from app.poultry.domain.models.animal import WeightSampling
from app.poultry.domain.repositories.feed_repository import AbstractFeedRepository
from app.poultry.domain.repositories.weight_repository import AbstractWeightRepository


class GetWeightHistoryUseCase:
    def __init__(self, weight_repo: AbstractWeightRepository) -> None:
        self._weight_repo = weight_repo

    async def execute(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[WeightSampling], int]:
        return await self._weight_repo.list_by_batch(batch_id, page, page_size)


class GetGrowthMetricsUseCase:
    def __init__(
        self,
        weight_repo: AbstractWeightRepository,
        feed_repo: AbstractFeedRepository,
    ) -> None:
        self._weight_repo = weight_repo
        self._feed_repo = feed_repo

    async def execute(self, batch_id: UUID) -> GrowthMetricsResponse:
        samplings = await self._weight_repo.all_by_batch(batch_id)
        total_feed_kg = await self._feed_repo.total_feed_kg(batch_id)

        if not samplings:
            return GrowthMetricsResponse(
                batch_id=batch_id,
                sampling_count=0,
                total_feed_kg=total_feed_kg if total_feed_kg > 0 else None,
            )

        latest = samplings[-1]
        earliest = samplings[0]

        adg: Optional[Decimal] = None
        if len(samplings) >= 2:
            age_span = (
                (latest.age_days or 0) - (earliest.age_days or 0)
            )
            if age_span > 0:
                weight_gain = latest.average_weight_kg - earliest.average_weight_kg
                adg = (weight_gain / age_span).quantize(Decimal("0.0001"))

        fcr: Optional[Decimal] = None
        if total_feed_kg > 0 and latest.average_weight_kg > 0:
            weight_gain_total = latest.average_weight_kg * latest.sample_size
            if weight_gain_total > 0:
                fcr = (total_feed_kg / weight_gain_total).quantize(Decimal("0.001"))

        return GrowthMetricsResponse(
            batch_id=batch_id,
            sampling_count=len(samplings),
            latest_avg_weight_kg=latest.average_weight_kg,
            age_days=latest.age_days,
            adg_kg=adg,
            total_feed_kg=total_feed_kg if total_feed_kg > 0 else None,
            fcr=fcr,
        )

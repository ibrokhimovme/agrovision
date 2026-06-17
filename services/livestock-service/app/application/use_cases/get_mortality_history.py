from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.application.dtos.mortality_dtos import MortalitySummaryResponse
from app.domain.models.animal import MortalityRecord
from app.domain.repositories.batch_repository import AbstractBatchRepository
from app.domain.repositories.mortality_repository import AbstractMortalityRepository
from shared.exceptions import EntityNotFoundError


class GetMortalityHistoryUseCase:

    def __init__(self, mortality_repo: AbstractMortalityRepository) -> None:
        self._mortality_repo = mortality_repo

    async def execute(
        self,
        batch_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[MortalityRecord], int]:
        return await self._mortality_repo.list_by_batch(batch_id, page, page_size)


class GetMortalitySummaryUseCase:

    def __init__(
        self,
        batch_repo: AbstractBatchRepository,
        mortality_repo: AbstractMortalityRepository,
    ) -> None:
        self._batch_repo = batch_repo
        self._mortality_repo = mortality_repo

    async def execute(self, batch_id: UUID) -> MortalitySummaryResponse:
        batch = await self._batch_repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        records, _ = await self._mortality_repo.list_by_batch(batch_id, page=1, page_size=10_000)

        total_deaths = sum(r.quantity for r in records)
        mortality_rate = (
            Decimal(str(round(total_deaths / batch.initial_count * 100, 2)))
            if batch.initial_count > 0
            else Decimal("0")
        )

        cause_breakdown: dict[str, int] = {}
        for r in records:
            key = r.cause_category or "nomalum"
            cause_breakdown[key] = cause_breakdown.get(key, 0) + r.quantity

        return MortalitySummaryResponse(
            batch_id=batch_id,
            total_deaths=total_deaths,
            initial_count=batch.initial_count,
            current_count=batch.current_count,
            mortality_rate=mortality_rate,
            cause_breakdown=cause_breakdown,
        )

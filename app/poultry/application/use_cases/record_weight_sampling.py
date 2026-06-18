from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.poultry.application.dtos.weight_dtos import RecordWeightRequest
from app.poultry.domain.models.animal import BatchStatus, WeightSampling
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository
from app.poultry.domain.repositories.weight_repository import AbstractWeightRepository
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class RecordWeightSamplingUseCase:
    def __init__(
        self,
        batch_repo: AbstractBatchRepository,
        weight_repo: AbstractWeightRepository,
    ) -> None:
        self._batch_repo = batch_repo
        self._weight_repo = weight_repo

    async def execute(self, batch_id: UUID, req: RecordWeightRequest) -> WeightSampling:
        batch = await self._batch_repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", str(batch_id))

        if batch.status != BatchStatus.ACTIVE:
            raise BusinessRuleViolationError(
                "WEIGHT_BATCH_NOT_ACTIVE",
                "Og'irlik o'lchovi faqat FAOL partiyalar uchun mumkin.",
            )

        measured_at = req.measured_at or datetime.now(timezone.utc)
        average_weight_kg = (req.total_sample_weight_kg / req.sample_size).quantize(
            Decimal("0.001")
        )

        placement = batch.placement_date
        if placement.tzinfo is None:
            placement = placement.replace(tzinfo=timezone.utc)
        if measured_at.tzinfo is None:
            measured_at = measured_at.replace(tzinfo=timezone.utc)
        age_days = (measured_at - placement).days

        sampling = WeightSampling()
        sampling.batch_id = batch.id
        sampling.farm_id = req.farm_id
        sampling.sample_size = req.sample_size
        sampling.total_sample_weight_kg = req.total_sample_weight_kg
        sampling.average_weight_kg = average_weight_kg
        sampling.age_days = age_days
        sampling.measured_at = measured_at
        sampling.notes = req.notes

        return await self._weight_repo.create(sampling)

from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from app.poultry.domain.models.health import VaccinationRecord, VaccinationStatus
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository
from app.poultry.domain.repositories.vaccination_repository import (
    AbstractVaccinationRepository,
    AbstractVaccinationScheduleRepository,
)
from shared.exceptions import EntityNotFoundError


class GenerateBatchVaccinationPlanUseCase:
    def __init__(
        self,
        batch_repo: AbstractBatchRepository,
        schedule_repo: AbstractVaccinationScheduleRepository,
        vaccination_repo: AbstractVaccinationRepository,
    ) -> None:
        self._batch_repo = batch_repo
        self._schedule_repo = schedule_repo
        self._vaccination_repo = vaccination_repo

    async def execute(self, batch_id: UUID) -> list[VaccinationRecord]:
        batch = await self._batch_repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", str(batch_id))

        schedules = await self._schedule_repo.list_by_farm_species(
            batch.farm_id, batch.species
        )
        if not schedules:
            return []

        records = []
        for schedule in schedules:
            scheduled_at = batch.placement_date + timedelta(days=schedule.day_of_age)
            record = VaccinationRecord()
            record.batch_id = batch.id
            record.farm_id = batch.farm_id
            record.schedule_id = schedule.id
            record.vaccine_name = schedule.vaccine_name
            record.status = VaccinationStatus.PLANNED
            record.scheduled_at = scheduled_at
            records.append(record)

        return await self._vaccination_repo.bulk_create_records(records)

from __future__ import annotations

from app.poultry.application.dtos.vaccination_dtos import CreateScheduleRequest
from app.poultry.domain.models.health import VaccinationSchedule
from app.poultry.domain.repositories.vaccination_repository import AbstractVaccinationScheduleRepository


class CreateVaccinationScheduleUseCase:
    def __init__(self, schedule_repo: AbstractVaccinationScheduleRepository) -> None:
        self._schedule_repo = schedule_repo

    async def execute(self, req: CreateScheduleRequest) -> VaccinationSchedule:
        schedule = VaccinationSchedule()
        schedule.farm_id = req.farm_id
        schedule.species = req.species
        schedule.vaccine_name = req.vaccine_name
        schedule.day_of_age = req.day_of_age
        schedule.is_mandatory = req.is_mandatory
        schedule.notes = req.notes
        return await self._schedule_repo.create(schedule)

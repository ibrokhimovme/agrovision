from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.poultry.domain.models.health import VaccinationRecord, VaccinationSchedule


class AbstractVaccinationRepository(ABC):
    @abstractmethod
    async def create_record(self, record: VaccinationRecord) -> VaccinationRecord: ...

    @abstractmethod
    async def update_record(self, record: VaccinationRecord) -> VaccinationRecord: ...

    @abstractmethod
    async def get_record_by_id(self, record_id: UUID) -> Optional[VaccinationRecord]: ...

    @abstractmethod
    async def list_by_batch(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[VaccinationRecord], int]: ...

    @abstractmethod
    async def bulk_create_records(
        self, records: list[VaccinationRecord]
    ) -> list[VaccinationRecord]: ...


class AbstractVaccinationScheduleRepository(ABC):
    @abstractmethod
    async def create(self, schedule: VaccinationSchedule) -> VaccinationSchedule: ...

    @abstractmethod
    async def get_by_id(self, schedule_id: UUID) -> Optional[VaccinationSchedule]: ...

    @abstractmethod
    async def list_by_farm(self, farm_id: UUID) -> list[VaccinationSchedule]: ...

    @abstractmethod
    async def list_by_farm_species(
        self, farm_id: UUID, species: str
    ) -> list[VaccinationSchedule]: ...

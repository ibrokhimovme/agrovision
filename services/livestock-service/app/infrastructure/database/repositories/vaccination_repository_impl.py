from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.health import VaccinationRecord, VaccinationSchedule
from app.domain.repositories.vaccination_repository import (
    AbstractVaccinationRepository,
    AbstractVaccinationScheduleRepository,
)


class SQLAlchemyVaccinationRepository(AbstractVaccinationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_record(self, record: VaccinationRecord) -> VaccinationRecord:
        self._session.add(record)
        await self._session.flush()
        return record

    async def update_record(self, record: VaccinationRecord) -> VaccinationRecord:
        await self._session.flush()
        return record

    async def get_record_by_id(self, record_id: UUID) -> Optional[VaccinationRecord]:
        result = await self._session.execute(
            select(VaccinationRecord).where(VaccinationRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def list_by_batch(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[VaccinationRecord], int]:
        count_q = select(func.count()).select_from(VaccinationRecord).where(
            VaccinationRecord.batch_id == batch_id
        )
        total = (await self._session.execute(count_q)).scalar_one()

        rows = await self._session.execute(
            select(VaccinationRecord)
            .where(VaccinationRecord.batch_id == batch_id)
            .order_by(VaccinationRecord.scheduled_at.asc().nullslast())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

    async def bulk_create_records(
        self, records: list[VaccinationRecord]
    ) -> list[VaccinationRecord]:
        for r in records:
            self._session.add(r)
        await self._session.flush()
        return records


class SQLAlchemyVaccinationScheduleRepository(AbstractVaccinationScheduleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, schedule: VaccinationSchedule) -> VaccinationSchedule:
        self._session.add(schedule)
        await self._session.flush()
        return schedule

    async def get_by_id(self, schedule_id: UUID) -> Optional[VaccinationSchedule]:
        result = await self._session.execute(
            select(VaccinationSchedule).where(VaccinationSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    async def list_by_farm(self, farm_id: UUID) -> list[VaccinationSchedule]:
        rows = await self._session.execute(
            select(VaccinationSchedule)
            .where(VaccinationSchedule.farm_id == farm_id)
            .order_by(VaccinationSchedule.day_of_age.asc())
        )
        return list(rows.scalars().all())

    async def list_by_farm_species(
        self, farm_id: UUID, species: str
    ) -> list[VaccinationSchedule]:
        rows = await self._session.execute(
            select(VaccinationSchedule)
            .where(
                VaccinationSchedule.farm_id == farm_id,
                VaccinationSchedule.species == species,
            )
            .order_by(VaccinationSchedule.day_of_age.asc())
        )
        return list(rows.scalars().all())

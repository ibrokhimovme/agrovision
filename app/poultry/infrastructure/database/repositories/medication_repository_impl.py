from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.poultry.domain.models.health import MedicationRecord
from app.poultry.domain.repositories.medication_repository import AbstractMedicationRepository


class SQLAlchemyMedicationRepository(AbstractMedicationRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, record: MedicationRecord) -> MedicationRecord:
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record

    async def get_by_id(self, record_id: UUID) -> Optional[MedicationRecord]:
        result = await self._session.execute(
            select(MedicationRecord).where(MedicationRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def list_by_batch(
        self,
        batch_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[MedicationRecord], int]:
        count_result = await self._session.execute(
            select(func.count()).where(MedicationRecord.batch_id == batch_id)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        rows = await self._session.execute(
            select(MedicationRecord)
            .where(MedicationRecord.batch_id == batch_id)
            .order_by(desc(MedicationRecord.administered_at))
            .offset(offset)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

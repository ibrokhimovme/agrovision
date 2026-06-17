from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.domain.models.health import VaccinationRecord, VaccinationStatus
from app.domain.repositories.vaccination_repository import AbstractVaccinationRepository


class GetBatchVaccinationsUseCase:
    def __init__(self, vaccination_repo: AbstractVaccinationRepository) -> None:
        self._vaccination_repo = vaccination_repo

    async def execute(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[VaccinationRecord], int]:
        records, total = await self._vaccination_repo.list_by_batch(batch_id, page, page_size)

        now = datetime.now(timezone.utc)
        overdue_updated = False
        for record in records:
            if record.status == VaccinationStatus.PLANNED and record.scheduled_at is not None:
                scheduled = record.scheduled_at
                if scheduled.tzinfo is None:
                    scheduled = scheduled.replace(tzinfo=timezone.utc)
                if now > scheduled:
                    record.status = VaccinationStatus.OVERDUE
                    overdue_updated = True

        if overdue_updated:
            for record in records:
                if record.status == VaccinationStatus.OVERDUE:
                    await self._vaccination_repo.update_record(record)

        return records, total

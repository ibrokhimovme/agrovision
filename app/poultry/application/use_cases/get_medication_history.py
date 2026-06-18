from __future__ import annotations

from uuid import UUID

from app.poultry.domain.models.health import MedicationRecord
from app.poultry.domain.repositories.medication_repository import AbstractMedicationRepository


class GetMedicationHistoryUseCase:

    def __init__(self, medication_repo: AbstractMedicationRepository) -> None:
        self._medication_repo = medication_repo

    async def execute(
        self,
        batch_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[MedicationRecord], int]:
        return await self._medication_repo.list_by_batch(batch_id, page, page_size)

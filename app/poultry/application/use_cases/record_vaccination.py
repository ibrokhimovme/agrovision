from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.poultry.application.dtos.vaccination_dtos import RecordVaccinationRequest
from app.poultry.domain.models.health import VaccinationRecord, VaccinationStatus
from app.poultry.domain.repositories.vaccination_repository import AbstractVaccinationRepository
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class RecordVaccinationUseCase:
    def __init__(self, vaccination_repo: AbstractVaccinationRepository) -> None:
        self._vaccination_repo = vaccination_repo

    async def execute(
        self, record_id: UUID, req: RecordVaccinationRequest
    ) -> VaccinationRecord:
        record = await self._vaccination_repo.get_record_by_id(record_id)
        if record is None:
            raise EntityNotFoundError("VaccinationRecord", str(record_id))

        if record.status not in (VaccinationStatus.PLANNED, VaccinationStatus.OVERDUE):
            raise BusinessRuleViolationError(
                "VACCINATION_ALREADY_COMPLETED",
                f"Bu emlash allaqachon '{record.status}' holatida.",
            )

        record.status = VaccinationStatus.COMPLETED
        record.vaccinated_at = req.vaccinated_at or datetime.now(timezone.utc)
        if req.quantity_used is not None:
            record.quantity_used = req.quantity_used
        if req.unit is not None:
            record.unit = req.unit
        if req.vaccine_inventory_item_id is not None:
            record.vaccine_inventory_item_id = req.vaccine_inventory_item_id
        if req.notes is not None:
            record.notes = req.notes

        return await self._vaccination_repo.update_record(record)

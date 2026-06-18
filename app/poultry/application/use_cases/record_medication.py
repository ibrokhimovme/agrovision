from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.poultry.application.dtos.medication_dtos import RecordMedicationRequest
from app.poultry.domain.models.animal import BatchStatus
from app.poultry.domain.models.health import MedicationRecord
from app.poultry.domain.repositories.batch_repository import AbstractBatchRepository
from app.poultry.domain.repositories.medication_repository import AbstractMedicationRepository
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class RecordMedicationUseCase:

    def __init__(
        self,
        batch_repo: AbstractBatchRepository,
        medication_repo: AbstractMedicationRepository,
    ) -> None:
        self._batch_repo = batch_repo
        self._medication_repo = medication_repo

    async def execute(self, batch_id: UUID, req: RecordMedicationRequest) -> MedicationRecord:
        batch = await self._batch_repo.get_by_id(batch_id)
        if batch is None:
            raise EntityNotFoundError("Batch", batch_id)

        # EX-09 (Medication Workflow Alignment, execution-v2): same ACTIVE-only
        # gate as feed/mortality/weight, for consistency under the 2-state
        # batch model (decision_log.md BMD-013).
        if batch.status != BatchStatus.ACTIVE:
            raise BusinessRuleViolationError(
                "MEDICATION_BATCH_NOT_ACTIVE",
                "Dori-darmon faqat faol (active) partiyalar uchun kiritiladi.",
            )

        record = MedicationRecord()
        record.id = uuid4()
        record.batch_id = batch_id
        record.farm_id = req.farm_id
        record.medicine_name = req.medicine_name
        record.medicine_inventory_item_id = req.medicine_inventory_item_id
        record.quantity_used = req.quantity_used
        record.unit = req.unit
        record.reason = req.reason
        record.dosage_notes = req.dosage_notes
        record.administered_at = req.administered_at or datetime.now(timezone.utc)
        record.notes = req.notes

        return await self._medication_repo.create(record)

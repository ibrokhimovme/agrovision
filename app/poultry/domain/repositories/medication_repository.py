from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.poultry.domain.models.health import MedicationRecord


class AbstractMedicationRepository(ABC):

    @abstractmethod
    async def create(self, record: MedicationRecord) -> MedicationRecord: ...

    @abstractmethod
    async def get_by_id(self, record_id: UUID) -> Optional[MedicationRecord]: ...

    @abstractmethod
    async def list_by_batch(
        self,
        batch_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[MedicationRecord], int]: ...

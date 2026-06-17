from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.models.animal import MortalityRecord


class AbstractMortalityRepository(ABC):

    @abstractmethod
    async def create(self, record: MortalityRecord) -> MortalityRecord: ...

    @abstractmethod
    async def get_by_id(self, record_id: UUID) -> Optional[MortalityRecord]: ...

    @abstractmethod
    async def list_by_batch(
        self,
        batch_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[MortalityRecord], int]: ...

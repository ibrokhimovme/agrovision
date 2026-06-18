from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.poultry.domain.models.animal import Batch, BatchStatus


class AbstractBatchRepository(ABC):

    @abstractmethod
    async def get_by_id(self, batch_id: UUID) -> Optional[Batch]: ...

    @abstractmethod
    async def get_by_code(self, batch_code: str, farm_id: UUID) -> Optional[Batch]: ...

    @abstractmethod
    async def list_by_farm(
        self,
        farm_id: UUID,
        status: Optional[BatchStatus],
        page: int,
        page_size: int,
    ) -> tuple[list[Batch], int]: ...

    @abstractmethod
    async def create(self, batch: Batch) -> Batch: ...

    @abstractmethod
    async def update(self, batch: Batch) -> Batch: ...

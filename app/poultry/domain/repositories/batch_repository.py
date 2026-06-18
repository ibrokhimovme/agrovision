from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.poultry.domain.models.animal import Batch, BatchStatus


class AbstractBatchRepository(ABC):

    @abstractmethod
    async def get_by_id(self, batch_id: UUID) -> Optional[Batch]: ...

    @abstractmethod
    async def list_by_farm(
        self,
        farm_id: UUID,
        status: Optional[BatchStatus],
        page: int,
        page_size: int,
        archived: Optional[bool] = False,
    ) -> tuple[list[Batch], int]:
        """EX-16 (execution-v2): archived=False (default) excludes archived
        batches from operational views; True returns only archived batches
        (the Archive view); None returns both (Reports' "all" filter)."""
        ...

    @abstractmethod
    async def create(self, batch: Batch) -> Batch: ...

    @abstractmethod
    async def update(self, batch: Batch) -> Batch: ...

    @abstractmethod
    async def get_farm_name(self, farm_id: UUID) -> Optional[str]:
        """Cross-schema read of farm.farms.name for batch-code generation (EX-05).
        Raw SQL, not an ORM import — app.farm internals stay off-limits per
        the module-boundary rule; only this column's value crosses the line.
        """
        ...

    @abstractmethod
    async def count_batches_with_code_prefix(self, farm_id: UUID, prefix: str) -> int: ...

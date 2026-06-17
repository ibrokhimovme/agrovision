from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.models.animal import WeightSampling


class AbstractWeightRepository(ABC):
    @abstractmethod
    async def create(self, sampling: WeightSampling) -> WeightSampling: ...

    @abstractmethod
    async def get_by_id(self, sampling_id: UUID) -> Optional[WeightSampling]: ...

    @abstractmethod
    async def list_by_batch(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[WeightSampling], int]: ...

    @abstractmethod
    async def all_by_batch(self, batch_id: UUID) -> list[WeightSampling]: ...

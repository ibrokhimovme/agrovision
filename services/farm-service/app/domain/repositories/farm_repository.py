from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.models.farm import Farm


class AbstractFarmRepository(ABC):

    @abstractmethod
    async def get_by_id(self, farm_id: UUID) -> Optional[Farm]: ...

    @abstractmethod
    async def list_active(self, page: int, page_size: int) -> tuple[list[Farm], int]: ...

    @abstractmethod
    async def create(self, farm: Farm) -> Farm: ...

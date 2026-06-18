from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.farm.domain.models.farm import Farm, Building, Section


class AbstractFarmRepository(ABC):

    @abstractmethod
    async def get_by_id(self, farm_id: UUID, account_id: Optional[UUID] = None) -> Optional[Farm]: ...

    @abstractmethod
    async def list_active(
        self, page: int, page_size: int, account_id: Optional[UUID] = None
    ) -> tuple[list[Farm], int]: ...

    @abstractmethod
    async def create(self, farm: Farm) -> Farm: ...

    @abstractmethod
    async def update(self, farm: Farm) -> Farm: ...

    @abstractmethod
    async def soft_delete(self, farm_id: UUID) -> Optional[Farm]: ...

    @abstractmethod
    async def list_buildings(self, farm_id: UUID) -> list[Building]: ...

    @abstractmethod
    async def get_building_by_id(self, building_id: UUID) -> Optional[Building]: ...

    @abstractmethod
    async def create_building(self, building: Building) -> Building: ...

    @abstractmethod
    async def list_sections(self, building_id: UUID) -> list[Section]: ...

    @abstractmethod
    async def create_section(self, section: Section) -> Section: ...

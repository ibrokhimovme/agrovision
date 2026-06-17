from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.models.feed import FeedConsumption


class AbstractFeedRepository(ABC):

    @abstractmethod
    async def create(self, record: FeedConsumption) -> FeedConsumption: ...

    @abstractmethod
    async def list_by_batch(
        self,
        batch_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[FeedConsumption], int]: ...

    @abstractmethod
    async def total_feed_kg(self, batch_id: UUID) -> Decimal: ...

    @abstractmethod
    async def get_by_id(self, record_id: UUID) -> Optional[FeedConsumption]: ...

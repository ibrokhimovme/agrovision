"""
Abstract repository interface for SaleRecord. SF-17.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.domain.models.finance import SaleRecord


class AbstractSaleRepository(ABC):

    @abstractmethod
    async def create(self, sale: SaleRecord) -> SaleRecord: ...

    @abstractmethod
    async def get_by_id(self, sale_id: UUID) -> Optional[SaleRecord]: ...

    @abstractmethod
    async def list_by_batch(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[SaleRecord], int]: ...

    @abstractmethod
    async def total_revenue_by_batch(self, batch_id: UUID) -> Decimal: ...

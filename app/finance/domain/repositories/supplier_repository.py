"""
Abstract repository interface for Supplier. EX-11 (execution-v2).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.finance.domain.models.finance import Supplier


class AbstractSupplierRepository(ABC):

    @abstractmethod
    async def create(self, supplier: Supplier) -> Supplier: ...

    @abstractmethod
    async def get_by_id(self, supplier_id: UUID) -> Optional[Supplier]: ...

    @abstractmethod
    async def list_by_farm(self, farm_id: UUID) -> list[Supplier]: ...

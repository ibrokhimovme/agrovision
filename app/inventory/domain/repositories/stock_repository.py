"""
Abstract repository interfaces for inventory domain. BP-09, SF-12.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.inventory.domain.models.inventory import StockBatch, StockItem, StockMovement, Warehouse


class AbstractWarehouseRepository(ABC):

    @abstractmethod
    async def create(self, warehouse: Warehouse) -> Warehouse: ...

    @abstractmethod
    async def get_by_id(self, warehouse_id: UUID) -> Optional[Warehouse]: ...

    @abstractmethod
    async def list_by_farm(self, farm_id: UUID) -> list[Warehouse]: ...

    @abstractmethod
    async def update(self, warehouse: Warehouse) -> Warehouse: ...


class AbstractStockItemRepository(ABC):

    @abstractmethod
    async def create(self, item: StockItem) -> StockItem: ...

    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[StockItem]: ...

    @abstractmethod
    async def list_by_warehouse(self, warehouse_id: UUID, page: int, page_size: int) -> tuple[list[StockItem], int]: ...

    @abstractmethod
    async def list_by_farm(self, farm_id: UUID, page: int, page_size: int) -> tuple[list[StockItem], int]: ...

    @abstractmethod
    async def update(self, item: StockItem) -> StockItem: ...

    @abstractmethod
    async def list_below_minimum(self, farm_id: UUID) -> list[StockItem]: ...


class AbstractStockBatchRepository(ABC):

    @abstractmethod
    async def create(self, batch: StockBatch) -> StockBatch: ...

    @abstractmethod
    async def get_by_id(self, batch_id: UUID) -> Optional[StockBatch]: ...

    @abstractmethod
    async def list_available_fifo(self, stock_item_id: UUID) -> list[StockBatch]: ...

    @abstractmethod
    async def list_available_fefo(self, stock_item_id: UUID) -> list[StockBatch]: ...

    @abstractmethod
    async def update(self, batch: StockBatch) -> StockBatch: ...

    @abstractmethod
    async def list_expiring_soon(self, days: int) -> list[StockBatch]: ...


class AbstractStockMovementRepository(ABC):

    @abstractmethod
    async def create(self, movement: StockMovement) -> StockMovement: ...

    @abstractmethod
    async def list_by_item(
        self, stock_item_id: UUID, page: int, page_size: int
    ) -> tuple[list[StockMovement], int]: ...

"""
CreateStockItemUseCase: T-09-10. SF-12.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from app.application.dtos.inventory_dtos import CreateStockItemRequest, StockItemResponse
from app.domain.models.inventory import StockItem
from app.domain.repositories.stock_repository import AbstractStockItemRepository, AbstractWarehouseRepository
from shared.exceptions import EntityNotFoundError


class CreateStockItemUseCase:

    def __init__(
        self,
        warehouse_repo: AbstractWarehouseRepository,
        stock_item_repo: AbstractStockItemRepository,
    ) -> None:
        self._warehouse_repo = warehouse_repo
        self._stock_item_repo = stock_item_repo

    async def execute(self, req: CreateStockItemRequest) -> StockItemResponse:
        warehouse = await self._warehouse_repo.get_by_id(req.warehouse_id)
        if not warehouse:
            raise EntityNotFoundError("Warehouse", str(req.warehouse_id))

        item = StockItem()
        item.id = uuid4()
        item.warehouse_id = req.warehouse_id
        item.name = req.name
        item.item_type = req.item_type
        item.unit = req.unit
        item.current_quantity = Decimal("0")
        item.minimum_quantity = req.minimum_quantity
        item.unit_cost = req.unit_cost
        item.sku = req.sku
        item.is_active = True
        now = datetime.now(timezone.utc)
        item.created_at = now
        item.updated_at = now

        item = await self._stock_item_repo.create(item)
        return StockItemResponse.model_validate(item)

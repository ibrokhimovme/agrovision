"""
GetStockLevelUseCase: T-09-05, T-09-12. SF-12.
"""
from __future__ import annotations

import math
from uuid import UUID

from app.inventory.application.dtos.inventory_dtos import StockItemResponse
from app.inventory.domain.repositories.stock_repository import AbstractStockItemRepository


class GetStockLevelUseCase:

    def __init__(self, stock_item_repo: AbstractStockItemRepository) -> None:
        self._stock_item_repo = stock_item_repo

    async def execute(
        self, farm_id: UUID, page: int, page_size: int
    ) -> tuple[list[StockItemResponse], int]:
        items, total = await self._stock_item_repo.list_by_farm(farm_id, page, page_size)
        return [StockItemResponse.model_validate(i) for i in items], total

"""
ReceiveStockUseCase: T-09-03, T-09-11. UC-05, BP-09.
Creates a StockBatch, updates item's current_quantity, logs RECEIPT movement.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.inventory.application.dtos.inventory_dtos import ReceiveStockRequest, StockBatchResponse
from app.inventory.domain.models.inventory import MovementType, StockBatch, StockMovement
from app.inventory.domain.repositories.stock_repository import (
    AbstractStockBatchRepository,
    AbstractStockItemRepository,
    AbstractStockMovementRepository,
)
from shared.exceptions import EntityNotFoundError


class ReceiveStockUseCase:

    def __init__(
        self,
        stock_item_repo: AbstractStockItemRepository,
        stock_batch_repo: AbstractStockBatchRepository,
        movement_repo: AbstractStockMovementRepository,
    ) -> None:
        self._stock_item_repo = stock_item_repo
        self._stock_batch_repo = stock_batch_repo
        self._movement_repo = movement_repo

    async def execute(self, stock_item_id: str, req: ReceiveStockRequest) -> StockBatchResponse:
        from uuid import UUID
        item_uuid = UUID(str(stock_item_id))

        item = await self._stock_item_repo.get_by_id(item_uuid)
        if not item:
            raise EntityNotFoundError("StockItem", str(stock_item_id))

        now = datetime.now(timezone.utc)

        batch = StockBatch()
        batch.id = uuid4()
        batch.stock_item_id = item_uuid
        batch.batch_number = req.batch_number
        batch.quantity = req.quantity
        batch.remaining_quantity = req.quantity
        batch.unit_cost = req.unit_cost
        batch.received_at = now
        batch.expiry_date = req.expiry_date
        batch.supplier_id = req.supplier_id
        batch.created_at = now
        batch.updated_at = now

        batch = await self._stock_batch_repo.create(batch)

        # update running total on item
        item.current_quantity = item.current_quantity + req.quantity
        item.updated_at = now
        if req.unit_cost is not None:
            item.unit_cost = req.unit_cost
        await self._stock_item_repo.update(item)

        # immutable movement record
        movement = StockMovement()
        movement.id = uuid4()
        movement.stock_item_id = item_uuid
        movement.warehouse_id = item.warehouse_id
        movement.movement_type = MovementType.RECEIPT
        movement.quantity = req.quantity
        movement.unit = item.unit
        movement.unit_cost = req.unit_cost
        movement.purpose = "Stock receipt"
        movement.notes = req.notes
        movement.moved_at = now
        movement.created_at = now
        movement.updated_at = now
        await self._movement_repo.create(movement)

        return StockBatchResponse.model_validate(batch)

"""
DispatchStockUseCase: T-09-04. BP-09 FIFO/FEFO.
Depletes StockBatches in order (oldest-first or nearest-expiry-first),
logs DISPATCH movements, updates item current_quantity.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from app.application.dtos.inventory_dtos import DispatchResultResponse, DispatchStockRequest
from app.domain.models.inventory import MovementType, StockMovement
from app.domain.repositories.stock_repository import (
    AbstractStockBatchRepository,
    AbstractStockItemRepository,
    AbstractStockMovementRepository,
)
from shared.exceptions import BusinessRuleViolationError, EntityNotFoundError


class DispatchStockUseCase:

    def __init__(
        self,
        stock_item_repo: AbstractStockItemRepository,
        stock_batch_repo: AbstractStockBatchRepository,
        movement_repo: AbstractStockMovementRepository,
    ) -> None:
        self._stock_item_repo = stock_item_repo
        self._stock_batch_repo = stock_batch_repo
        self._movement_repo = movement_repo

    async def execute(self, stock_item_id: UUID, req: DispatchStockRequest) -> DispatchResultResponse:
        item = await self._stock_item_repo.get_by_id(stock_item_id)
        if not item:
            raise EntityNotFoundError("StockItem", str(stock_item_id))

        if item.current_quantity < req.quantity:
            raise BusinessRuleViolationError(
                rule="INSUFFICIENT_STOCK",
                message=f"Available: {item.current_quantity} {item.unit}, requested: {req.quantity}",
            )

        batches = (
            await self._stock_batch_repo.list_available_fefo(stock_item_id)
            if req.use_fefo
            else await self._stock_batch_repo.list_available_fifo(stock_item_id)
        )

        now = datetime.now(timezone.utc)
        remaining_to_dispatch = req.quantity
        movements_created = 0

        for batch in batches:
            if remaining_to_dispatch <= 0:
                break

            take = min(batch.remaining_quantity, remaining_to_dispatch)
            batch.remaining_quantity = batch.remaining_quantity - take
            batch.updated_at = now
            await self._stock_batch_repo.update(batch)

            movement = StockMovement()
            movement.id = uuid4()
            movement.stock_item_id = stock_item_id
            movement.warehouse_id = item.warehouse_id
            movement.movement_type = MovementType.DISPATCH
            movement.quantity = take
            movement.unit = item.unit
            movement.unit_cost = batch.unit_cost
            movement.purpose = req.purpose
            movement.reference_id = req.reference_id
            movement.reference_type = req.reference_type
            movement.notes = req.notes
            movement.moved_at = now
            movement.created_at = now
            movement.updated_at = now
            await self._movement_repo.create(movement)
            movements_created += 1

            remaining_to_dispatch -= take

        dispatched = req.quantity - remaining_to_dispatch
        item.current_quantity = item.current_quantity - dispatched
        item.updated_at = now
        await self._stock_item_repo.update(item)

        return DispatchResultResponse(
            dispatched_quantity=dispatched,
            stock_item_id=stock_item_id,
            remaining_stock=item.current_quantity,
            movements_created=movements_created,
        )

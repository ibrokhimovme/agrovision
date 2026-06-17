"""
CreateWarehouseUseCase: T-09-09. SF-13.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.application.dtos.inventory_dtos import CreateWarehouseRequest, WarehouseResponse
from app.domain.models.inventory import Warehouse
from app.domain.repositories.stock_repository import AbstractWarehouseRepository


class CreateWarehouseUseCase:

    def __init__(self, warehouse_repo: AbstractWarehouseRepository) -> None:
        self._warehouse_repo = warehouse_repo

    async def execute(self, req: CreateWarehouseRequest) -> WarehouseResponse:
        warehouse = Warehouse()
        warehouse.id = uuid4()
        warehouse.farm_id = req.farm_id
        warehouse.name = req.name
        warehouse.location = req.location
        warehouse.notes = req.notes
        warehouse.is_active = True
        now = datetime.now(timezone.utc)
        warehouse.created_at = now
        warehouse.updated_at = now

        warehouse = await self._warehouse_repo.create(warehouse)
        return WarehouseResponse.model_validate(warehouse)

"""
Warehouse endpoints. T-09-09, SF-13.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.application.dtos.inventory_dtos import CreateWarehouseRequest, WarehouseResponse
from app.inventory.application.use_cases.create_warehouse import CreateWarehouseUseCase
from app.inventory.infrastructure.database.repositories.stock_repository_impl import SQLAlchemyWarehouseRepository
from app.inventory.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse

router = APIRouter()


@router.post(
    "/warehouses/",
    response_model=APIResponse[WarehouseResponse],
    status_code=201,
    tags=["Warehouses"],
)
async def create_warehouse(
    body: CreateWarehouseRequest,
    db: AsyncSession = Depends(get_db),
):
    warehouse_repo = SQLAlchemyWarehouseRepository(db)
    result = await CreateWarehouseUseCase(warehouse_repo).execute(body)
    return APIResponse(data=result)


@router.get(
    "/warehouses/",
    response_model=APIResponse[list[WarehouseResponse]],
    tags=["Warehouses"],
)
async def list_warehouses(
    farm_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    warehouse_repo = SQLAlchemyWarehouseRepository(db)
    warehouses = await warehouse_repo.list_by_farm(farm_id)
    return APIResponse(data=[WarehouseResponse.model_validate(w) for w in warehouses])

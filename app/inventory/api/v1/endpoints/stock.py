"""
Stock item endpoints. T-09-10 through T-09-13, SF-12.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.application.dtos.inventory_dtos import (
    CreateStockItemRequest,
    DispatchResultResponse,
    DispatchStockRequest,
    ReceiveStockRequest,
    StockBatchResponse,
    StockItemResponse,
    StockMovementResponse,
)
from app.inventory.application.use_cases.create_stock_item import CreateStockItemUseCase
from app.inventory.application.use_cases.dispatch_stock import DispatchStockUseCase
from app.inventory.application.use_cases.get_stock_level import GetStockLevelUseCase
from app.inventory.application.use_cases.receive_stock import ReceiveStockUseCase
from app.inventory.infrastructure.database.repositories.stock_repository_impl import (
    SQLAlchemyStockBatchRepository,
    SQLAlchemyStockItemRepository,
    SQLAlchemyStockMovementRepository,
    SQLAlchemyWarehouseRepository,
)
from app.inventory.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/stock-items/",
    response_model=APIResponse[StockItemResponse],
    status_code=201,
    tags=["Stock"],
)
async def create_stock_item(
    body: CreateStockItemRequest,
    db: AsyncSession = Depends(get_db),
):
    warehouse_repo = SQLAlchemyWarehouseRepository(db)
    stock_item_repo = SQLAlchemyStockItemRepository(db)
    result = await CreateStockItemUseCase(warehouse_repo, stock_item_repo).execute(body)
    return APIResponse(data=result)


@router.get(
    "/stock-items/",
    response_model=PaginatedResponse[StockItemResponse],
    tags=["Stock"],
)
async def list_stock_items(
    farm_id: UUID = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stock_item_repo = SQLAlchemyStockItemRepository(db)
    items, total = await GetStockLevelUseCase(stock_item_repo).execute(farm_id, page, page_size)

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
    return PaginatedResponse(data=items, pagination=pagination)


@router.post(
    "/stock-items/{item_id}/receive",
    response_model=APIResponse[StockBatchResponse],
    status_code=201,
    tags=["Stock"],
)
async def receive_stock(
    item_id: UUID,
    body: ReceiveStockRequest,
    db: AsyncSession = Depends(get_db),
):
    stock_item_repo = SQLAlchemyStockItemRepository(db)
    stock_batch_repo = SQLAlchemyStockBatchRepository(db)
    movement_repo = SQLAlchemyStockMovementRepository(db)
    result = await ReceiveStockUseCase(stock_item_repo, stock_batch_repo, movement_repo).execute(item_id, body)
    return APIResponse(data=result)


@router.post(
    "/stock-items/{item_id}/dispatch",
    response_model=APIResponse[DispatchResultResponse],
    tags=["Stock"],
)
async def dispatch_stock(
    item_id: UUID,
    body: DispatchStockRequest,
    db: AsyncSession = Depends(get_db),
):
    stock_item_repo = SQLAlchemyStockItemRepository(db)
    stock_batch_repo = SQLAlchemyStockBatchRepository(db)
    movement_repo = SQLAlchemyStockMovementRepository(db)
    result = await DispatchStockUseCase(stock_item_repo, stock_batch_repo, movement_repo).execute(item_id, body)
    return APIResponse(data=result)


@router.get(
    "/stock-items/{item_id}/movements",
    response_model=PaginatedResponse[StockMovementResponse],
    tags=["Stock"],
)
async def list_movements(
    item_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    movement_repo = SQLAlchemyStockMovementRepository(db)
    movements, total = await movement_repo.list_by_item(item_id, page, page_size)

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
    return PaginatedResponse(
        data=[StockMovementResponse.model_validate(m) for m in movements],
        pagination=pagination,
    )

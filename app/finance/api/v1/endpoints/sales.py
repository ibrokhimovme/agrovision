"""
Sales endpoints. T-11-04, T-11-05. SF-17.
Routes under /sales/ prefix to avoid collision with /batches/ (livestock-service).
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.application.dtos.sale_dtos import (
    BatchSalesSummaryResponse,
    RecordSalePaymentRequest,
    RecordSaleRequest,
    SaleRecordResponse,
)
from app.finance.application.use_cases.record_sale import RecordSaleUseCase
from app.finance.application.use_cases.record_sale_payment import RecordSalePaymentUseCase
from app.finance.infrastructure.database.repositories.sale_repository_impl import SQLAlchemySaleRepository
from app.finance.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/sales/batch/{batch_id}",
    response_model=APIResponse[SaleRecordResponse],
    status_code=201,
    tags=["Sales"],
)
async def record_sale(
    batch_id: UUID,
    body: RecordSaleRequest,
    db: AsyncSession = Depends(get_db),
):
    sale_repo = SQLAlchemySaleRepository(db)
    result = await RecordSaleUseCase(sale_repo).execute(batch_id, body)
    return APIResponse(data=result)


@router.get(
    "/sales/batch/{batch_id}",
    response_model=PaginatedResponse[SaleRecordResponse],
    tags=["Sales"],
)
async def list_batch_sales(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    sale_repo = SQLAlchemySaleRepository(db)
    sales, total = await sale_repo.list_by_batch(batch_id, page, page_size)

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
        data=[SaleRecordResponse.model_validate(s) for s in sales],
        pagination=pagination,
    )


@router.get(
    "/sales/batch/{batch_id}/summary",
    response_model=APIResponse[BatchSalesSummaryResponse],
    tags=["Sales"],
)
async def batch_sales_summary(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    sale_repo = SQLAlchemySaleRepository(db)
    total_revenue = await sale_repo.total_revenue_by_batch(batch_id)
    _, count = await sale_repo.list_by_batch(batch_id, page=1, page_size=1)
    return APIResponse(data=BatchSalesSummaryResponse(
        batch_id=batch_id,
        total_revenue_uzs=total_revenue,
        sale_count=count,
    ))


@router.patch(
    "/sales/{sale_id}/payment",
    response_model=APIResponse[SaleRecordResponse],
    tags=["Sales"],
)
async def record_sale_payment(
    sale_id: UUID,
    body: RecordSalePaymentRequest,
    db: AsyncSession = Depends(get_db),
):
    sale_repo = SQLAlchemySaleRepository(db)
    result = await RecordSalePaymentUseCase(sale_repo).execute(sale_id, body)
    return APIResponse(data=result)

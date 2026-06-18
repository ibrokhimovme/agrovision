"""
Expense endpoints. T-10-08, T-10-09, T-10-10. SF-14, SF-15, FG-01.
"""
from __future__ import annotations

import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.application.dtos.expense_dtos import (
    BatchCostSummaryResponse,
    ExpenseResponse,
    RecordExpensePaymentRequest,
    RecordManualExpenseRequest,
)
from app.finance.application.use_cases.get_batch_cost_summary import GetBatchCostSummaryUseCase
from app.finance.application.use_cases.record_expense_payment import RecordExpensePaymentUseCase
from app.finance.application.use_cases.record_manual_expense import RecordManualExpenseUseCase
from app.finance.infrastructure.database.repositories.expense_repository_impl import SQLAlchemyExpenseRepository
from app.finance.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse, PaginatedResponse, PaginationMeta

router = APIRouter()


@router.post(
    "/expenses/",
    response_model=APIResponse[ExpenseResponse],
    status_code=201,
    tags=["Expenses"],
)
async def record_expense(
    body: RecordManualExpenseRequest,
    db: AsyncSession = Depends(get_db),
):
    expense_repo = SQLAlchemyExpenseRepository(db)
    result = await RecordManualExpenseUseCase(expense_repo).execute(body)
    return APIResponse(data=result)


@router.get(
    "/expenses/batch/{batch_id}",
    response_model=PaginatedResponse[ExpenseResponse],
    tags=["Expenses"],
)
async def list_batch_expenses(
    batch_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    expense_repo = SQLAlchemyExpenseRepository(db)
    expenses, total = await expense_repo.list_by_batch(batch_id, page, page_size)

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
        data=[ExpenseResponse.model_validate(e) for e in expenses],
        pagination=pagination,
    )


@router.get(
    "/expenses/batch/{batch_id}/cost-summary",
    response_model=APIResponse[BatchCostSummaryResponse],
    tags=["Expenses"],
)
async def batch_cost_summary(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    expense_repo = SQLAlchemyExpenseRepository(db)
    summary = await GetBatchCostSummaryUseCase(expense_repo).execute(batch_id)
    return APIResponse(data=summary)


@router.patch(
    "/expenses/{expense_id}/payment",
    response_model=APIResponse[ExpenseResponse],
    tags=["Expenses"],
)
async def record_expense_payment(
    expense_id: UUID,
    body: RecordExpensePaymentRequest,
    db: AsyncSession = Depends(get_db),
):
    expense_repo = SQLAlchemyExpenseRepository(db)
    result = await RecordExpensePaymentUseCase(expense_repo).execute(expense_id, body)
    return APIResponse(data=result)

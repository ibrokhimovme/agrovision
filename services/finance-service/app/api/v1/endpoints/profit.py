"""
Profit analysis endpoints. P-12, SF-18.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.profit_dtos import BatchProfitResponse
from app.application.use_cases.calculate_batch_profit import CalculateBatchProfitUseCase
from app.infrastructure.database.repositories.expense_repository_impl import SQLAlchemyExpenseRepository
from app.infrastructure.database.repositories.sale_repository_impl import SQLAlchemySaleRepository
from app.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse

router = APIRouter()


@router.get(
    "/profit/batch/{batch_id}",
    response_model=APIResponse[BatchProfitResponse],
    tags=["Profit"],
)
async def batch_profit(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    expense_repo = SQLAlchemyExpenseRepository(db)
    sale_repo = SQLAlchemySaleRepository(db)
    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(batch_id)
    return APIResponse(data=result)

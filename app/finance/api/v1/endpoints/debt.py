"""
Debtor/creditor summary endpoint. EX-11 (Finance Improvements,
execution-v2) — "show debtor/creditor summary in Finance" per
decision_log.md BMD-015.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.application.dtos.debt_dtos import DebtorCreditorSummaryResponse
from app.finance.application.use_cases.get_debtor_creditor_summary import (
    GetDebtorCreditorSummaryUseCase,
)
from app.finance.infrastructure.database.repositories.expense_repository_impl import SQLAlchemyExpenseRepository
from app.finance.infrastructure.database.repositories.sale_repository_impl import SQLAlchemySaleRepository
from app.finance.infrastructure.database.repositories.supplier_repository_impl import (
    SQLAlchemySupplierRepository,
)
from app.finance.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse

router = APIRouter()


@router.get(
    "/debtors-creditors-summary",
    response_model=APIResponse[DebtorCreditorSummaryResponse],
    tags=["Finance"],
)
async def debtors_creditors_summary(
    farm_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    sale_repo = SQLAlchemySaleRepository(db)
    expense_repo = SQLAlchemyExpenseRepository(db)
    supplier_repo = SQLAlchemySupplierRepository(db)
    use_case = GetDebtorCreditorSummaryUseCase(sale_repo, expense_repo, supplier_repo)
    result = await use_case.execute(farm_id)
    return APIResponse(data=result)

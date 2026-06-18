"""
RecordExpensePaymentUseCase: EX-11 (Finance Improvements, execution-v2).
Records an additional payment against an existing expense (the farm paying
off a supplier debt over time) — per decision_log.md BMD-015.
"""
from __future__ import annotations

from uuid import UUID

from app.finance.application.dtos.expense_dtos import ExpenseResponse, RecordExpensePaymentRequest
from app.finance.domain.repositories.expense_repository import AbstractExpenseRepository
from shared.exceptions import EntityNotFoundError


class RecordExpensePaymentUseCase:

    def __init__(self, expense_repo: AbstractExpenseRepository) -> None:
        self._expense_repo = expense_repo

    async def execute(self, expense_id: UUID, req: RecordExpensePaymentRequest) -> ExpenseResponse:
        expense = await self._expense_repo.get_by_id(expense_id)
        if expense is None:
            raise EntityNotFoundError("Expense", expense_id)

        expense.amount_paid = min(expense.amount_paid + req.amount, expense.amount)

        expense = await self._expense_repo.update(expense)
        return ExpenseResponse.model_validate(expense)

"""
RecordManualExpenseUseCase: T-10-06. SF-14, BP-11.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.application.dtos.expense_dtos import ExpenseResponse, RecordManualExpenseRequest
from app.domain.models.finance import Expense
from app.domain.repositories.expense_repository import AbstractExpenseRepository


class RecordManualExpenseUseCase:

    def __init__(self, expense_repo: AbstractExpenseRepository) -> None:
        self._expense_repo = expense_repo

    async def execute(self, req: RecordManualExpenseRequest) -> ExpenseResponse:
        now = datetime.now(timezone.utc)

        expense = Expense()
        expense.id = uuid4()
        expense.farm_id = req.farm_id
        expense.batch_id = req.batch_id
        expense.category = req.category
        expense.expense_type = req.expense_type
        expense.description = req.description
        expense.amount = req.amount
        expense.currency = req.currency
        expense.expense_date = req.expense_date or now
        expense.reference_document = req.reference_document
        expense.notes = req.notes
        expense.created_at = now
        expense.updated_at = now

        expense = await self._expense_repo.create(expense)
        return ExpenseResponse.model_validate(expense)

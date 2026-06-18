"""
GetBatchCostSummaryUseCase: T-10-07. FG-01, SF-15.
Returns total cost and per-type breakdown for a batch.
"""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.finance.application.dtos.expense_dtos import BatchCostSummaryResponse
from app.finance.domain.repositories.expense_repository import AbstractExpenseRepository


class GetBatchCostSummaryUseCase:

    def __init__(self, expense_repo: AbstractExpenseRepository) -> None:
        self._expense_repo = expense_repo

    async def execute(self, batch_id: UUID) -> BatchCostSummaryResponse:
        total = await self._expense_repo.total_by_batch(batch_id)
        by_type = await self._expense_repo.sum_by_batch_and_type(batch_id)

        # count total expenses
        _, count = await self._expense_repo.list_by_batch(batch_id, page=1, page_size=1)

        breakdown = {t.value: amt for t, amt in by_type.items()}

        return BatchCostSummaryResponse(
            batch_id=batch_id,
            total_uzs=total,
            breakdown=breakdown,
            expense_count=count,
        )

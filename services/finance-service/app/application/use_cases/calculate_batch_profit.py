"""
CalculateBatchProfitUseCase: P-12, SF-18.
gross_profit = total_revenue - total_cost
profit_margin = gross_profit / total_revenue * 100  (0 if no revenue)
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from app.application.dtos.profit_dtos import BatchProfitResponse
from app.domain.repositories.expense_repository import AbstractExpenseRepository
from app.domain.repositories.sale_repository import AbstractSaleRepository


class CalculateBatchProfitUseCase:

    def __init__(
        self,
        expense_repo: AbstractExpenseRepository,
        sale_repo: AbstractSaleRepository,
    ) -> None:
        self._expense_repo = expense_repo
        self._sale_repo = sale_repo

    async def execute(self, batch_id: UUID) -> BatchProfitResponse:
        total_revenue = await self._sale_repo.total_revenue_by_batch(batch_id)
        total_cost = await self._expense_repo.total_by_batch(batch_id)

        gross_profit = total_revenue - total_cost

        if total_revenue > Decimal("0"):
            profit_margin = (gross_profit / total_revenue * Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            profit_margin = Decimal("0.00")

        _, sale_count = await self._sale_repo.list_by_batch(batch_id, page=1, page_size=1)
        _, expense_count = await self._expense_repo.list_by_batch(batch_id, page=1, page_size=1)

        return BatchProfitResponse(
            batch_id=batch_id,
            total_revenue_uzs=total_revenue,
            total_cost_uzs=total_cost,
            gross_profit_uzs=gross_profit,
            profit_margin_pct=profit_margin,
            sale_count=sale_count,
            expense_count=expense_count,
        )

"""
GetFarmComparisonUseCase: EX-12 (execution-v2) — farm-to-farm comparison.
Aggregates each farm's batch performance data into one summary row per farm.
"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from uuid import UUID

from app.reporting.application.dtos.report_dtos import BatchReportResponse, FarmComparisonRow
from app.reporting.application.use_cases.get_farm_batch_performance import (
    GetFarmBatchPerformanceUseCase,
)
from app.reporting.infrastructure.clients.finance_client import FinanceClient
from app.reporting.infrastructure.clients.livestock_client import LivestockClient


def _avg(values: list[Decimal]) -> Decimal | None:
    if not values:
        return None
    return sum(values, Decimal("0")) / len(values)


def _sum_optional(values: list[Decimal | None]) -> Decimal | None:
    present = [v for v in values if v is not None]
    if not present:
        return None
    return sum(present, Decimal("0"))


def _aggregate(farm_id: UUID, reports: list[BatchReportResponse]) -> FarmComparisonRow:
    fcrs = [r.fcr for r in reports if r.fcr is not None]
    mortality_rates = [r.mortality_rate_pct for r in reports if r.mortality_rate_pct is not None]
    margins = [r.profit_margin_pct for r in reports if r.profit_margin_pct is not None]
    total_revenue = _sum_optional([r.total_revenue_uzs for r in reports])
    total_cost = _sum_optional([r.total_cost_uzs for r in reports])
    total_profit = (
        total_revenue - total_cost if total_revenue is not None and total_cost is not None else None
    )

    return FarmComparisonRow(
        farm_id=farm_id,
        batch_count=len(reports),
        avg_fcr=_avg(fcrs),
        avg_mortality_rate_pct=_avg(mortality_rates),
        total_feed_kg=_sum_optional([r.total_feed_kg for r in reports]),
        total_revenue_uzs=total_revenue,
        total_cost_uzs=total_cost,
        total_profit_uzs=total_profit,
        avg_profit_margin_pct=_avg(margins),
    )


class GetFarmComparisonUseCase:

    def __init__(
        self,
        livestock_client: LivestockClient,
        finance_client: FinanceClient,
    ) -> None:
        self._livestock = livestock_client
        self._finance = finance_client

    async def execute(self, farm_ids: list[UUID], archived: str = "false") -> list[FarmComparisonRow]:
        per_farm_use_case = GetFarmBatchPerformanceUseCase(self._livestock, self._finance)
        all_reports = await asyncio.gather(
            *(per_farm_use_case.execute(farm_id, archived) for farm_id in farm_ids)
        )
        return [
            _aggregate(farm_id, reports)
            for farm_id, reports in zip(farm_ids, all_reports)
        ]

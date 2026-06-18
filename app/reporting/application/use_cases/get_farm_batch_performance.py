"""
GetFarmBatchPerformanceUseCase: EX-12 (execution-v2) — Cross-Batch Trend
Reporting. Batch performance comparison, mortality/weight/feed/revenue-profit
trends are all views over the same per-batch report data, ordered
chronologically by placement date.
"""
from __future__ import annotations

import asyncio
from uuid import UUID

from app.reporting.application.dtos.report_dtos import BatchReportResponse
from app.reporting.application.use_cases.generate_batch_report import GenerateBatchReportUseCase
from app.reporting.infrastructure.clients.finance_client import FinanceClient
from app.reporting.infrastructure.clients.livestock_client import LivestockClient


class GetFarmBatchPerformanceUseCase:

    def __init__(
        self,
        livestock_client: LivestockClient,
        finance_client: FinanceClient,
    ) -> None:
        self._livestock = livestock_client
        self._finance = finance_client

    async def execute(self, farm_id: UUID, archived: str = "false") -> list[BatchReportResponse]:
        batches = await self._livestock.list_batches(farm_id, archived)
        report_use_case = GenerateBatchReportUseCase(self._livestock, self._finance)
        reports = await asyncio.gather(
            *(report_use_case.execute(UUID(b["id"])) for b in batches)
        )
        return sorted(reports, key=lambda r: r.placement_date)

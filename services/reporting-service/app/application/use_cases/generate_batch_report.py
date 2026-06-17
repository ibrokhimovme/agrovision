"""
GenerateBatchReportUseCase: T-14-03. SF-21.
Aggregates batch data from livestock-service and finance-service.
All downstream calls run concurrently via asyncio.gather.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.application.dtos.report_dtos import BatchReportResponse
from app.infrastructure.clients.finance_client import FinanceClient
from app.infrastructure.clients.livestock_client import LivestockClient
from shared.exceptions import EntityNotFoundError


class GenerateBatchReportUseCase:

    def __init__(
        self,
        livestock_client: LivestockClient,
        finance_client: FinanceClient,
    ) -> None:
        self._livestock = livestock_client
        self._finance = finance_client

    async def execute(self, batch_id: UUID) -> BatchReportResponse:
        # Fetch all data concurrently
        batch, weight_metrics, feed_summary, mortality_summary, cost_summary, profit, sales_summary = (
            await asyncio.gather(
                self._livestock.get_batch(batch_id),
                self._livestock.get_weight_metrics(batch_id),
                self._livestock.get_feed_summary(batch_id),
                self._livestock.get_mortality_summary(batch_id),
                self._finance.get_cost_summary(batch_id),
                self._finance.get_profit(batch_id),
                self._finance.get_sales_summary(batch_id),
                return_exceptions=False,
            )
        )

        if batch is None:
            raise EntityNotFoundError("Batch", str(batch_id))

        def _dec(d: dict | None, key: str) -> Decimal | None:
            if d is None:
                return None
            v = d.get(key)
            return Decimal(str(v)) if v is not None else None

        def _int(d: dict | None, key: str) -> int | None:
            if d is None:
                return None
            v = d.get(key)
            return int(v) if v is not None else None

        return BatchReportResponse(
            batch_id=batch_id,
            generated_at=datetime.now(timezone.utc),

            batch_code=batch.get("batch_code"),
            farm_id=UUID(batch["farm_id"]),
            species=batch.get("species", ""),
            initial_count=batch.get("initial_count", 0),
            current_count=batch.get("current_count", 0),
            status=batch.get("status", ""),
            placement_date=batch.get("placement_date", ""),
            age_days=_int(batch, "age_days"),

            fcr=_dec(weight_metrics, "fcr"),
            adg_grams=_dec(weight_metrics, "adg_grams"),
            latest_avg_weight_kg=_dec(weight_metrics, "latest_avg_weight_kg"),

            total_feed_kg=_dec(feed_summary, "total_feed_kg"),
            total_water_liters=_dec(feed_summary, "total_water_liters"),

            total_deaths=_int(mortality_summary, "total_deaths"),
            mortality_rate_pct=_dec(mortality_summary, "mortality_rate_pct"),
            survival_rate_pct=_dec(mortality_summary, "survival_rate_pct"),

            total_cost_uzs=_dec(cost_summary, "total_uzs"),
            total_revenue_uzs=_dec(profit, "total_revenue_uzs"),
            gross_profit_uzs=_dec(profit, "gross_profit_uzs"),
            profit_margin_pct=_dec(profit, "profit_margin_pct"),
            sale_count=_int(profit, "sale_count"),
            expense_count=_int(profit, "expense_count"),
        )

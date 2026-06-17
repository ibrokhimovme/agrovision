"""
HTTP client for finance-service. T-14-02. SF-21.
Fetches cost summary and profit data.
"""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

import httpx

from app.core.config import settings


class FinanceClient:

    def __init__(self) -> None:
        self._base = f"{settings.FINANCE_SERVICE_URL}/api/v1"

    async def get_cost_summary(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/expenses/batch/{batch_id}/cost-summary")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_profit(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/profit/batch/{batch_id}")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_sales_summary(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/sales/batch/{batch_id}/summary")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

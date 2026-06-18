"""
In-process client for the finance module. T-14-02. SF-21.
Fetches cost summary and profit data.

M5: was an httpx call over the network to finance-service
(settings.FINANCE_SERVICE_URL). Now uses httpx.ASGITransport to call the
same /api/v1/expenses|profit|sales/... routes in-process against the single
monolith FastAPI app, with zero network hop. See livestock_client.py for the
full rationale (identical pattern).
"""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

import httpx


def _client() -> httpx.AsyncClient:
    # Uses fastapi_app (no JWT middleware), not the externally-served `app` —
    # see app/main.py's module docstring: this mirrors the old direct
    # service-to-service httpx call, which also bypassed the gateway/JWT layer.
    from app.main import fastapi_app
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=fastapi_app),
        base_url="http://internal/api/v1",
        timeout=10.0,
    )


class FinanceClient:

    async def get_cost_summary(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with _client() as client:
            resp = await client.get(f"/expenses/batch/{batch_id}/cost-summary")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_profit(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with _client() as client:
            resp = await client.get(f"/profit/batch/{batch_id}")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_sales_summary(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with _client() as client:
            resp = await client.get(f"/sales/batch/{batch_id}/summary")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

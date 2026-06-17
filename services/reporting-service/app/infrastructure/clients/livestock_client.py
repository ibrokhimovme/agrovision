"""
HTTP client for livestock-service. T-14-01. SF-21.
Fetches batch data, weight metrics, feed summary, mortality summary.
"""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

import httpx

from app.core.config import settings


class LivestockClient:

    def __init__(self) -> None:
        self._base = f"{settings.LIVESTOCK_SERVICE_URL}/api/v1"

    async def get_batch(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/batches/{batch_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_weight_metrics(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/batches/{batch_id}/weight/metrics")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_feed_summary(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/batches/{batch_id}/feed/summary")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_mortality_summary(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base}/batches/{batch_id}/mortality/summary")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

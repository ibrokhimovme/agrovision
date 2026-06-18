"""
In-process client for the poultry module. T-14-01. SF-21.
Fetches batch data, weight metrics, feed summary, mortality summary.

M5: was an httpx call over the network to livestock-service
(settings.LIVESTOCK_SERVICE_URL). Now uses httpx.ASGITransport to call the
same /api/v1/batches/... routes in-process against the single monolith
FastAPI app, with zero network hop. Response parsing (.json().get("data"),
status-code handling) is unchanged — only the transport changed, so this
class's external behavior (return values, exceptions) is identical.
The import of app.main is deferred to call time to avoid a circular import
(app.main mounts this module's router, which imports this client).
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


class LivestockClient:

    async def get_batch(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with _client() as client:
            resp = await client.get(f"/batches/{batch_id}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_weight_metrics(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with _client() as client:
            resp = await client.get(f"/batches/{batch_id}/weight/metrics")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_feed_summary(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with _client() as client:
            resp = await client.get(f"/batches/{batch_id}/feed/summary")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

    async def get_mortality_summary(self, batch_id: UUID) -> Optional[dict[str, Any]]:
        async with _client() as client:
            resp = await client.get(f"/batches/{batch_id}/mortality/summary")
            if resp.status_code in (404, 422):
                return None
            resp.raise_for_status()
            return resp.json().get("data")

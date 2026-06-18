"""
In-process client for the farm module. EX-15 (execution-v2): used to
validate that a farm belongs to the caller's account before letting that
account create/list users scoped to it (cross-account user-management
denial, decision_log.md BMD-017).

Same in-process ASGI pattern as app/reporting/infrastructure/clients/
livestock_client.py — zero network hop, calls the same /api/v1/farms/...
routes against the single monolith FastAPI app. Unlike reporting's clients,
this one must forward the caller's X-Account-Id/X-User-Roles headers,
because GET /farms/{id} is itself account-scoped (EX-02) and returns 404
for anyone outside the farm's account, including an internal caller with
no headers at all.
"""
from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

import httpx


def _client() -> httpx.AsyncClient:
    from app.main import fastapi_app
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=fastapi_app),
        base_url="http://internal/api/v1",
        timeout=10.0,
    )


class FarmClient:

    async def get_farm(
        self, farm_id: UUID, account_id: str, user_roles: str
    ) -> Optional[dict[str, Any]]:
        async with _client() as client:
            resp = await client.get(
                f"/farms/{farm_id}",
                headers={"X-Account-Id": account_id, "X-User-Roles": user_roles},
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json().get("data")

"""
API Gateway v1 router — reverse-proxy to downstream services.
Routes are prefixed by domain and forwarded with user context headers.
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.core.config import settings
from app.middleware.auth import verify_token

router = APIRouter()

ROUTE_MAP = {
    "/auth": settings.IDENTITY_SERVICE_URL,
    "/users": settings.IDENTITY_SERVICE_URL,
    "/roles": settings.IDENTITY_SERVICE_URL,
    "/farms": settings.FARM_SERVICE_URL,
    "/buildings": settings.FARM_SERVICE_URL,
    "/animals": settings.LIVESTOCK_SERVICE_URL,
    "/batches": settings.LIVESTOCK_SERVICE_URL,
    "/vaccinations": settings.LIVESTOCK_SERVICE_URL,
    "/health-records": settings.LIVESTOCK_SERVICE_URL,
    "/mortality": settings.LIVESTOCK_SERVICE_URL,
    "/slaughter": settings.LIVESTOCK_SERVICE_URL,
    "/warehouses": settings.INVENTORY_SERVICE_URL,
    "/inventory": settings.INVENTORY_SERVICE_URL,
    "/expenses": settings.FINANCE_SERVICE_URL,
    "/revenue": settings.FINANCE_SERVICE_URL,
    "/payments": settings.FINANCE_SERVICE_URL,
    "/notifications": settings.NOTIFICATION_SERVICE_URL,
    "/reports": settings.REPORTING_SERVICE_URL,
}


def _resolve_target(path: str) -> str | None:
    for prefix, base_url in ROUTE_MAP.items():
        if path.startswith(prefix):
            return base_url
    return None


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
async def proxy(
    path: str,
    request: Request,
    token_payload: dict | None = Depends(verify_token),
):
    target_base = _resolve_target(f"/{path}")
    if target_base is None:
        return Response(
            content='{"error":"Route not found"}',
            status_code=404,
            media_type="application/json",
        )

    url = f"{target_base}/api/v1/{path}"
    headers = dict(request.headers)
    headers.pop("host", None)

    if token_payload:
        headers["X-User-Id"] = str(token_payload.get("sub", ""))
        headers["X-User-Roles"] = ",".join(token_payload.get("roles", []))
        headers["X-Farm-Id"] = str(token_payload.get("farm_id", ""))

    body = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.headers.get("content-type", "application/json"),
    )

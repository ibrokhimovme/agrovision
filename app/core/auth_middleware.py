"""
M5 — single app-wide JWT verification, replacing the gateway's per-request
reverse-proxy header injection (app/gateway/api/v1/router.py + middleware/auth.py).

Behavior is preserved exactly: verify the bearer JWT (with Redis blacklist
check), then inject X-User-Id / X-User-Roles / X-Farm-Id into the request
before it reaches a module's router — every module's endpoints already read
these via `Header(...)` dependencies (carried over unchanged from the
microservices, per the anti-destruction/no-rewrite principle of this
migration), so this is the only place that needed new code.
"""
from __future__ import annotations

from typing import Optional

import redis.asyncio as aioredis
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings

UNPROTECTED_PATHS = {
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/docs",
    "/redoc",
    "/openapi.json",
}

_redis: Optional[aioredis.Redis] = None


def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def verify_token(request: Request) -> Optional[dict]:
    """Identical logic to app/gateway/middleware/auth.py:verify_token."""
    if request.url.path in UNPROTECTED_PATHS:
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "AUTH_001", "message": "Missing or invalid Authorization header"},
        )

    token = auth_header.split(" ", 1)[1]

    redis = _get_redis()
    is_blacklisted = await redis.exists(f"blacklist:{token}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "AUTH_002", "message": "Token has been revoked"},
        )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "AUTH_003", "message": "Token is invalid or expired"},
        )

    return payload


class AuthHeaderInjectionMiddleware:
    """
    Pure ASGI middleware (not BaseHTTPMiddleware, to avoid double-buffering
    the request body): verifies the JWT, then rewrites scope["headers"] in
    place so every downstream router sees X-User-Id/X-User-Roles/X-Farm-Id
    exactly as if the old gateway proxy had set them.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        try:
            payload = await verify_token(request)
        except HTTPException as exc:
            response = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
            await response(scope, receive, send)
            return

        if payload:
            injected = {
                b"x-user-id": str(payload.get("sub", "")).encode(),
                b"x-user-roles": ",".join(payload.get("roles", [])).encode(),
                b"x-farm-id": str(payload.get("farm_id", "")).encode(),
                # EX-02 (execution-v2): account_id is None for an
                # account-less user (e.g. platform super-admin), so this
                # uses `or ""` rather than `str(...)` to avoid encoding the
                # literal text "None" into the header — unlike x-farm-id
                # above (a pre-existing, currently-unconsumed header left
                # unchanged here, out of this phase's scope), x-account-id
                # IS parsed downstream by app/farm's endpoints, so the
                # "None"-string quirk would be a real bug here, not a latent
                # no-op.
                b"x-account-id": (payload.get("account_id") or "").encode(),
            }
            headers = [(k, v) for k, v in scope["headers"] if k.lower() not in injected]
            headers.extend(injected.items())
            scope["headers"] = headers

        await self.app(scope, receive, send)

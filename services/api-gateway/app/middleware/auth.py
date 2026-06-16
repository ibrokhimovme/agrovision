"""
JWT verification middleware for the API Gateway.
Verifies token signature, expiry, and Redis blacklist before forwarding.
Downstream services trust X-User-Id / X-User-Roles headers — they do not re-verify JWT.

SRS §5.1, §11 (Security NFRs). ADR-002: JWT verified at gateway only.
"""
from __future__ import annotations

from typing import Optional

import redis.asyncio as aioredis
from fastapi import Request, HTTPException, status
from jose import JWTError, jwt

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
    """
    Extracts and verifies JWT. Returns decoded payload or raises 401.
    Also checks Redis blacklist (for logged-out tokens).
    """
    if request.url.path in UNPROTECTED_PATHS:
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "AUTH_001", "message": "Missing or invalid Authorization header"},
        )

    token = auth_header.split(" ", 1)[1]

    # Check blacklist (logged-out tokens)
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

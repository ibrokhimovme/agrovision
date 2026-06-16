"""
JWT verification middleware for the API Gateway.
Verifies token signature and injects X-User-Id / X-User-Roles headers
before forwarding the request to downstream services.
Downstream services trust these headers — they do not re-verify JWT.

Security note: This is the single point of JWT verification.
All services sit behind the gateway and must not be exposed directly.
"""

from __future__ import annotations

from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

_bearer_scheme = HTTPBearer(auto_error=False)


async def verify_token(request: Request) -> Optional[dict]:
    """
    Extracts and verifies JWT from Authorization: Bearer <token>.
    Returns decoded payload or raises 401.
    Public paths (see UNPROTECTED_PATHS) bypass this check.
    """
    UNPROTECTED_PATHS = {"/health", "/api/v1/auth/login", "/api/v1/auth/refresh", "/docs", "/redoc", "/openapi.json"}
    if request.url.path in UNPROTECTED_PATHS:
        return None

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "AUTH_001", "message": "Missing or invalid Authorization header"},
        )

    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "AUTH_003", "message": "Token is invalid or expired"},
        )

    return payload

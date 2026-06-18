"""
FastAPI dependency providers for the Identity Service.
Other services use the same pattern: extract X-User-Id / X-User-Roles
headers injected by the API Gateway (they do not re-verify JWT here).
"""
from __future__ import annotations

from uuid import UUID

from fastapi import Header, HTTPException, status


async def get_current_user_id(x_user_id: str = Header(...)) -> UUID:
    try:
        return UUID(x_user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user context")


async def get_current_user_roles(x_user_roles: str = Header(default="")) -> list[str]:
    return [r.strip() for r in x_user_roles.split(",") if r.strip()]

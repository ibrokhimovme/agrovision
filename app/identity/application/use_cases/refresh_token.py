from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.identity.core.config import settings
from app.identity.domain.repositories.user_repository import AbstractUserRepository
from shared.exceptions import AuthenticationError


class RefreshTokenUseCase:

    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, refresh_token: str) -> dict:
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except JWTError:
            raise AuthenticationError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise AuthenticationError("Token type mismatch")

        from uuid import UUID
        user_id = UUID(payload["sub"])
        user = await self._user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        now = datetime.now(timezone.utc)
        roles = [r.name for r in user.roles]
        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "roles": roles,
            "farm_id": str(user.farm_id) if user.farm_id else None,
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "type": "access",
        }
        access_token = jwt.encode(
            access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return {"access_token": access_token, "token_type": "bearer"}

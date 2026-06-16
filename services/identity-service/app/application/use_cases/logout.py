from __future__ import annotations

from jose import JWTError, jwt

from app.core.config import settings

# TTL for blacklisted tokens: matches access token lifetime + small buffer
_BLACKLIST_TTL_SECONDS = (settings.ACCESS_TOKEN_EXPIRE_MINUTES + 5) * 60
_BLACKLIST_PREFIX = "blacklist:"


class LogoutUseCase:

    def __init__(self, redis) -> None:
        self._redis = redis

    async def execute(self, access_token: str) -> None:
        try:
            payload = jwt.decode(
                access_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            jti = payload.get("sub", access_token[:32])
        except JWTError:
            jti = access_token[:32]

        await self._redis.setex(
            f"{_BLACKLIST_PREFIX}{access_token}",
            _BLACKLIST_TTL_SECONDS,
            "1",
        )

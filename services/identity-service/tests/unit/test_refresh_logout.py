"""
Unit tests for RefreshTokenUseCase and LogoutUseCase.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from jose import jwt

from app.application.use_cases.refresh_token import RefreshTokenUseCase
from app.application.use_cases.logout import LogoutUseCase
from app.core.config import settings
from shared.exceptions import AuthenticationError
from tests.conftest import make_user


def _make_refresh_token(user_id: str, expired: bool = False) -> str:
    now = datetime.now(timezone.utc)
    exp = now - timedelta(minutes=1) if expired else now + timedelta(days=7)
    payload = {"sub": user_id, "type": "refresh", "iat": now, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.mark.asyncio
async def test_refresh_issues_new_access_token():
    user = make_user()
    repo = AsyncMock()
    repo.get_by_id.return_value = user

    token = _make_refresh_token(str(user.id))
    result = await RefreshTokenUseCase(repo).execute(token)

    assert result["access_token"]
    assert result["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_expired_token_raises():
    repo = AsyncMock()
    expired = _make_refresh_token("some-id", expired=True)

    with pytest.raises(AuthenticationError):
        await RefreshTokenUseCase(repo).execute(expired)


@pytest.mark.asyncio
async def test_refresh_wrong_type_raises():
    user = make_user()
    repo = AsyncMock()
    repo.get_by_id.return_value = user
    now = datetime.now(timezone.utc)
    access_token = jwt.encode(
        {"sub": str(user.id), "type": "access", "exp": now + timedelta(minutes=30)},
        settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(AuthenticationError):
        await RefreshTokenUseCase(repo).execute(access_token)


@pytest.mark.asyncio
async def test_logout_blacklists_token(mock_redis):
    use_case = LogoutUseCase(mock_redis)
    token = "some.jwt.token"
    await use_case.execute(token)

    mock_redis.setex.assert_called_once()
    call_args = mock_redis.setex.call_args[0]
    assert f"blacklist:{token}" in call_args[0]

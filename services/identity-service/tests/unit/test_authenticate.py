"""
Unit tests for AuthenticateUserUseCase. SRS §5.1.
Tests: happy path, wrong password, locked account, account locking after 5 failures.
"""
from __future__ import annotations

import bcrypt as _bcrypt_mod
import pytest
from unittest.mock import AsyncMock

from app.application.use_cases.authenticate import AuthenticateUserUseCase, MAX_FAILED_ATTEMPTS
from shared.exceptions import AuthenticationError, BusinessRuleViolationError
from tests.conftest import make_user, make_role


def _hash(pw: str) -> str:
    return _bcrypt_mod.hashpw(pw.encode(), _bcrypt_mod.gensalt()).decode()


@pytest.fixture
def real_password() -> str:
    return "SecurePass@123"


@pytest.fixture
def user_with_password(real_password):
    u = make_user(
        email="manager@farm.uz",
        hashed_password=_hash(real_password),
        roles=[make_role("farm_manager")],
    )
    return u


@pytest.mark.asyncio
async def test_login_happy_path(user_with_password, real_password):
    repo = AsyncMock()
    repo.get_by_email.return_value = user_with_password
    repo.reset_failed_attempts.return_value = None

    use_case = AuthenticateUserUseCase(repo)
    result = await use_case.execute("manager@farm.uz", real_password)

    assert result.access_token
    assert result.refresh_token
    assert result.token_type == "bearer"
    repo.reset_failed_attempts.assert_called_once_with(user_with_password.id)


@pytest.mark.asyncio
async def test_wrong_password_raises(user_with_password):
    repo = AsyncMock()
    repo.get_by_email.return_value = user_with_password
    repo.increment_failed_attempts.return_value = None

    use_case = AuthenticateUserUseCase(repo)
    with pytest.raises(AuthenticationError):
        await use_case.execute("manager@farm.uz", "WrongPassword!")

    repo.increment_failed_attempts.assert_called_once_with(user_with_password.id)


@pytest.mark.asyncio
async def test_user_not_found_raises():
    repo = AsyncMock()
    repo.get_by_email.return_value = None

    use_case = AuthenticateUserUseCase(repo)
    with pytest.raises(AuthenticationError):
        await use_case.execute("nobody@farm.uz", "anypassword")


@pytest.mark.asyncio
async def test_locked_account_raises():
    repo = AsyncMock()
    user = make_user(is_locked=True, hashed_password=_hash("pass"))
    repo.get_by_email.return_value = user

    use_case = AuthenticateUserUseCase(repo)
    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await use_case.execute("locked@farm.uz", "pass")

    assert "ACCOUNT_LOCKED" in str(exc_info.value.rule)


@pytest.mark.asyncio
async def test_account_locks_after_max_failures():
    repo = AsyncMock()
    user = make_user(
        hashed_password=_hash("correct"),
        failed_login_attempts=MAX_FAILED_ATTEMPTS - 1,
    )
    repo.get_by_email.return_value = user
    repo.increment_failed_attempts.return_value = None
    repo.lock_account.return_value = None

    use_case = AuthenticateUserUseCase(repo)
    with pytest.raises(AuthenticationError):
        await use_case.execute("user@farm.uz", "wrong_password")

    repo.lock_account.assert_called_once_with(user.id)


@pytest.mark.asyncio
async def test_tokens_contain_user_data(user_with_password, real_password):
    from jose import jwt
    from app.core.config import settings

    repo = AsyncMock()
    repo.get_by_email.return_value = user_with_password
    repo.reset_failed_attempts.return_value = None

    use_case = AuthenticateUserUseCase(repo)
    result = await use_case.execute("manager@farm.uz", real_password)

    payload = jwt.decode(result.access_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == str(user_with_password.id)
    assert payload["email"] == user_with_password.email
    assert "farm_manager" in payload["roles"]
    assert payload["type"] == "access"

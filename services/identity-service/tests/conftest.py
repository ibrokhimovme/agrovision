from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.domain.models.user import User, Role


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


def make_user(
    email: str = "test@farm.uz",
    full_name: str = "Test User",
    hashed_password: str = "$2b$12$placeholder",
    is_active: bool = True,
    is_locked: bool = False,
    failed_login_attempts: int = 0,
    roles: list | None = None,
) -> User:
    user = User()
    user.id = uuid4()
    user.email = email
    user.full_name = full_name
    user.hashed_password = hashed_password
    user.is_active = is_active
    user.is_locked = is_locked
    user.failed_login_attempts = failed_login_attempts
    user.farm_id = None
    user.roles = roles or []
    user.individual_permissions = []
    return user


def make_role(name: str = "farm_manager") -> Role:
    role = Role()
    role.id = uuid4()
    role.name = name
    role.display_name = "Ferma Boshqaruvchisi"
    role.is_system = True
    role.permissions = []
    return role


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.exists.return_value = 0
    redis.setex.return_value = True
    return redis

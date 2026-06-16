"""
Integration tests for auth endpoints.
These tests mock the DB repository to avoid requiring a live database.
For full integration testing with a real DB, use docker compose up before running.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import bcrypt as _bcrypt_mod
import pytest
from httpx import AsyncClient

from tests.conftest import make_user, make_role

PASSWORD = "TestPass@123"


@pytest.fixture
def active_user():
    return make_user(
        email="user@farm.uz",
        hashed_password=_bcrypt_mod.hashpw(PASSWORD.encode(), _bcrypt_mod.gensalt()).decode(),
        roles=[make_role("farm_manager")],
    )


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, active_user):
    with patch(
        "app.api.v1.endpoints.auth.SQLAlchemyUserRepository"
    ) as MockRepo:
        repo_instance = AsyncMock()
        repo_instance.get_by_email.return_value = active_user
        repo_instance.reset_failed_attempts.return_value = None
        MockRepo.return_value = repo_instance

        resp = await client.post("/api/v1/auth/login", json={
            "email": "user@farm.uz",
            "password": PASSWORD,
        })

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]
    assert body["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, active_user):
    with patch(
        "app.api.v1.endpoints.auth.SQLAlchemyUserRepository"
    ) as MockRepo:
        repo_instance = AsyncMock()
        repo_instance.get_by_email.return_value = active_user
        repo_instance.increment_failed_attempts.return_value = None
        MockRepo.return_value = repo_instance

        resp = await client.post("/api/v1/auth/login", json={
            "email": "user@farm.uz",
            "password": "WrongPassword!",
        })

    assert resp.status_code == 401
    assert resp.json()["success"] is False


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    with patch(
        "app.api.v1.endpoints.auth.SQLAlchemyUserRepository"
    ) as MockRepo:
        repo_instance = AsyncMock()
        repo_instance.get_by_email.return_value = None
        MockRepo.return_value = repo_instance

        resp = await client.post("/api/v1/auth/login", json={
            "email": "ghost@farm.uz",
            "password": "any",
        })

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_locked_account(client: AsyncClient):
    locked = make_user(
        email="locked@farm.uz",
        hashed_password=_bcrypt_mod.hashpw(PASSWORD.encode(), _bcrypt_mod.gensalt()).decode(),
        is_locked=True,
    )
    with patch(
        "app.api.v1.endpoints.auth.SQLAlchemyUserRepository"
    ) as MockRepo:
        repo_instance = AsyncMock()
        repo_instance.get_by_email.return_value = locked
        MockRepo.return_value = repo_instance

        resp = await client.post("/api/v1/auth/login", json={
            "email": "locked@farm.uz",
            "password": PASSWORD,
        })

    assert resp.status_code == 422
    body = resp.json()
    assert body["error_code"] == "BUSINESS_RULE"
    assert body["details"]["rule"] == "ACCOUNT_LOCKED"


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient):
    from app.main import app as fastapi_app
    from app.infrastructure.cache.redis_client import get_redis

    mock_redis = AsyncMock()
    mock_redis.setex.return_value = True

    async def override_get_redis():
        return mock_redis

    fastapi_app.dependency_overrides[get_redis] = override_get_redis
    try:
        resp = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer some.fake.token"},
        )
    finally:
        fastapi_app.dependency_overrides.pop(get_redis, None)

    assert resp.status_code == 200
    assert resp.json()["data"]["message"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["service"] == "identity-service"

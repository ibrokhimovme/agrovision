"""
Authentication use case skeleton.
Implements SRS §5.1 requirements:
  - Email + password login
  - Account lockout after 5 failed attempts (15-min lockout) — SRS §6 NFR Security
  - JWT access + refresh token issuance
  - 30-min access token TTL — SRS §6
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import jwt

from app.identity.core.config import settings
from app.identity.domain.repositories.user_repository import AbstractUserRepository
from shared.exceptions import AuthenticationError, BusinessRuleViolationError


MAX_FAILED_ATTEMPTS = 5


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 if hasattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES") else 1800


class AuthenticateUserUseCase:
    """
    Validates credentials and returns JWT tokens.
    Does NOT implement password hashing directly — delegates to domain service.
    """

    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, email: str, password: str) -> AuthTokens:
        user = await self._user_repo.get_by_email(email)
        if user is None:
            raise AuthenticationError("Invalid credentials")

        if user.is_locked:
            raise BusinessRuleViolationError(
                "ACCOUNT_LOCKED",
                "Account is locked due to too many failed login attempts. Try again in 15 minutes.",
            )

        if not self._verify_password(password, user.hashed_password):
            await self._user_repo.increment_failed_attempts(user.id)
            if user.failed_login_attempts + 1 >= MAX_FAILED_ATTEMPTS:
                await self._user_repo.lock_account(user.id)
            raise AuthenticationError("Invalid credentials")

        await self._user_repo.reset_failed_attempts(user.id)
        return self._issue_tokens(user)

    def _verify_password(self, plain: str, hashed: str) -> bool:
        import bcrypt
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    def _issue_tokens(self, user) -> AuthTokens:
        now = datetime.now(timezone.utc)
        roles = [r.name for r in user.roles]

        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "roles": roles,
            "farm_id": str(user.farm_id) if user.farm_id else None,
            "iat": now,
            "exp": now + timedelta(minutes=30),
            "type": "access",
        }
        refresh_payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": now + timedelta(days=7),
            "type": "refresh",
        }

        access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        return AuthTokens(access_token=access_token, refresh_token=refresh_token)

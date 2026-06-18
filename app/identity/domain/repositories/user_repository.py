"""
User repository interface (abstract base).
Concrete implementation lives in infrastructure/database/user_repository_impl.py.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.identity.domain.models.user import User


class AbstractUserRepository(ABC):

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def list_by_farm(self, farm_id: UUID, offset: int, limit: int) -> tuple[list[User], int]: ...

    @abstractmethod
    async def list_by_account(
        self, account_id: Optional[UUID], offset: int, limit: int
    ) -> tuple[list[User], int]:
        """EX-15 (execution-v2): account-wide (multi-farm) user listing.
        account_id=None means unrestricted — only valid for a superuser caller."""
        ...

    @abstractmethod
    async def increment_failed_attempts(self, user_id: UUID) -> None: ...

    @abstractmethod
    async def reset_failed_attempts(self, user_id: UUID) -> None: ...

    @abstractmethod
    async def lock_account(self, user_id: UUID) -> None: ...

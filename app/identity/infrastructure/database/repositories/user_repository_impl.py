from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.identity.domain.models.user import User
from app.identity.domain.repositories.user_repository import AbstractUserRepository


class SQLAlchemyUserRepository(AbstractUserRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.roles), selectinload(User.individual_permissions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.roles), selectinload(User.individual_permissions))
            .where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def list_by_farm(self, farm_id: UUID, offset: int, limit: int) -> tuple[list[User], int]:
        total_result = await self._session.execute(
            select(func.count(User.id)).where(User.farm_id == farm_id)
        )
        total = total_result.scalar_one()

        result = await self._session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.farm_id == farm_id)
            .offset(offset)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all(), total

    async def increment_failed_attempts(self, user_id: UUID) -> None:
        await self._session.execute(
            update(User)
            .where(User.id == user_id)
            .values(failed_login_attempts=User.failed_login_attempts + 1)
        )

    async def reset_failed_attempts(self, user_id: UUID) -> None:
        await self._session.execute(
            update(User)
            .where(User.id == user_id)
            .values(failed_login_attempts=0, is_locked=False)
        )

    async def lock_account(self, user_id: UUID) -> None:
        await self._session.execute(
            update(User).where(User.id == user_id).values(is_locked=True)
        )

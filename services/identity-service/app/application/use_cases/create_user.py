from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import bcrypt as _bcrypt_mod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.models.user import User, Role
from app.domain.repositories.user_repository import AbstractUserRepository
from shared.exceptions import DuplicateEntityError, EntityNotFoundError


@dataclass
class CreateUserRequest:
    email: str
    full_name: str
    password: str
    role_name: str
    farm_id: Optional[UUID] = None
    phone: Optional[str] = None


class CreateUserUseCase:

    def __init__(self, user_repo: AbstractUserRepository, session: AsyncSession) -> None:
        self._user_repo = user_repo
        self._session = session

    async def execute(self, req: CreateUserRequest) -> User:
        existing = await self._user_repo.get_by_email(req.email)
        if existing is not None:
            raise DuplicateEntityError(f"User with email '{req.email}' already exists")

        role_result = await self._session.execute(
            select(Role).where(Role.name == req.role_name)
        )
        role = role_result.scalar_one_or_none()
        if role is None:
            raise EntityNotFoundError("Role", req.role_name)

        user = User(
            email=req.email.lower(),
            full_name=req.full_name,
            phone=req.phone,
            hashed_password=_bcrypt_mod.hashpw(req.password.encode(), _bcrypt_mod.gensalt()).decode(),
            farm_id=req.farm_id,
        )
        user.roles.append(role)
        return await self._user_repo.create(user)

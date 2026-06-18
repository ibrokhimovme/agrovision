from __future__ import annotations

from uuid import UUID

from app.identity.domain.models.user import User
from app.identity.domain.repositories.user_repository import AbstractUserRepository
from shared.exceptions import EntityNotFoundError


class GetCurrentUserUseCase:

    def __init__(self, user_repo: AbstractUserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: UUID) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise EntityNotFoundError("User", user_id)
        return user

from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.farm.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class DeleteFarmUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(
        self, farm_id: UUID, account_id: Optional[UUID] = None, is_superuser: bool = False
    ) -> None:
        # EX-02 (execution-v2): verify ownership before soft-deleting — same
        # super-admin-bypass / account-less-sees-nothing rule as
        # GetFarmUseCase. `soft_delete` itself is unchanged (no account_id
        # param) so this ownership check is done explicitly here first.
        if not is_superuser and account_id is None:
            raise EntityNotFoundError("Farm", str(farm_id))
        effective_account_id = None if is_superuser else account_id
        existing = await self._repo.get_by_id(farm_id, account_id=effective_account_id)
        if existing is None:
            raise EntityNotFoundError("Farm", str(farm_id))
        farm = await self._repo.soft_delete(farm_id)
        if farm is None:
            raise EntityNotFoundError("Farm", str(farm_id))

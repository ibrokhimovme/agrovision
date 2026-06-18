from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.farm.domain.models.farm import Farm
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class GetFarmUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(
        self, farm_id: UUID, account_id: Optional[UUID] = None, is_superuser: bool = False
    ) -> Farm:
        # EX-02 (execution-v2): a platform super-admin is unrestricted
        # regardless of their own account_id (verified via live data that a
        # super-admin can legitimately end up owning an Account too, so
        # "account_id is None" alone is not a safe proxy for "is
        # super-admin" — discovered during this phase's live verification,
        # not assumed). A non-superuser caller with no account sees nothing
        # (same 404 as a farm belonging to someone else's account, not a
        # distinct "forbidden").
        effective_account_id = None if is_superuser else account_id
        if effective_account_id is None and not is_superuser:
            raise EntityNotFoundError("Farm", farm_id)
        farm = await self._repo.get_by_id(farm_id, account_id=effective_account_id)
        if farm is None:
            raise EntityNotFoundError("Farm", farm_id)
        return farm

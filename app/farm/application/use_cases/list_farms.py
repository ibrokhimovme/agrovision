from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.farm.domain.models.farm import Farm
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository


class ListFarmsUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(
        self, page: int, page_size: int, account_id: Optional[UUID] = None, is_superuser: bool = False
    ) -> tuple[list[Farm], int]:
        # EX-02 (execution-v2): a platform super-admin is unrestricted
        # regardless of their own account_id (see get_farm.py for why this
        # can't be inferred from account_id alone). A non-superuser caller
        # with no account sees an empty list, not every farm.
        if not is_superuser and account_id is None:
            return [], 0
        effective_account_id = None if is_superuser else account_id
        return await self._repo.list_active(page, page_size, account_id=effective_account_id)

from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.farm.application.dtos.farm_dtos import UpdateFarmRequest
from app.farm.domain.models.farm import Farm
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository
from shared.exceptions import EntityNotFoundError


class UpdateFarmUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        farm_id: UUID,
        req: UpdateFarmRequest,
        account_id: Optional[UUID] = None,
        is_superuser: bool = False,
    ) -> Farm:
        # EX-02 (execution-v2): same super-admin-bypass / account-less-sees-
        # nothing rule as GetFarmUseCase — see that file for why is_superuser
        # can't be inferred from account_id alone.
        if not is_superuser and account_id is None:
            raise EntityNotFoundError("Farm", str(farm_id))
        effective_account_id = None if is_superuser else account_id
        farm = await self._repo.get_by_id(farm_id, account_id=effective_account_id)
        if farm is None:
            raise EntityNotFoundError("Farm", str(farm_id))

        if req.name is not None:
            farm.name = req.name
        if req.farm_type is not None:
            farm.farm_type = req.farm_type
        if req.address is not None:
            farm.address = req.address
        if req.region is not None:
            farm.region = req.region
        if req.notes is not None:
            farm.notes = req.notes

        return await self._repo.update(farm)

from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.farm.application.dtos.farm_dtos import CreateFarmRequest
from app.farm.domain.models.farm import Farm
from app.farm.domain.repositories.farm_repository import AbstractFarmRepository


class CreateFarmUseCase:

    def __init__(self, repo: AbstractFarmRepository) -> None:
        self._repo = repo

    async def execute(
        self, req: CreateFarmRequest, owner_user_id: UUID, account_id: Optional[UUID] = None
    ) -> Farm:
        farm = Farm()
        farm.name = req.name
        farm.farm_type = req.farm_type
        farm.address = req.address
        farm.region = req.region
        farm.notes = req.notes
        farm.owner_user_id = owner_user_id
        # EX-02 (execution-v2): implicit, not user-selectable — derived
        # from the caller's own JWT/X-Account-Id, never from the request
        # body. None for an account-less caller (super-admin).
        farm.account_id = account_id
        farm.is_active = True

        return await self._repo.create(farm)

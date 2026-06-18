"""
ListSuppliersUseCase: EX-11 (Finance Improvements, execution-v2).
"""
from __future__ import annotations

from uuid import UUID

from app.finance.application.dtos.supplier_dtos import SupplierResponse
from app.finance.domain.repositories.supplier_repository import AbstractSupplierRepository


class ListSuppliersUseCase:

    def __init__(self, supplier_repo: AbstractSupplierRepository) -> None:
        self._supplier_repo = supplier_repo

    async def execute(self, farm_id: UUID) -> list[SupplierResponse]:
        suppliers = await self._supplier_repo.list_by_farm(farm_id)
        return [SupplierResponse.model_validate(s) for s in suppliers]

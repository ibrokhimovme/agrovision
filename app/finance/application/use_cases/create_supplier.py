"""
CreateSupplierUseCase: EX-11 (Finance Improvements, execution-v2).
"""
from __future__ import annotations

from uuid import uuid4

from app.finance.application.dtos.supplier_dtos import CreateSupplierRequest, SupplierResponse
from app.finance.domain.models.finance import Supplier
from app.finance.domain.repositories.supplier_repository import AbstractSupplierRepository


class CreateSupplierUseCase:

    def __init__(self, supplier_repo: AbstractSupplierRepository) -> None:
        self._supplier_repo = supplier_repo

    async def execute(self, req: CreateSupplierRequest) -> SupplierResponse:
        supplier = Supplier()
        supplier.id = uuid4()
        supplier.farm_id = req.farm_id
        supplier.name = req.name
        supplier.phone = req.phone
        supplier.address = req.address
        supplier.is_active = True

        supplier = await self._supplier_repo.create(supplier)
        return SupplierResponse.model_validate(supplier)

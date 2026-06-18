"""
Supplier registry endpoints. EX-11 (Finance Improvements, execution-v2).
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.application.dtos.supplier_dtos import CreateSupplierRequest, SupplierResponse
from app.finance.application.use_cases.create_supplier import CreateSupplierUseCase
from app.finance.application.use_cases.list_suppliers import ListSuppliersUseCase
from app.finance.infrastructure.database.repositories.supplier_repository_impl import (
    SQLAlchemySupplierRepository,
)
from app.finance.infrastructure.database.session import get_db
from shared.contracts.api_standards import APIResponse

router = APIRouter()


@router.post(
    "/suppliers/",
    response_model=APIResponse[SupplierResponse],
    status_code=201,
    tags=["Suppliers"],
)
async def create_supplier(
    body: CreateSupplierRequest,
    db: AsyncSession = Depends(get_db),
):
    supplier_repo = SQLAlchemySupplierRepository(db)
    result = await CreateSupplierUseCase(supplier_repo).execute(body)
    return APIResponse(data=result)


@router.get(
    "/suppliers/",
    response_model=APIResponse[list[SupplierResponse]],
    tags=["Suppliers"],
)
async def list_suppliers(
    farm_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    supplier_repo = SQLAlchemySupplierRepository(db)
    result = await ListSuppliersUseCase(supplier_repo).execute(farm_id)
    return APIResponse(data=result)

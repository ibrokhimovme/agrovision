from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.domain.models.finance import Supplier
from app.finance.domain.repositories.supplier_repository import AbstractSupplierRepository


class SQLAlchemySupplierRepository(AbstractSupplierRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, supplier: Supplier) -> Supplier:
        self._session.add(supplier)
        await self._session.commit()
        await self._session.refresh(supplier)
        return supplier

    async def get_by_id(self, supplier_id: UUID) -> Optional[Supplier]:
        result = await self._session.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        return result.scalar_one_or_none()

    async def list_by_farm(self, farm_id: UUID) -> list[Supplier]:
        result = await self._session.execute(
            select(Supplier).where(Supplier.farm_id == farm_id, Supplier.is_active.is_(True))
        )
        return list(result.scalars().all())

"""
SQLAlchemy implementation of sale repository. SF-17.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.domain.models.finance import SaleRecord
from app.finance.domain.repositories.sale_repository import AbstractSaleRepository


class SQLAlchemySaleRepository(AbstractSaleRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, sale: SaleRecord) -> SaleRecord:
        self._session.add(sale)
        await self._session.commit()
        await self._session.refresh(sale)
        return sale

    async def get_by_id(self, sale_id: UUID) -> Optional[SaleRecord]:
        result = await self._session.execute(
            select(SaleRecord).where(SaleRecord.id == sale_id)
        )
        return result.scalar_one_or_none()

    async def list_by_batch(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[SaleRecord], int]:
        count_result = await self._session.execute(
            select(func.count()).where(SaleRecord.batch_id == batch_id)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        rows = await self._session.execute(
            select(SaleRecord)
            .where(SaleRecord.batch_id == batch_id)
            .order_by(desc(SaleRecord.sold_at))
            .offset(offset)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

    async def total_revenue_by_batch(self, batch_id: UUID) -> Decimal:
        result = await self._session.execute(
            select(func.sum(SaleRecord.total_revenue_uzs)).where(SaleRecord.batch_id == batch_id)
        )
        val = result.scalar_one_or_none()
        return val if val is not None else Decimal("0")

    async def update(self, sale: SaleRecord) -> SaleRecord:
        await self._session.commit()
        await self._session.refresh(sale)
        return sale

    async def list_outstanding_by_farm(self, farm_id: UUID) -> list[SaleRecord]:
        result = await self._session.execute(
            select(SaleRecord).where(
                SaleRecord.farm_id == farm_id,
                SaleRecord.amount_paid < SaleRecord.total_revenue_uzs,
            )
        )
        return list(result.scalars().all())

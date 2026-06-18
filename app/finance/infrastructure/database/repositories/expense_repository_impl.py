"""
SQLAlchemy implementation of expense repository. SF-14, SF-15.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.domain.models.finance import BatchExpenseType, Expense
from app.finance.domain.repositories.expense_repository import AbstractExpenseRepository


class SQLAlchemyExpenseRepository(AbstractExpenseRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, expense: Expense) -> Expense:
        self._session.add(expense)
        await self._session.commit()
        await self._session.refresh(expense)
        return expense

    async def get_by_id(self, expense_id: UUID) -> Optional[Expense]:
        result = await self._session.execute(
            select(Expense).where(Expense.id == expense_id)
        )
        return result.scalar_one_or_none()

    async def list_by_batch(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[Expense], int]:
        count_result = await self._session.execute(
            select(func.count()).where(Expense.batch_id == batch_id)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        rows = await self._session.execute(
            select(Expense)
            .where(Expense.batch_id == batch_id)
            .order_by(desc(Expense.expense_date))
            .offset(offset)
            .limit(page_size)
        )
        return list(rows.scalars().all()), total

    async def sum_by_batch_and_type(
        self, batch_id: UUID
    ) -> dict[BatchExpenseType, Decimal]:
        rows = await self._session.execute(
            select(Expense.expense_type, func.sum(Expense.amount))
            .where(
                Expense.batch_id == batch_id,
                Expense.expense_type != None,
            )
            .group_by(Expense.expense_type)
        )
        return {
            BatchExpenseType(row[0]): row[1] or Decimal("0")
            for row in rows.all()
        }

    async def total_by_batch(self, batch_id: UUID) -> Decimal:
        result = await self._session.execute(
            select(func.sum(Expense.amount)).where(Expense.batch_id == batch_id)
        )
        val = result.scalar_one_or_none()
        return val if val is not None else Decimal("0")

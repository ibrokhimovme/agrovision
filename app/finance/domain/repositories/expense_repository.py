"""
Abstract repository interfaces for finance domain. SF-14, SF-15.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.finance.domain.models.finance import BatchExpenseType, Expense


class AbstractExpenseRepository(ABC):

    @abstractmethod
    async def create(self, expense: Expense) -> Expense: ...

    @abstractmethod
    async def get_by_id(self, expense_id: UUID) -> Optional[Expense]: ...

    @abstractmethod
    async def list_by_batch(
        self, batch_id: UUID, page: int, page_size: int
    ) -> tuple[list[Expense], int]: ...

    @abstractmethod
    async def sum_by_batch_and_type(
        self, batch_id: UUID
    ) -> dict[BatchExpenseType, Decimal]: ...

    @abstractmethod
    async def total_by_batch(self, batch_id: UUID) -> Decimal: ...

    @abstractmethod
    async def update(self, expense: Expense) -> Expense: ...

    @abstractmethod
    async def list_outstanding_by_farm(self, farm_id: UUID) -> list[Expense]:
        """EX-11 (execution-v2): expenses with amount_paid < amount and a
        supplier_id set, for the creditor summary."""
        ...

"""
Unit tests for expense use cases. SF-14, SF-15, FG-01.
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos.expense_dtos import RecordManualExpenseRequest
from app.application.use_cases.get_batch_cost_summary import GetBatchCostSummaryUseCase
from app.application.use_cases.record_manual_expense import RecordManualExpenseUseCase
from app.domain.models.finance import BatchExpenseType, Expense, ExpenseCategory


def _make_expense(amount: str, expense_type: BatchExpenseType | None = None) -> Expense:
    from datetime import datetime, timezone
    e = Expense()
    e.id = uuid4()
    e.farm_id = uuid4()
    e.batch_id = uuid4()
    e.category = ExpenseCategory.FEED
    e.expense_type = expense_type
    e.description = "Test"
    e.amount = Decimal(amount)
    e.currency = "UZS"
    e.expense_date = datetime.now(timezone.utc)
    e.created_at = datetime.now(timezone.utc)
    e.updated_at = datetime.now(timezone.utc)
    return e


# ── RecordManualExpenseUseCase ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_record_expense_ok():
    expense_repo = AsyncMock()
    expense_repo.create = AsyncMock(side_effect=lambda e: e)

    req = RecordManualExpenseRequest(
        farm_id=uuid4(),
        batch_id=uuid4(),
        category=ExpenseCategory.FEED,
        expense_type=BatchExpenseType.FEED,
        description="Yem xarajati",
        amount=Decimal("500000"),
        currency="UZS",
    )
    result = await RecordManualExpenseUseCase(expense_repo).execute(req)

    assert result.amount == Decimal("500000")
    assert result.expense_type == BatchExpenseType.FEED
    expense_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_record_expense_no_batch_ok():
    expense_repo = AsyncMock()
    expense_repo.create = AsyncMock(side_effect=lambda e: e)

    req = RecordManualExpenseRequest(
        farm_id=uuid4(),
        category=ExpenseCategory.LABOR,
        description="Mehnat xarajati",
        amount=Decimal("200000"),
    )
    result = await RecordManualExpenseUseCase(expense_repo).execute(req)

    assert result.batch_id is None
    assert result.currency == "UZS"


# ── GetBatchCostSummaryUseCase ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_cost_summary_empty_batch():
    expense_repo = AsyncMock()
    expense_repo.total_by_batch = AsyncMock(return_value=Decimal("0"))
    expense_repo.sum_by_batch_and_type = AsyncMock(return_value={})
    expense_repo.list_by_batch = AsyncMock(return_value=([], 0))

    summary = await GetBatchCostSummaryUseCase(expense_repo).execute(uuid4())

    assert summary.total_uzs == Decimal("0")
    assert summary.expense_count == 0
    assert summary.breakdown == {}


@pytest.mark.asyncio
async def test_cost_summary_multiple_types():
    batch_id = uuid4()
    expense_repo = AsyncMock()
    expense_repo.total_by_batch = AsyncMock(return_value=Decimal("1500000"))
    expense_repo.sum_by_batch_and_type = AsyncMock(return_value={
        BatchExpenseType.FEED: Decimal("1000000"),
        BatchExpenseType.VACCINE: Decimal("300000"),
        BatchExpenseType.CHICK: Decimal("200000"),
    })
    expense_repo.list_by_batch = AsyncMock(return_value=([], 5))

    summary = await GetBatchCostSummaryUseCase(expense_repo).execute(batch_id)

    assert summary.total_uzs == Decimal("1500000")
    assert summary.breakdown["feed"] == Decimal("1000000")
    assert summary.breakdown["vaccine"] == Decimal("300000")
    assert summary.breakdown["chick"] == Decimal("200000")
    assert summary.expense_count == 5


@pytest.mark.asyncio
async def test_cost_summary_single_feed_expense():
    expense_repo = AsyncMock()
    expense_repo.total_by_batch = AsyncMock(return_value=Decimal("750000"))
    expense_repo.sum_by_batch_and_type = AsyncMock(return_value={
        BatchExpenseType.FEED: Decimal("750000"),
    })
    expense_repo.list_by_batch = AsyncMock(return_value=([], 3))

    summary = await GetBatchCostSummaryUseCase(expense_repo).execute(uuid4())

    assert summary.total_uzs == Decimal("750000")
    assert "feed" in summary.breakdown
    assert "vaccine" not in summary.breakdown

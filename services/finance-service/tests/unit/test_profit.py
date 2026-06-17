"""
Unit tests for CalculateBatchProfitUseCase. P-12.
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.use_cases.calculate_batch_profit import CalculateBatchProfitUseCase


@pytest.fixture
def batch_id():
    return uuid4()


@pytest.fixture
def expense_repo():
    repo = AsyncMock()
    repo.total_by_batch = AsyncMock(return_value=Decimal("5000000"))
    repo.list_by_batch = AsyncMock(return_value=([], 3))
    return repo


@pytest.fixture
def sale_repo():
    repo = AsyncMock()
    repo.total_revenue_by_batch = AsyncMock(return_value=Decimal("8000000"))
    repo.list_by_batch = AsyncMock(return_value=([], 2))
    return repo


@pytest.mark.asyncio
async def test_gross_profit_calculated(batch_id, expense_repo, sale_repo):
    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(batch_id)
    assert result.gross_profit_uzs == Decimal("3000000")


@pytest.mark.asyncio
async def test_profit_margin_calculated(batch_id, expense_repo, sale_repo):
    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(batch_id)
    assert result.profit_margin_pct == Decimal("37.50")


@pytest.mark.asyncio
async def test_profit_margin_zero_when_no_revenue(batch_id, expense_repo, sale_repo):
    sale_repo.total_revenue_by_batch = AsyncMock(return_value=Decimal("0"))
    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(batch_id)
    assert result.profit_margin_pct == Decimal("0.00")
    assert result.gross_profit_uzs == Decimal("-5000000")


@pytest.mark.asyncio
async def test_counts_forwarded(batch_id, expense_repo, sale_repo):
    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(batch_id)
    assert result.sale_count == 2
    assert result.expense_count == 3


@pytest.mark.asyncio
async def test_batch_id_in_response(batch_id, expense_repo, sale_repo):
    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(batch_id)
    assert result.batch_id == batch_id

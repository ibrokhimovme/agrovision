"""
E2E workflow test for finance-service use cases.
Tests the full chain: record expense → record sale → calculate profit.
"""
from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock


BATCH_ID = uuid4()
FARM_ID = uuid4()


@pytest.mark.asyncio
async def test_record_manual_expense():
    from app.application.use_cases.record_manual_expense import RecordManualExpenseUseCase
    from app.application.dtos.expense_dtos import RecordManualExpenseRequest
    from app.domain.models.finance import ExpenseCategory

    req = RecordManualExpenseRequest(
        farm_id=FARM_ID,
        batch_id=BATCH_ID,
        category=ExpenseCategory.FEED,
        description="Starter yemi",
        amount=Decimal("1500000"),
    )

    repo = AsyncMock()
    # Return the same object the use case builds so all fields are present
    repo.create = AsyncMock(side_effect=lambda e: e)

    result = await RecordManualExpenseUseCase(repo).execute(req)

    assert result.batch_id == BATCH_ID
    assert result.amount == Decimal("1500000")
    assert result.category == ExpenseCategory.FEED


@pytest.mark.asyncio
async def test_record_sale():
    from app.application.use_cases.record_sale import RecordSaleUseCase
    from app.application.dtos.sale_dtos import RecordSaleRequest
    from app.domain.models.finance import SalePaymentStatus

    req = RecordSaleRequest(
        farm_id=FARM_ID,
        customer_name="Ahmedov Sherzod",
        head_count=200,
        quantity_kg=Decimal("400.0"),
        price_per_kg_uzs=Decimal("22000"),
        payment_status=SalePaymentStatus.PAID,
    )

    repo = AsyncMock()
    # Return the same object the use case builds so all fields are present
    repo.create = AsyncMock(side_effect=lambda s: s)

    result = await RecordSaleUseCase(repo).execute(BATCH_ID, req)

    assert result.batch_id == BATCH_ID
    assert result.total_revenue_uzs == Decimal("8800000")
    assert result.head_count == 200


@pytest.mark.asyncio
async def test_calculate_batch_profit():
    from app.application.use_cases.calculate_batch_profit import CalculateBatchProfitUseCase

    expense_repo = AsyncMock()
    expense_repo.total_by_batch = AsyncMock(return_value=Decimal("3000000"))
    expense_repo.list_by_batch = AsyncMock(return_value=([], 5))

    sale_repo = AsyncMock()
    sale_repo.total_revenue_by_batch = AsyncMock(return_value=Decimal("8800000"))
    sale_repo.list_by_batch = AsyncMock(return_value=([], 2))

    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(BATCH_ID)

    assert result.gross_profit_uzs == Decimal("5800000")
    assert result.total_revenue_uzs == Decimal("8800000")
    assert result.total_cost_uzs == Decimal("3000000")
    assert result.sale_count == 2
    assert result.expense_count == 5


@pytest.mark.asyncio
async def test_profit_negative_when_costs_exceed_revenue():
    from app.application.use_cases.calculate_batch_profit import CalculateBatchProfitUseCase

    expense_repo = AsyncMock()
    expense_repo.total_by_batch = AsyncMock(return_value=Decimal("10000000"))
    expense_repo.list_by_batch = AsyncMock(return_value=([], 8))

    sale_repo = AsyncMock()
    sale_repo.total_revenue_by_batch = AsyncMock(return_value=Decimal("7000000"))
    sale_repo.list_by_batch = AsyncMock(return_value=([], 1))

    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(BATCH_ID)

    assert result.gross_profit_uzs == Decimal("-3000000")
    assert result.profit_margin_pct < Decimal("0")


@pytest.mark.asyncio
async def test_profit_margin_zero_when_no_revenue():
    from app.application.use_cases.calculate_batch_profit import CalculateBatchProfitUseCase

    expense_repo = AsyncMock()
    expense_repo.total_by_batch = AsyncMock(return_value=Decimal("5000000"))
    expense_repo.list_by_batch = AsyncMock(return_value=([], 3))

    sale_repo = AsyncMock()
    sale_repo.total_revenue_by_batch = AsyncMock(return_value=Decimal("0"))
    sale_repo.list_by_batch = AsyncMock(return_value=([], 0))

    result = await CalculateBatchProfitUseCase(expense_repo, sale_repo).execute(BATCH_ID)

    assert result.profit_margin_pct == Decimal("0.00")
    assert result.gross_profit_uzs == Decimal("-5000000")

"""
Unit tests for sales use cases. SF-17, BP-12.
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dtos.sale_dtos import RecordSaleRequest
from app.application.use_cases.record_sale import RecordSaleUseCase
from app.domain.models.finance import SalePaymentStatus


def _req(**kwargs) -> RecordSaleRequest:
    defaults = dict(
        farm_id=uuid4(),
        customer_name="Alisher Xo'jaev",
        head_count=500,
        quantity_kg=Decimal("1200.000"),
        price_per_kg_uzs=Decimal("22000.00"),
        payment_status=SalePaymentStatus.PAID,
    )
    defaults.update(kwargs)
    return RecordSaleRequest(**defaults)


@pytest.mark.asyncio
async def test_record_sale_computes_total_revenue():
    sale_repo = AsyncMock()
    sale_repo.create = AsyncMock(side_effect=lambda s: s)

    result = await RecordSaleUseCase(sale_repo).execute(uuid4(), _req())

    assert result.total_revenue_uzs == Decimal("1200.000") * Decimal("22000.00")
    assert result.customer_name == "Alisher Xo'jaev"
    assert result.payment_status == SalePaymentStatus.PAID
    sale_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_record_sale_pending_payment():
    sale_repo = AsyncMock()
    sale_repo.create = AsyncMock(side_effect=lambda s: s)

    result = await RecordSaleUseCase(sale_repo).execute(
        uuid4(), _req(payment_status=SalePaymentStatus.PENDING)
    )

    assert result.payment_status == SalePaymentStatus.PENDING


@pytest.mark.asyncio
async def test_record_sale_total_is_qty_times_price():
    sale_repo = AsyncMock()
    sale_repo.create = AsyncMock(side_effect=lambda s: s)

    req = _req(
        quantity_kg=Decimal("800.500"),
        price_per_kg_uzs=Decimal("25000.00"),
    )
    result = await RecordSaleUseCase(sale_repo).execute(uuid4(), req)

    expected = Decimal("800.500") * Decimal("25000.00")
    assert result.total_revenue_uzs == expected


@pytest.mark.asyncio
async def test_record_sale_optional_phone_and_notes():
    sale_repo = AsyncMock()
    sale_repo.create = AsyncMock(side_effect=lambda s: s)

    result = await RecordSaleUseCase(sale_repo).execute(
        uuid4(),
        _req(customer_phone="+998901234567", notes="Naqd to'lov"),
    )

    assert result.customer_phone == "+998901234567"
    assert result.notes == "Naqd to'lov"

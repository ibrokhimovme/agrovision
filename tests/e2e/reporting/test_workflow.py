"""
E2E workflow test for reporting-service use cases.
Tests: GenerateBatchReportUseCase (with mocked clients) + PDF byte generation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock


BATCH_ID = uuid4()
FARM_ID = uuid4()


def _mock_livestock_client(batch_found: bool = True):
    client = MagicMock()
    if batch_found:
        client.get_batch = AsyncMock(return_value={
            "batch_code": "TEST-001",
            "farm_id": str(FARM_ID),
            "species": "broiler",
            "initial_count": 5000,
            "current_count": 4850,
            "status": "active",
            "placement_date": "2026-05-01",
            "age_days": 47,
        })
    else:
        client.get_batch = AsyncMock(return_value=None)

    client.get_weight_metrics = AsyncMock(return_value={
        "fcr": "1.85",
        "adg_grams": "62.5",
        "latest_avg_weight_kg": "2.938",
    })
    client.get_feed_summary = AsyncMock(return_value={
        "total_feed_kg": "13750.5",
        "total_water_liters": "27501.0",
    })
    client.get_mortality_summary = AsyncMock(return_value={
        "total_deaths": 150,
        "mortality_rate_pct": "3.00",
    })
    return client


def _mock_finance_client():
    client = MagicMock()
    client.get_cost_summary = AsyncMock(return_value={
        "total_cost_uzs": "45000000",
        "expense_count": 12,
    })
    client.get_profit = AsyncMock(return_value={
        "total_revenue_uzs": "68000000",
        "gross_profit_uzs": "23000000",
        "profit_margin_pct": "33.82",
        "sale_count": 3,
    })
    client.get_sales_summary = AsyncMock(return_value={
        "total_revenue_uzs": "68000000",
        "sale_count": 3,
    })
    return client


@pytest.mark.asyncio
async def test_generate_batch_report():
    from app.application.use_cases.generate_batch_report import GenerateBatchReportUseCase

    livestock = _mock_livestock_client()
    finance = _mock_finance_client()

    result = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)

    assert result.batch_id == BATCH_ID
    assert result.batch_code == "TEST-001"
    assert result.species == "broiler"
    assert result.initial_count == 5000
    assert result.age_days == 47
    assert result.total_deaths == 150
    assert result.gross_profit_uzs == Decimal("23000000")


@pytest.mark.asyncio
async def test_generate_report_not_found_raises():
    from app.application.use_cases.generate_batch_report import GenerateBatchReportUseCase
    from shared.exceptions import EntityNotFoundError

    livestock = _mock_livestock_client(batch_found=False)
    finance = _mock_finance_client()

    with pytest.raises(EntityNotFoundError):
        await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)


@pytest.mark.asyncio
async def test_generate_report_null_metrics_handled():
    """Report generation succeeds even when optional metrics are missing."""
    from app.application.use_cases.generate_batch_report import GenerateBatchReportUseCase

    livestock = _mock_livestock_client()
    livestock.get_weight_metrics = AsyncMock(return_value=None)
    livestock.get_feed_summary = AsyncMock(return_value=None)
    livestock.get_mortality_summary = AsyncMock(return_value=None)

    finance = _mock_finance_client()
    finance.get_cost_summary = AsyncMock(return_value=None)
    finance.get_profit = AsyncMock(return_value=None)
    finance.get_sales_summary = AsyncMock(return_value=None)

    result = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)

    assert result.batch_id == BATCH_ID
    assert result.fcr is None
    assert result.total_feed_kg is None
    assert result.total_deaths is None
    assert result.gross_profit_uzs is None


@pytest.mark.asyncio
async def test_pdf_generation_produces_valid_pdf():
    from app.application.use_cases.generate_batch_report import GenerateBatchReportUseCase
    from app.infrastructure.pdf.batch_report_pdf import generate_batch_report_pdf

    livestock = _mock_livestock_client()
    finance = _mock_finance_client()

    report = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)
    pdf_bytes = generate_batch_report_pdf(report)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_pdf_with_null_metrics_does_not_crash():
    """PDF generation must handle all-null optional fields gracefully."""
    from app.application.use_cases.generate_batch_report import GenerateBatchReportUseCase
    from app.infrastructure.pdf.batch_report_pdf import generate_batch_report_pdf

    livestock = _mock_livestock_client()
    livestock.get_weight_metrics = AsyncMock(return_value=None)
    livestock.get_feed_summary = AsyncMock(return_value=None)
    livestock.get_mortality_summary = AsyncMock(return_value=None)

    finance = _mock_finance_client()
    finance.get_cost_summary = AsyncMock(return_value=None)
    finance.get_profit = AsyncMock(return_value=None)
    finance.get_sales_summary = AsyncMock(return_value=None)

    report = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)
    pdf_bytes = generate_batch_report_pdf(report)

    assert pdf_bytes[:4] == b"%PDF"

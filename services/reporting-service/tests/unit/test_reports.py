"""
Unit tests for GenerateBatchReportUseCase and PDF builder. P-14, SF-21.
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.use_cases.generate_batch_report import GenerateBatchReportUseCase
from app.infrastructure.pdf.batch_report_pdf import generate_batch_report_pdf
from shared.exceptions import EntityNotFoundError


BATCH_ID = uuid4()
FARM_ID = uuid4()

BATCH_DATA = {
    "id": str(BATCH_ID),
    "farm_id": str(FARM_ID),
    "species": "broiler",
    "batch_code": "B-2026-001",
    "initial_count": 10000,
    "current_count": 9800,
    "status": "active",
    "placement_date": "2026-06-01",
    "age_days": 30,
}

WEIGHT_DATA = {
    "fcr": "1.85",
    "adg_grams": "62.5",
    "latest_avg_weight_kg": "1.875",
}

FEED_DATA = {
    "total_feed_kg": "3471.5",
    "total_water_liters": "10414.5",
}

MORTALITY_DATA = {
    "total_deaths": 200,
    "mortality_rate_pct": "2.00",
    "survival_rate_pct": "98.00",
}

COST_DATA = {
    "total_uzs": "12500000",
    "breakdown": {},
    "expense_count": 8,
}

PROFIT_DATA = {
    "total_revenue_uzs": "18000000",
    "total_cost_uzs": "12500000",
    "gross_profit_uzs": "5500000",
    "profit_margin_pct": "30.56",
    "sale_count": 3,
    "expense_count": 8,
}

SALES_DATA = {
    "total_revenue_uzs": "18000000",
    "sale_count": 3,
}


@pytest.fixture
def livestock():
    c = AsyncMock()
    c.get_batch = AsyncMock(return_value=BATCH_DATA)
    c.get_weight_metrics = AsyncMock(return_value=WEIGHT_DATA)
    c.get_feed_summary = AsyncMock(return_value=FEED_DATA)
    c.get_mortality_summary = AsyncMock(return_value=MORTALITY_DATA)
    return c


@pytest.fixture
def finance():
    c = AsyncMock()
    c.get_cost_summary = AsyncMock(return_value=COST_DATA)
    c.get_profit = AsyncMock(return_value=PROFIT_DATA)
    c.get_sales_summary = AsyncMock(return_value=SALES_DATA)
    return c


@pytest.mark.asyncio
async def test_generate_report_happy_path(livestock, finance):
    report = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)
    assert report.batch_id == BATCH_ID
    assert report.species == "broiler"
    assert report.initial_count == 10000
    assert report.fcr == Decimal("1.85")
    assert report.total_feed_kg == Decimal("3471.5")
    assert report.total_deaths == 200
    assert report.gross_profit_uzs == Decimal("5500000")
    assert report.profit_margin_pct == Decimal("30.56")


@pytest.mark.asyncio
async def test_generate_report_batch_not_found(livestock, finance):
    livestock.get_batch = AsyncMock(return_value=None)
    with pytest.raises(EntityNotFoundError):
        await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)


@pytest.mark.asyncio
async def test_generate_report_no_finance_data(livestock, finance):
    finance.get_profit = AsyncMock(return_value=None)
    finance.get_cost_summary = AsyncMock(return_value=None)
    report = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)
    assert report.gross_profit_uzs is None
    assert report.total_cost_uzs is None


@pytest.mark.asyncio
async def test_generate_report_no_weight_data(livestock, finance):
    livestock.get_weight_metrics = AsyncMock(return_value=None)
    report = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)
    assert report.fcr is None
    assert report.adg_grams is None


@pytest.mark.asyncio
async def test_pdf_generation(livestock, finance):
    report = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)
    pdf_bytes = generate_batch_report_pdf(report)
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000


@pytest.mark.asyncio
async def test_pdf_with_null_fields(livestock, finance):
    livestock.get_weight_metrics = AsyncMock(return_value=None)
    livestock.get_feed_summary = AsyncMock(return_value=None)
    finance.get_profit = AsyncMock(return_value=None)
    report = await GenerateBatchReportUseCase(livestock, finance).execute(BATCH_ID)
    pdf_bytes = generate_batch_report_pdf(report)
    assert pdf_bytes[:4] == b"%PDF"

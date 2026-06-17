"""
DTOs for batch performance report. T-14-04. SF-21.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BatchReportResponse(BaseModel):
    batch_id: UUID
    generated_at: datetime

    # Batch info
    batch_code: Optional[str]
    farm_id: UUID
    species: str
    initial_count: int
    current_count: int
    status: str
    placement_date: str
    age_days: Optional[int]

    # Growth performance
    fcr: Optional[Decimal]
    adg_grams: Optional[Decimal]
    latest_avg_weight_kg: Optional[Decimal]

    # Feed
    total_feed_kg: Optional[Decimal]
    total_water_liters: Optional[Decimal]

    # Mortality
    total_deaths: Optional[int]
    mortality_rate_pct: Optional[Decimal]
    survival_rate_pct: Optional[Decimal]

    # Financial
    total_cost_uzs: Optional[Decimal]
    total_revenue_uzs: Optional[Decimal]
    gross_profit_uzs: Optional[Decimal]
    profit_margin_pct: Optional[Decimal]
    sale_count: Optional[int]
    expense_count: Optional[int]

"""
DTOs for batch profit analysis. P-12, SF-18.
"""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class BatchProfitResponse(BaseModel):
    batch_id: UUID
    total_revenue_uzs: Decimal
    total_cost_uzs: Decimal
    gross_profit_uzs: Decimal
    profit_margin_pct: Decimal
    sale_count: int
    expense_count: int

"""
Feed Consumption Domain Models — MVP
======================================
Daily feed and water recording per batch.

SRS §5.10 (SF-10), §5.11 (SF-11 simplified).
BRD §6.1 item 6, BP-04 (feeding operations), BP-05 (water management).

MVP: water_liters is recorded on the same form as feed (SF-11 simplified).
FCR = total_feed_kg / weight_gain_kg — computed on demand.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


class FeedConsumption(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Daily feed and water consumption record per batch.
    One record per batch per day is the expected pattern (not enforced at DB level).
    """
    __tablename__ = "feed_consumptions"

    batch_id: Mapped[UUID] = mapped_column(ForeignKey("batches.id"), nullable=False, index=True)
    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    feed_date: Mapped[date] = mapped_column(Date, nullable=False)
    feed_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    water_liters: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    age_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # Optional link to inventory item — used by P-09 to auto-deduct stock.
    # EX-10 (Inventory Linkage Hardening, execution-v2): was a bare UUID
    # with no FK enforcement; hardened per decision_log.md BMD-014.
    feed_inventory_item_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("inventory.stock_items.id"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

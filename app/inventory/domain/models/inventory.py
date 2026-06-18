"""
Inventory domain models: warehouses, items, stock movements.
SRS §5.12 (Inventory management), §5.13 (Warehouse operations).
SF-12, SF-13. BP-09: FIFO/FEFO rules; expired items blocked; variance ≤2%.
BRD §6.1 items 10-11. OG-03: inventory accuracy.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


class ItemType(str, Enum):
    FEED = "feed"
    VACCINE = "vaccine"
    MEDICINE = "medicine"
    EQUIPMENT = "equipment"
    PACKAGING = "packaging"
    OTHER = "other"


class MovementType(str, Enum):
    RECEIPT = "receipt"         # incoming from supplier
    DISPATCH = "dispatch"       # outgoing (feed to batch, medicine to treatment)
    TRANSFER = "transfer"       # between warehouses
    ADJUSTMENT = "adjustment"   # inventory count correction
    WRITE_OFF = "write_off"     # expired / spoiled


class Warehouse(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Physical warehouse. SG-02: ≥10 warehouses supported.
    """
    __tablename__ = "warehouses"

    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    stock_items: Mapped[list["StockItem"]] = relationship(
        "StockItem", back_populates="warehouse", cascade="all, delete-orphan"
    )


class StockItem(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    A product catalog entry within a warehouse with current stock balance.
    Minimum stock alert threshold triggers LowStockAlertEvent (SRS §5.22).
    """
    __tablename__ = "stock_items"

    warehouse_id: Mapped[UUID] = mapped_column(
        ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    item_type: Mapped[ItemType] = mapped_column(String(20), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    current_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False, default=Decimal("0"))
    minimum_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False, default=Decimal("0"))
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="stock_items")
    batches: Mapped[list["StockBatch"]] = relationship(
        "StockBatch", back_populates="stock_item", cascade="all, delete-orphan"
    )
    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement", back_populates="stock_item", cascade="all, delete-orphan"
    )

    @property
    def is_below_minimum(self) -> bool:
        return self.current_quantity < self.minimum_quantity


class StockBatch(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    A received lot of a stock item with expiry date.
    Enables FIFO (First In First Out) and FEFO (First Expired First Out).
    BP-09: expired items blocked from use.
    """
    __tablename__ = "stock_batches"

    stock_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("stock_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    remaining_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    supplier_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)

    stock_item: Mapped["StockItem"] = relationship("StockItem", back_populates="batches")

    @property
    def is_expired(self) -> bool:
        if self.expiry_date is None:
            return False
        from shared.utils import utcnow
        return self.expiry_date < utcnow()


class StockMovement(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Immutable record of every stock change. Audit trail for inventory.
    BP-09: every receipt/dispatch documented formally.
    SRS §5.24 audit requirements.
    """
    __tablename__ = "stock_movements"

    stock_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("stock_items.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    warehouse_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    movement_type: Mapped[MovementType] = mapped_column(String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    purpose: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reference_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    moved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    stock_item: Mapped["StockItem"] = relationship("StockItem", back_populates="movements")

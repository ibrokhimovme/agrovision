"""
Finance domain models: expenses, revenue, payments, debtors/creditors.
SRS §5.15 (Financial tracking), §5.16 (Cost management),
§5.17 (Revenue management), §5.18 (Sales management).
SF-14, SF-15, SF-16, SF-17. BRD §6.1 items 12-13.
FG-01: batch cost calculation. FG-02: cash flow and receivables.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.models.base import Base, UUIDPrimaryKeyMixin, AuditMixin


class ExpenseCategory(str, Enum):
    FEED = "feed"
    VETERINARY = "veterinary"
    LABOR = "labor"
    TRANSPORT = "transport"
    EQUIPMENT = "equipment"
    UTILITIES = "utilities"
    DEPRECIATION = "depreciation"
    OTHER = "other"


class BatchExpenseType(str, Enum):
    FEED = "feed"
    VACCINE = "vaccine"
    MEDICINE = "medicine"
    CHICK = "chick"
    OTHER = "other"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    WRITTEN_OFF = "written_off"


class Supplier(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Supplier registry. EX-11 (Finance Improvements, execution-v2):
    supplier debt tracking, per decision_log.md BMD-015.
    """
    __tablename__ = "suppliers"

    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Expense(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    An expense record. Every transaction backed by a primary document.
    BP-11: approval authorities respected.
    FG-01: expenses allocated to batches for cost calculation.

    EX-11 (execution-v2): supplier_id/amount_paid added for supplier debt
    and partial-payment tracking (decision_log.md BMD-015). amount_paid
    defaults to the full amount (i.e. "already settled") so existing
    expense-recording behavior is unchanged unless a supplier debt is
    explicitly declared at creation time.
    """
    __tablename__ = "expenses"

    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    category: Mapped[ExpenseCategory] = mapped_column(String(50), nullable=False)
    expense_type: Mapped[Optional[BatchExpenseType]] = mapped_column(String(20), nullable=True, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="UZS")
    batch_id: Mapped[Optional[UUID]] = mapped_column(nullable=True, index=True)
    supplier_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("suppliers.id"), nullable=True, index=True
    )
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    source_event_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    reference_document: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expense_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_by: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    @property
    def outstanding_amount(self) -> Decimal:
        return self.amount - self.amount_paid

    @property
    def payment_status(self) -> str:
        if self.amount_paid <= 0:
            return "pending"
        if self.amount_paid >= self.amount:
            return "paid"
        return "partial"


class SalesOrder(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Sales order. SF-17. BP-12: sales above threshold require director approval.
    BP-12: sales to over-limit debtors blocked.
    """
    __tablename__ = "sales_orders"

    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    customer_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    status: Mapped[PaymentStatus] = mapped_column(String(20), nullable=False, default=PaymentStatus.PENDING)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="UZS")
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fulfilled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    director_approval_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    line_items: Mapped[list["SalesOrderLine"]] = relationship(
        "SalesOrderLine", back_populates="order", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="order", cascade="all, delete-orphan"
    )

    @property
    def outstanding_amount(self) -> Decimal:
        return self.total_amount - self.paid_amount


class SalesOrderLine(Base, UUIDPrimaryKeyMixin):
    """Line item within a sales order."""
    __tablename__ = "sales_order_lines"

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False
    )
    product_description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="line_items")


class Payment(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """Payment received for a sales order. FG-02: receivables management."""
    __tablename__ = "payments"

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("sales_orders.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    customer_id: Mapped[UUID] = mapped_column(nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="UZS")
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="payments")


class SalePaymentStatus(str, Enum):
    PAID = "paid"
    PENDING = "pending"
    PARTIAL = "partial"  # EX-11 (execution-v2): added per decision_log.md BMD-015


class SaleRecord(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Simple batch sale record. SF-17, BP-12.
    MVP alternative to full SalesOrder workflow.
    total_revenue_uzs = quantity_kg × price_per_kg_uzs (computed on creation).

    EX-11 (execution-v2): amount_paid added for customer debt and
    partial-payment tracking (decision_log.md BMD-015). payment_status is
    always server-computed from amount_paid vs total_revenue_uzs, never
    set directly by the client, to avoid the two ever disagreeing.
    """
    __tablename__ = "sale_records"

    batch_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    head_count: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    price_per_kg_uzs: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_revenue_uzs: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    payment_status: Mapped[SalePaymentStatus] = mapped_column(String(20), nullable=False, default=SalePaymentStatus.PENDING)
    sold_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    @property
    def outstanding_amount(self) -> Decimal:
        return self.total_revenue_uzs - self.amount_paid


class Customer(Base, UUIDPrimaryKeyMixin, AuditMixin):
    """
    Customer registry. SF-17 sales management.
    FG-02: debt tracking. BP-12: sales blocked if debtor limit exceeded.
    """
    __tablename__ = "customers"

    farm_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    current_debt: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=Decimal("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    @property
    def is_over_credit_limit(self) -> bool:
        return self.current_debt >= self.credit_limit and self.credit_limit > 0

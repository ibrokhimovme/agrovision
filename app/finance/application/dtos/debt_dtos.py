"""
DTOs for the debtor/creditor summary. EX-11 (Finance Improvements,
execution-v2): "show debtor/creditor summary in Finance" per
decision_log.md BMD-015.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DebtorEntry(BaseModel):
    """A customer who owes the farm money (unpaid/partially-paid sales)."""
    customer_name: str
    customer_phone: Optional[str]
    outstanding_amount: Decimal
    sale_count: int


class CreditorEntry(BaseModel):
    """A supplier the farm owes money to (unpaid/partially-paid expenses)."""
    supplier_id: UUID
    supplier_name: str
    outstanding_amount: Decimal
    expense_count: int


class DebtorCreditorSummaryResponse(BaseModel):
    farm_id: UUID
    total_receivable_uzs: Decimal  # owed TO the farm, by customers
    total_payable_uzs: Decimal     # owed BY the farm, to suppliers
    debtors: list[DebtorEntry]
    creditors: list[CreditorEntry]

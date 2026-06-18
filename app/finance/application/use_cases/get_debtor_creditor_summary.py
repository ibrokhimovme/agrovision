"""
GetDebtorCreditorSummaryUseCase: EX-11 (Finance Improvements, execution-v2).
"Show debtor/creditor summary in Finance" per decision_log.md BMD-015.

Debtors  = customers who owe the farm money (unpaid/partially-paid sales).
Creditors = suppliers the farm owes money to (unpaid/partially-paid expenses).
"""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.finance.application.dtos.debt_dtos import (
    CreditorEntry,
    DebtorCreditorSummaryResponse,
    DebtorEntry,
)
from app.finance.domain.repositories.expense_repository import AbstractExpenseRepository
from app.finance.domain.repositories.sale_repository import AbstractSaleRepository
from app.finance.domain.repositories.supplier_repository import AbstractSupplierRepository


class GetDebtorCreditorSummaryUseCase:

    def __init__(
        self,
        sale_repo: AbstractSaleRepository,
        expense_repo: AbstractExpenseRepository,
        supplier_repo: AbstractSupplierRepository,
    ) -> None:
        self._sale_repo = sale_repo
        self._expense_repo = expense_repo
        self._supplier_repo = supplier_repo

    async def execute(self, farm_id: UUID) -> DebtorCreditorSummaryResponse:
        outstanding_sales = await self._sale_repo.list_outstanding_by_farm(farm_id)
        outstanding_expenses = await self._expense_repo.list_outstanding_by_farm(farm_id)
        suppliers = await self._supplier_repo.list_by_farm(farm_id)
        supplier_names = {s.id: s.name for s in suppliers}

        debtor_map: dict[tuple[str, str | None], list] = {}
        for sale in outstanding_sales:
            key = (sale.customer_name, sale.customer_phone)
            debtor_map.setdefault(key, []).append(sale.outstanding_amount)

        creditor_map: dict[UUID, list] = {}
        for expense in outstanding_expenses:
            creditor_map.setdefault(expense.supplier_id, []).append(expense.outstanding_amount)

        debtors = [
            DebtorEntry(
                customer_name=name,
                customer_phone=phone,
                outstanding_amount=sum(amounts, Decimal("0")),
                sale_count=len(amounts),
            )
            for (name, phone), amounts in debtor_map.items()
        ]
        creditors = [
            CreditorEntry(
                supplier_id=supplier_id,
                supplier_name=supplier_names.get(supplier_id, "Noma'lum"),
                outstanding_amount=sum(amounts, Decimal("0")),
                expense_count=len(amounts),
            )
            for supplier_id, amounts in creditor_map.items()
        ]

        return DebtorCreditorSummaryResponse(
            farm_id=farm_id,
            total_receivable_uzs=sum((d.outstanding_amount for d in debtors), Decimal("0")),
            total_payable_uzs=sum((c.outstanding_amount for c in creditors), Decimal("0")),
            debtors=debtors,
            creditors=creditors,
        )

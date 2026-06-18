"""
RecordSalePaymentUseCase: EX-11 (Finance Improvements, execution-v2).
Records an additional payment against an existing sale (a customer paying
off debt over time) — "track partial payments" per decision_log.md BMD-015.
"""
from __future__ import annotations

from uuid import UUID

from app.finance.application.dtos.sale_dtos import RecordSalePaymentRequest, SaleRecordResponse
from app.finance.application.use_cases.record_sale import _compute_status
from app.finance.domain.repositories.sale_repository import AbstractSaleRepository
from shared.exceptions import EntityNotFoundError


class RecordSalePaymentUseCase:

    def __init__(self, sale_repo: AbstractSaleRepository) -> None:
        self._sale_repo = sale_repo

    async def execute(self, sale_id: UUID, req: RecordSalePaymentRequest) -> SaleRecordResponse:
        sale = await self._sale_repo.get_by_id(sale_id)
        if sale is None:
            raise EntityNotFoundError("SaleRecord", sale_id)

        sale.amount_paid = min(sale.amount_paid + req.amount, sale.total_revenue_uzs)
        sale.payment_status = _compute_status(sale.amount_paid, sale.total_revenue_uzs)

        sale = await self._sale_repo.update(sale)
        return SaleRecordResponse.model_validate(sale)

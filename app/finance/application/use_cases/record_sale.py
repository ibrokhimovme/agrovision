"""
RecordSaleUseCase: T-11-03. SF-17, BP-12.
total_revenue_uzs = quantity_kg × price_per_kg_uzs (computed here).
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from app.finance.application.dtos.sale_dtos import RecordSaleRequest, SaleRecordResponse
from app.finance.domain.models.finance import SalePaymentStatus, SaleRecord
from app.finance.domain.repositories.sale_repository import AbstractSaleRepository


def _compute_status(paid: Decimal, total: Decimal) -> SalePaymentStatus:
    if paid <= 0:
        return SalePaymentStatus.PENDING
    if paid >= total:
        return SalePaymentStatus.PAID
    return SalePaymentStatus.PARTIAL


class RecordSaleUseCase:

    def __init__(self, sale_repo: AbstractSaleRepository) -> None:
        self._sale_repo = sale_repo

    async def execute(self, batch_id: UUID, req: RecordSaleRequest) -> SaleRecordResponse:
        now = datetime.now(timezone.utc)
        total = (req.quantity_kg * req.price_per_kg_uzs).quantize(req.price_per_kg_uzs)

        # EX-11 (execution-v2): amount_paid is the source of truth for
        # payment_status, server-computed — never trusts a client-supplied
        # status directly (decision_log.md BMD-015). If amount_paid is
        # omitted, derive it from payment_status for backward compatibility.
        if req.amount_paid is not None:
            paid = min(max(req.amount_paid, Decimal("0")), total)
        else:
            paid = total if req.payment_status == SalePaymentStatus.PAID else Decimal("0")

        sale = SaleRecord()
        sale.id = uuid4()
        sale.batch_id = batch_id
        sale.farm_id = req.farm_id
        sale.customer_name = req.customer_name
        sale.customer_phone = req.customer_phone
        sale.head_count = req.head_count
        sale.quantity_kg = req.quantity_kg
        sale.price_per_kg_uzs = req.price_per_kg_uzs
        sale.total_revenue_uzs = total
        sale.amount_paid = paid
        sale.payment_status = _compute_status(paid, total)
        sale.sold_at = req.sold_at or now
        sale.notes = req.notes
        sale.created_at = now
        sale.updated_at = now

        sale = await self._sale_repo.create(sale)
        return SaleRecordResponse.model_validate(sale)

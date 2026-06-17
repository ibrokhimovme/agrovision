"""
RecordSaleUseCase: T-11-03. SF-17, BP-12.
total_revenue_uzs = quantity_kg × price_per_kg_uzs (computed here).
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.application.dtos.sale_dtos import RecordSaleRequest, SaleRecordResponse
from app.domain.models.finance import SaleRecord
from app.domain.repositories.sale_repository import AbstractSaleRepository


class RecordSaleUseCase:

    def __init__(self, sale_repo: AbstractSaleRepository) -> None:
        self._sale_repo = sale_repo

    async def execute(self, batch_id: UUID, req: RecordSaleRequest) -> SaleRecordResponse:
        now = datetime.now(timezone.utc)
        total = (req.quantity_kg * req.price_per_kg_uzs).quantize(req.price_per_kg_uzs)

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
        sale.payment_status = req.payment_status
        sale.sold_at = req.sold_at or now
        sale.notes = req.notes
        sale.created_at = now
        sale.updated_at = now

        sale = await self._sale_repo.create(sale)
        return SaleRecordResponse.model_validate(sale)

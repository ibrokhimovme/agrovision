"""
Batch report endpoints. T-14-05, T-14-06. SF-21.
GET /reports/batch/{id}       — JSON performance report
GET /reports/batch/{id}/pdf   — PDF export
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import Response

from app.application.use_cases.generate_batch_report import GenerateBatchReportUseCase
from app.infrastructure.clients.finance_client import FinanceClient
from app.infrastructure.clients.livestock_client import LivestockClient
from app.infrastructure.pdf.batch_report_pdf import generate_batch_report_pdf
from shared.contracts.api_standards import APIResponse

router = APIRouter()


def _use_case() -> GenerateBatchReportUseCase:
    return GenerateBatchReportUseCase(LivestockClient(), FinanceClient())


@router.get(
    "/reports/batch/{batch_id}",
    tags=["Reports"],
)
async def batch_report_json(batch_id: UUID):
    report = await _use_case().execute(batch_id)
    return APIResponse(data=report)


@router.get(
    "/reports/batch/{batch_id}/pdf",
    tags=["Reports"],
    response_class=Response,
)
async def batch_report_pdf(batch_id: UUID):
    report = await _use_case().execute(batch_id)
    pdf_bytes = generate_batch_report_pdf(report)
    filename = f"batch-report-{str(batch_id)[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

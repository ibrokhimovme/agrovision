"""
Batch report endpoints. T-14-05, T-14-06. SF-21.
GET /reports/batch/{id}       — JSON performance report
GET /reports/batch/{id}/pdf   — PDF export

EX-12 (execution-v2) — Cross-Farm and Cross-Batch Trend Reporting:
GET /reports/farms/{farm_id}/batch-performance — per-batch report rows for one farm, chronologically ordered (batch comparison + mortality/weight/feed/revenue-profit trends)
GET /reports/farm-comparison                   — one aggregated row per farm, for farm-to-farm comparison
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.reporting.application.dtos.report_dtos import BatchReportResponse, FarmComparisonRow
from app.reporting.application.use_cases.generate_batch_report import GenerateBatchReportUseCase
from app.reporting.application.use_cases.get_farm_batch_performance import (
    GetFarmBatchPerformanceUseCase,
)
from app.reporting.application.use_cases.get_farm_comparison import GetFarmComparisonUseCase
from app.reporting.infrastructure.clients.finance_client import FinanceClient
from app.reporting.infrastructure.clients.livestock_client import LivestockClient
from app.reporting.infrastructure.pdf.batch_report_pdf import generate_batch_report_pdf
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


@router.get(
    "/reports/farms/{farm_id}/batch-performance",
    response_model=APIResponse[list[BatchReportResponse]],
    tags=["Reports"],
)
async def farm_batch_performance(
    farm_id: UUID,
    archived: str = Query(
        "false",
        pattern="^(true|false|all)$",
        description="EX-16 (execution-v2): 'false' (default), 'true', or 'all' — Reports supports all three.",
    ),
):
    use_case = GetFarmBatchPerformanceUseCase(LivestockClient(), FinanceClient())
    rows = await use_case.execute(farm_id, archived)
    return APIResponse(data=rows)


@router.get(
    "/reports/farm-comparison",
    response_model=APIResponse[list[FarmComparisonRow]],
    tags=["Reports"],
)
async def farm_comparison(
    farm_ids: str = Query(..., description="Comma-separated farm UUIDs"),
    archived: str = Query("false", pattern="^(true|false|all)$"),
):
    try:
        ids = [UUID(f.strip()) for f in farm_ids.split(",") if f.strip()]
    except ValueError:
        raise HTTPException(status_code=422, detail="farm_ids must be comma-separated UUIDs")
    use_case = GetFarmComparisonUseCase(LivestockClient(), FinanceClient())
    rows = await use_case.execute(ids, archived)
    return APIResponse(data=rows)

"""
PDF generator for batch performance report. T-14-06. SF-21.
Uses reportlab to produce a single-page performance card.
"""
from __future__ import annotations

import io
from decimal import Decimal
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.reporting.application.dtos.report_dtos import BatchReportResponse

_GREEN = colors.HexColor("#16a34a")
_LIGHT_GREEN = colors.HexColor("#f0fdf4")
_GRAY = colors.HexColor("#6b7280")
_DARK = colors.HexColor("#111827")
_RED = colors.HexColor("#dc2626")
_LIGHT_RED = colors.HexColor("#fef2f2")
_BLUE = colors.HexColor("#2563eb")
_LIGHT_BLUE = colors.HexColor("#eff6ff")


def _fmt(val: Optional[Decimal], decimals: int = 2, suffix: str = "") -> str:
    if val is None:
        return "—"
    return f"{float(val):,.{decimals}f}{suffix}"


def _fmt_int(val: Optional[int]) -> str:
    if val is None:
        return "—"
    return f"{val:,}"


def generate_batch_report_pdf(report: BatchReportResponse) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=18,
        textColor=_GREEN,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=_GRAY,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=11,
        textColor=_DARK,
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=4,
    )

    elements = []

    # ── Header ──────────────────────────────────────────────────────────────
    elements.append(Paragraph("AgroVision — Partiya hisoboti", title_style))
    code = report.batch_code or str(report.batch_id)[:8]
    elements.append(Paragraph(
        f"Partiya: {code}  |  Tur: {report.species.upper()}  |  Holat: {report.status}  |  "
        f"Sana: {report.generated_at.strftime('%Y-%m-%d %H:%M')} UTC",
        subtitle_style,
    ))

    # ── Batch info table ─────────────────────────────────────────────────────
    elements.append(Paragraph("Umumiy ma'lumot", section_style))
    info_data = [
        ["Ko'rsatkich", "Qiymat"],
        ["Boshlang'ich soni", _fmt_int(report.initial_count) + " bosh"],
        ["Joriy soni", _fmt_int(report.current_count) + " bosh"],
        ["Joylashtirilgan sana", report.placement_date],
        ["Yosh (kun)", _fmt_int(report.age_days)],
    ]
    _append_table(elements, info_data, _LIGHT_GREEN, _GREEN)

    # ── Growth performance ───────────────────────────────────────────────────
    elements.append(Paragraph("O'sish ko'rsatkichlari", section_style))
    growth_data = [
        ["Ko'rsatkich", "Qiymat"],
        ["FCR (yem konversiya koeffitsienti)", _fmt(report.fcr, 3)],
        ["O'rtacha kunlik o'sish (ADG)", _fmt(report.adg_grams, 1, " g/kun")],
        ["Oxirgi o'rtacha vazn", _fmt(report.latest_avg_weight_kg, 3, " kg")],
        ["Jami yem sarfi", _fmt(report.total_feed_kg, 1, " kg")],
        ["Jami suv sarfi", _fmt(report.total_water_liters, 1, " L")],
    ]
    _append_table(elements, growth_data, _LIGHT_BLUE, _BLUE)

    # ── Mortality ────────────────────────────────────────────────────────────
    elements.append(Paragraph("O'lim ko'rsatkichlari", section_style))
    mortality_data = [
        ["Ko'rsatkich", "Qiymat"],
        ["Jami nobud bo'lganlar", _fmt_int(report.total_deaths) + " bosh"],
        ["O'lim darajasi", _fmt(report.mortality_rate_pct, 2, "%")],
        ["Omon qolish darajasi", _fmt(report.survival_rate_pct, 2, "%")],
    ]
    _append_table(elements, mortality_data, _LIGHT_RED, _RED)

    # ── Financial ────────────────────────────────────────────────────────────
    elements.append(Paragraph("Moliyaviy ko'rsatkichlar", section_style))
    profit = report.gross_profit_uzs
    profit_color = _GREEN if (profit is None or profit >= 0) else _RED
    financial_data = [
        ["Ko'rsatkich", "Qiymat (UZS)"],
        ["Jami xarajat", _fmt(report.total_cost_uzs, 0)],
        ["Jami daromad", _fmt(report.total_revenue_uzs, 0)],
        ["Sof foyda", _fmt(report.gross_profit_uzs, 0)],
        ["Foyda marjasi", _fmt(report.profit_margin_pct, 2, "%")],
        ["Sotuvlar soni", _fmt_int(report.sale_count)],
        ["Xarajatlar soni", _fmt_int(report.expense_count)],
    ]
    _append_table(elements, financial_data, _LIGHT_GREEN, profit_color)

    doc.build(elements)
    return buffer.getvalue()


def _append_table(
    elements: list,
    data: list[list[str]],
    row_bg: colors.Color,
    header_text_color: colors.Color,
) -> None:
    col_w = [90 * mm, 70 * mm]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, 0), header_text_color),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        # Data rows
        ("BACKGROUND", (0, 1), (-1, -1), row_bg),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#1f2937")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [row_bg, colors.white]),
        # Grid
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 4 * mm))

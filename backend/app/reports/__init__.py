"""Reports layer.

Builds, renders and stores screening reports. All output is non-diagnostic
and carries the limitation notice.
"""

from __future__ import annotations

from app.reports.pdf_renderer import ReportRenderError, is_pdf_available, render_pdf
from app.reports.report_builder import (
    ReportCondition,
    ReportDocument,
    build_report_document,
)
from app.reports.report_constants import REPORT_MEDIA_TYPE, REPORT_TITLE
from app.reports.report_storage import StoredReport, store_report
from app.reports.report_templates import render_text

__all__ = [
    "REPORT_MEDIA_TYPE",
    "REPORT_TITLE",
    "ReportCondition",
    "ReportDocument",
    "ReportRenderError",
    "StoredReport",
    "build_report_document",
    "is_pdf_available",
    "render_pdf",
    "render_text",
    "store_report",
]

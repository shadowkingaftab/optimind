"""PDF rendering of a report document.

Uses ReportLab lazily. When ReportLab is not installed, rendering fails with
an honest unavailable error so callers do not silently emit a partial or
plain-text file mislabelled as a PDF.
"""

from __future__ import annotations

import io
from typing import Optional

from app.exceptions.base import APIException
from app.reports.report_builder import ReportDocument
from app.reports.report_templates import render_text


class ReportRenderError(APIException):
    """Raised when PDF rendering cannot be performed."""

    status_code = 503
    error_code = "report_render_unavailable"
    default_message = "Report rendering is currently unavailable."


def is_pdf_available() -> bool:
    """Return True when ReportLab is importable."""
    try:
        import reportlab  # type: ignore  # noqa: F401

        return True
    except Exception:  # noqa: BLE001
        return False


def _sanitize(text: str) -> str:
    """Best-effort replacement of characters unsupported by core PDF fonts."""
    return text.encode("latin-1", "replace").decode("latin-1")


def render_pdf(
    document: ReportDocument,
    *,
    text: Optional[str] = None,
    page_size: str = "A4",
) -> bytes:
    """Render ``document`` to PDF bytes.

    Raises:
        ReportRenderError: when ReportLab is not installed or rendering fails.
    """
    try:
        from reportlab.lib.pagesizes import A4, LETTER  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise ReportRenderError(
            "PDF rendering requires the 'reportlab' package to be installed."
        ) from exc

    size = A4 if str(page_size).upper() == "A4" else LETTER
    body = text if text is not None else render_text(document)

    buffer = io.BytesIO()
    try:
        pdf = canvas.Canvas(buffer, pagesize=size)
        _, height = size
        left, top = 40, height - 50
        line_height = 14
        y = top
        pdf.setFont("Helvetica", 10)
        for raw_line in body.splitlines():
            for chunk in _wrap(_sanitize(raw_line), 100):
                if y < 40:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
                    y = top
                pdf.drawString(left, y, chunk)
                y -= line_height
        pdf.showPage()
        pdf.save()
    except Exception as exc:  # noqa: BLE001
        raise ReportRenderError("The report could not be rendered as a PDF.") from exc

    return buffer.getvalue()


def _wrap(line: str, width: int) -> list[str]:
    if len(line) <= width:
        return [line]
    wrapped: list[str] = []
    current = ""
    for word in line.split(" "):
        if len(current) + len(word) + 1 > width and current:
            wrapped.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        wrapped.append(current)
    return wrapped or [""]

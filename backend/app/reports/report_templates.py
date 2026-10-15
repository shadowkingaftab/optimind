"""Plain-text rendering of a report document.

Used for previews, notifications and as a fallback when PDF rendering is
unavailable. Contains only the same non-diagnostic content as the document.
"""

from __future__ import annotations

from app.reports.report_builder import ReportDocument
from app.reports.report_constants import (
    SECTION_CONDITIONS,
    SECTION_MODEL,
    SECTION_NOTICE,
    SECTION_SUMMARY,
)


def render_text(document: ReportDocument) -> str:
    """Render ``document`` as a plain-text report."""
    lines: list[str] = [
        document.title,
        "=" * len(document.title),
        f"Generated: {document.generated_at.isoformat()}",
    ]
    if document.patient_code:
        lines.append(f"Patient reference: {document.patient_code}")

    lines.append("")
    lines.append(SECTION_SUMMARY)
    lines.append("-" * len(SECTION_SUMMARY))
    lines.append(f"Screening status: {document.status}")
    lines.append(f"Risk level: {document.risk_level or 'unknown'}")
    if document.outcome_label:
        lines.append(f"Primary label: {document.outcome_label}")
    if document.confidence is not None:
        lines.append(f"Confidence: {document.confidence:.3f}")

    if document.conditions:
        lines.append("")
        lines.append(SECTION_CONDITIONS)
        lines.append("-" * len(SECTION_CONDITIONS))
        for condition in document.conditions:
            score = (
                f"{condition.score:.3f}"
                if condition.score is not None
                else "n/a"
            )
            lines.append(
                f"- {condition.label}: score={score}, "
                f"risk={condition.risk_level or 'unknown'}"
            )

    lines.append("")
    lines.append(SECTION_MODEL)
    lines.append("-" * len(SECTION_MODEL))
    lines.append(f"Model version: {document.model_version or 'unknown'}")

    lines.append("")
    lines.append(SECTION_NOTICE)
    lines.append("-" * len(SECTION_NOTICE))
    lines.append(document.notice)
    lines.append(document.disclaimer)
    return "\n".join(lines)

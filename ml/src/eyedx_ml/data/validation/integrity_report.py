"""Validation issue and integrity report types.

A single, shared report shape used by every validator and cleaning step so the
pipeline can aggregate problems and fail clearly. Context fields must never
contain patient identifiers; use hashes or record indexes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__all__ = ["Severity", "ValidationIssue", "ValidationReport"]

_SEVERITIES = ("info", "warning", "error")


@dataclass(frozen=True)
class Severity:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = Severity.ERROR
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.severity not in _SEVERITIES:
            raise ValueError(f"invalid severity: {self.severity}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "context": dict(self.context),
        }


@dataclass
class ValidationReport:
    issues: List[ValidationIssue] = field(default_factory=list)
    checked: int = 0

    def add(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)

    def error(self, code: str, message: str, **context: Any) -> None:
        self.add(ValidationIssue(code, message, Severity.ERROR, context))

    def warning(self, code: str, message: str, **context: Any) -> None:
        self.add(ValidationIssue(code, message, Severity.WARNING, context))

    def info(self, code: str, message: str, **context: Any) -> None:
        self.add(ValidationIssue(code, message, Severity.INFO, context))

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: "ValidationReport") -> None:
        self.issues.extend(other.issues)
        self.checked += other.checked

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "checked": self.checked,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [i.to_dict() for i in self.issues],
        }


# Alias kept for readability at call sites that prefer the longer name.
IntegrityReport = ValidationReport

__all__ += ["IntegrityReport"]

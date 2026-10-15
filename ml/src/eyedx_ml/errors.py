"""Shared ML errors and optional-dependency helpers.

Heavy ML dependencies (torch, torchvision, onnx, captum, matplotlib,
scikit-learn) are optional at import time: the packages here import lazily so the
library can be imported, inspected and disposed without them installed. Calls
that genuinely need a dependency raise :class:`DependencyError` with a clear
remediation hint rather than failing obscurely.

Missing *external inputs* (approved labels, pretrained weights, validation
cohorts, calibration artifacts) raise :class:`NotConfiguredError` or a specific
subclass, so absence is handled safely and never masked by fabricated values.
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Optional

__all__ = [
    "MLPackageError",
    "DependencyError",
    "NotConfiguredError",
    "LabelUnavailableError",
    "ArtifactUnavailableError",
    "TrainingError",
    "EvaluationError",
    "CalibrationError",
    "ExplainabilityError",
    "ExportError",
    "RegistryError",
    "require_dependency",
    "is_available",
]


class MLPackageError(Exception):
    """Base class for all eyedx_ml errors."""


class DependencyError(MLPackageError):
    """Raised when an optional third-party dependency is not installed."""


class NotConfiguredError(MLPackageError):
    """Raised when a required external input has not been supplied yet."""


class LabelUnavailableError(NotConfiguredError):
    """Raised when approved labels / label map are not available."""


class ArtifactUnavailableError(NotConfiguredError):
    """Raised when model weights, checkpoints or artifacts are absent."""


class TrainingError(MLPackageError):
    """Raised for invalid training configuration or state."""


class EvaluationError(MLPackageError):
    """Raised for invalid evaluation inputs or state."""


class CalibrationError(MLPackageError):
    """Raised for invalid calibration inputs or state."""


class ExplainabilityError(MLPackageError):
    """Raised for invalid explainability inputs or unsupported methods."""


class ExportError(MLPackageError):
    """Raised for invalid or unverifiable model exports."""


class RegistryError(MLPackageError):
    """Raised for registry operation failures."""


def require_dependency(
    module_name: str,
    *,
    purpose: str = "",
    extra: Optional[str] = None,
) -> ModuleType:
    """Import and return a module, raising a clear error when it is absent."""
    try:
        return importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - depends on environment
        hint = f" (install: pip install {extra})" if extra else ""
        why = f" to {purpose}" if purpose else ""
        raise DependencyError(
            f"optional dependency '{module_name}' is required{why} but is not "
            f"installed{hint}"
        ) from exc


def is_available(module_name: str) -> bool:
    """Return True when a module can be imported without error."""
    try:
        importlib.import_module(module_name)
        return True
    except Exception:  # pragma: no cover - depends on environment
        return False

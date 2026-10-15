"""EyeDx ML package.

Screening-only research tooling for data preparation, model training and
evaluation. Nothing in this package fabricates clinical results. Data, labels
and model artifacts must be supplied under licence; the code fails clearly when
required inputs are absent.
"""

from __future__ import annotations

from .errors import (
    ArtifactUnavailableError,
    CalibrationError,
    DependencyError,
    EvaluationError,
    ExplainabilityError,
    ExportError,
    LabelUnavailableError,
    MLPackageError,
    NotConfiguredError,
    RegistryError,
    TrainingError,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
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
]

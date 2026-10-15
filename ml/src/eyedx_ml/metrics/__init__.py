"""Evaluation metrics."""

from __future__ import annotations

from .auroc import roc_auc, roc_auc_per_label
from .bootstrap_confidence_intervals import bootstrap_ci
from .calibration import (
    brier_score,
    expected_calibration_error,
    maximum_calibration_error,
    reliability_curve,
)
from .classification import accuracy, classification_metrics, confusion_matrix, f1_score
from .precision_recall import average_precision, precision, recall
from .segmentation import dice_coefficient, iou, mean_dice
from .sensitivity import sensitivity, sensitivity_at_threshold
from .specificity import specificity, specificity_at_threshold

__all__ = [
    "roc_auc",
    "roc_auc_per_label",
    "average_precision",
    "precision",
    "recall",
    "sensitivity",
    "sensitivity_at_threshold",
    "specificity",
    "specificity_at_threshold",
    "confusion_matrix",
    "accuracy",
    "f1_score",
    "classification_metrics",
    "brier_score",
    "expected_calibration_error",
    "maximum_calibration_error",
    "reliability_curve",
    "bootstrap_ci",
    "dice_coefficient",
    "iou",
    "mean_dice",
]

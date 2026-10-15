"""Classifier architectures."""

from __future__ import annotations

from .binary_classifier import BinaryClassifier
from .multiclass_classifier import MulticlassClassifier
from .multilabel_classifier import MultiLabelClassifier

__all__ = ["BinaryClassifier", "MulticlassClassifier", "MultiLabelClassifier"]

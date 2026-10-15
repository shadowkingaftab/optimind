"""Segmentation metrics (Dice, IoU)."""

from __future__ import annotations

import numpy as np

__all__ = ["dice_coefficient", "iou", "mean_dice"]


def dice_coefficient(pred: np.ndarray, target: np.ndarray, *, eps: float = 1e-6) -> float:
    pred = np.asarray(pred).astype(bool)
    target = np.asarray(target).astype(bool)
    intersection = np.logical_and(pred, target).sum()
    denom = pred.sum() + target.sum()
    if denom == 0:
        return 1.0
    return float((2 * intersection + eps) / (denom + eps))


def iou(pred: np.ndarray, target: np.ndarray, *, eps: float = 1e-6) -> float:
    pred = np.asarray(pred).astype(bool)
    target = np.asarray(target).astype(bool)
    intersection = np.logical_and(pred, target).sum()
    union = np.logical_or(pred, target).sum()
    if union == 0:
        return 1.0
    return float((intersection + eps) / (union + eps))


def mean_dice(pred: np.ndarray, target: np.ndarray) -> float:
    """Mean Dice over classes for (n, C, H, W) predictions of class indices or masks."""
    pred = np.asarray(pred)
    target = np.asarray(target)
    scores = []
    if pred.ndim >= 4:
        for c in range(pred.shape[1]):
            scores.append(dice_coefficient(pred[:, c], target[:, c]))
    else:
        scores.append(dice_coefficient(pred, target))
    return float(np.mean(scores)) if scores else float("nan")

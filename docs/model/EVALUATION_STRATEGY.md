# Evaluation Strategy

**Scope:** Evaluation of screening models. Screening only; not a diagnosis.

## 1. Principles
- **Held-out test set:** Internal test split never used for training/tuning/calibration/threshold selection.
- **Frozen thresholds:** External evaluation uses frozen operating points from internal validation; thresholds are never tuned on external data.
- **Bootstrap confidence intervals:** Compute when enabled (percentile bootstrap over samples; caller must handle grouping).
- **Small-cell suppression:** Subgroups with < min_cell_size are suppressed (no metrics reported).
- **Privacy:** Pseudonymous `record_id` only; no PHI in reports.
- **No fabrication:** Metrics only computed when data available; missing values reported as None.

## 2. Internal Evaluation
- **Metrics:** AUROC, average precision, sensitivity, specificity, F1, accuracy, Brier, ECE (configurable).
- **Thresholded metrics:** Require approved threshold per label (or global). When omitted, threshold-free metrics only.
- **Per-label & macro:** Evaluator computes per-label and macro averages (ignoring NaNs).
- **Error analysis:** False positives/negatives surfaced with `record_id` if provided.
- **Confusion matrices:** Per label at approved threshold(s).

## 3. Subgroup Evaluation
- **Dimensions:** `site_id`, `device_id`, `eye_side`, and metadata columns (e.g., `age_bucket`, `sex`) from non-identifying tables.
- **Suppression:** `min_cell_size` default 5.
- **Metrics:** Focus on AUROC/sensitivity/specificity/F1 (configurable).
- **Consistency:** Site/device consistency summaries report spread (min/max/range/mean).

## 4. External Validation
- **Frozen:** Thresholds frozen from internal validation. Harmonisation mapping (`external -> canonical`) is `INPUT_REQUIRED`.
- **Unlabelled/mismatched:** Excluded with documentation.
- **Reporting:** Same metric set; note added if no thresholds supplied.
- **No leakage:** External cohort never used for training/calibration/threshold selection.

## 5. Calibration Assessment
- **Metrics:** ECE, MCE, Brier; reliability diagram.
- **Data:** Validation set for fitting calibrators; test set for post-calibration assessment.
- **Reporting:** Calibration report includes reliability bins and method/temperature if applicable.

## 6. Implementation
- **Modules:** `eyedx_ml.evaluation.evaluator`, `subgroup_analysis`, `site_analysis`, `device_analysis`, `error_analysis`, `confusion_analysis`, `external_validation`, `evaluation_report`.
- **Bootstrap:** `eyedx_ml.metrics.bootstrap_confidence_intervals` (percentile).
- **Scripts:** `ml/scripts/evaluate.py` (internal), `ml/scripts/external_validate.py` (external).

## Notes
- Thresholds must be approved and documented. The code does not invent operating points.
- Subgroup definitions must use only non-identifying columns.
- External validation enforces frozen thresholds and requires harmonisation.

# Calibration Strategy

**Scope:** Probability calibration for screening models. Screening only; not a diagnosis.

## 1. Principles
- **Validation-only fitting:** Calibrators (temperature scaling, isotonic) are fitted on the validation split only.
- **No threshold tuning:** Calibration adjusts probabilities; threshold selection remains separate (done on validation under stated criterion).
- **Frozen on external:** External evaluation uses frozen calibrated probabilities and frozen thresholds.
- **Measured metrics:** ECE/MCE/Brier computed on the held-out test set after calibration.
- **Safe defaults:** Unfitted calibrators cannot be applied.

## 2. Methods
- **Temperature scaling:** Single scalar temperature fitted by minimising NLL (BCE for binary, cross-entropy for multiclass). Implemented in `calibration.temperature_scaling`.
- **Isotonic regression:** Monotonic mapping from scores to calibrated probabilities (`sklearn.isotonic.IsotonicRegression`). Use with care on small validation sets.
- **Reliability diagrams:** Binned accuracy vs confidence, generated via `calibration.reliability_diagram`.

## 3. Workflow
1. Train model on training split; select checkpoint on validation.
2. Collect validation logits/scores and targets to fit calibrator.
3. Apply calibrator to validation/test/external as appropriate.
4. Evaluate calibration on test (ECE/MCE/Brier) and report.
5. Persist calibration artifact (method, parameters, fitted status) for export/inference.

## 4. Reporting
- **Calibration report:** JSON with ECE, MCE, Brier, reliability bins (`calibration.calibration_report`).
- **Artifact:** JSON with method name and parameters (e.g., `temperature`) for reproducibility.
- **Plots:** Reliability diagram PNG (headless, Agg backend).

## 5. Inference
- **Configuration:** Inference config may specify `calibration.method` and `calibration.temperature` (INPUT_REQUIRED when using temperature scaling).
- **Application:** Calibrated probabilities used for thresholding/uncertainty only if calibrator is available; otherwise raw probabilities used with a documented rationale.

## 6. Implementation
- **Modules:** `eyedx_ml.calibration.{temperature_scaling,isotonic_regression,reliability_diagram,calibration_report,threshold_optimizer}`.
- **Script:** `ml/scripts/calibrate.py`.

## Notes
- Calibration is not a substitute for good model performance.
- Thresholds must remain approved after calibration.
- Calibration data must never include the test split.
- No PHI in calibration artifacts/reports.

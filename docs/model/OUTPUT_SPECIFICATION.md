# Model Output Specification

**Scope:** Defines model outputs across training, evaluation, export and inference. Screening only; not a diagnosis.

## 1. Inference Outputs (Prediction Response)
Aligned to `contracts/json-schemas/prediction-response.schema.json`:
- **request_id** (uuid, required)
- **status** (enum: `success | low_quality | uncertain | abstained | failed`)
- **model_id**, **model_version** (required)
- **processing_time_ms** (int >= 0, required)
- **predictions** (array of `{label, score[0..1]}`) — present when status allows; absent for low_quality/failed/abstained unless specified.
- **uncertainty** (object, optional) — uncertainty estimates when `supports_uncertainty=true`.
- **explanation** (object, optional) — explanation metadata/availability when `supports_explanation=true`.
- **quality_checks** (object, optional) — image quality assessment results.
- **abstention_reason** (string, optional) — when status is `abstained`.
- **failure_reason** (string, optional) — when status is `failed` (non-clinical, safe).
- **limitation_notice** (string, optional but mandatory in user-facing contexts) — screening limitation notice.

All fields comply with the contract; no extra diagnostic fields are emitted.

## 2. Training Outputs
- **Checkpoints:** `last.pt`, `best.pt` (TorchScript-serialisable state dicts) plus `*.meta.json` sidecars containing metadata.
- **Experiment logs:** JSONL under `ml/experiments/` (privacy-safe; redacted identifiers).
- **History:** Per-epoch train/validation metrics returned by trainer (losses; no fabricated performance claims).

## 3. Evaluation Outputs
- **Evaluation reports:** JSON under `ml/outputs/reports/` (internal/external/subgroup) assembled via `evaluation.evaluation_report`.
- **Confusion matrices, subgroup summaries:** Produced by evaluator/subgroup analyzers. Small cells suppressed (min count configurable).
- **Bootstrap CIs:** Included when enabled (point estimate + lower/upper, n_resamples, confidence level).

## 4. Calibration Outputs
- **Calibration report:** `ml/outputs/calibration/calibration-report.json` (ECE/MCE/Brier, reliability bins).
- **Calibration artifact:** `ml/outputs/calibration/calibration-artifact.json` (method, parameters, e.g. temperature).
- **Reliability diagram:** PNG (optional) when plotting enabled.

## 5. Explainability Outputs
- **Heatmaps:** Normalised 2D arrays saved as images/JSON under `ml/outputs/explainability/` (review only).
- **Validation:** Sanity checks (shape, finite, unit range) recorded in the report.

## 6. Export Outputs
- **Model package:** Directory containing `model-metadata.json`, `package-manifest.json`, TorchScript (`model.pt`) and optional ONNX (`model.onnx`).
- **Model metadata:** Contract-aligned (`model_id`, `model_version`, `created_at`, `labels`, `preprocessing`, `capabilities`, optional `calibration`, `description`).
- **Validation:** `validate_export` confirms presence of required files and contract compliance.

## 7. Registry Outputs
- **Index:** `ml/models/registry/index.json` (file-based registry) tracking registered versions, stages and history.
- **Staged packages:** Copies of approved packages under `ml/models/registry/{model_id}/{model_version}/`.

## Notes
- No PHI in outputs. `patient_key`/identifiers never appear in reports or artifacts.
- All numeric values are measured or computed from data; none are invented.
- Screening limitation notice is included in all user-facing inference responses.

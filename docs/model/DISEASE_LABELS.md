# Disease Labels

**Scope:** Canonical disease label vocabulary for screening. Screening only; not a diagnosis.

## 1. Source of Truth
- **Primary:** `datasets/annotations/label-map.json`
- **Status:** Must be `approved` with non-empty `labels` array before training/evaluation/export/inference.
- **Enforcement:** `LabelUnavailableError` is raised if the label map is missing, unapproved or empty.
- **Format:** `{schema_version, status, labels:[{code, display_name, source_values[], is_normal, description}], ignore_values[], notes}`

## 2. Label Selection
- Labels are determined from the approved label map only. No hardcoded disease list is assumed by the codebase.
- `source_values[]` documents how raw annotations map to canonical codes (harmonisation INPUT_REQUIRED for external cohorts).
- `is_normal` identifies negative/normal classes (used for interpretation only; not a diagnostic claim).
- `ignore_values[]` lists annotation values excluded from training.

## 3. Usage in Code
- `ModelConfig.load_approved_labels()` returns canonical codes in order.
- `MultiLabelClassifier` requires `num_labels` and uses the approved vocabulary.
- `ModelMetadata.labels` (export) contains the canonical codes array.
- Inference responses include per-label `predictions` with scores for approved labels only.

## 4. External Harmonisation
- External datasets require a harmonisation mapping from external labels to canonical codes (`harmonisation: INPUT_REQUIRED` in `ml/configs/evaluation/external.yaml`).
- External labels not mapped to canonical codes are excluded and documented.

## 5. Governance
- Label map changes require review/approval before use.
- No labels are invented during preprocessing/ingestion/training/evaluation.
- Screening outputs must not imply a definitive diagnosis.

## Notes
- The example `contracts/examples/prediction-response.json` uses generic `"reference_class"` only as an example shape; actual labels come from the approved map.
- All label-related fields marked `INPUT_REQUIRED` must be satisfied before running scripts.

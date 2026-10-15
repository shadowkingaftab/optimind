# Model Requirements

**Scope:** Technical and non-functional requirements for screening models. Screening only; not a diagnosis.

## 1. Functional Requirements
- **Architecture:** Support multilabel/multiclass/binary/multitask/segmentation/ensemble as configured.
- **Labels:** Require approved label map (`status==approved`, non-empty). Raise `LabelUnavailableError` if absent.
- **Preprocessing:** Deterministic, configurable (resize/normalise). Mean/std are `INPUT_REQUIRED`.
- **Inference contract:** Comply with `prediction-response.schema.json` (status enum, required fields, limitation notice).
- **Metadata:** Export contract-aligned `model-metadata.json` (labels array, preprocessing object, capabilities with three booleans).
- **Uncertainty:** Support `max_prob` (default), `entropy`, `mc_dropout` when `supports_uncertainty=true`.
- **Abstention:** Configurable threshold; sets status `abstained` or `uncertain` per config.
- **Quality gating:** Enforce resolution/brightness/blur thresholds; return `low_quality` when failed.

## 2. Non-Functional Requirements
- **Privacy:** No PHI in code, configs, logs, artifacts or registry. Pseudonymous `patient_key` only.
- **Reproducibility:** Versioned configs, fixed seeds, deterministic ops option, split checksums.
- **Safety:** Screening limitation notice included in user-facing responses. No diagnostic claims. Safe failure messages.
- **Portability:** Lazy heavy deps; module imports stay light; errors when deps missing.
- **Performance:** Latency benchmarked (measured, not assumed). Batch inference supported.

## 3. Data Requirements
- **Splits:** Patient-level (train/val/test/external). Test never used for tuning.
- **Provenance:** Approved/licence-compliant sources; source registry used when ingesting.
- **Leakage:** Leakage detection run during validation.
- **Small cells:** Subgroup suppression (min_cell_size >= 5 by default).

## 4. Export & Registry
- **TorchScript:** Primary export format; ONNX optional.
- **Packaging:** Include metadata + manifest; validate before registration.
- **Staging:** Development/Staging/Production/Archived. Promotion to Production requires named approver.
- **Rollback:** Supported with approval trail in registry history.

## 5. Dependencies
- **Lightweight core:** numpy, pandas, pydantic (backend), PyYAML; standard library.
- **Heavy (optional):** torch, torchvision, onnx, captum, matplotlib, scikit-learn, albumentations — imported lazily. Not declared as hard deps in packaging yet (Phase 5).
- **Validation:** All required inputs must be present; code fails fast with clear errors.

## 6. Testing & Compliance
- **No execution:** Phase 5 does not run tests/builds/linters/migrations/downloads/pipelines.
- **Placeholders:** `ml/tests/*.py` remain blank (Phase 13).
- **Documentation:** All artifacts documented with INPUT_REQUIRED markers where applicable.

## Notes
- Thresholds and clinical operating points are not defined here and must come from approval.
- Pretrained weights never downloaded automatically; explicit path required under licence.
- All values marked INPUT_REQUIRED must be supplied before any script runs.

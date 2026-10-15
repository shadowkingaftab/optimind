# Model Release Process

**Scope:** Release process for screening models. Screening only; not a diagnosis.

## 1. Prerequisites
- [ ] Approved label map (`datasets/annotations/label-map.json`, status `approved`).
- [ ] Approved dataset (provenance/licence documented; source registry current).
- [ ] Canonical manifest and patient-level splits (train/val/test/external-test) validated.
- [ ] Leakage detection passed; no known data leakage issues.
- [ ] Model config and training config versioned in git.

## 2. Training & Selection
- [ ] Train on training split only.
- [ ] Select checkpoint on validation (early stopping + metric). Document selection criterion.
- [ ] Evaluate on internal test split (held-out). Record metrics with CIs if enabled.
- [ ] Fit calibrator on validation; assess calibration on test.
- [ ] Select operating thresholds on validation under approved criterion. Document rationale and that thresholds are not tuned on test/external.
- [ ] Perform subgroup evaluation (site/device/eye_side); ensure small-cell suppression applied.

## 3. External Validation (if applicable)
- [ ] Frozen thresholds from step 2.
- [ ] Harmonisation mapping external -> canonical (`INPUT_REQUIRED`).
- [ ] Evaluate on external cohort; report metrics with CIs.
- [ ] Document external cohort characteristics (non-identifying) and any exclusions.

## 4. Safety & Explainability Review
- [ ] Error analysis complete (FP/FN cases) with pseudonymous record ids.
- [ ] Explainability review for sampled cases (review-only; not diagnostic).
- [ ] Quality gate thresholds reviewed per model.
- [ ] Uncertainty/abstention configuration reviewed and approved.
- [ ] Screening limitation notice confirmed in inference contract.

## 5. Export & Packaging
- [ ] Export model to TorchScript (primary); ONNX if required.
- [ ] Build contract-aligned `model-metadata.json` (labels, preprocessing, capabilities, calibration if any).
- [ ] Package with `package-manifest.json`; run `validate_export`.
- [ ] Include calibration artifact and metadata sidecar as required.

## 6. Registration & Staging
- [ ] Register package in file registry (`ml/scripts/register_model.py`) to `development` or `staging` as appropriate.
- [ ] Review package contents (no PHI, weights/licences OK).
- [ ] Promotion to `staging` requires documented review.
- [ ] Promotion to `production` requires named approver (`approved_by`, `INPUT_REQUIRED`) and audit trail in registry history.

## 7. Approval & Release
- [ ] All checkboxes satisfied; review sign-off recorded (non-PHI).
- [ ] Registry entry updated with stage history, approver, notes.
- [ ] Release notes document model_id, model_version, capabilities, thresholds, calibration, known limitations.
- [ ] Model service updated to consume approved package (Phase 6) — out of scope here.

## 8. Post-Release
- [ ] Monitor performance/latency per monitoring plan (privacy-safe metrics).
- [ ] Rollback procedure available via registry (`rollback_model`) with approval.
- [ ] Archive superseded versions when no longer in use.

## Notes
- No automated promotion to production. Human approval is mandatory.
- Test set results must never influence threshold/model selection.
- External validation requires frozen thresholds and harmonisation.
- All `INPUT_REQUIRED` items must be satisfied at each step.
- Screening only; not a diagnosis.

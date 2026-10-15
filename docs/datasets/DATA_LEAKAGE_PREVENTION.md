# Data leakage prevention

Leakage is any information in the training data that would not be available at
prediction time, or overlap between splits that inflates measured performance.
This document defines the policies enforced by the pipeline.

## 1. Split integrity (patient-level)

**Rule:** all images of a patient stay in exactly one split. Splits are grouped
by `patient_key`, never by image.

- Implemented by `eyedx_ml.data.splitting.split_by_patient`.
- Verified by `eyedx_ml.data.validation.detect_patient_leakage`, which fails when
  a patient appears in more than one split.

## 2. Duplicate leakage

**Rule:** identical images must not appear across splits.

- Exact duplicates: identical SHA-256 checksums.
- Near duplicates: perceptual (dHash) distance at or below a threshold.
- Verified by `detect_duplicate_leakage`; both checks report split names, not
  patient identifiers.

## 3. External validation isolation

**Rule:** external data is held out entirely and never used for training or
threshold selection. It is not split; it is one test cohort.

- Implemented by `split_by_site` (leave-site-out) and the external config.

## 4. Source/site/device confounds

**Rule:** when performance is sensitive to acquisition conditions, prefer
leave-site-out or leave-device-out splits so the model is evaluated on unseen
conditions rather than memorising them.

## 5. Temporal leakage

**Rule:** if the data spans time, splits should be chronological (train on the
past, evaluate on the future). Record the time field used; INPUT_REQUIRED.

## 6. Label leakage

**Rule:** labels must never be derived from filenames, paths or metadata that
would not exist at prediction time. Raw source values are mapped only via the
approved label map.

## 7. Preprocessing leakage

**Rule:** normalisation statistics (mean/std) are computed from the **training
split only** and then frozen. Computing them over the whole dataset leaks
evaluation information.

## 8. Checks in CI / review

1. Run `validate_dataset.py` — zero errors required.
2. Run the leakage detector and require zero leakage issues.
3. Record the split manifest (`split-manifest.json`) with its input checksum for
   auditability.

## 9. Related

- [`../../ml/src/eyedx_ml/data/validation/leakage_detector.py`](../../ml/src/eyedx_ml/data/validation/leakage_detector.py)
- [`../../ml/src/eyedx_ml/data/splitting/`](../../ml/src/eyedx_ml/data/splitting/)

# Quality control

Structural quality checks applied to images and metadata in the dataset pipeline.
These are **data-quality** signals, not clinical measures, and never constitute a
diagnosis.

## 1. Manifest validation

`ml/scripts/validate_dataset.py` checks:

- Required fields present; no duplicate `record_id`.
- `patient_key` present on every record.
- Eye side and site/device references valid or flagged.
- Labels present (when required), numeric, and within range.
- No patient leakage or checksum/perceptual-hash duplicates across splits.

## 2. Image validation

`ml/scripts/validate_dataset.py --images` probes a sample (or all) images and
flags:

| Signal | Rule (default) | Severity |
| --- | --- | --- |
| Unreadable | decode fails | error |
| Unsupported format | not JPEG/PNG | error |
| Low resolution | below `min_width`×`min_height` | warning |
| Low brightness | mean luminance below `min_brightness` | warning |
| Possible blur | blur score above `max_blur_score` | warning |

Thresholds are configuration inputs (`ml/configs/datasets/*.yaml`); defaults are
conservative and must be reviewed per model.

## 3. Cleaning

`ml/scripts/clean_dataset.py` detects and reports (never deletes):

- **Exact duplicates** by SHA-256 checksum.
- **Near duplicates** by perceptual (dHash) distance.
- **Corrupted images** by a full decode.
- **Size outliers** by the IQR rule (optional).

It writes an exclude list (`*.exclude.csv`) that downstream steps can apply.

## 4. Statistics

`ml/scripts/calculate_statistics.py` produces aggregate class/image/demographic
statistics. Demographic cells below `min_cell_size` (default 5) are suppressed to
avoid re-identification.

## 5. Reporting and thresholds

- A run is acceptable only when validation has zero error-level issues.
- Warnings are reviewed and either accepted (with justification) or fixed.
- All reports are JSON artifacts alongside the manifest in `datasets/interim/`.

## 6. Related

- [`../../datasets/image-quality.schema.json`](../../datasets/image-quality.schema.json)
- [`../../ml/src/eyedx_ml/data/validation/`](../../ml/src/eyedx_ml/data/validation/)

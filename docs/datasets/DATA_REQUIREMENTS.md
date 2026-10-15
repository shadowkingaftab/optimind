# Data requirements

Defines what data EyeDx needs, in what form, and the inputs that must be supplied
before the dataset pipeline can run. Nothing here is downloaded automatically.

## 1. Required inputs

| Input | Format | Schema / columns | Source | Owner | Delivery |
| --- | --- | --- | --- | --- | --- |
| Image manifest | CSV or JSON | `record_id, image_path, patient_key, site_id, device_id, eye_side, image_format, checksum_sha256` (see `ml/src/eyedx_ml/data/ingestion/dataset_importer.py`) | Data owner | Data owner | Secure transfer into `datasets/raw` |
| Images | JPEG/PNG | One file per record; referenced by `image_path` | Source site | Data owner | Secure transfer into `datasets/raw` |
| Patient table | CSV | `patient_key` (+ coarse attributes) | Data owner | Data owner | Into `datasets/metadata` |
| Site/device tables | CSV | `site_id` / `device_id` (+ descriptors) | Data owner | Data owner | Into `datasets/metadata` |
| Label map | JSON | see `datasets/annotations/label-map.json` | Clinical owner | Clinical owner | Committed (after approval) |
| Annotations | CSV | `record_id, raw_label, value\|label_present` | Clinical owner | Clinical owner | Into `datasets/annotations` |
| Source registry | JSON | `source_id, name, owner, contact, license, consent_basis, retention, approved` | Governance | Governance | Into `datasets/external` |
| Pseudonymization salt | secret string | ≥32 random bytes | Security | Security | Injected via `EYEDX_PSEUDONYMIZATION_SALT` env; **never committed** |

## 2. Data quality expectations

- Images decodable; preferred format JPEG/PNG.
- Minimum resolution and brightness gates per `ml/configs/datasets/*.yaml`.
- `patient_key` present on every record (required for leakage-safe splits).
- One label map covers all sources; external codes harmonise to canonical codes.

## 3. Privacy requirements

- No direct identifiers in any tracked file.
- Patient keys are salted hashes; salts are never committed.
- Metadata uses coarse buckets, not exact identifying values.
- Demographics reports suppress cells smaller than `min_cell_size` (default 5).

## 4. Absence handling

The pipeline **fails clearly** when required inputs are missing rather than
proceeding with defaults:

- Missing manifest / registry / label map → non-zero exit with a message.
- `status != approved` label map → mapping refused.
- Missing pseudonymization salt → ingestion refused.

## 5. Not required here

Model weights, GPUs, training frameworks and network access. Those belong to
later phases.

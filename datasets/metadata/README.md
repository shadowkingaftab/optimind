# Metadata tables

Canonical metadata tables referenced by the manifest. Only schemas/headers are
committed here; rows are supplied under licence out of band. **Patient tables
contain pseudonymous keys and coarse, non-identifying attributes only — never
direct identifiers.**

## Tables

| File | Required columns | Notes |
| --- | --- | --- |
| `patients.csv` | `patient_key` | Pseudonymous patient key + coarse attributes (e.g. `age_bucket`). No names, MRNs or dates of birth. |
| `clinical-sites.csv` | `site_id` | Registered acquisition sites. |
| `acquisition-devices.csv` | `device_id` | Camera/device descriptors. |
| `images.csv` | `record_id`, `image_path`, `patient_key` | The manifest linking records to images and patients. |

## Conventions

- Keys (`patient_key`, `site_id`, `device_id`, `record_id`) are stable
  identifiers; never repurpose a key.
- `patient_key` is a salted hash produced by
  `eyedx_ml.data.ingestion.pseudonymize`. The salt is never committed.
- `image_path` is relative to `image_root` (`datasets/raw` by default).
- Prefer coarse buckets over exact values for any potentially identifying
  attribute.
- Column headers in the committed files define the contract; do not rename them.
- Cross-references between tables must resolve; the validators warn on unknown
  `site_id`/`device_id` values in the manifest.

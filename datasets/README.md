# Datasets

Governance, contracts and (empty) layout for the screening datasets used to
build and evaluate the EyeDx model.

> **No patient images are committed to this repository.** Every content
> directory below is a placeholder guarded by `.gitkeep`. Actual image bytes and
> clinical tables are supplied under licence, out of band, and are excluded from
> version control. See [`../docs/datasets/DATA_REQUIREMENTS.md`](../docs/datasets/DATA_REQUIREMENTS.md).

This project is a **screening** tool. Nothing here defines or implies a
diagnosis; dataset labels describe a screening reference, not clinical truth.

## Layout

| Path | Tracked? | Purpose |
| --- | --- | --- |
| `raw/` | no | Immutable images exactly as received from a registered source. |
| `external/` | no | External-site / external-device validation images. |
| `interim/` | no | Normalised manifests and intermediate artifacts. |
| `processed/` | no | Preprocessed, model-ready tensors/arrays. |
| `metadata/` | schemas/headers only | Canonical metadata tables (pseudonymous keys only). |
| `annotations/` | schemas/templates only | Label map and annotation schema/labels. |
| `splits/` | generated | Per-split CSVs and the split manifest. |
| `licenses/` | yes | Licence register and attribution. |
| `datasheets/` | yes | Dataset card and protocol documentation. |
| `documentation/` | yes | Additional dataset notes. |

## Provenance and governance

1. **Registered sources only.** Each source must be recorded in the source
   registry with licence, consent basis, retention and owner before ingestion.
   Unknown or unapproved sources are refused (`eyedx_ml.data.ingestion`).
2. **Pseudonymous keys.** Patient identifiers are hashed with a deployment salt
   (`input.pseudonymization_salt`, inject via environment). The salt is never
   committed.
3. **Labels are owned by clinicians.** The canonical label map must be explicitly
   approved (`status: approved`). The pipeline refuses to map labels otherwise.
4. **No leakage.** Splits are patient-level by default; external validation is
   held out entirely.

## Pipeline

The dataset pipeline lives in `ml/` and is driven by
[`params.yaml`](params.yaml) / `ml/configs/datasets/*.yaml`:

```text
raw manifest ──ingest_dataset──▶ interim manifest
              ──validate_dataset──▶ validation report (JSON)
              ──clean_dataset──▶ cleaning report + exclude list
              ──generate_splits──▶ splits/*.csv + split-manifest.json
              ──calculate_statistics──▶ dataset statistics report (JSON)
```

Scripts never download data, delete files or fabricate records; they fail with a
clear message when required inputs are absent.

## Related documentation

- [`../docs/datasets/DATA_REQUIREMENTS.md`](../docs/datasets/DATA_REQUIREMENTS.md)
- [`../docs/datasets/DATASET_SOURCES.md`](../docs/datasets/DATASET_SOURCES.md)
- [`../docs/datasets/LABELING_GUIDELINES.md`](../docs/datasets/LABELING_GUIDELINES.md)
- [`../docs/datasets/QUALITY_CONTROL.md`](../docs/datasets/QUALITY_CONTROL.md)
- [`../docs/datasets/DATA_LEAKAGE_PREVENTION.md`](../docs/datasets/DATA_LEAKAGE_PREVENTION.md)
- [`../docs/datasets/DATASET_VERSIONING.md`](../docs/datasets/DATASET_VERSIONING.md)

# `raw/` — immutable source images

This directory holds fundus images **exactly as received** from a registered
source. Nothing here is committed to version control; the directory is kept in
the tree only via `.gitkeep`.

## Rules

- **Immutable.** Never edit, crop, rename or re-encode images in `raw/`.
  Preprocessing happens later and writes to `processed/`.
- **Provenance required.** A source must be registered (licence, consent basis,
  owner, retention) before images are placed here. See
  [`../external/README.md`](../external/README.md) and
  [`../../docs/datasets/DATASET_SOURCES.md`](../../docs/datasets/DATASET_SOURCES.md).
- **Pseudonymous metadata.** The manifest that references these images
  (`../metadata/images.csv`) contains only pseudonymous `patient_key` values,
  never direct identifiers.
- **No downloads by tooling.** The pipeline scripts read from here but never
  fetch data from the network.

## Expected layout

```text
raw/
  <source_id>/
    <record_id>.<ext>
```

`image_path` values in the manifest are relative to the `image_root` configured
in `ml/configs/datasets/*.yaml` (default: `datasets/raw`).

## Checksums

On ingestion, each image's SHA-256 is recorded in the manifest
(`checksum_sha256`) so duplicates across sources can be detected without
comparing pixels. Do not alter files after hashing.

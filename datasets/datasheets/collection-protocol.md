# Collection protocol

Defines how source images are collected and prepared for the screening dataset.
Fill in the `INPUT_REQUIRED` fields with the agreed protocol; do not invent
details.

## 1. Sources

- Registered sources only. Each source is recorded in the source registry with
  licence, consent basis, owner and retention (see
  [`../external/README.md`](../external/README.md)).
- Acquisition sites and devices: INPUT_REQUIRED (see `../metadata/`).

## 2. Consent and legal basis

- **Consent basis:** INPUT_REQUIRED (e.g. explicit consent, ethics waiver).
- **Ethics approval reference:** INPUT_REQUIRED
- **Data-use agreement reference:** INPUT_REQUIRED

## 3. De-identification

1. Direct identifiers are removed at the source where possible.
2. Patient identifiers are replaced with a salted hash (`patient_key`); the salt
   is injected via environment and never committed.
3. Images are stored without embedded identifiers where feasible; embedded
   metadata is reviewed on ingestion.

## 4. Inclusion / exclusion

- **Inclusion criteria:** INPUT_REQUIRED
- **Exclusion criteria:** INPUT_REQUIRED
- **Unusable/ungradable images:** handled as `ignore_values` in the label map or
  excluded by the cleaning step.

## 5. Transfer and storage

- Data is transferred over an approved, encrypted channel into `datasets/raw/`.
- Files are treated as immutable and hashed (SHA-256) on ingestion.
- Access is limited to authorised personnel; retention follows the source policy.

## 6. Change control

Any re-ingestion, correction or removal is recorded with a new dataset version
(see `../../docs/datasets/DATASET_VERSIONING.md`).

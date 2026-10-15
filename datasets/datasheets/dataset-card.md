# Dataset card

A datasheet describing the screening dataset used to develop and evaluate the
EyeDx model. This card is a **template**; fields marked `INPUT_REQUIRED` must be
completed by the data owner before the dataset is used. No values here are
fabricated.

> This dataset and model are for **screening** research only. They do not
> provide a diagnosis and have not been established as a medical device.

## 1. Motivation

- **Purpose:** support development and evaluation of a retinal screening model
  that flags images for human review.
- **Intended users:** research/engineering staff under governance oversight.
- **Out-of-scope uses:** diagnosis, treatment decisions, triage without human
  review, any use without a valid licence.

## 2. Composition

| Attribute | Value |
| --- | --- |
| Number of images | INPUT_REQUIRED |
| Number of patients | INPUT_REQUIRED |
| Number of sites | INPUT_REQUIRED |
| Number of devices | INPUT_REQUIRED |
| Capture period | INPUT_REQUIRED |
| Geography | INPUT_REQUIRED |
| Label provenance | INPUT_REQUIRED (see `../annotations/label-map.json`) |

- **Unit of data:** one fundus image per record; records grouped by patient.
- **Labels:** screening reference labels only; authored by the clinical owner.
- **Exclusions:** see `known-limitations.md` and the cleaning report.

## 3. Collection process

See [`collection-protocol.md`](collection-protocol.md). Summarise here:
consent basis, de-identification, and any sampling.

## 4. Annotation process

See [`annotation-protocol.md`](annotation-protocol.md). Summarise annotator
qualifications, protocol version and agreement statistics (INPUT_REQUIRED).

## 5. Preprocessing / cleaning

- Resize, retinal crop, illumination correction, normalisation per
  `ml/configs/datasets/*.yaml`.
- Duplicate/corruption/outlier handling per `ml/scripts/clean_dataset.py` (records
  excluded, never deleted).

## 6. Uses

- **Permitted:** screening-model research, internal validation, subgroup
  analysis.
- **Prohibited:** re-identification, redistribution beyond the licence, clinical
  deployment without regulatory clearance.

## 7. Distribution and licence

- **Licence:** INPUT_REQUIRED (see [`../licenses/DATASET_LICENSES.md`](../licenses/DATASET_LICENSES.md)).
- **Access:** data is provided out of band; it is never committed to this repo.

## 8. Maintenance

- **Owner:** INPUT_REQUIRED
- **Version / last updated:** INPUT_REQUIRED (see `../../docs/datasets/DATASET_VERSIONING.md`).

## 9. Ethical and legal considerations

- Data minimisation: only pseudonymous keys and coarse attributes are stored.
- No direct identifiers are present in tracked files.
- Subgroup representation and known biases: see `known-limitations.md`.

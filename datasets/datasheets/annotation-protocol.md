# Annotation protocol

Defines how screening reference labels are produced. Labels are owned by the
clinical owner and must be captured in the approved
[`../annotations/label-map.json`](../annotations/label-map.json).

> Annotations are a **screening reference**, not a clinical gold standard or
> diagnosis.

## 1. Label vocabulary

- Canonical codes, display names and raw `source_values` are defined in the
  label map; `status` must be `approved` before use.
- Values to drop (ungradable, unusable) are listed under `ignore_values`.

## 2. Annotators

| Attribute | Value |
| --- | --- |
| Roles/qualifications | INPUT_REQUIRED |
| Number of annotators | INPUT_REQUIRED |
| Training provided | INPUT_REQUIRED |

## 3. Process

1. Each image is presented without any model output (to avoid anchoring).
2. Two independent annotations are taken where feasible.
3. Disagreements are adjudicated by a senior reviewer.
4. Batch metadata (annotator id, protocol version, timestamp) is recorded in the
   annotation table.

## 4. Quality metrics

- **Inter-rater agreement (e.g. Cohen's kappa):** INPUT_REQUIRED
- **Adjudication rate:** INPUT_REQUIRED
- **Audit sampling rate:** INPUT_REQUIRED

## 5. Imbalance and sampling

Document how positive/negative examples were sampled and any deliberate
enrichment, so prevalence in reports can be interpreted correctly.

## 6. Storage

Annotations live in `../annotations/labels.csv` (header only in this repository)
and are applied to records via the approved label map. Raw source values are
retained so mappings remain auditable.

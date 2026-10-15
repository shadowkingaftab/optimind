# Labeling guidelines

Guidelines for producing screening reference labels. Labels are authored and
approved by the clinical owner; this document describes the process, not the
label vocabulary (which lives in the approved
[`label-map.json`](../../datasets/annotations/label-map.json)).

> Labels are a **screening reference**, not a diagnosis.

## 1. Vocabulary and codes

- Canonical codes are lowercase and space-free. Raw source values are preserved
  and mapped to codes by the label map.
- Each raw value maps to exactly one code; ambiguous mappings are rejected.
- `ignore_values` lists raw values that are dropped (e.g. ungradable) rather than
  assigned a code.

## 2. Annotator workflow

1. Views are shown without model predictions.
2. Apply the annotation protocol consistently; use the same protocol version for
   a whole batch.
3. Mark unusable images using the agreed `ignore_values` rather than guessing.
4. Record `annotator_id` (pseudonymous), `annotated_at` and `protocol` per row.

## 3. Multi-label data

Multiple rows per `record_id` express multiple labels. Binary tasks use 0/1;
where a graded score is used, document the scale in the protocol and keep it
consistent across sources.

## 4. Quality control

- Double-read a sample; compute inter-rater agreement (e.g. Cohen's kappa).
- Adjudicate disagreements with a senior reviewer.
- Track the adjudication rate and audit a random sample.
- Report agreement in the dataset card (INPUT_REQUIRED until measured).

## 5. Harmonisation across sources

External sources may use different vocabularies. Map their raw values into the
same canonical codes; document the mapping and any values that cannot be mapped.

## 6. Prohibited practices

- Do not infer labels from filenames, folder names or metadata side channels.
- Do not copy labels between records/images of the same patient.
- Do not invent a label for an ungradable image.

## 7. Related

- [`../datasets/annotations/README.md`](../../datasets/annotations/README.md)
- [`../datasets/datasheets/annotation-protocol.md`](../../datasets/datasheets/annotation-protocol.md)

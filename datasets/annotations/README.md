# Annotations

Schemas and templates for dataset labels and annotations.

> **Labels are not defined in this repository.** Disease/screening label codes
> must be authored and approved by the clinical owner. Until then,
> [`label-map.json`](label-map.json) has `status: "INPUT_REQUIRED"` and the
> ingestion/annotation code refuses to map labels.

## Files

| File | Purpose |
| --- | --- |
| `annotation-schema.json` | JSON Schema for an annotation record. |
| `label-map.json` | Canonical label map (template; requires approval). |
| `labels.csv` | Annotation table (header only; rows supplied under licence). |
| `README.md` | This document. |

## Label map

A canonical label map translates raw source values into stable codes:

```json
{
  "schema_version": "1.0.0",
  "status": "approved",
  "labels": [
    {"code": "reference_class", "display_name": "...", "source_values": ["..."], "is_normal": false}
  ],
  "ignore_values": ["unusable", "ungradable"],
  "notes": "..."
}
```

Rules:

- `status` must be `approved` and `labels` non-empty before any mapping occurs.
- Each raw `source_values` entry maps to exactly one code (no ambiguity).
- `ignore_values` lists raw values that are dropped rather than labelled.
- Codes are lowercase, without spaces; prefer the vocabulary used by
  `contracts/` where possible.

## Annotation table (`labels.csv`)

Columns: `record_id`, `raw_label`, and either `value` (0/1 or score) or
`label_present` (truthy). Multiple rows per record express multi-label
annotations.

| record_id | raw_label | value |
| --- | --- | --- |
| _(example row supplied under licence)_ | | |

## Governance

Every annotation batch must record who annotated it, under which protocol, and
with what inter-rater agreement. See
[`../../docs/datasets/LABELING_GUIDELINES.md`](../../docs/datasets/LABELING_GUIDELINES.md).

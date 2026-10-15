# `external/` — external validation sources

Holds external-site and external-device data used **only** for validation of a
trained model. This data must never be used for training or threshold tuning,
and it is never committed to the repository.

## Source registry

Before any external data is placed here, record the source in a registry file
(for example `sources.json`) with the fields below. The importer refuses sources
that are missing required provenance or whose licence is `INPUT_REQUIRED`.

| Field | Required | Description |
| --- | --- | --- |
| `source_id` | yes | Stable identifier for the source. |
| `name` | yes | Human-readable name. |
| `owner` | yes | Organisation accountable for the data. |
| `contact` | yes | Responsible contact (role email, not personal if possible). |
| `license` | yes | Licence identifier; `INPUT_REQUIRED` is refused. |
| `consent_basis` | yes | Legal/ethical basis for use (e.g. consent, waiver). |
| `retention` | yes | Retention/expiry policy. |
| `approved` | yes | `true` only after governance sign-off. |

## Rules

- **Held out entirely.** External data is one whole test cohort; it is not split
  into train/validation/test.
- **Preprocessing parity.** The evaluation transform must match the training
  evaluation transform exactly.
- **No augmentation.**
- **Label harmonisation.** External label values must map into the same
  canonical codes as training via an approved label map.

See [`../../docs/datasets/DATASET_SOURCES.md`](../../docs/datasets/DATASET_SOURCES.md)
and `ml/configs/datasets/external_validation.yaml`.

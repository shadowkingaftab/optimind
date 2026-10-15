# Dataset sources

How dataset sources are registered, approved and ingested. Only approved sources
with a recorded licence and consent basis may be used.

## 1. Registration

Every source is recorded in a registry (e.g. `datasets/external/sources.json`)
with these fields:

| Field | Required | Description |
| --- | --- | --- |
| `source_id` | yes | Stable unique identifier. |
| `name` | yes | Human-readable name. |
| `owner` | yes | Accountable organisation. |
| `contact` | yes | Responsible contact. |
| `license` | yes | Licence identifier; `INPUT_REQUIRED` is refused. |
| `consent_basis` | yes | Legal/ethical basis for use. |
| `retention` | yes | Retention/expiry policy. |
| `approved` | yes | `true` only after governance sign-off. |

The importer (`eyedx_ml.data.ingestion.source_registry`) validates these fields
and refuses unknown or unapproved sources.

## 2. Categories

- **Internal site data** — collected under the project's ethics approval.
- **External validation data** — held out entirely; used only for evaluation.
- **Public datasets** — permitted only if the licence allows the intended use
  and if ethically appropriate; still registered like any other source.

## 3. Provenance chain

```text
source (registry) ─▶ raw images (immutable, hashed)
                  ─▶ manifest (pseudonymous keys)
                  ─▶ interim artifacts ─▶ splits ─▶ processed data
```

Every derived artifact is reproducible from the source plus configuration; the
registry and manifest checksums make this auditable.

## 4. Redistribution

If a source forbids redistribution, neither the images nor derived data that
could reconstruct them may be redistributed. Trained model weights may also be
restricted depending on the licence — check `usage-rights.csv`.

## 5. Related

- [`../../datasets/licenses/DATASET_LICENSES.md`](../../datasets/licenses/DATASET_LICENSES.md)
- [`../../datasets/external/README.md`](../../datasets/external/README.md)
- [`DATA_REQUIREMENTS.md`](DATA_REQUIREMENTS.md)

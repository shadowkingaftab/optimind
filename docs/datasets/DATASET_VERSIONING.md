# Dataset versioning

How dataset versions are identified, produced and reproduced. Data content is
never committed to Git; versions and their parameters are.

## 1. What is versioned

| Artifact | Committed? | Identified by |
| --- | --- | --- |
| Images and clinical tables | no | source registry entry + manifest checksums |
| Manifest | no | `input_checksum` in the split manifest |
| Split manifest | generated | `version`, `seed`, `ratios`, `input_checksum` |
| Label map | yes | `schema_version` + Git revision |
| Configs / params | yes | Git revision (`ml/configs`, `datasets/params.yaml`) |
| Code | yes | Git revision |

## 2. Reproducing a version

A dataset version is fully described by:

1. The source registry entries (licence, consent, retention).
2. The manifest and its checksum.
3. The pipeline configuration and code revision.
4. The split seed and ratios.

Given these, `ml/scripts/*` regenerate identical interim artifacts and splits.

## 3. Version identifiers

- Use a monotonic scheme, e.g. `YYYY.MM[-N]` or semantic `MAJOR.MINOR.PATCH`.
- Record the label-map version separately, since labels can change independently
  of images.
- Tag the Git revision that produced each version.

## 4. Change control

Any of the following requires a new version:

- Adding/removing images or patients.
- Changing labels or the label map.
- Changing split ratios, seed or strategy.
- Re-running cleaning with different thresholds.

Record the reason for each change in the dataset card's changelog.

## 5. DVC

The pipeline is expressed in [`../../datasets/dvc.yaml`](../../datasets/dvc.yaml).
`dvc.lock` is intentionally empty until licensed data is present; run
`dvc repro` once inputs are supplied. Never hand-edit lock hashes.

## 6. Related

- [`../../datasets/params.yaml`](../../datasets/params.yaml)
- [`../../datasets/dvc.yaml`](../../datasets/dvc.yaml)

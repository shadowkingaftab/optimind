# Phase 4 disposition — Dataset and ML input pipeline

Status: **implemented (code + governance docs)**; pipeline not executed, no data
present. This report accounts for every in-scope file and records the inputs
still required before any run.

## Scope

Phase 4 covers the dataset and ML input pipeline: reproducible ingestion,
manifest/metadata validation, label mapping, duplicate/leakage checks,
patient-level splits, image decoding/quality checks, preprocessing, augmentation
config, statistics and provenance. Screens are **screening-only**; nothing here
produces or implies a diagnosis. No images are downloaded, fabricated, relabeled
or committed.

In-scope trees: `ml/src/eyedx_ml/{data,preprocessing,augmentation}/`,
`ml/configs/{datasets,augmentation}/`, `ml/scripts/{ingest_dataset,
validate_dataset,generate_splits,clean_dataset,calculate_statistics}.py`,
`datasets/**`, `docs/datasets/**`.

## Implemented

### Package utilities (support)

| File | Purpose |
| --- | --- |
| `ml/src/eyedx_ml/__init__.py` | Package metadata (`__version__ = 0.1.0`). |
| `ml/src/eyedx_ml/utils/reproducibility.py` | Seeding helpers (`seed_everything`, `resolve_seed`, `EYEDX_SEED`). |
| `ml/src/eyedx_ml/utils/file_hash.py` | SHA-256 of bytes/files for manifests and dedup. |
| `ml/src/eyedx_ml/utils/config_loader.py` | YAML load, `${ENV}` resolution, required-key checks. |
| `ml/src/eyedx_ml/utils/logging.py` | Privacy-scrubbing logger (no identifiers/paths in logs). |
| `ml/src/eyedx_ml/utils/device.py` | Lazy device selection (no torch import at import time). |

### `data/ingestion`

| File | Purpose |
| --- | --- |
| `source_registry.py` | `DataSource`/`SourceRegistry`; validates licence/consent/owner/retention; refuses `INPUT_REQUIRED` licences. |
| `dataset_importer.py` | Canonical manifest read/write (`DatasetRecord`, `MANIFEST_COLUMNS`), salted `pseudonymize`. |
| `metadata_importer.py` | Loads patients/sites/devices/images tables with required-column checks. |
| `annotation_importer.py` | `LabelMap` (must be `approved`), `load_annotations`, `apply_label_map`, `attach_labels`. |

### `data/validation`

| File | Purpose |
| --- | --- |
| `integrity_report.py` | Shared `ValidationIssue`/`ValidationReport` (`Severity`, `ok`, merge). |
| `metadata_validator.py` | Record field/consistency checks (ids, patient_key, eye side, site/device refs). |
| `annotation_validator.py` | Label coverage, known codes, binary/range checks. |
| `image_validator.py` | Pillow-based decode + structural quality gates (resolution/brightness/blur/format). |
| `leakage_detector.py` | Patient-across-split and duplicate (checksum + perceptual) leakage. |

### `data/cleaning`

| File | Purpose |
| --- | --- |
| `corrupted_image_remover.py` | Partitions records into readable/corrupted (no deletion). |
| `duplicate_detector.py` | Exact (checksum) and near (dHash) duplicate groups, deterministic keep rule. |
| `label_cleaner.py` | Drops ignored codes, flags unknown, optional binarisation. |
| `metadata_cleaner.py` | Trims/normalises eye side and image format; never invents values. |
| `outlier_detector.py` | IQR-based size outliers. |

### `data/splitting`

| File | Purpose |
| --- | --- |
| `stratified_splitter.py` | Deterministic largest-remainder allocation per stratum. |
| `patient_splitter.py` | Patient-level, label-stratified split (default). |
| `site_splitter.py` | Leave-site-out holdout for external-style validation. |
| `split_manifest.py` | `SplitManifest` persistence + per-split CSVs + input checksum. |

### `data/statistics`

| File | Purpose |
| --- | --- |
| `class_distribution.py` | Per-label and per-split prevalence. |
| `image_statistics.py` | Aggregate dimension/brightness/format distributions. |
| `demographic_statistics.py` | Coarse aggregates with small-cell suppression. |
| `dataset_report.py` | Assembles/writes the JSON dataset report. |

### `data/loaders`

| File | Purpose |
| --- | --- |
| `image_dataset.py` | Map-style dataset; torch imported lazily. |
| `multilabel_dataset.py` | Multi-hot targets + class counts. |
| `sampler_factory.py` | Deterministic weighted/balanced samplers. |
| `dataloader_factory.py` | DataLoader construction with seed and worker settings. |

### `preprocessing` (deterministic, training/eval parity)

`resize.py`, `normalize.py`, `crop_retina.py`, `illumination_correction.py`,
`color_correction.py`, `artifact_removal.py`, `pipeline.py` (config-driven
`PreprocessingPipeline`).

### `augmentation` (training split only)

`geometric.py`, `photometric.py`, `noise.py`, `mixup.py`, `cutmix.py`,
`augmentation_factory.py` (seeded per-image pipeline + batch mixers).

### Configs and scripts

- `ml/configs/datasets/fundus_dataset.yaml`, `external_validation.yaml`.
- `ml/configs/augmentation/light.yaml`, `strong.yaml`.
- `ml/scripts/ingest_dataset.py`, `validate_dataset.py`, `generate_splits.py`,
  `clean_dataset.py`, `calculate_statistics.py` (CLI, fail clearly on missing
  inputs).

### `datasets/**` (governance + placeholders; no image content)

- `README.md`, `params.yaml`, `dvc.yaml`, `dvc.lock` (empty stages), `image-quality.schema.json`.
- `raw/README.md`, `external/README.md`, `interim/README.md`, `processed/README.md`.
- `annotations/{README.md,annotation-schema.json,label-map.json,labels.csv}`.
- `datasheets/{dataset-card,collection-protocol,annotation-protocol,known-limitations}.md`.
- `licenses/{DATASET_LICENSES.md,attribution.md,usage-rights.csv}`.
- `metadata/{README.md,patients.csv,images.csv,clinical-sites.csv,acquisition-devices.csv}`.
- `splits/{train,validation,test,external-test}.csv`, `splits/split-manifest.json`.

### `docs/datasets/**`

`DATA_REQUIREMENTS.md`, `DATASET_SOURCES.md`, `LABELING_GUIDELINES.md`,
`QUALITY_CONTROL.md`, `DATA_LEAKAGE_PREVENTION.md`, `DATASET_VERSIONING.md`.

## Inputs required (INPUT_REQUIRED)

| Input | Where | Owner | Notes |
| --- | --- | --- | --- |
| Label vocabulary + label map | `datasets/annotations/label-map.json` (`status != approved`) | Clinical owner | Must be approved with non-empty codes; code refuses to map otherwise. |
| Images + manifest | `datasets/raw`, `datasets/metadata/images.csv` | Data owner | Supplied under licence, out of band. |
| Patient/site/device tables (rows) | `datasets/metadata/*.csv` | Data owner | Headers committed; rows supplied. |
| Source registry | `datasets/external/sources.json` | Governance | licence/consent/owner/retention. |
| Pseudonymization salt | `EYEDX_PSEUDONYMIZATION_SALT` env | Security | Never committed. |
| Split ratios/seed/stratify label | configs / `params.yaml` | Modelling lead | `stratify_on` unset until labels exist. |
| Quality thresholds; normalisation mean/std | `ml/configs/datasets/*.yaml` | Modelling lead | Mean/std computed from **training split only**. |
| External subgroups / harmonisation | `ml/configs/datasets/external_validation.yaml` | Modelling lead | Reporting subgroups. |

## Not implemented (by design)

- No dataset acquisition/download and no synthetic data generation.
- No trained weights, model architecture or training loops (later phases; no ML
  deps declared).
- `datasets/documentation/` has only `.gitkeep` (no content required).
- No real lock hashes in `datasets/dvc.lock` (empty until a real run).

## Phase 5 dependencies

- Packaging/dependency declaration for `numpy`, `Pillow`, `PyYAML` and later
  `torch`/`albumentations`/`tensorflow` (imported lazily today).
- CI wiring to run the validation/leakage checks and enforce zero errors.

## Confirmation

No tests, builds, linters, migrations, servers, debuggers, pipelines or
downloads were run. No patient data, labels, metrics or credentials were
fabricated. All in-scope files are implemented or explicitly accounted for.

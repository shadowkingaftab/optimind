# `processed/` — model-ready data

Holds preprocessed, model-ready artifacts (resized/normalised arrays or tensors)
derived from `raw/` using the preprocessing pipeline. Contents are generated,
not committed, and never contain new information — only deterministic transforms
of licensed source images.

## Rules

- **Derived only.** Everything here is reproducible from `raw/` + configuration;
  deletion and regeneration must be safe.
- **No augmentation here.** Augmentation is applied on the fly to the training
  split only; it is never written to disk.
- **Deterministic.** Preprocessing uses fixed parameters (target size,
  normalisation statistics) recorded in the dataset config.
- **External data treated identically** but with the evaluation transform.

See `ml/src/eyedx_ml/preprocessing/` for the implementation and
`ml/configs/datasets/*.yaml` for the declared steps.

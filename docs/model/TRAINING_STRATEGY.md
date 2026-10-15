# Training Strategy

**Scope:** Strategy for training screening models. Screening only; not a diagnosis.

## 1. Principles
- **Data hygiene:** Use approved datasets only; patient-level splits; no data leakage.
- **No fabrication:** Never invent labels, metrics, thresholds or weights. Inputs marked `INPUT_REQUIRED` must be supplied.
- **Reproducibility:** Fixed seeds (`resolve_seed`, `seed_everything`), deterministic ops when requested, versioned configs.
- **Privacy:** No PHI in artifacts/logs; pseudonymous `patient_key` only.
- **Safe defaults:** Heavy deps imported lazily; unavailable artifacts raise clear errors.

## 2. Data Splits
- **Patient-level:** `patient_splitter` ensures no patient spans train/validation/test.
- **Cohorts:** `train`, `validation`, `test` (internal), `external-test` (frozen).
- **Selection:** Validation used for early stopping, checkpoint selection, calibration and threshold exploration. Test split is held-out and never used for tuning.
- **Manifest:** Canonical manifest with checksums; split CSVs written to `datasets/splits/`.

## 3. Model Selection
- **Architectures:** `binary_classifier`, `multiclass_classifier`, `multilabel_classifier`, `multitask`, `segmentation`, `ensemble` (ensembles assembled from approved checkpoints).
- **Backbones:** ResNet/EfficientNet/ConvNeXt/ViT via `eyedx_ml.models.backbones` (pretrained weights only if explicit `weights_path` supplied, under licence).
- **Labels:** Bound via approved label map; builders raise `LabelUnavailableError` if unavailable.

## 4. Optimisation
- **Optimisers:** Adam/AdamW/SGD via `optimizer_factory` (LR is `INPUT_REQUIRED`).
- **Schedulers:** Step/Cosine/OneCycle/Plateau; warmup configurable.
- **Losses:** Weighted BCE, Focal, Dice, Multi-task (weights are `INPUT_REQUIRED`).
- **Regularisation:** Dropout, weight decay, gradient clipping; augmentation light/strong from configs.

## 5. Training Loop
- **Framework:** PyTorch-based trainer (`eyedx_ml.training.Trainer`) with epoch-level loops (`train_epoch`, `validate`).
- **Mixed precision:** AMP only when CUDA available and explicitly enabled (errors if requested without GPU).
- **Early stopping:** Monitors validation metric (`val_loss` default); min_delta/patience configurable.
- **Checkpointing:** Saves `best.pt`/`last.pt` + metadata sidecar (contract-aligned); metadata includes labels/preprocessing/capabilities.
- **Logging:** JSONL experiment logs (redacted) every N steps.

## 6. Calibration & Thresholds
- **Calibration:** Temperature scaling (default) or isotonic on validation split only.
- **Thresholds:** Selected on validation under stated criterion (Youden/target_sensitivity/target_specificity/fixed). Never invented; must be approved before use in inference.

## 7. Reproducibility & Distributed
- **Seeding:** Global seed applied to Python/numpy/torch; cuDNN settings configurable.
- **DDP:** Supported via `distributed_training` (cluster params are `INPUT_REQUIRED`).
- **Determinism:** Optional deterministic execution (trade-off with speed).

## Notes
- Training scripts require approved labels, manifest, splits, image root.
- No test-split data used for model/threshold selection.
- Screening outputs remain probabilistic; decision thresholds require clinical/approval sign-off.

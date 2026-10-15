# Phase 5 Disposition Report: ML models and export

## Objective
Implement Phase 5 per README.md: ML architectures, losses, training orchestration, checkpoint metadata, reproducibility, metrics, subgroup reporting hooks, calibration, uncertainty/abstention, explanations and export; plus remaining ML configs/scripts, `ml/models`, `ml/notebooks`, `docs/model`, model configs. Use only approved labels; implement configurable loading and safe unavailable states when labels/pretrained weights/GPU/cohorts are absent; never invent weights, metrics, clinical thresholds or notebook findings. Then produce this disposition report.

## Status Summary
- Phase 1-4: complete (documented in prior disposition reports).
- Phase 5: implemented (code + configs + scripts + docs + artifact dirs + notebook templates), with no execution of tests/builds/linters/migrations/servers/debug/pipelines/downloads.

## Implemented (Phase 5)
1. Errors
- `ml/src/eyedx_ml/errors.py`: shared error hierarchy (`MLPackageError`, `DependencyError`, `NotConfiguredError`, `LabelUnavailableError`, `ArtifactUnavailableError`, `TrainingError`, `EvaluationError`, `CalibrationError`, `ExplainabilityError`, `ExportError`, `RegistryError`) + `require_dependency()`, `is_available()`.
- `ml/src/eyedx_ml/__init__.py`: exports version `0.1.0` and Phase 5 errors.

2. Configs
- `ml/configs/models/{baseline,multilabel,multitask,ensemble}.yaml` (ensemble notes INPUT_REQUIRED members/weights).
- `ml/configs/training/{baseline,production,distributed}.yaml`.
- `ml/configs/evaluation/{internal,external,subgroup}.yaml`.
- `ml/configs/inference/{default,production}.yaml`.

3. Models
- `ml/src/eyedx_ml/models/model_config.py`: loads YAML, validates, binds labels; `resolved_num_labels()`, `load_approved_labels()` (requires approved label map), `pretrained_weights_path()`; raises `LabelUnavailableError` when labels unavailable.
- `ml/src/eyedx_ml/models/model_factory.py`: builds models lazily; multitask/ensemble handled; raises on missing required inputs.
- Backbones (lazy torch/torchvision): `resnet.py`, `efficientnet.py`, `convnext.py`, `vision_transformer.py`, registry in `backbones/__init__.py` (feature maps, `out_channels`).
- Layers: `attention.py`, `pooling.py`, `classification_head.py`, `layers/__init__.py`.
- Classifiers: `binary_classifier.py`, `multiclass_classifier.py`, `multilabel_classifier.py`.
- Multitask: `disease_head.py`, `quality_head.py`, `severity_head.py`, `multitask_model.py` (supports `heads` config style; skips disabled severity).
- Segmentation: `unet.py`, `optic_disc_segmenter.py`, `lesion_segmenter.py`.
- Ensembles: `soft_voting.py`, `weighted_voting.py`, `stacking.py` (sklearn optional for stacking).
- Losses: `focal_loss.py`, `weighted_bce.py`, `dice_loss.py`, `multitask_loss.py`.

4. Training
- `seed.py` (reproducibility), `optimizer_factory.py`, `scheduler_factory.py`, `mixed_precision.py` (AMP requires CUDA or allow_cpu opt), `early_stopping.py`, `checkpoint_manager.py` (contract-aligned metadata: labels array, preprocessing, capabilities with booleans; extra/arch in capabilities per schema), `experiment_logger.py` (privacy-safe redaction), `distributed_training.py` (DDP, cluster params INPUT_REQUIRED), `training_loop.py`, `validation_loop.py`, `trainer.py`.

5. Metrics
- `auroc.py`, `precision_recall.py`, `sensitivity.py`, `specificity.py`, `classification.py`, `calibration.py` (ECE/MCE/Brier/reliability), `bootstrap_confidence_intervals.py`, `segmentation.py`.

6. Evaluation
- `evaluator.py`, `evaluation_report.py`, `subgroup_analysis.py`, `site_analysis.py`, `device_analysis.py`, `error_analysis.py`, `confusion_analysis.py`, `external_validation.py` (frozen thresholds enforced, harmonisation noted as INPUT_REQUIRED).

7. Calibration
- `temperature_scaling.py`, `isotonic_regression.py` (sklearn optional), `reliability_diagram.py` (matplotlib optional, Agg), `calibration_report.py`, `threshold_optimizer.py`.

8. Explainability
- `gradcam.py`, `integrated_gradients.py` (captum optional + manual fallback), `occlusion.py`, `attention_rollout.py`, `heatmap_utils.py` (matplotlib/PIL optional), `explanation_validator.py`.

9. Export
- `export_metadata.py` (validates model-metadata contract), `export_torchscript.py`, `export_onnx.py` (onnx optional), `package_model.py`, `validate_export.py`.

10. Inference
- `predictor.py` (loads approved checkpoint/labels, applies quality gate, uncertainty/abstention, formats to contract), `batch_predictor.py`, `quality_gate.py`, `uncertainty_estimator.py`, `prediction_formatter.py`, `benchmark_inference.py`.

11. Registry
- `registry_client.py` (file-based), `register_model.py`, `promote_model.py` (production requires approved_by), `rollback_model.py`.

12. Scripts
- `ml/scripts/{train,evaluate,calibrate,export_model,external_validate,generate_explanations,benchmark_model,register_model}.py` (all CLI, sys.path insert of ml/src, fail fast on missing INPUT_REQUIRED).

13. Artifact directories & READMEs
- `ml/models/` and subdirs (benchmarks, backbones, classifiers, ensembles, layers, losses, multitask, segmentation, calibration, checkpoints, data, datasets, evaluation, experiments, explainability, export, feature_engineering, inference, metrics, optimization, outputs/{metrics,plots,predictions,reports}) with README.md files documenting INPUT_REQUIRED and privacy rules.

14. Notebooks
- `ml/notebooks/01_dataset_exploration.ipynb`, `02_data_quality_analysis.ipynb`, `03_baseline_experiment.ipynb`, `04_error_analysis.ipynb`, `05_subgroup_analysis.ipynb`, `06_explainability_review.ipynb` — valid JSON templates with `eyedx.phase: 5`, `notes: "No fabricated findings; all values INPUT_REQUIRED"`.

15. Documentation
- `docs/model/{INPUT_SPECIFICATION,OUTPUT_SPECIFICATION,DISEASE_LABELS,TRAINING_STRATEGY,EVALUATION_STRATEGY,CALIBRATION_STRATEGY,EXPLAINABILITY_STRATEGY,MODEL_REQUIREMENTS,MODEL_RELEASE_PROCESS}.md`.

## Inputs Required (not present in repo)
- Approved label map: `datasets/annotations/label-map.json` must have `status="approved"` and non-empty labels.
- Pretrained weights (licence-compliant): set `pretrained_weights` when `pretrained=true`.
- Model artifacts/checkpoints: produced by training/export; paths INPUT_REQUIRED for evaluation/export/inference.
- Datasets/manifests/splits: approved, patient-level; external cohort + harmonisation for external validation.
- Runtime resources: GPU for AMP/DDP; cluster params for distributed training; `approved_by` for production promotion.

## Safety & Compliance
- No PHI committed; `patient_key` pseudonymous; small-cell suppression in subgroup reports.
- Screening-only wording throughout; limitation notice in inference responses.
- Heavy deps lazy-loaded; safe absence handling (clear errors).
- No tests/builds/linters/migrations/servers/debug/pipelines/downloads executed.
- `ml/tests/*.py` remain blank placeholders (Phase 13).
- Contracts aligned: model-metadata, prediction-request/response, error-response.

## Phase 6 Dependencies
- Model service consumes packaged models and inference configs; integrates with backend prediction flow (Phase 3 contracts).
- Registry artifacts (staging/production) and approved thresholds required before serving.

## No-Execution Confirmation
No pytest, python -m compileall, py_compile, linters, typecheckers, Docker builds, servers, debug runs, migrations, or dataset downloads were run. All files written as specified.

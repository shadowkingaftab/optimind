# Model/Inference Configuration

Model service configuration.
- MODEL_PATH: INPUT_REQUIRED (format: absolute path or registry reference) - if using local artifacts
- MODEL_VERSION: INPUT_REQUIRED (format: semver/string) - must match registry
- DEVICE: cpu/gpu (default: cpu)
- BATCH_SIZE: 1 (default, safe)
- TIMEOUT_SECONDS: 30 (default)
- MAX_IMAGE_SIZE_MB: 10 (default)
- QUALITY_THRESHOLD: configurable, needs model-owner approval
- UNCERTAINTY_THRESHOLD: configurable, needs clinical/model approval

**Safe absence**: Model service must report not_ready with clear message if MODEL_PATH missing and no artifact configured.
**Consuming**: model_service/app/core/config.py
**Owner**: ML/model lead

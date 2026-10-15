# Model Input Specification

**Scope:** Defines the expected inputs to the ML screening model (for training and inference). Screening only; not a diagnosis.

## 1. Image Inputs
- **Format:** JPEG/PNG (original or standardised). No DICOM assumed unless explicitly specified in an approved config.
- **Colour space:** RGB (3 channels). Grayscale converted to RGB.
- **Resolution:** Minimum resolution defined per model (INPUT_REQUIRED). Typical 512x512 up to 1024x1024 depending on backbone.
- **Orientation:** Standardised during preprocessing (INPUT_REQUIRED if acquisition varies).
- **Quality:** Must pass `QualityGate` thresholds (brightness, blur, resolution). Images failing quality checks produce `low_quality` or `abstained` responses.
- **Provenance:** Images must come from approved, licence-compliant sources with documented acquisition protocols.

## 2. Labels and Vocabulary
- **Source:** `datasets/annotations/label-map.json` (approved). 
- **Requirements:** `status == "approved"`, non-empty `labels` array. Codes are canonical.
- **Constraints:** Labels are never invented. The codebase raises `LabelUnavailableError` if the map is missing/unapproved.
- **Multi-label:** Screening outputs are per approved label (0..1 scores). No implicit default diagnosis.

## 3. Metadata Inputs
- **Manifest:** Canonical manifest columns as per `MANIFEST_COLUMNS` (`record_id`, `image_path`, `patient_key`, `site_id`, `device_id`, `eye_side`, `image_format`, `checksum_sha256`, optional `labels`, `split`).
- **Splits:** Patient-level splits (`train/validation/test/external-test`) written to `datasets/splits/`.
- **Privacy:** `patient_key` is pseudonymous. No PHI stored in model artifacts or outputs.

## 4. Preprocessing
- **Pipeline:** Defined in dataset/model configs (`mean`, `std`, resize/crop, normalisation). Values are `INPUT_REQUIRED` (computed from the training split).
- **Determinism:** Preprocessing is deterministic given the same config and inputs.

## 5. Training Inputs
- **Data:** Approved training split only. Validation split used for early stopping/checkpoints/threshold exploration; test split held out.
- **Artifacts:** Optional pretrained weights, supplied under licence (`pretrained_weights` = INPUT_REQUIRED if `pretrained=true`).
- **Configs:** Training/model/evaluation/inference YAML files (schema versioned).

## 6. Inference Inputs
- **Request:** `image` (base64 JPEG/PNG), `consent_id` (UUID), optional `request_id`, `image_format` (per `contracts/json-schemas/prediction-request.schema.json`).
- **Runtime:** Inference config specifies device, batch size, thresholds, uncertainty, abstention, explanation flags (all `INPUT_REQUIRED` where marked).

## Notes
- All `INPUT_REQUIRED` fields must be supplied before training/evaluation/export/inference. The code refuses to proceed when missing.
- Screening limitation notice is included in user-facing responses.

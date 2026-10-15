# Explainability Strategy

**Scope:** Model explainability for screening models. Explanations support review/safety oversight only and are not diagnostic.

## 1. Principles
- **Review-only:** Explanations must not be presented as diagnostic evidence or clinical justification.
- **Privacy-safe:** No PHI; use pseudonymous `record_id` when referencing cases.
- **Validation:** Heatmaps undergo sanity checks (shape, finite values, unit range) before use.
- **No fabrication:** Explanations are computed from the model and input; no invented annotations.
- **Optional:** Explanations are disabled by default (`explanation.enabled=false` in inference configs).

## 2. Methods
- **Grad-CAM:** Class activation maps for spatial feature layers (`explainability.gradcam`). Target layer is the backbone's final spatial stage (model-dependent).
- **Integrated Gradients:** Attribution via gradient integration (`explainability.integrated_gradients`). Uses captum when available, with a manual fallback.
- **Occlusion:** Sliding-window occlusion to measure score drop (`explainability.occlusion`).
- **Attention Rollout:** Aggregates transformer attention maps (`explainability.attention_rollout`).

## 3. Usage
- **Training/evaluation:** Generated for a sample of records (e.g., error cases, subgroup samples) to support error analysis and safety review.
- **Inference:** Only when explicitly enabled and approved; produces explanation metadata/availability per the prediction response contract.
- **Heatmaps:** Normalised to [0,1], can be overlaid on images for review (headless rendering only in CI).

## 4. Validation & Quality
- **Sanity checks:** `validate_heatmap` checks shape, finiteness, unit range.
- **Faithfulness (optional):** Deletion/insertion curves provide rough checks of attribution quality (placeholder implementations, use with caution).
- **Limitations:** Grad-CAM is resolution-limited by feature map size; IG depends on baseline choice; occlusion is compute-intensive.

## 5. Outputs
- **Heatmaps:** Saved under `ml/outputs/explainability/` (images/JSON). No PHI.
- **Report:** Explanation summary for reviewed samples.
- **Contract alignment:** Explanation fields appear only in `prediction-response` when `supports_explanation=true`.

## 6. Implementation
- **Modules:** `eyedx_ml.explainability.{gradcam,integrated_gradients,occlusion,attention_rollout,heatmap_utils,explanation_validator}`.
- **Script:** `ml/scripts/generate_explanations.py`.

## Notes
- All explanations are screening assistance only. They must not imply a diagnosis or replace clinical judgment.
- Enabling explanations increases compute cost; requires approved method and compute budget.
- Transformer backbones should use attention rollout rather than Grad-CAM where appropriate.

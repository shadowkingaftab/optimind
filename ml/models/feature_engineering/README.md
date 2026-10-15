# Model artifact directories (feature_engineering)

Feature pipelines (optional; lazy to avoid heavy deps).

**Guidelines:**
- Keep lightweight; avoid importing heavy deps at module level.
- `INPUT_REQUIRED` only when feature caching is used.
- No PHI committed.

# Model artifact directories (inference)

Inference-time caches (optional; no patient data).

**Guidelines:**
- Must not store patient images, PHI or identifiers.
- `INPUT_REQUIRED` only when runtime caching is enabled.
- Cache contents must be safe to delete.

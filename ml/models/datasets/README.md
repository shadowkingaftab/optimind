# Model artifact directories (datasets)

Dataset-level model-specific splits or cached arrays (optional). Never contains PHI.

**Guidelines:**
- Use only derived, de-identified arrays derived from approved datasets.
- `INPUT_REQUIRED` only when caching preprocessed arrays.
- Patient-level splits are maintained under `datasets/splits/`.

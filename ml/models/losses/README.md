# Model artifact directories (losses)

Holds loss weight histories and curve artifacts (optional).

**Guidelines:**
- Purely numeric/curve artifacts; no PHI or patient data.
- Useful for debugging multi-task training; `INPUT_REQUIRED` only when logging losses.

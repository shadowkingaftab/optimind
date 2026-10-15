# Model artifact directories (classifiers)

Holds saved classifier heads and weights for trained models.

**Guidelines:**
- No PHI, patient data, or sensitive identifiers.
- Files are `INPUT_REQUIRED` when a checkpoint is produced (e.g., `classifier.pt`, `head.pt`).
- Use contract-aligned model metadata when exporting.

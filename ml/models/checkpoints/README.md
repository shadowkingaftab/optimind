# Model artifact directories (checkpoints)

Training checkpoints from the trainer (e.g., `best.pt`, `last.pt`, `*.meta.json`).

**Guidelines:**
- `INPUT_REQUIRED` at runtime for evaluation/export/inference.
- Checkpoint metadata must be contract-aligned (see `export.export_metadata`).
- No PHI committed.

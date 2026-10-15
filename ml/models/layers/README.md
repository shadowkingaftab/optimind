# Model artifact directories (layers)

Holds layer-level checkpoints or feature extractors when fine-tuning specific layers.

**Guidelines:**
- Artifacts are `INPUT_REQUIRED` only when produced by an experiment.
- No PHI or patient data committed.
- Document which layers are frozen/unfrozen in experiment logs.

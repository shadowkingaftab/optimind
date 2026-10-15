# Model artifact directories (ensembles)

Holds ensemble member configurations, weights and combination metadata.

**Guidelines:**
- Member checkpoint paths and weights are `INPUT_REQUIRED`; they must come from approved models.
- Do not commit weights or PHI.
- Record the combination rule (soft voting, weighted voting, stacking) and the source of weights.

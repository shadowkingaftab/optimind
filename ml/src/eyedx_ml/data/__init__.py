"""Dataset and ML input pipeline.

Subpackages cover ingestion, validation, cleaning, splitting, statistics and
loaders. Nothing here downloads data, fabricates records or commits patient
images; the pipeline assumes licensed data is supplied out of band.
"""

from __future__ import annotations

from . import cleaning, ingestion, loaders, splitting, statistics, validation

__all__ = [
    "cleaning",
    "ingestion",
    "loaders",
    "splitting",
    "statistics",
    "validation",
]

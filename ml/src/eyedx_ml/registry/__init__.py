"""File-based model registry."""

from __future__ import annotations

from .register_model import register_model
from .registry_client import STAGES, FileRegistry
from .promote_model import promote_model
from .rollback_model import rollback_model

__all__ = [
    "FileRegistry",
    "STAGES",
    "register_model",
    "promote_model",
    "rollback_model",
]

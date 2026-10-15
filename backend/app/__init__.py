"""EyeDx backend application package.

This package exposes the FastAPI app factory at ``app.main.create_app``.
Importing this package intentionally has no side effects (no database or
network access) so tooling can import submodules safely.
"""

from __future__ import annotations

from app.core.constants import APP_VERSION as __version__

__all__ = ["__version__"]

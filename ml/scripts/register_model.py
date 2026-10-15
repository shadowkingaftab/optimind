#!/usr/bin/env python
"""Register a packaged model in the local file registry.

Accepts a packaged model directory and registers it under a model_id/version.
Promotion to production requires a named approver and is handled by the registry
rule set.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eyedx_ml.registry import FileRegistry, register_model
from eyedx_ml.utils.logging import get_logger

logger = get_logger("eyedx_ml.register_model")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True)
    parser.add_argument("--registry-root", default="ml/models/registry")
    parser.add_argument("--stage", default="development")
    parser.add_argument("--notes", default=None)
    args = parser.parse_args(argv)

    try:
        entry = register_model(
            args.package,
            registry_root=args.registry_root,
            stage=args.stage,
            notes=args.notes,
        )
        logger.info(
            "registered %s@%s -> %s", entry["model_id"], entry["model_version"], entry["path"]
        )
        return 0
    except Exception as exc:
        logger.error("registration failed: %s", exc)
        return 5


if __name__ == "__main__":
    raise SystemExit(main())

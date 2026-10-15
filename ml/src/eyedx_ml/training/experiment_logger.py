"""Local experiment logging.

Writes JSONL records for epochs/runs. Logs are privacy-safe: only metrics,
hyper-parameters and identifiers the caller explicitly passes are written. The
logger never reads patient data.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Union

from eyedx_ml.utils.logging import get_logger, redact_identifier

__all__ = ["ExperimentLogger"]

_logger = get_logger(__name__)

_SENSITIVE = {"patient_key", "patient_id", "mrn", "name", "dob", "postcode"}


def _scrub(record: Mapping[str, Any]) -> dict:
    clean = {}
    for key, value in record.items():
        if key.lower() in _SENSITIVE:
            clean[key] = redact_identifier(str(value))
        else:
            clean[key] = value
    return clean


class ExperimentLogger:
    def __init__(
        self,
        output_dir: Union[str, Path],
        *,
        name: str,
        log_every_n_steps: int = 50,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.name = name
        self.log_every_n_steps = int(log_every_n_steps)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = f"{name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.path = self.output_dir / f"{self.run_id}.jsonl"
        self._handle = self.path.open("a", encoding="utf-8")

    def _write(self, record: Mapping[str, Any]) -> None:
        record = {"timestamp": datetime.now(timezone.utc).isoformat(), **_scrub(record)}
        self._handle.write(json.dumps(record, default=str) + "\n")
        self._handle.flush()

    def log_config(self, config: Mapping[str, Any]) -> None:
        self._write({"event": "config", "config": dict(config)})

    def log_epoch(self, *, epoch: int, metrics: Mapping[str, Any], lr: Optional[float] = None) -> None:
        record = {"event": "epoch", "epoch": epoch, **dict(metrics)}
        if lr is not None:
            record["lr"] = lr
        self._write(record)

    def log_step(
        self, *, epoch: int, step: int, metrics: Mapping[str, Any]
    ) -> None:
        if step % self.log_every_n_steps != 0:
            return
        self._write({"event": "step", "epoch": epoch, "step": step, **dict(metrics)})

    def log_event(self, event: str, **fields: Any) -> None:
        self._write({"event": event, **fields})

    def close(self) -> None:
        try:
            self._handle.close()
        except Exception:  # pragma: no cover
            pass

    def __enter__(self) -> "ExperimentLogger":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

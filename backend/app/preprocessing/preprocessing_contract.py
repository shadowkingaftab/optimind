"""Shared datatypes for the preprocessing pipeline.

These are internal, non-contract structures. Public API shapes remain defined
by ``contracts/``.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ImageInfo:
    width: int
    height: int
    mode: str
    format: str


@dataclass(frozen=True)
class QualityResult:
    acceptable: bool
    score: float | None = None
    issues: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "acceptable": self.acceptable,
            "score": self.score,
            "issues": list(self.issues),
            "metrics": dict(self.metrics),
        }


@dataclass(frozen=True)
class PreprocessedImage:
    data: bytes
    media_type: str
    width: int
    height: int
    format: str
    checksum_sha256: str

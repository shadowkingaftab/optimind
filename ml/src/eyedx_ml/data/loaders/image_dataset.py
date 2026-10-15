"""Map-style image dataset.

A PyTorch ``Dataset`` that yields ``(image, target)`` pairs from manifest
records. PyTorch is imported lazily so this module can be imported (and type
checked) without torch installed. Images are read on demand and never cached to
disk.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord

__all__ = ["LoaderError", "ImageDataset", "require_torch"]


class LoaderError(RuntimeError):
    """Raised when an optional ML dependency is unavailable."""


def require_torch():
    try:  # pragma: no cover - optional dependency
        import torch
    except Exception as exc:  # pragma: no cover
        raise LoaderError(
            "PyTorch is required for datasets/loaders; install it to run training"
        ) from exc
    return torch


class ImageDataset:
    """Yields decoded images and numeric targets.

    Args:
        records: manifest records.
        image_root: base directory for relative ``image_path`` values.
        transform: callable applied to a PIL image (typically a preprocessing
            or augmentation pipeline).
        label_order: ordered label codes; when set, targets are multi-hot
            vectors of length ``len(label_order)``.
        single_label: when set (and ``label_order`` is not), targets are a
            scalar probability for this label code.
        color_mode: PIL mode to convert to before transforms.
    """

    def __init__(
        self,
        records: Sequence[DatasetRecord],
        *,
        image_root: Union[str, Path],
        transform: Optional[Callable] = None,
        label_order: Optional[Sequence[str]] = None,
        single_label: Optional[str] = None,
        color_mode: str = "RGB",
    ) -> None:
        self.torch = require_torch()
        self.records: List[DatasetRecord] = list(records)
        self.image_root = Path(image_root)
        self.transform = transform
        self.label_order = list(label_order) if label_order else None
        self.single_label = single_label
        self.color_mode = color_mode

    def __len__(self) -> int:
        return len(self.records)

    def _resolve(self, relative: str) -> Path:
        return self.image_root / relative

    def _load_image(self, record: DatasetRecord):
        try:  # pragma: no cover - optional dependency
            from PIL import Image
        except Exception as exc:  # pragma: no cover
            raise LoaderError("Pillow is required to load images") from exc
        with Image.open(self._resolve(record.image_path)) as image:
            converted = image.convert(self.color_mode)
        return converted

    def _target(self, record: DatasetRecord):
        torch = self.torch
        if self.label_order:
            vector = [float(record.labels.get(code, 0.0)) for code in self.label_order]
            return torch.tensor(vector, dtype=torch.float32)
        if self.single_label:
            return torch.tensor(
                float(record.labels.get(self.single_label, 0.0)), dtype=torch.float32
            )
        return torch.tensor(0.0, dtype=torch.float32)

    def __getitem__(self, index: int) -> Tuple[object, object]:
        record = self.records[index]
        image = self._load_image(record)
        if self.transform is not None:
            image = self.transform(image)
        return image, self._target(record)

    def label_matrix(self):
        """Return a ``(n_samples, n_labels)`` multi-hot tensor for sampling."""
        if not self.label_order:
            raise LoaderError("label_order is required to build a label matrix")
        torch = self.torch
        rows = [
            [float(r.labels.get(code, 0.0)) for code in self.label_order]
            for r in self.records
        ]
        return torch.tensor(rows, dtype=torch.float32)

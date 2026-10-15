"""Multi-label dataset.

A thin, explicit subclass of :class:`ImageDataset` that always returns multi-hot
targets and exposes the label vocabulary and class weights for sampling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional, Sequence, Union

from eyedx_ml.data.ingestion.dataset_importer import DatasetRecord
from eyedx_ml.data.loaders.image_dataset import ImageDataset, LoaderError

__all__ = ["MultiLabelDataset"]


class MultiLabelDataset(ImageDataset):
    def __init__(
        self,
        records: Sequence[DatasetRecord],
        *,
        image_root: Union[str, Path],
        label_order: Sequence[str],
        transform: Optional[Callable] = None,
        color_mode: str = "RGB",
    ) -> None:
        if not label_order:
            raise LoaderError("MultiLabelDataset requires a non-empty label_order")
        super().__init__(
            records,
            image_root=image_root,
            transform=transform,
            label_order=list(label_order),
            single_label=None,
            color_mode=color_mode,
        )

    @property
    def num_labels(self) -> int:
        return len(self.label_order or [])

    @property
    def label_names(self) -> List[str]:
        return list(self.label_order or [])

    def positive_counts(self) -> List[int]:
        counts = [0] * self.num_labels
        for record in self.records:
            for i, code in enumerate(self.label_order or []):
                if float(record.labels.get(code, 0.0)) >= 0.5:
                    counts[i] += 1
        return counts

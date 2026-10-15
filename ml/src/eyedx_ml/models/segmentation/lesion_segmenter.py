"""Retinal lesion segmentation model."""

from __future__ import annotations

from eyedx_ml.errors import NotConfiguredError

__all__ = ["build_lesion_segmenter"]


def build_lesion_segmenter(
    num_classes: int = 0,
    *,
    in_channels: int = 3,
    base_channels: int = 64,
    depth: int = 4,
):
    """Return a U-Net for lesion segmentation.

    ``num_classes`` (background + lesion types) is INPUT_REQUIRED from the
    approved annotation schema and must be >= 2.
    """
    from eyedx_ml.models.segmentation.unet import build_unet

    if num_classes < 2:
        raise NotConfiguredError(
            "num_classes is INPUT_REQUIRED: supply background + lesion classes "
            "from the approved annotation schema"
        )
    return build_unet(
        in_channels,
        num_classes,
        base_channels=base_channels,
        depth=depth,
    )

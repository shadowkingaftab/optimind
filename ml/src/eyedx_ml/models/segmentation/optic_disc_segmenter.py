"""Optic disc / cup segmentation model."""

from __future__ import annotations

from eyedx_ml.errors import NotConfiguredError

__all__ = ["build_optic_disc_segmenter"]


def build_optic_disc_segmenter(
    in_channels: int = 3,
    *,
    include_cup: bool = True,
    base_channels: int = 64,
    depth: int = 4,
):
    """Return a U-Net segmenting background (+disc, +cup).

    Class definitions and annotation protocol are INPUT_REQUIRED. This wrapper
    only configures the output channel count.
    """
    from eyedx_ml.models.segmentation.unet import build_unet

    num_classes = 3 if include_cup else 2
    if num_classes < 2:
        raise NotConfiguredError("optic disc segmentation needs a background class")
    return build_unet(
        in_channels,
        num_classes,
        base_channels=base_channels,
        depth=depth,
    )

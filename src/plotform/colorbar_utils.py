"""Vertical capsule tracks for continuous scalar colorbars."""

from __future__ import annotations

from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.transforms import IdentityTransform

from .palette import INK
from .rounded import capsule_path


class DisplayCapsulePatch(PathPatch):
    """An invisible display-space capsule used to clip colorbar artists."""

    def __init__(self):
        super().__init__(
            capsule_path(0, 0, 1, 1),
            facecolor="none",
            edgecolor="none",
            transform=IdentityTransform(),
        )

    def get_path(self) -> Path:
        ax = getattr(self, "axes", None)
        if ax is None:
            return capsule_path(0, 0, 1, 1)
        bounds = ax.bbox
        return capsule_path(bounds.x0, bounds.y0, bounds.width, bounds.height)


def capsule_colorbar(fig, ax, mappable, **kwargs):
    """Create a vertical colorbar whose visible gradient is an exact capsule.

    Tick marks and numeric labels remain outside the track. Additional keyword
    arguments are forwarded to ``Figure.colorbar``. The returned Colorbar has a
    ``capsule_patch`` attribute for inspection and advanced customization.
    """
    if kwargs.get("orientation", "vertical") != "vertical":
        raise ValueError("capsule_colorbar currently supports vertical orientation only")
    kwargs["orientation"] = "vertical"
    colorbar = fig.colorbar(mappable, ax=ax, **kwargs)
    cax = colorbar.ax

    clip = DisplayCapsulePatch()
    clip.set_clip_on(False)
    cax.add_patch(clip)
    for artist in (*cax.images, *cax.collections):
        artist.set_clip_path(clip)
    if getattr(colorbar, "solids", None) is not None:
        colorbar.solids.set_clip_path(clip)

    if getattr(colorbar, "outline", None) is not None:
        colorbar.outline.set_visible(False)
    for spine in cax.spines.values():
        spine.set_visible(False)
    cax.patch.set_visible(False)
    cax.yaxis.set_ticks_position("right")
    cax.yaxis.set_label_position("right")
    cax.tick_params(
        axis="y",
        which="both",
        direction="out",
        length=3,
        width=0.8,
        colors=INK,
        labelcolor=INK,
        pad=5,
    )

    colorbar.capsule_patch = clip
    return colorbar


__all__ = ["capsule_colorbar"]

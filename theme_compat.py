"""Optional Teal Minimal integration with native Matplotlib fallbacks.

Copy this file into a project and ``import theme_compat as tm``. No installation
of Teal Minimal is required. When it is available, its enhanced helpers are
used; otherwise native Matplotlib behavior and the current style are preserved.
"""

from __future__ import annotations

from contextlib import nullcontext

import matplotlib.pyplot as plt

try:
    import teal_minimal as _theme
except ImportError:
    _theme = None

PRIMARY = _theme.PRIMARY if _theme is not None else "#008080"
CORAL = _theme.CORAL if _theme is not None else "#D55E00"
INK = _theme.INK if _theme is not None else "#000000"
WHITE = _theme.WHITE if _theme is not None else "#FFFFFF"
SCALAR_CMAP = _theme.SCALAR_CMAP if _theme is not None else "viridis"
DIVERGING_CMAP = _theme.DIVERGING_CMAP if _theme is not None else "coolwarm"
SEQUENTIAL_CMAP = _theme.SEQUENTIAL_CMAP if _theme is not None else "viridis"


def apply_theme(*, enabled=True):
    """Apply Teal Minimal globally when available and enabled; otherwise no-op."""
    if enabled and _theme is not None:
        _theme.apply_theme()


def theme(*, enabled=True):
    """Temporarily apply Teal Minimal; otherwise preserve the current style."""
    if enabled and _theme is not None:
        return _theme.theme()
    return nullcontext()


def _axes(ax=None):
    return plt.gca() if ax is None else ax


def get_palette(n_colors=8):
    """Return theme colors, or the active Matplotlib cycle as a fallback."""
    if _theme is not None:
        return _theme.get_palette(n_colors)
    cycle = [entry["color"] for entry in plt.rcParams["axes.prop_cycle"]]
    return [cycle[index % len(cycle)] for index in range(n_colors)]


def legend(ax=None, **kwargs):
    """Use a pill legend when available, otherwise call ``Axes.legend``."""
    ax = _axes(ax)
    if _theme is not None:
        return _theme.legend(ax, **kwargs)

    # Enhanced-only options are translated or intentionally ignored.
    kwargs.pop("styles", None)
    kwargs.pop("alpha", None)
    kwargs.pop("pill_height", None)
    kwargs.pop("target_contrast", None)
    outside = kwargs.pop("outside", False)
    backdrop = kwargs.pop("backdrop", False)
    backdrop_alpha = kwargs.pop("backdrop_alpha", 0.88)
    backdrop_color = kwargs.pop("backdrop_color", WHITE)
    kwargs.pop("backdrop_pad", None)

    if outside:
        kwargs.setdefault("loc", "lower left")
        kwargs.setdefault("bbox_to_anchor", (0.0, 1.02))
        kwargs.setdefault("ncols", max(1, len(ax.get_legend_handles_labels()[0])))
        kwargs.setdefault("borderaxespad", 0.0)
    if backdrop:
        kwargs.setdefault("frameon", True)
        kwargs.setdefault("fancybox", True)
        kwargs.setdefault("framealpha", backdrop_alpha)
        kwargs.setdefault("facecolor", backdrop_color)
        kwargs.setdefault("edgecolor", "none")
    return ax.legend(**kwargs)


def bar(*args, ax=None, **kwargs):
    """Use rounded bars when available, otherwise call ``Axes.bar``."""
    ax = _axes(ax)
    if _theme is not None:
        return _theme.bar(*args, ax=ax, **kwargs)
    kwargs.pop("radius", None)
    kwargs.pop("ends", None)
    return ax.bar(*args, **kwargs)


def barh(*args, ax=None, **kwargs):
    """Use rounded horizontal bars when available, otherwise ``Axes.barh``."""
    ax = _axes(ax)
    if _theme is not None:
        return _theme.barh(*args, ax=ax, **kwargs)
    kwargs.pop("radius", None)
    kwargs.pop("ends", None)
    return ax.barh(*args, **kwargs)


def colorbar(mappable, *, fig=None, ax=None, **kwargs):
    """Use a capsule colorbar when available, otherwise ``Figure.colorbar``."""
    fig = plt.gcf() if fig is None else fig
    ax = _axes(ax)
    if _theme is not None:
        return _theme.colorbar(mappable, fig=fig, ax=ax, **kwargs)
    return fig.colorbar(mappable, ax=ax, **kwargs)


def annotate(text, xy, *, ax=None, **kwargs):
    """Use a capsule annotation when available, otherwise ``Axes.annotate``."""
    ax = _axes(ax)
    if _theme is not None:
        return _theme.annotate(text, xy, ax=ax, **kwargs)

    facecolor = kwargs.pop("facecolor", None)
    textcolor = kwargs.pop("textcolor", None)
    edgecolor = kwargs.pop("edgecolor", None)
    pad = kwargs.pop("pad", None)
    height = kwargs.pop("height", None)
    if any(value is not None for value in (facecolor, edgecolor, pad, height)):
        bbox = kwargs.pop("bbox", {})
        bbox.setdefault("boxstyle", f"round,pad={0.3 if pad is None else pad}")
        if facecolor is not None:
            bbox.setdefault("facecolor", facecolor)
        if edgecolor is not None:
            bbox.setdefault("edgecolor", edgecolor)
        kwargs["bbox"] = bbox
    if textcolor is not None:
        kwargs["color"] = textcolor
    return ax.annotate(text, xy, **kwargs)


def style_3d(ax, **kwargs):
    """Apply 3D theme styling when available; otherwise return the axes."""
    if _theme is not None:
        return _theme.style_3d(ax, **kwargs)
    return ax


__all__ = [
    "CORAL",
    "DIVERGING_CMAP",
    "INK",
    "PRIMARY",
    "SCALAR_CMAP",
    "SEQUENTIAL_CMAP",
    "WHITE",
    "annotate",
    "apply_theme",
    "bar",
    "barh",
    "colorbar",
    "get_palette",
    "legend",
    "style_3d",
    "theme",
]

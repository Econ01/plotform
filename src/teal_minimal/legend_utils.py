"""Solid and soft exact-capsule legends with explicit semantics."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from matplotlib.colors import to_hex, to_rgb, to_rgba

from .palette import INK, WHITE
from .rounded import CapsuleBox, capsule_path


def _relative_luminance(color) -> float:
    rgb = np.asarray(to_rgb(color), dtype=float)
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return float(np.dot(linear, (0.2126, 0.7152, 0.0722)))


def _contrast_ratio(first, second) -> float:
    light, dark = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (light + 0.05) / (dark + 0.05)


def _solid_text_color(color, target_contrast: float) -> str:
    """Choose white or black for readable text on a solid category fill."""
    white_ratio = _contrast_ratio(WHITE, color)
    black_ratio = _contrast_ratio(INK, color)
    if white_ratio >= target_contrast and white_ratio >= black_ratio:
        return WHITE
    if black_ratio >= target_contrast:
        return INK
    return WHITE if white_ratio > black_ratio else INK


def _text_color(color, background, alpha: float, target_contrast: float) -> str:
    """Darken a category color until it reads on its own tinted fill."""
    source = np.asarray(to_rgb(color), dtype=float)
    backdrop = np.asarray(to_rgb(background), dtype=float)
    fill = alpha * source + (1.0 - alpha) * backdrop
    if _contrast_ratio(source, fill) >= target_contrast:
        return to_hex(source)

    low, high = 0.0, 1.0
    for _ in range(36):
        factor = (low + high) / 2
        candidate = source * factor
        if _contrast_ratio(candidate, fill) >= target_contrast:
            low = factor
        else:
            high = factor
    return to_hex(source * low)


def _first_rgba(values):
    array = np.asarray(values)
    if array.size == 0:
        return None
    if array.ndim == 1:
        return array
    return array.reshape(-1, array.shape[-1])[0]


def _artist_color(artist):
    """Extract a representative color from common legendable artists."""
    if hasattr(artist, "patches") and artist.patches:
        artist = artist.patches[0]
    elif hasattr(artist, "lines") and artist.lines:
        lines = artist.lines
        artist = lines[0] if isinstance(lines, (tuple, list)) else lines
    elif hasattr(artist, "markerline"):
        artist = artist.markerline

    if hasattr(artist, "get_color"):
        color = artist.get_color()
        if isinstance(color, str):
            return color
        if color is not None:
            first = _first_rgba(color)
            if first is not None:
                return first

    if hasattr(artist, "get_facecolor"):
        color = _first_rgba(artist.get_facecolor())
        if color is not None and color[-1] > 0:
            return color
    if hasattr(artist, "get_edgecolor"):
        color = _first_rgba(artist.get_edgecolor())
        if color is not None:
            return color
    return INK


class _BackdropBox:
    def __init__(self, pad: float):
        self.pad = pad

    def __call__(self, x0, y0, width, height, mutation_size):
        pad = mutation_size * self.pad
        return capsule_path(x0 - pad, y0 - pad, width + 2 * pad, height + 2 * pad)


def pill_legend(
    ax,
    *,
    styles: Mapping[str, str] | None = None,
    alpha: float = 0.14,
    pad: float = 0.65,
    pill_height: float | None = 1.9,
    target_contrast: float = 4.5,
    outside: bool = False,
    backdrop: bool = False,
    backdrop_alpha: float = 0.88,
    backdrop_color: str = WHITE,
    backdrop_pad: float = 0.45,
    **kwargs,
):
    """Create an exact-capsule legend with solid or explicitly soft labels.

    Solid entries use full category-color fills and adaptive white/black text.
    ``styles={'95% interval': 'soft'}`` marks auxiliary regions for tinted
    fills and darkened category text. Generated marker/line handles are hidden
    rather than merely assigned zero width, preventing overlap with labels.

    ``outside=True`` places the legend above the axes. ``backdrop=True`` adds a
    semi-transparent white capsule behind the complete legend group.
    """
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be greater than 0 and at most 1")
    if not 0 < backdrop_alpha <= 1:
        raise ValueError("backdrop_alpha must be greater than 0 and at most 1")
    if target_contrast < 1:
        raise ValueError("target_contrast must be at least 1")

    handles, labels = ax.get_legend_handles_labels()
    styles = dict(styles or {})
    unknown_labels = set(styles).difference(labels)
    if unknown_labels:
        raise ValueError(f"styles contains unknown legend labels: {sorted(unknown_labels)}")
    invalid_styles = set(styles.values()).difference({"solid", "soft"})
    if invalid_styles:
        raise ValueError(f"Unknown legend styles: {sorted(invalid_styles)}")

    colors = [_artist_color(handle) for handle in handles]
    options = {
        "handlelength": 0,
        "handletextpad": 0,
        "labelspacing": 1.25,
        "columnspacing": 2.0,
        "borderpad": 0.35,
        "borderaxespad": 2.0,
        "frameon": False,
    }
    if outside:
        options.update({
            "loc": "lower left",
            "bbox_to_anchor": (0.0, 1.02),
            "borderaxespad": 0.0,
            "ncols": max(1, len(labels)),
        })
    options.update(kwargs)
    legend = ax.legend(handles, labels, **options)

    # handlelength=0 alone still allows some marker and errorbar artists to draw.
    for handle in legend.legend_handles:
        if handle is not None:
            handle.set_visible(False)

    background = ax.get_facecolor()
    for text, label, color in zip(legend.get_texts(), labels, colors):
        style = styles.get(label, "solid")
        if style == "soft":
            facecolor = to_rgba(color, alpha)
            textcolor = _text_color(color, background, alpha, target_contrast)
        else:
            facecolor = to_rgba(color, 1.0)
            textcolor = _solid_text_color(color, target_contrast)
        text.set_color(textcolor)
        text.set_bbox({
            "boxstyle": CapsuleBox(pad=pad, height=pill_height),
            "facecolor": facecolor,
            "edgecolor": "none",
        })

    if backdrop:
        legend.set_frame_on(True)
        frame = legend.get_frame()
        frame.set_boxstyle(_BackdropBox(backdrop_pad))
        frame.set_facecolor(backdrop_color)
        frame.set_alpha(backdrop_alpha)
        frame.set_edgecolor("none")
    return legend


__all__ = ["pill_legend"]

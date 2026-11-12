"""Vivid categorical colors, scalar colormaps, and theme neutrals."""

from __future__ import annotations

import colorsys
import operator

import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, to_hex

PRIMARY = "#008080"
CORAL = "#D55E00"
INK = "#000000"
MUTED = "#64727A"
GRID = "#E7ECEE"
AXIS = "#000000"
MUTED_AXIS = "#B9C4C9"
WHITE = "#FFFFFF"

# Vivid, accessibility-inspired categorical colors. Later colors are generated
# rather than repeating this cycle silently.
BASE_COLORS = (
    PRIMARY,
    "#E69F00",  # amber
    "#0072B2",  # blue
    CORAL,  # vermillion/coral
    "#6A51A3",  # purple
    "#4C9A2A",  # green
    "#CC79A7",  # rose
    "#4B5563",  # dark slate
)

# Brand teal map retained for optional use. SCALAR_CMAP is the default for
# continuous data because every stop remains visible against white.
SEQUENTIAL_CMAP = "plotform_seq"
DIVERGING_CMAP = "plotform_div"
SCALAR_CMAP = "plotform_scalar"
SCALAR_STOPS = ("#17324D", "#0072B2", PRIMARY, "#4C9A2A", "#C47F00")


def _validate_count(n_colors: int) -> int:
    n = operator.index(n_colors)
    if n < 1:
        raise ValueError("n_colors must be at least 1")
    return n


def get_palette(n_colors: int = len(BASE_COLORS)) -> list[str]:
    """Return *n_colors* distinct theme colors as hexadecimal strings.

    The curated colors always come first. Additional colors use a deterministic
    golden-angle hue sequence with alternating lightness and saturation. For
    more than about 12 categories, combine color with labels, markers, line
    styles, or small multiples.
    """
    n = _validate_count(n_colors)
    if n <= len(BASE_COLORS):
        return list(BASE_COLORS[:n])

    colors = list(BASE_COLORS)
    golden_angle = 0.618033988749895
    lightness = (0.42, 0.52, 0.36, 0.58)
    saturation = (0.65, 0.55, 0.70)

    for i in range(n - len(colors)):
        hue = (0.09 + i * golden_angle) % 1.0
        rgb = colorsys.hls_to_rgb(
            hue,
            lightness[i % len(lightness)],
            saturation[i % len(saturation)],
        )
        candidate = to_hex(rgb).upper()
        while candidate in colors:
            hue = (hue + 0.037) % 1.0
            candidate = to_hex(
                colorsys.hls_to_rgb(hue, lightness[i % 4], saturation[i % 3])
            ).upper()
        colors.append(candidate)

    return colors


def build_colormaps() -> tuple[
    LinearSegmentedColormap, LinearSegmentedColormap, LinearSegmentedColormap
]:
    """Build fresh brand-sequential, diverging, and full-range scalar maps."""
    sequential = LinearSegmentedColormap.from_list(
        SEQUENTIAL_CMAP,
        ["#F2FAF9", "#C6E8E5", "#75BCB7", PRIMARY, "#004C4C"],
    )
    diverging = LinearSegmentedColormap.from_list(
        DIVERGING_CMAP,
        ["#B84F00", "#F0A6A0", "#FAFAF8", "#62C3BC", PRIMARY],
    )
    scalar = LinearSegmentedColormap.from_list(SCALAR_CMAP, SCALAR_STOPS)
    return sequential, diverging, scalar


def register_colormaps() -> None:
    """Register theme colormaps with Matplotlib, once per process."""
    for cmap in build_colormaps():
        if cmap.name not in mpl.colormaps:
            mpl.colormaps.register(cmap, name=cmap.name)

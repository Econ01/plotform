"""Plotform: a minimalist Matplotlib theme and plotting toolkit."""

from importlib.metadata import version as _distribution_version

from .api import annotate, bar, barh, colorbar, legend
from .fonts import MONO_FONT, SANS_FONT
from .palette import (
    AXIS,
    BASE_COLORS,
    CORAL,
    DIVERGING_CMAP,
    GRID,
    INK,
    MUTED,
    MUTED_AXIS,
    PRIMARY,
    SCALAR_CMAP,
    SCALAR_STOPS,
    SEQUENTIAL_CMAP,
    WHITE,
    get_palette,
)
from .theme import apply_theme, theme
from .three_d import style_3d

__version__ = _distribution_version("plotform")

__all__ = [
    "AXIS",
    "BASE_COLORS",
    "CORAL",
    "DIVERGING_CMAP",
    "GRID",
    "INK",
    "MONO_FONT",
    "MUTED",
    "MUTED_AXIS",
    "PRIMARY",
    "SANS_FONT",
    "SCALAR_CMAP",
    "SCALAR_STOPS",
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

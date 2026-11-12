"""Teal Minimal: a portable, minimalist Matplotlib theme."""

from .api import annotate, bar, barh, colorbar, legend
from .colorbar_utils import capsule_colorbar
from .fonts import MONO_FONT, SANS_FONT, font_paths, register_fonts
from .legend_utils import pill_legend
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
from .rounded import (
    CapsuleBox,
    RoundedBarPatch,
    SquircleBox,
    add_pill,
    add_squircle,
    capsule_path,
    rounded_bar,
    rounded_barh,
    squircle_path,
)
from .theme import apply_theme, theme
from .three_d import style_3d

__version__ = "0.5.0"

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
    "CapsuleBox",
    "RoundedBarPatch",
    "SquircleBox",
    "add_pill",
    "add_squircle",
    "annotate",
    "apply_theme",
    "bar",
    "barh",
    "capsule_colorbar",
    "capsule_path",
    "colorbar",
    "font_paths",
    "get_palette",
    "legend",
    "pill_legend",
    "register_fonts",
    "rounded_bar",
    "rounded_barh",
    "squircle_path",
    "style_3d",
    "theme",
]

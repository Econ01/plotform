"""Global and scoped application of the Teal Minimal theme."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import matplotlib as mpl
from cycler import cycler
from matplotlib import style

from .fonts import MONO_FONT, SANS_FONT, register_fonts
from .palette import (
    AXIS,
    BASE_COLORS,
    DIVERGING_CMAP,
    GRID,
    INK,
    MUTED,
    MUTED_AXIS,
    PRIMARY,
    SCALAR_CMAP,
    WHITE,
    get_palette,
    register_colormaps,
)


def _rc_params(n_colors: int, gray_decorations: bool) -> dict:
    register_fonts()
    register_colormaps()
    axis_color = MUTED_AXIS if gray_decorations else AXIS
    tick_label_color = MUTED if gray_decorations else INK
    return {
        # Typography. Font weight is deliberately left at Matplotlib's default.
        "font.family": "sans-serif",
        "font.sans-serif": [SANS_FONT, "DejaVu Sans", "Arial", "sans-serif"],
        "font.monospace": [MONO_FONT, "DejaVu Sans Mono", "monospace"],
        "font.size": 10.5,
        "mathtext.fontset": "dejavusans",
        "text.color": INK,
        # Figure and output.
        "figure.facecolor": WHITE,
        "figure.edgecolor": WHITE,
        "figure.figsize": (8.0, 5.0),
        "figure.dpi": 120,
        "figure.constrained_layout.use": True,
        "figure.titlesize": 17.0,
        "savefig.facecolor": WHITE,
        "savefig.edgecolor": WHITE,
        "savefig.dpi": 800,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.15,
        "savefig.transparent": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "path",
        # Axes and minimalist decoration.
        "axes.facecolor": WHITE,
        "axes.edgecolor": axis_color,
        "axes.linewidth": 0.8,
        "axes.labelcolor": INK,
        "axes.labelsize": 10.5,
        "axes.labelpad": 8.0,
        "axes.titlesize": 15.0,
        "axes.titlecolor": INK,
        "axes.titlelocation": "left",
        "axes.titlepad": 14.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.prop_cycle": cycler("color", get_palette(n_colors)),
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "axes.unicode_minus": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "grid.alpha": 1.0,
        "xtick.color": axis_color,
        "xtick.labelcolor": tick_label_color,
        "xtick.labelsize": 9.5,
        "xtick.direction": "out",
        "xtick.major.size": 3.0,
        "xtick.major.width": 0.8,
        "xtick.major.pad": 6.0,
        "xtick.top": False,
        "ytick.color": axis_color,
        "ytick.labelcolor": tick_label_color,
        "ytick.labelsize": 9.5,
        "ytick.direction": "out",
        "ytick.major.size": 3.0,
        "ytick.major.width": 0.8,
        "ytick.major.pad": 6.0,
        "ytick.right": False,
        # Data ink.
        "lines.linewidth": 2.0,
        "lines.markersize": 6.5,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "lines.dash_capstyle": "round",
        "lines.dash_joinstyle": "round",
        "lines.markeredgewidth": 0.0,
        "scatter.marker": "o",
        "scatter.edgecolors": "none",
        "patch.linewidth": 0.8,
        "patch.edgecolor": WHITE,
        "patch.antialiased": True,
        "errorbar.capsize": 3.0,
        # Legends and common plot families.
        "legend.frameon": False,
        "legend.fontsize": 9.5,
        "legend.labelcolor": tick_label_color,
        "legend.labelspacing": 0.7,
        "legend.handlelength": 2.0,
        "legend.handletextpad": 0.7,
        "legend.borderaxespad": 0.5,
        "boxplot.boxprops.color": PRIMARY,
        "boxplot.boxprops.linewidth": 1.4,
        "boxplot.whiskerprops.color": MUTED,
        "boxplot.whiskerprops.linewidth": 1.2,
        "boxplot.capprops.color": MUTED,
        "boxplot.capprops.linewidth": 1.2,
        "boxplot.medianprops.color": INK,
        "boxplot.medianprops.linewidth": 1.5,
        "boxplot.flierprops.marker": "o",
        "boxplot.flierprops.markersize": 4.0,
        "boxplot.flierprops.markerfacecolor": PRIMARY,
        "boxplot.flierprops.markeredgecolor": "none",
        "image.cmap": SCALAR_CMAP,
        "contour.negative_linestyle": "dashed",
        # Exposed for users who prefer the diverging map without importing it.
        "axes.formatter.use_mathtext": False,
    }


def apply_theme(n_colors: int = len(BASE_COLORS), *, gray_decorations: bool = False) -> None:
    """Apply the theme globally, resetting Matplotlib to defaults first.

    Parameters
    ----------
    n_colors : int, default: 8
        Number of colors in the default categorical cycle. Values above eight
        use the deterministic palette extension.
    gray_decorations : bool, default: False
        Use the previous muted-gray axes and tick labels. Gridlines stay light
        in both modes; the default uses black axes and tick labels.
    """
    params = _rc_params(n_colors, gray_decorations)
    style.use("default")
    mpl.rcParams.update(params)


@contextmanager
def theme(n_colors: int = len(BASE_COLORS), *, gray_decorations: bool = False) -> Iterator[None]:
    """Temporarily apply the theme and restore previous settings on exit.

    This is useful for applications that create figures with multiple themes.
    Font registration and colormap registration remain process-global.
    """
    params = _rc_params(n_colors, gray_decorations)
    with style.context("default"):
        mpl.rcParams.update(params)
        yield


__all__ = ["apply_theme", "theme", "PRIMARY", "DIVERGING_CMAP"]

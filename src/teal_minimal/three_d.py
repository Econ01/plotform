"""Minimal styling for Matplotlib's mplot3d axes."""

from __future__ import annotations

from .palette import AXIS, GRID, INK, MUTED, MUTED_AXIS, WHITE


def style_3d(
    ax,
    *,
    grid: bool = True,
    transparent_panes: bool = True,
    elev: float = 25,
    azim: float = -55,
    gray_decorations: bool = False,
):
    """Apply the theme's pane, grid, tick, and viewing-angle defaults to 3D axes.

    Matplotlib does not expose these options through the normal 2D rcParams.
    Call this after creating an axes with ``projection='3d'``.
    """
    ax.set_facecolor(WHITE)
    ax.view_init(elev=elev, azim=azim)
    ax.grid(grid)
    axis_color = MUTED_AXIS if gray_decorations else AXIS
    label_color = MUTED if gray_decorations else INK

    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        if transparent_panes:
            axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        else:
            axis.set_pane_color(WHITE)
        axis._axinfo["grid"].update(color=GRID, linewidth=0.7)
        axis._axinfo["axisline"].update(color=axis_color, linewidth=0.8)

    ax.tick_params(axis="both", colors=label_color, labelcolor=label_color, width=0.8, pad=4)
    return ax


__all__ = ["style_3d"]

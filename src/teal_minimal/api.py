"""Native-style convenience names for Teal Minimal helpers."""

from __future__ import annotations

from matplotlib import pyplot as plt

from .colorbar_utils import capsule_colorbar
from .legend_utils import pill_legend
from .rounded import add_pill, rounded_bar, rounded_barh


def _axes(ax=None):
    return plt.gca() if ax is None else ax


def legend(ax=None, **kwargs):
    """Create a pill legend, using the current axes when ``ax`` is omitted."""
    return pill_legend(_axes(ax), **kwargs)


def bar(*args, ax=None, **kwargs):
    """Draw rounded bars with native ``plt.bar``-style argument order."""
    return rounded_bar(_axes(ax), *args, **kwargs)


def barh(*args, ax=None, **kwargs):
    """Draw horizontal rounded bars with native ``plt.barh``-style order."""
    return rounded_barh(_axes(ax), *args, **kwargs)


def colorbar(mappable, *, fig=None, ax=None, **kwargs):
    """Create a capsule colorbar, using the current figure/axes by default."""
    fig = plt.gcf() if fig is None else fig
    return capsule_colorbar(fig, _axes(ax), mappable, **kwargs)


def annotate(text, xy, *, ax=None, **kwargs):
    """Add a capsule annotation with native ``Axes.annotate`` argument order."""
    return add_pill(_axes(ax), xy[0], xy[1], text, **kwargs)


__all__ = ["annotate", "bar", "barh", "colorbar", "legend"]

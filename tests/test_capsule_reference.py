"""Compare rendered capsule silhouettes with analytic stadium masks."""

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.patches import PathPatch

from plotform import rounded as rf


def _render_and_reference(orientation):
    if orientation == "horizontal":
        figure_size = (4, 2)
        limits = (4, 2)
        bounds = (0.5, 0.5, 3, 1)
    else:
        figure_size = (2, 4)
        limits = (2, 4)
        bounds = (0.5, 0.5, 1, 3)

    fig = plt.figure(figsize=figure_size, dpi=100, layout="none")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, limits[0]), ylim=(0, limits[1]))
    ax.axis("off")
    ax.add_patch(PathPatch(rf.capsule_path(*bounds), facecolor="black", edgecolor="none"))
    fig.canvas.draw()

    rgb = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    rendered = rgb.mean(axis=2) < 127.5
    height, width = rendered.shape
    pixel_x = np.arange(width) + 0.5
    pixel_y = height - (np.arange(height) + 0.5)
    xx, yy = np.meshgrid(pixel_x, pixel_y)
    data = ax.transData.inverted().transform(np.column_stack((xx.ravel(), yy.ravel())))
    x = data[:, 0].reshape(height, width)
    y = data[:, 1].reshape(height, width)

    # A capsule is a line segment dilated by a disk of radius 0.5.
    if orientation == "horizontal":
        dx = np.maximum(np.maximum(1 - x, x - 3), 0)
        distance = np.hypot(dx, y - 1)
    else:
        dy = np.maximum(np.maximum(1 - y, y - 3), 0)
        distance = np.hypot(x - 1, dy)
    reference = distance <= 0.5
    plt.close(fig)
    return rendered, reference


@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
def test_rendered_capsule_matches_analytic_reference(orientation):
    rendered, reference = _render_and_reference(orientation)
    intersection = np.count_nonzero(rendered & reference)
    union = np.count_nonzero(rendered | reference)
    assert union > 0
    # Antialiasing accounts for the remaining subpixel boundary differences.
    assert intersection / union > 0.995

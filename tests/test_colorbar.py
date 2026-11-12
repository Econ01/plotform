import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np
import pytest

import teal_minimal as tm


def test_capsule_colorbar_clips_gradient_and_keeps_ticks_outside():
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    image = ax.imshow(np.arange(25).reshape(5, 5), cmap=tm.SCALAR_CMAP)
    colorbar = tm.capsule_colorbar(fig, ax, image, pad=0.05)
    fig.canvas.draw()
    cax = colorbar.ax
    clip = colorbar.capsule_patch

    assert colorbar.solids.get_clip_path()._patch is clip
    assert not colorbar.outline.get_visible()
    assert Path.CURVE4 in clip.get_path().codes
    bounds = cax.bbox
    extents = np.ptp(clip.get_path().vertices, axis=0)
    assert extents[0] == pytest.approx(bounds.width)
    assert extents[1] == pytest.approx(bounds.height)

    renderer = fig.canvas.get_renderer()
    for label in cax.get_yticklabels():
        if label.get_text():
            assert label.get_window_extent(renderer).x0 >= bounds.x1

    # The upper corner is outside the capsule and remains white, while the
    # upper center contains actual gradient pixels.
    canvas = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    x_corner = int(bounds.x0 + 1)
    x_center = int((bounds.x0 + bounds.x1) / 2)
    y_top = int(fig.canvas.get_width_height()[1] - bounds.y1)
    assert np.all(canvas[y_top, x_corner] > 245)
    assert np.any(canvas[y_top, x_center] < 240)
    plt.close(fig)


def test_capsule_colorbar_supports_contour_mappables():
    fig, ax = plt.subplots()
    values = np.linspace(-1, 1, 100).reshape(10, 10)
    contour = ax.contourf(values, cmap=tm.DIVERGING_CMAP)
    colorbar = tm.capsule_colorbar(fig, ax, contour)
    fig.canvas.draw()
    assert colorbar.solids.get_clip_path()._patch is colorbar.capsule_patch
    plt.close(fig)


def test_horizontal_capsule_colorbar_is_rejected():
    fig, ax = plt.subplots()
    image = ax.imshow(np.arange(9).reshape(3, 3))
    with pytest.raises(ValueError):
        tm.capsule_colorbar(fig, ax, image, orientation="horizontal")
    plt.close(fig)

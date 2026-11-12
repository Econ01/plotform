import matplotlib.pyplot as plt
import numpy as np

import plotform as tm
from plotform import rounded as rf
from plotform.colorbar_utils import capsule_colorbar
from plotform.legend_utils import pill_legend


def test_native_style_legend_uses_current_axes():
    fig, ax = plt.subplots()
    ax.plot([0, 1], label="Series")
    plt.sca(ax)
    legend = tm.legend()
    assert legend.get_texts()[0].get_bbox_patch() is not None
    plt.close(fig)


def test_native_style_bar_and_barh():
    fig, (ax1, ax2) = plt.subplots(1, 2)
    vertical = tm.bar([0, 1], [2, 3], ax=ax1)
    horizontal = tm.barh([0, 1], [2, 3], ax=ax2)
    assert isinstance(vertical.patches[0], rf.RoundedBarPatch)
    assert isinstance(horizontal.patches[0], rf.RoundedBarPatch)
    fig.canvas.draw()
    plt.close(fig)


def test_native_style_colorbar():
    fig, ax = plt.subplots()
    image = ax.imshow(np.arange(9).reshape(3, 3), cmap=tm.SCALAR_CMAP)
    colorbar = tm.colorbar(image, ax=ax)
    assert colorbar.capsule_patch is not None
    plt.close(fig)


def test_native_style_annotation_and_advanced_modules():
    fig, ax = plt.subplots()
    annotation = tm.annotate("Note", (0.5, 0.5), ax=ax, transform=ax.transAxes)
    assert annotation.get_bbox_patch() is not None
    assert pill_legend is not None
    assert rf.rounded_bar is not None
    assert capsule_colorbar is not None
    plt.close(fig)

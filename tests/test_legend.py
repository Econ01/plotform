import matplotlib.pyplot as plt
import numpy as np
import pytest

import plotform as tm
from plotform.legend_utils import _contrast_ratio, _solid_text_color


def _assert_handles_hidden(legend):
    assert legend.legend_handles
    assert all(not handle.get_visible() for handle in legend.legend_handles)


def test_solid_pills_use_adaptive_text_and_hide_handles():
    fig, ax = plt.subplots()
    x = np.linspace(0, 1, 10)
    ax.plot(x, x, label="Teal")
    ax.plot(x, 1 - x, label="Amber")
    ax.plot(x, x**2, label="Blue")
    legend = tm.legend(ax, ncols=3)

    assert legend.handlelength == 0
    assert legend.borderaxespad == 2.0
    _assert_handles_hidden(legend)
    text_colors = set()
    for text in legend.get_texts():
        patch = text.get_bbox_patch()
        facecolor = patch.get_facecolor()
        assert facecolor[-1] == pytest.approx(1.0)
        assert _contrast_ratio(text.get_color(), facecolor[:3]) >= 4.5 - 1e-8
        text_colors.add(text.get_color())
    assert text_colors == {tm.INK, tm.WHITE}

    fig.canvas.draw()
    heights = [
        np.ptp(text.get_bbox_patch().get_path().vertices[:, 1]) for text in legend.get_texts()
    ]
    assert np.allclose(heights, heights[0])
    plt.close(fig)


def test_every_palette_color_has_readable_solid_legend_text():
    for color in tm.BASE_COLORS:
        text_color = _solid_text_color(color, 4.5)
        assert _contrast_ratio(text_color, color) >= 4.5 - 1e-8


def test_public_helper_names_remain_callable_after_internal_imports():
    assert callable(tm.legend)
    assert callable(tm.colorbar)


def test_uncertainty_region_is_soft_and_estimate_is_solid():
    fig, ax = plt.subplots()
    x = np.linspace(0, 4, 8)
    y = np.sin(x)
    ax.fill_between(x, y - 0.2, y + 0.2, alpha=0.14, label="95% interval")
    ax.errorbar(x, y, yerr=0.2, fmt="o-", label="Estimate")
    legend = tm.legend(ax, styles={"95% interval": "soft"})
    _assert_handles_hidden(legend)

    region, estimate = legend.get_texts()
    region_fill = region.get_bbox_patch().get_facecolor()
    estimate_fill = estimate.get_bbox_patch().get_facecolor()
    assert region_fill[-1] == pytest.approx(0.14)
    assert estimate_fill[-1] == pytest.approx(1.0)
    background = np.asarray(region_fill[:3]) * region_fill[-1] + (1 - region_fill[-1])
    assert _contrast_ratio(region.get_color(), background) >= 4.5 - 1e-8
    assert _contrast_ratio(estimate.get_color(), estimate_fill[:3]) >= 4.5 - 1e-8
    fig.canvas.draw()
    plt.close(fig)


def test_scatter_handle_is_not_drawn_over_single_character_pill():
    fig, ax = plt.subplots()
    ax.scatter([0, 1], [1, 2], label="A")
    legend = tm.legend(ax)
    _assert_handles_hidden(legend)
    fig.canvas.draw()
    extents = np.ptp(legend.get_texts()[0].get_bbox_patch().get_path().vertices, axis=0)
    assert extents[0] == pytest.approx(extents[1])
    plt.close(fig)


def test_right_aligned_pills_stay_inside_axes():
    fig, ax = plt.subplots()
    rng = np.random.default_rng(4)
    ax.hist(rng.normal(size=100), label="A")
    tm.legend(ax, loc="upper right")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in ax.get_legend().get_texts():
        bounds = text.get_bbox_patch().get_window_extent(renderer)
        assert bounds.x1 <= ax.bbox.x1 + 0.1
    plt.close(fig)


def test_outside_legend_is_above_axes():
    fig, ax = plt.subplots()
    ax.stackplot([0, 1], [1, 2], [2, 1], labels=("A", "B"))
    legend = tm.legend(ax, outside=True)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    assert legend.get_window_extent(renderer).y0 >= ax.bbox.y1
    plt.close(fig)


def test_white_group_backdrop_is_a_capsule():
    fig, ax = plt.subplots()
    ax.plot([0, 1], label="Series")
    legend = tm.legend(ax, backdrop=True)
    frame = legend.get_frame()
    assert frame.get_visible()
    assert frame.get_facecolor()[-1] == pytest.approx(0.88)
    fig.canvas.draw()
    assert frame.get_path().vertices.shape[0] > 10
    plt.close(fig)


def test_pill_legend_supports_bars_and_scatter():
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.bar([0, 1], [2, 3], label="Bars")
    ax2.scatter([0, 1], [1, 2], label="Points")
    first = tm.legend(ax1)
    second = tm.legend(ax2)
    _assert_handles_hidden(first)
    _assert_handles_hidden(second)
    fig.canvas.draw()
    plt.close(fig)


@pytest.mark.parametrize("alpha", [0, -0.1, 1.1])
def test_invalid_legend_alpha(alpha):
    fig, ax = plt.subplots()
    ax.plot([0, 1], label="Line")
    with pytest.raises(ValueError):
        tm.legend(ax, alpha=alpha)
    plt.close(fig)


@pytest.mark.parametrize("styles", [{"Missing": "soft"}, {"Line": "unknown"}])
def test_invalid_style_mapping(styles):
    fig, ax = plt.subplots()
    ax.plot([0, 1], label="Line")
    with pytest.raises(ValueError):
        tm.legend(ax, styles=styles)
    plt.close(fig)

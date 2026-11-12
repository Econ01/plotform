import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.path import Path

from plotform import rounded as rf


def assert_vertex(path, point, tolerance=1e-7):
    assert np.any(np.all(np.isclose(path.vertices, point, atol=tolerance), axis=1)), (
        f"Missing path vertex {point}"
    )


def test_squircle_bounds_and_closure():
    path = rf.squircle_path(1, 2, 4, 6)
    vertices = path.vertices
    assert np.allclose(vertices[0], vertices[-1])
    assert vertices[:, 0].min() == pytest.approx(1)
    assert vertices[:, 0].max() == pytest.approx(5)
    assert vertices[:, 1].min() == pytest.approx(2)
    assert vertices[:, 1].max() == pytest.approx(8)


def test_horizontal_capsule_has_exact_straights_and_semicircle_endpoints():
    path = rf.capsule_path(0, 0, 8, 2)
    # Radius 1; right cap center (7, 1), left cap center (1, 1).
    for point in ((1, 2), (7, 2), (8, 1), (7, 0), (1, 0), (0, 1)):
        assert_vertex(path, point)

    # The top edge is exactly horizontal from x=1 to x=7.
    top_index = next(i for i, point in enumerate(path.vertices) if np.allclose(point, (1, 2)))
    assert path.codes[top_index + 1] == Path.LINETO
    assert np.allclose(path.vertices[top_index + 1], (7, 2))
    # Its first right-cap control point is horizontal, proving tangent alignment.
    assert np.allclose(path.vertices[top_index + 2], (7 + 0.5522847498307936, 2))


def test_vertical_capsule_has_exact_semicircle_endpoints():
    path = rf.capsule_path(0, 0, 2, 8)
    for point in ((0, 7), (1, 8), (2, 7), (2, 1), (1, 0), (0, 1)):
        assert_vertex(path, point)
    assert np.isclose(path.vertices[:, 0].min(), 0)
    assert np.isclose(path.vertices[:, 0].max(), 2)
    assert np.isclose(path.vertices[:, 1].min(), 0)
    assert np.isclose(path.vertices[:, 1].max(), 8)


def test_square_capsule_is_a_circle():
    path = rf.capsule_path(0, 0, 2, 2)
    extent = np.ptp(path.vertices, axis=0)
    assert np.allclose(extent, (2, 2))
    assert_vertex(path, (0, 1))
    assert_vertex(path, (1, 2))
    assert_vertex(path, (2, 1))
    assert_vertex(path, (1, 0))


def test_invalid_shapes():
    with pytest.raises(ValueError):
        rf.squircle_path(0, 0, 1, 1, exponent=1)
    with pytest.raises(ValueError):
        rf.capsule_path(0, 0, -1, 1)


def test_pills_have_consistent_height_and_single_character_circles():
    fig, ax = plt.subplots()
    single = rf.add_pill(ax, 0.25, 0.5, "A", transform=ax.transAxes)
    longer = rf.add_pill(ax, 0.65, 0.5, "Long label", transform=ax.transAxes)
    fig.canvas.draw()
    single_extents = np.ptp(single.get_bbox_patch().get_path().vertices, axis=0)
    longer_extents = np.ptp(longer.get_bbox_patch().get_path().vertices, axis=0)
    assert single_extents[0] == pytest.approx(single_extents[1])
    assert longer_extents[0] > longer_extents[1]
    assert single_extents[1] == pytest.approx(longer_extents[1])
    plt.close(fig)


def test_positive_and_negative_rounded_bars():
    fig, ax = plt.subplots()
    container = rf.rounded_bar(ax, [0, 1, 2], [3, -2, 0], radius=0.2, label="Values")
    assert len(container.patches) == 3
    assert container.get_label() == "Values"
    assert ax.dataLim.y0 <= -2
    assert ax.dataLim.y1 >= 3
    ax.legend()
    fig.canvas.draw()
    assert Path.CURVE4 in container.patches[0].get_path().codes
    plt.close(fig)


@pytest.mark.parametrize("figsize", [(5, 3), (8, 4)])
def test_full_cap_has_exact_display_radius_and_join_endpoints(figsize):
    fig, ax = plt.subplots(figsize=figsize, dpi=100)
    width = 0.2
    container = rf.rounded_bar(ax, [0, 1, 2, 3], [3, 3, 3, 3], width=width, radius="full")
    fig.canvas.draw()
    path = container.patches[0].get_path()
    x0, _ = ax.transData.transform((-width / 2, 0))
    x1, _ = ax.transData.transform((width / 2, 0))
    _, baseline = ax.transData.transform((0, 0))
    _, top = ax.transData.transform((0, 3))
    radius = (x1 - x0) / 2

    assert_vertex(path, (x0, top - radius))
    assert_vertex(path, ((x0 + x1) / 2, top))
    assert_vertex(path, (x1, top - radius))
    assert_vertex(path, (x0, baseline))
    assert_vertex(path, (x1, baseline))
    plt.close(fig)


def test_both_ends_make_an_exact_vertical_capsule():
    fig, ax = plt.subplots(dpi=100)
    width = 0.2
    container = rf.rounded_bar(
        ax, [0, 1, 2, 3], [3, 3, 3, 3], width=width, radius="full", ends="both"
    )
    fig.canvas.draw()
    path = container.patches[0].get_path()
    x0, _ = ax.transData.transform((-width / 2, 0))
    x1, _ = ax.transData.transform((width / 2, 0))
    _, baseline = ax.transData.transform((0, 0))
    _, top = ax.transData.transform((0, 3))
    radius = (x1 - x0) / 2
    center = (x0 + x1) / 2

    assert_vertex(path, (center, top))
    assert_vertex(path, (center, baseline))
    assert_vertex(path, (x0, top - radius))
    assert_vertex(path, (x1, top - radius))
    assert_vertex(path, (x0, baseline + radius))
    assert_vertex(path, (x1, baseline + radius))
    plt.close(fig)


def test_horizontal_and_negative_full_bars_render():
    fig, (ax1, ax2) = plt.subplots(1, 2)
    vertical = rf.rounded_bar(ax1, [0, 1], [-2, -4], radius="full", ends="both")
    horizontal = rf.rounded_barh(ax2, [0, 1], [4, -2], radius="full")
    assert ax1.dataLim.y0 <= -4
    assert ax2.dataLim.x0 <= -2
    assert ax2.dataLim.x1 >= 4
    fig.canvas.draw()
    assert Path.CURVE4 in vertical.patches[0].get_path().codes
    assert Path.CURVE4 in horizontal.patches[0].get_path().codes
    plt.close(fig)


def test_short_full_bar_fails_clearly_but_fit_and_zero_radius_render():
    fig, ax = plt.subplots()
    rf.rounded_bar(ax, [0], [0.01], radius="full", ends="both")
    with pytest.raises(ValueError, match="exact full capsule"):
        fig.canvas.draw()
    plt.close(fig)

    fig, ax = plt.subplots()
    short = rf.rounded_bar(ax, [0], [0.01], radius="fit", ends="both")
    square = rf.rounded_bar(ax, [1], [2], radius=0)
    fig.canvas.draw()
    assert np.isfinite(short.patches[0].get_path().vertices).all()
    assert square.patches[0].get_path().vertices.shape[0] == 5
    plt.close(fig)


def test_empty_rounded_bars():
    fig, ax = plt.subplots()
    container = rf.rounded_bar(ax, [], [])
    assert container.patches == []
    fig.canvas.draw()
    plt.close(fig)


@pytest.mark.parametrize("options", [{"radius": -1}, {"radius": "circle"}, {"ends": "top"}])
def test_invalid_bar_options(options):
    fig, ax = plt.subplots()
    with pytest.raises(ValueError):
        rf.rounded_bar(ax, [0], [1], **options)
    plt.close(fig)

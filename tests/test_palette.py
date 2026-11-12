import matplotlib as mpl
from matplotlib.colors import is_color_like
import pytest

import teal_minimal as tm
from teal_minimal.palette import register_colormaps
from teal_minimal.legend_utils import _contrast_ratio


def test_curated_palette_order():
    assert tm.get_palette(1) == [tm.PRIMARY]
    assert tm.get_palette(3) == ["#008080", "#E69F00", "#0072B2"]
    assert tm.get_palette(8) == list(tm.BASE_COLORS)


def test_palette_extension_is_deterministic_and_unique():
    first = tm.get_palette(64)
    second = tm.get_palette(64)
    assert first == second
    assert len(first) == len(set(first)) == 64
    assert first[:8] == list(tm.BASE_COLORS)
    assert all(is_color_like(color) for color in first)


@pytest.mark.parametrize("count", [0, -1])
def test_invalid_palette_size(count):
    with pytest.raises(ValueError):
        tm.get_palette(count)


def test_custom_colormaps_are_registered():
    register_colormaps()
    assert mpl.colormaps[tm.SEQUENTIAL_CMAP].N == 256
    assert mpl.colormaps[tm.DIVERGING_CMAP].N == 256
    assert mpl.colormaps[tm.SCALAR_CMAP].N == 256


def test_scalar_map_is_opaque_and_visible_against_white():
    cmap = mpl.colormaps[tm.SCALAR_CMAP]
    for position in (0, 0.25, 0.5, 0.75, 1):
        color = cmap(position)
        assert color[-1] == 1
        assert _contrast_ratio(color, tm.WHITE) >= 3.0

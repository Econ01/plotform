import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

import teal_minimal as tm


def cycle_colors():
    return [entry["color"] for entry in mpl.rcParams["axes.prop_cycle"]]


def test_theme_defaults():
    assert mpl.rcParams["figure.facecolor"] == tm.WHITE
    assert mpl.rcParams["axes.facecolor"] == tm.WHITE
    assert cycle_colors()[0] == tm.PRIMARY
    assert mpl.rcParams["font.sans-serif"][0] == tm.SANS_FONT
    assert mpl.rcParams["font.monospace"][0] == tm.MONO_FONT
    assert mpl.rcParams["lines.solid_capstyle"] == "round"
    assert not mpl.rcParams["axes.spines.top"]
    assert not mpl.rcParams["axes.spines.right"]
    assert mpl.rcParams["savefig.dpi"] == 800
    assert mpl.rcParams["axes.edgecolor"] == tm.INK
    assert mpl.rcParams["xtick.labelcolor"] == tm.INK
    assert mpl.rcParams["ytick.labelcolor"] == tm.INK
    assert mpl.rcParams["grid.color"] == tm.GRID
    assert mpl.rcParams["image.cmap"] == tm.SCALAR_CMAP


def test_optional_gray_decorations():
    tm.apply_theme(gray_decorations=True)
    assert mpl.rcParams["axes.edgecolor"] == tm.MUTED_AXIS
    assert mpl.rcParams["xtick.labelcolor"] == tm.MUTED
    assert mpl.rcParams["ytick.labelcolor"] == tm.MUTED
    assert mpl.rcParams["grid.color"] == tm.GRID


def test_font_weight_is_not_overridden():
    assert mpl.rcParams["font.weight"] == mpl.rcParamsDefault["font.weight"]
    assert mpl.rcParams["axes.titleweight"] == mpl.rcParamsDefault["axes.titleweight"]


def test_extended_cycle():
    tm.apply_theme(n_colors=14)
    colors = cycle_colors()
    assert len(colors) == 14
    assert colors == tm.get_palette(14)


def test_scoped_theme_restores_previous_settings():
    original = mpl.rcParams["axes.titlesize"]
    with tm.theme(n_colors=3):
        assert len(cycle_colors()) == 3
        mpl.rcParams["axes.titlesize"] = 99
    assert mpl.rcParams["axes.titlesize"] == original


@pytest.mark.parametrize("suffix,signature", [("png", b"\x89PNG"), ("pdf", b"%PDF"), ("svg", b"<?xml")])
def test_export_formats(tmp_path, suffix, signature):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 2])
    ax.set_title("Portable export")
    path = tmp_path / f"figure.{suffix}"
    fig.savefig(path, dpi=32)
    plt.close(fig)
    assert path.read_bytes().startswith(signature)
    assert path.stat().st_size > 500


def test_3d_style():
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    result = tm.style_3d(ax)
    assert result is ax
    assert ax.xaxis.pane.get_facecolor()[-1] == 0
    assert ax.xaxis._axinfo["axisline"]["color"] == tm.INK
    fig.canvas.draw()
    plt.close(fig)

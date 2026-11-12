import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import teal_minimal as tm
import theme_compat as compat


def test_compat_enhanced_theme_is_scoped():
    previous = mpl.rcParams["font.sans-serif"][0]
    with compat.theme():
        assert mpl.rcParams["font.sans-serif"][0] == tm.SANS_FONT
    assert mpl.rcParams["font.sans-serif"][0] == previous


def test_compat_missing_theme_preserves_current_style(monkeypatch):
    monkeypatch.setattr(compat, "_theme", None)
    original = mpl.rcParams["axes.titlesize"]
    with compat.theme():
        assert mpl.rcParams["axes.titlesize"] == original
    compat.apply_theme()
    assert mpl.rcParams["axes.titlesize"] == original


def test_compat_disabled_theme_preserves_current_style():
    original = mpl.rcParams["axes.titlesize"]
    with compat.theme(enabled=False):
        assert mpl.rcParams["axes.titlesize"] == original


def test_compat_legend_enhanced_and_fallback(monkeypatch):
    fig, ax = plt.subplots()
    ax.plot([0, 1], label="Series")
    enhanced = compat.legend(ax)
    assert enhanced.get_texts()[0].get_bbox_patch() is not None
    monkeypatch.setattr(compat, "_theme", None)
    fallback = compat.legend(
        ax,
        styles={"Series": "soft"},
        outside=True,
        backdrop=True,
        alpha=0.14,
    )
    assert fallback.get_frame().get_visible()
    fig.canvas.draw()
    plt.close(fig)


def test_compat_bar_and_barh_fallbacks(monkeypatch):
    fig, (ax1, ax2) = plt.subplots(1, 2)
    vertical = compat.bar([0, 1], [2, 3], ax=ax1, radius="full")
    horizontal = compat.barh([0, 1], [2, 3], ax=ax2, radius="full")
    assert isinstance(vertical.patches[0], tm.RoundedBarPatch)
    assert isinstance(horizontal.patches[0], tm.RoundedBarPatch)
    monkeypatch.setattr(compat, "_theme", None)
    native_vertical = compat.bar([0, 1], [2, 3], ax=ax1, radius="full")
    native_horizontal = compat.barh([0, 1], [2, 3], ax=ax2, radius="full")
    assert not isinstance(native_vertical.patches[0], tm.RoundedBarPatch)
    assert not isinstance(native_horizontal.patches[0], tm.RoundedBarPatch)
    plt.close(fig)


def test_compat_colorbar_fallback(monkeypatch):
    fig, ax = plt.subplots()
    image = ax.imshow(np.arange(9).reshape(3, 3))
    enhanced = compat.colorbar(image, ax=ax)
    assert hasattr(enhanced, "capsule_patch")
    monkeypatch.setattr(compat, "_theme", None)
    fallback = compat.colorbar(image, ax=ax)
    assert not hasattr(fallback, "capsule_patch")
    plt.close(fig)


def test_compat_annotate_and_3d_fallbacks(monkeypatch):
    fig = plt.figure()
    ax = fig.add_subplot()
    monkeypatch.setattr(compat, "_theme", None)
    annotation = compat.annotate(
        "Note",
        (0.5, 0.5),
        ax=ax,
        facecolor="#008080",
        textcolor="white",
        edgecolor="none",
        height=1.9,
    )
    assert annotation.get_bbox_patch() is not None
    ax3d = fig.add_subplot(projection="3d")
    assert compat.style_3d(ax3d) is ax3d
    plt.close(fig)

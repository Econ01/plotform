import runpy
from pathlib import Path

import plotform as tm


def test_public_api_is_focused():
    assert set(tm.__all__) == {
        "AXIS",
        "BASE_COLORS",
        "CORAL",
        "DIVERGING_CMAP",
        "GRID",
        "INK",
        "MONO_FONT",
        "MUTED",
        "MUTED_AXIS",
        "PRIMARY",
        "SANS_FONT",
        "SCALAR_CMAP",
        "SCALAR_STOPS",
        "SEQUENTIAL_CMAP",
        "WHITE",
        "annotate",
        "apply_theme",
        "bar",
        "barh",
        "colorbar",
        "get_palette",
        "legend",
        "style_3d",
        "theme",
    }


def test_version_matches_initial_release():
    assert tm.__version__ == "0.1.0"


def test_native_matplotlib_example_runs_without_plotform(tmp_path, monkeypatch):
    example = Path(__file__).parents[1] / "examples" / "native_matplotlib.py"
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(example), run_name="__main__")
    assert (tmp_path / "artifacts" / "native-matplotlib.png").is_file()

import matplotlib

matplotlib.use("Agg")

import pytest

import plotform as tm


@pytest.fixture(autouse=True)
def clean_theme():
    tm.apply_theme()
    yield

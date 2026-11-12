from fontTools.ttLib import TTFont

import plotform as tm
from plotform.fonts import font_paths, register_fonts


def test_bundled_fonts_resolve_exactly():
    resolved = register_fonts()
    assert resolved[tm.SANS_FONT].name == "PlotformSans-Rounded.ttf"
    assert resolved[tm.MONO_FONT].name == "PlotformMono-Regular.ttf"


def test_fonts_are_static_default_weight_instances():
    for family, path in font_paths().items():
        font = TTFont(path)
        assert "fvar" not in font
        assert font["OS/2"].usWeightClass == 400
        assert font["name"].getDebugName(1) == family
        assert font["name"].getDebugName(2) == "Regular"


def test_font_licenses_are_bundled():
    directory = font_paths()[tm.SANS_FONT].parent
    assert len(list(directory.glob("*-OFL.txt"))) == 2

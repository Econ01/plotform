"""Registration and verification of the bundled theme fonts."""

from __future__ import annotations

from pathlib import Path

from matplotlib import font_manager

SANS_FONT = "Teal Minimal Sans"
MONO_FONT = "Teal Minimal Mono"
FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"
FONT_FILES = ("TealMinimalSans-Rounded.ttf", "TealMinimalMono-Regular.ttf")

_registered = False


def font_paths() -> dict[str, Path]:
    """Return the expected bundled font paths by family name."""
    return {
        SANS_FONT: FONT_DIR / FONT_FILES[0],
        MONO_FONT: FONT_DIR / FONT_FILES[1],
    }


def register_fonts(*, verify: bool = True) -> dict[str, Path]:
    """Register bundled fonts with Matplotlib without modifying the OS.

    Returns the resolved font files. With ``verify=True``, a missing or invalid
    font raises instead of silently falling back to a system font.
    """
    global _registered

    paths = font_paths()
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Bundled theme fonts are missing: " + ", ".join(missing)
        )

    if not _registered:
        for path in paths.values():
            font_manager.fontManager.addfont(str(path))
        _registered = True

    if verify:
        resolved: dict[str, Path] = {}
        for family in (SANS_FONT, MONO_FONT):
            properties = font_manager.FontProperties(family=family)
            found = Path(
                font_manager.findfont(properties, fallback_to_default=False)
            ).resolve()
            expected = paths[family].resolve()
            if found != expected:
                raise RuntimeError(
                    f"Matplotlib resolved {family!r} to {found}, expected {expected}"
                )
            resolved[family] = found
        return resolved

    return paths

"""Download and instantiate the open-licensed fonts bundled with the theme.

Run from the repository root with ``python tools/prepare_fonts.py``. Network
access and fontTools are required only when regenerating the font assets, not
when installing or using the package.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "src" / "teal_minimal" / "assets" / "fonts"
BASE_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl"

SOURCES = {
    "sans": {
        "url": f"{BASE_URL}/googlesansflex/GoogleSansFlex%5BROND%2Copsz%2Cslnt%2Cwdth%2Cwght%5D.ttf",
        "license": f"{BASE_URL}/googlesansflex/OFL.txt",
        "trademarks": f"{BASE_URL}/googlesansflex/TRADEMARKS.md",
        "output": "TealMinimalSans-Rounded.ttf",
        "family": "Teal Minimal Sans",
        "postscript": "TealMinimalSans-Rounded",
    },
    "mono": {
        "url": f"{BASE_URL}/googlesanscode/GoogleSansCode%5Bwght%5D.ttf",
        "license": f"{BASE_URL}/googlesanscode/OFL.txt",
        "trademarks": f"{BASE_URL}/googlesanscode/TRADEMARKS.md",
        "output": "TealMinimalMono-Regular.ttf",
        "family": "Teal Minimal Mono",
        "postscript": "TealMinimalMono-Regular",
    },
}


def download(url: str) -> bytes:
    with urlopen(url, timeout=60) as response:
        return response.read()


def rename_font(font: TTFont, family: str, postscript: str) -> None:
    names = font["name"]
    replacements = {
        1: family,
        2: "Regular",
        3: f"{postscript}-0.1.0",
        4: family,
        6: postscript,
        16: family,
        17: "Regular",
    }
    names.names = [record for record in names.names if record.nameID not in replacements]
    for name_id, value in replacements.items():
        names.setName(value, name_id, 3, 1, 0x409)
        names.setName(value, name_id, 1, 0, 0)


def instantiate(source: bytes, *, rounded: bool, family: str, postscript: str) -> TTFont:
    font = TTFont(BytesIO(source))
    axes = {axis.axisTag: axis.defaultValue for axis in font["fvar"].axes}
    if rounded:
        if "ROND" not in axes:
            raise RuntimeError("The downloaded Google Sans Flex font has no ROND axis")
        axes["ROND"] = 100.0
    # Every other axis, especially weight, stays at its source default.
    instantiateVariableFont(font, axes, inplace=True, updateFontNames=False)
    rename_font(font, family, postscript)
    return font


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for kind, source in SOURCES.items():
        print(f"Downloading {source['family']} source...")
        raw = download(source["url"])
        font = instantiate(
            raw,
            rounded=(kind == "sans"),
            family=source["family"],
            postscript=source["postscript"],
        )
        destination = OUTPUT / source["output"]
        font.save(destination)
        print(f"Wrote {destination.relative_to(ROOT)}")

        license_name = f"{source['family'].replace(' ', '')}-OFL.txt"
        (OUTPUT / license_name).write_bytes(download(source["license"]))
        trademark_name = f"{source['family'].replace(' ', '')}-TRADEMARKS.md"
        (OUTPUT / trademark_name).write_bytes(download(source["trademarks"]))


if __name__ == "__main__":
    main()

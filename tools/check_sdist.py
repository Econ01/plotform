"""Check that the source distribution contains all required project files."""

from __future__ import annotations

import tarfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def main() -> None:
    version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
    archives = sorted(Path("dist").glob(f"plotform-{version}.tar.gz"))
    if len(archives) != 1:
        raise SystemExit(f"Expected one source archive for version {version}")

    required = {
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        "MANIFEST.in",
        "docs/images/overview.png",
        "docs/images/capsules.png",
        "docs/images/contact-sheet.png",
        "examples/native_matplotlib.py",
        "tools/make_doc_images.py",
        "tools/prepare_fonts.py",
        "src/plotform/assets/fonts/PlotformSans-Rounded.ttf",
        "src/plotform/assets/fonts/PlotformMono-Regular.ttf",
        "src/plotform/assets/fonts/PlotformSans-OFL.txt",
        "src/plotform/assets/fonts/PlotformMono-OFL.txt",
    }
    root = f"plotform-{version}"
    with tarfile.open(archives[0], "r:gz") as archive:
        names = set(archive.getnames())
    missing = sorted(f"{root}/{name}" for name in required if f"{root}/{name}" not in names)
    if missing:
        raise SystemExit("Source distribution is missing:\n" + "\n".join(missing))
    print(f"Source distribution contains all required files: {archives[0]}")


if __name__ == "__main__":
    main()

"""Verify that a release tag matches the version in pyproject.toml."""

from __future__ import annotations

import os
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def main() -> None:
    version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
    reference = os.environ.get("GITHUB_REF_NAME", "")
    if reference.startswith("v"):
        release_version = reference[1:]
        if release_version != version:
            raise SystemExit(
                f"Release tag {reference!r} does not match pyproject version {version!r}"
            )
        print(f"Release tag matches version {version}")
    else:
        print(f"Package version is {version}; no release tag to check")


if __name__ == "__main__":
    main()

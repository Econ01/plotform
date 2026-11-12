"""Render exact capsule geometry specimens for visual review."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

import teal_minimal as tm


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/capsule-geometry.png"))
    parser.add_argument("--preview", type=Path, default=Path("artifacts/capsule-geometry-preview.png"))
    parser.add_argument("--dpi", type=int, default=800)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.preview.parent.mkdir(parents=True, exist_ok=True)

    tm.apply_theme()
    fig = plt.figure(figsize=(12, 7.5))
    grid = fig.add_gridspec(2, 2, height_ratios=(0.8, 1.6))

    labels = fig.add_subplot(grid[0, :])
    labels.set(xlim=(0, 12), ylim=(0, 2))
    labels.axis("off")
    labels.set_title("Horizontal capsules · radius = height / 2")
    tm.add_pill(labels, 1.0, 1.0, "A")
    tm.add_pill(labels, 3.7, 1.0, "Water 48%", facecolor=tm.BASE_COLORS[1])
    tm.add_pill(labels, 8.4, 1.0, "Soft Drink 21%", facecolor=tm.BASE_COLORS[2])
    labels.text(6, 0.25, "Fixed height · circular single-character badge · optically centered text", ha="center", color=tm.MUTED)

    free = fig.add_subplot(grid[1, 0])
    both = fig.add_subplot(grid[1, 1])
    x = np.arange(4)
    values = np.array((2.5, 4.5, 3.5, 5.5))
    tm.rounded_bar(free, x, values, radius="full", ends="free")
    free.set_xticks(x, ("A", "B", "C", "D"))
    free.set_title("Semicircular free caps")
    free.set_ylabel("Value")

    tm.rounded_bar(both, x, values, radius="full", ends="both")
    both.set_xticks(x, ("A", "B", "C", "D"))
    both.set_title("Complete vertical capsules")

    fig.suptitle("Exact capsule geometry · straight segments + semicircles", x=0.02, ha="left")
    fig.savefig(args.output, dpi=args.dpi)
    fig.savefig(args.preview, dpi=150)
    plt.close(fig)
    print(f"Saved {args.output.resolve()} at {args.dpi} DPI")
    print(f"Saved {args.preview.resolve()}")


if __name__ == "__main__":
    main()

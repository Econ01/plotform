"""Run the same plot with or without Teal Minimal installed.

Run from the repository root with ``python -m examples.optional_theme``.
For reuse, copy theme_compat.py alongside your own script. If Teal Minimal is
unavailable, native Matplotlib bars, legends, and the current style are used.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import theme_compat as tm


def main():
    with tm.theme():
        x = np.arange(4)
        fig, ax = plt.subplots()
        tm.bar(x, [3, 5, 2, 4], ax=ax, label="Example")
        ax.set(title="Optional Teal Minimal", xlabel="Category", ylabel="Value")
        tm.legend(ax)
        output = Path("artifacts/optional-theme.png")
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=300)
        print(f"Saved {output.resolve()}")


if __name__ == "__main__":
    main()

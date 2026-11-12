"""A complete plotting example with no Plotform dependency."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main():
    x = np.arange(4)
    values = np.array([3, 5, 2, 4])

    fig, ax = plt.subplots()
    ax.bar(x, values, label="Example")
    ax.set(
        title="Native Matplotlib only",
        xlabel="Category",
        ylabel="Value",
        xticks=x,
        xticklabels=("A", "B", "C", "D"),
    )
    ax.legend()

    output = Path("artifacts/native-matplotlib.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300)
    print(f"Saved {output.resolve()}")


if __name__ == "__main__":
    main()

"""Render Matplotlib-default versus Teal Minimal comparison charts.

Final PNGs default to 800 DPI; contact-sheet previews stay lightweight.
Usage:
    python examples/showcase.py
    python examples/showcase.py --dpi 140 --output artifacts/showcase-check
    python examples/showcase.py --only 01-line 07-rounded-bars 20-pills
"""

from __future__ import annotations

import argparse
import gc
from collections.abc import Callable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import style
from PIL import Image, ImageDraw, ImageFont

import teal_minimal as tm

Chart = Callable[[], plt.Figure]
CHARTS: list[tuple[str, str, Chart]] = []


def chart(slug: str, title: str):
    def decorate(function: Chart) -> Chart:
        CHARTS.append((slug, title, function))
        return function

    return decorate


def using_theme() -> bool:
    return matplotlib.rcParams["font.sans-serif"][0] == tm.SANS_FONT


def palette(n_colors: int) -> list[str]:
    if using_theme():
        return tm.get_palette(n_colors)
    cycle = [entry["color"] for entry in matplotlib.rcParams["axes.prop_cycle"]]
    return [cycle[i % len(cycle)] for i in range(n_colors)]


def colormap(kind: str = "sequential") -> str:
    if using_theme():
        return tm.DIVERGING_CMAP if kind == "diverging" else tm.SCALAR_CMAP
    return "coolwarm" if kind == "diverging" else "viridis"


def add_legend(ax, **kwargs):
    if using_theme():
        return tm.pill_legend(ax, **kwargs)
    for key in ("styles", "outside", "backdrop", "backdrop_alpha", "backdrop_color", "backdrop_pad"):
        kwargs.pop(key, None)
    return ax.legend(**kwargs)


def add_colorbar(fig, ax, mappable, **kwargs):
    if using_theme():
        return tm.capsule_colorbar(fig, ax, mappable, **kwargs)
    return fig.colorbar(mappable, ax=ax, **kwargs)


def neutral(themed_color: str, default_color: str = "0.35") -> str:
    return themed_color if using_theme() else default_color


def finish(fig: plt.Figure, ax, title: str, xlabel: str = "", ylabel: str = ""):
    ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    return fig


@chart("01-line", "Multi-series lines")
def line_chart():
    x = np.linspace(0, 10, 200)
    fig, ax = plt.subplots()
    ax.plot(x, np.sin(x) + 0.15 * x, label="Baseline")
    ax.plot(x, np.cos(x) + 0.15 * x, label="Comparison")
    ax.plot(x, 0.55 * np.sin(1.7 * x) + 0.15 * x, label="Variant")
    add_legend(ax, ncols=3)
    return finish(fig, ax, "A restrained line hierarchy", "Time", "Signal")


@chart("02-time-series", "Time series")
def time_series_chart():
    rng = np.random.default_rng(12)
    dates = np.arange("2025-01-01", "2025-07-01", dtype="datetime64[D]")
    changes = rng.normal(0.15, 1.0, (dates.size, 2))
    values = 100 + np.cumsum(changes, axis=0)
    fig, ax = plt.subplots()
    ax.plot(dates, values[:, 0], label="Revenue")
    ax.plot(dates, values[:, 1], label="Cost")
    add_legend(ax, )
    fig.autofmt_xdate(rotation=0)
    return finish(fig, ax, "Dates stay quiet and readable", ylabel="Index")


@chart("03-scatter", "Scatter and bubbles")
def scatter_chart():
    rng = np.random.default_rng(3)
    fig, ax = plt.subplots()
    for i, label in enumerate(("Control", "Treatment")):
        x = rng.normal(i * 1.3, 0.65, 65)
        y = 0.7 * x + rng.normal(i * 0.5, 0.75, 65)
        size = rng.uniform(24, 170, x.size)
        ax.scatter(x, y, s=size, alpha=0.68, label=label)
    add_legend(ax, )
    return finish(fig, ax, "Soft markers without heavy outlines", "Exposure", "Response")


@chart("04-error-bars", "Errors and uncertainty")
def error_bar_chart():
    x = np.linspace(0, 8, 9)
    y = np.sin(x / 1.4) + 0.25 * x
    error = 0.16 + 0.03 * x
    fig, ax = plt.subplots()
    ax.fill_between(x, y - error, y + error, alpha=0.14, label="95% interval")
    ax.errorbar(x, y, yerr=error, fmt="o-", label="Estimate")
    add_legend(ax, styles={"95% interval": "soft"})
    return finish(fig, ax, "Uncertainty remains visible, not dominant", "Dose", "Effect")


@chart("05-grouped-bars", "Grouped bars")
def grouped_bar_chart():
    labels = ("North", "South", "East", "West")
    x = np.arange(len(labels))
    fig, ax = plt.subplots()
    for offset, values, name in (
        (-0.25, (4.2, 5.1, 3.8, 4.7), "2023"),
        (0.0, (5.0, 4.8, 4.5, 5.5), "2024"),
        (0.25, (5.8, 5.6, 5.1, 6.2), "2025"),
    ):
        ax.bar(x + offset, values, width=0.23, label=name)
    ax.set_xticks(x, labels)
    add_legend(ax, ncols=3)
    return finish(fig, ax, "Grouped bars with breathing room", ylabel="Score")


@chart("06-stacked-bars", "Stacked bars")
def stacked_bar_chart():
    labels = ("Q1", "Q2", "Q3", "Q4")
    x = np.arange(4)
    bottom = np.zeros(4)
    fig, ax = plt.subplots()
    for values, name in zip(((3, 4, 4, 5), (2, 3, 3, 3), (1, 1, 2, 2)), ("Core", "New", "Other")):
        ax.bar(x, values, bottom=bottom, width=0.58, label=name)
        bottom += values
    ax.set_xticks(x, labels)
    add_legend(ax, ncols=3)
    return finish(fig, ax, "Stacks inherit the same color cycle", ylabel="Total")


@chart("07-rounded-bars", "Rounded bars")
def rounded_bar_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
    x = np.arange(5)
    values = np.array((3.0, 5.0, -2.0, 4.0, -3.0))
    if using_theme():
        tm.rounded_bar(ax1, x - 0.18, values, width=0.32, radius="full", ends="free", label="Free end")
        tm.rounded_bar(ax1, x + 0.18, values, width=0.32, radius="full", ends="both", label="Both ends")
    else:
        ax1.bar(x - 0.18, values, width=0.32, label="Free end")
        ax1.bar(x + 0.18, values, width=0.32, label="Both ends")
    ax1.set_xticks(x, ("A", "B", "C", "D", "E"))
    ax1.axhline(0, color=neutral(tm.AXIS), linewidth=0.8)
    ax1.set_title("Full free caps and complete capsules")
    ax1.set_ylabel("Value")
    add_legend(ax1, ncols=2)

    y = np.arange(4)
    if using_theme():
        tm.rounded_barh(ax2, y, (5, 3, 4, 2), radius="full", color=palette(3)[2])
    else:
        ax2.barh(y, (5, 3, 4, 2), color=palette(3)[2])
    ax2.set_yticks(y, ("Alpha", "Beta", "Gamma", "Delta"))
    ax2.set_title("Horizontal full caps")
    ax2.grid(axis="x")
    ax2.grid(axis="y", visible=False)
    return fig


@chart("08-histogram", "Histograms")
def histogram_chart():
    rng = np.random.default_rng(19)
    fig, ax = plt.subplots()
    for mean, label in ((0.0, "A"), (1.0, "B"), (2.0, "C")):
        ax.hist(rng.normal(mean, 0.8, 600), bins=28, alpha=0.55, label=label)
    add_legend(ax, )
    return finish(fig, ax, "Overlapping distributions", "Value", "Frequency")


@chart("09-boxplot", "Boxplots")
def boxplot_chart():
    rng = np.random.default_rng(20)
    data = [rng.normal(i * 0.6, 0.65 + i * 0.1, 150) for i in range(4)]
    fig, ax = plt.subplots()
    if using_theme():
        result = ax.boxplot(data, patch_artist=True)
        for patch, color in zip(result["boxes"], palette(4)):
            patch.set_facecolor(color)
            patch.set_alpha(0.30)
    else:
        ax.boxplot(data)
    ax.set_xticklabels(("Alpha", "Beta", "Gamma", "Delta"))
    return finish(fig, ax, "Distribution summaries with light boxes", ylabel="Measurement")


@chart("10-violin", "Violin plots")
def violin_chart():
    rng = np.random.default_rng(21)
    data = [rng.normal(i * 0.5, 0.55 + i * 0.08, 250) for i in range(4)]
    fig, ax = plt.subplots()
    result = ax.violinplot(data, showmedians=True, showextrema=False)
    if using_theme():
        for body, color in zip(result["bodies"], palette(4)):
            body.set_facecolor(color)
            body.set_edgecolor(color)
            body.set_alpha(0.42)
        result["cmedians"].set_color(tm.INK)
        result["cmedians"].set_linewidth(1.5)
    ax.set_xticks((1, 2, 3, 4), ("Alpha", "Beta", "Gamma", "Delta"))
    return finish(fig, ax, "Violins use shape instead of heavy borders", ylabel="Measurement")


@chart("11-stacked-area", "Stacked area")
def stacked_area_chart():
    x = np.arange(12)
    fig, ax = plt.subplots()
    ax.stackplot(
        x,
        2 + np.sin(x / 2),
        1.5 + np.cos(x / 3),
        1 + 0.2 * x,
        labels=("Organic", "Referral", "Paid"),
        alpha=0.85 if using_theme() else 1.0,
    )
    add_legend(ax, ncols=3, loc="upper left", outside=True)
    return finish(fig, ax, "Continuous composition over time", "Month", "Visits")


@chart("12-heatmap", "Heatmap")
def heatmap_chart():
    rng = np.random.default_rng(22)
    values = rng.normal(size=(9, 12)).cumsum(axis=1)
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    image = ax.imshow(values, cmap=colormap("diverging"), aspect="auto")
    ax.grid(False)
    ax.set_xticks(range(12), [f"M{i}" for i in range(1, 13)])
    ax.set_yticks(range(9), [f"Group {i}" for i in range(1, 10)])
    add_colorbar(fig, ax, image, pad=0.02, shrink=0.85)
    ax.set_title("A balanced diverging scale")
    return fig


@chart("13-contour", "Contours")
def contour_chart():
    x = np.linspace(-3, 3, 150)
    y = np.linspace(-3, 3, 150)
    xx, yy = np.meshgrid(x, y)
    zz = np.exp(-(xx**2 + yy**2) / 3) - 0.6 * np.exp(-((xx - 1.2) ** 2 + (yy + 0.8) ** 2))
    fig, ax = plt.subplots()
    filled = ax.contourf(xx, yy, zz, levels=18, cmap=colormap("diverging"))
    ax.contour(xx, yy, zz, levels=9, colors="white", linewidths=0.55, alpha=0.7)
    ax.grid(False)
    add_colorbar(fig, ax, filled, pad=0.02)
    return finish(fig, ax, "Filled and line contours", "x", "y")


@chart("14-donut", "Donut chart")
def donut_chart():
    fig, ax = plt.subplots(figsize=(7, 5.5))
    values = (44, 27, 18, 11)
    ax.pie(
        values,
        labels=("Core", "Adjacent", "Experimental", "Other"),
        colors=palette(4),
        startangle=90,
        counterclock=False,
        wedgeprops={"width": 0.36, "edgecolor": "white", "linewidth": 2},
        textprops={"color": neutral(tm.MUTED)},
    )
    ax.text(0, 0, "100%", ha="center", va="center", fontsize=22, color=neutral(tm.INK, "black"))
    ax.set_title("A donut used sparingly")
    return fig


@chart("15-polar", "Polar plot")
def polar_chart():
    theta = np.linspace(0, 2 * np.pi, 300)
    radius = 1 + 0.25 * np.sin(5 * theta) + 0.1 * np.cos(9 * theta)
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.plot(theta, radius)
    ax.fill(theta, radius, alpha=0.12)
    ax.set_rticks((0.5, 1.0, 1.5))
    ax.grid(color=neutral(tm.GRID, "#b0b0b0"))
    ax.set_title("Polar coordinates retain the theme", pad=20)
    return fig


@chart("16-log-scale", "Logarithmic scale")
def log_chart():
    x = np.linspace(1, 100, 200)
    fig, ax = plt.subplots()
    ax.semilogy(x, np.exp(x / 25), label="Exponential")
    ax.semilogy(x, x**2.2, label="Power law")
    ax.grid(True, which="major")
    add_legend(ax, )
    return finish(fig, ax, "Major gridlines only on a log scale", "x", "Magnitude")


@chart("17-stem", "Stem plot")
def stem_chart():
    x = np.arange(18)
    values = np.sin(x / 2) + 0.15 * x
    fig, ax = plt.subplots()
    marker, stems, baseline = ax.stem(x, values, label="Signal")
    if using_theme():
        plt.setp(stems, linewidth=1.3, color=tm.PRIMARY)
        plt.setp(marker, markerfacecolor=tm.PRIMARY)
        plt.setp(baseline, color=tm.CORAL, linewidth=1.4)
    return finish(fig, ax, "Discrete samples with light stems", "Sample", "Amplitude")


@chart("18-quiver", "Quiver")
def quiver_chart():
    x = np.linspace(-2, 2, 13)
    y = np.linspace(-2, 2, 13)
    xx, yy = np.meshgrid(x, y)
    fig, ax = plt.subplots()
    options = {"color": tm.PRIMARY} if using_theme() else {}
    ax.quiver(xx, yy, -yy, xx, angles="xy", scale_units="xy", scale=7, width=0.004, **options)
    ax.set_aspect("equal")
    return finish(fig, ax, "A vector field in one quiet color", "x", "y")


@chart("19-streamplot", "Streamplot")
def streamplot_chart():
    x = np.linspace(-2, 2, 80)
    y = np.linspace(-2, 2, 80)
    xx, yy = np.meshgrid(x, y)
    speed = np.hypot(xx, yy)
    fig, ax = plt.subplots()
    stream = ax.streamplot(xx, yy, -yy, xx, color=speed, cmap=colormap(), density=1.2, linewidth=1.2)
    add_colorbar(fig, ax, stream.lines, pad=0.02)
    return finish(fig, ax, "Flow intensity through the sequential map", "x", "y")


@chart("20-pills", "Pills and annotations")
def pills_chart():
    x = np.linspace(0, 10, 200)
    y = np.sin(x) + 0.12 * x
    fig, ax = plt.subplots()
    ax.plot(x, y)
    peak = int(np.argmax(y))
    ax.annotate(
        "Peak",
        (x[peak], y[peak]),
        xytext=(x[peak] - 1.7, y[peak] + 0.6),
        arrowprops={"arrowstyle": "-", "color": neutral(tm.MUTED), "connectionstyle": "arc3,rad=0.15"},
        color=neutral(tm.MUTED),
    )
    if using_theme():
        tm.add_pill(ax, 0.20, 0.86, "ROND 100", transform=ax.transAxes)
        tm.add_pill(ax, 0.20, 0.56, "Exact capsule", transform=ax.transAxes, facecolor=palette(2)[1])
    else:
        for vertical, text, color in ((0.86, "Default box", palette(1)[0]), (0.56, "Rounded corners", palette(2)[1])):
            ax.text(
                0.20, vertical, text, transform=ax.transAxes,
                ha="center", va="center", color="white",
                bbox={"boxstyle": "round,pad=0.55", "facecolor": color, "edgecolor": "none"},
            )
    ax.text(
        0.98,
        0.06,
        "font = 'Teal Minimal Mono'" if using_theme() else "font = 'DejaVu Sans Mono'",
        transform=ax.transAxes,
        ha="right",
        family=tm.MONO_FONT if using_theme() else "monospace",
        fontsize=9,
        color=neutral(tm.MUTED),
    )
    return finish(fig, ax, "Rounded annotations without visual clutter", "Time", "Signal")


@chart("21-subplots", "Small multiples")
def subplots_chart():
    rng = np.random.default_rng(24)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
    x = np.linspace(0, 5, 60)
    axes[0, 0].plot(x, np.sin(x))
    axes[0, 0].set_title("Line")
    axes[0, 1].scatter(rng.normal(size=70), rng.normal(size=70), alpha=0.65)
    axes[0, 1].set_title("Scatter")
    axes[1, 0].hist(rng.normal(size=500), bins=22)
    axes[1, 0].set_title("Histogram")
    axes[1, 1].bar(np.arange(4), (2, 4, 3, 5))
    axes[1, 1].set_title("Bars")
    fig.suptitle("One system across small multiples", x=0.02, ha="left")
    return fig


@chart("22-extended-palette", "Extended palette")
def palette_chart():
    colors = palette(16)
    fig, ax = plt.subplots(figsize=(8, 7))
    for i, color in enumerate(colors):
        ax.hlines(i, 0, 1, color=color, linewidth=8)
        ax.text(
            1.04, i, color, va="center",
            family=tm.MONO_FONT if using_theme() else "monospace",
            fontsize=9, color=neutral(tm.MUTED),
        )
    ax.set_xlim(0, 1.35)
    ax.set_ylim(-1, len(colors))
    ax.set_yticks(range(len(colors)), [f"{i + 1:02d}" for i in range(len(colors))])
    ax.set_xticks([])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Eight curated colors, then deterministic extension")
    return fig


@chart("23-3d-line", "3D line")
def three_d_line_chart():
    t = np.linspace(0, 8 * np.pi, 400)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection="3d")
    if using_theme():
        tm.style_3d(ax)
    ax.plot(np.cos(t), np.sin(t), t / (4 * np.pi))
    ax.set_title("3D curves with transparent panes", pad=14)
    ax.set_xlabel("x", labelpad=8)
    ax.set_ylabel("y", labelpad=8)
    ax.set_zlabel("z", labelpad=8)
    return fig


@chart("24-3d-scatter", "3D scatter")
def three_d_scatter_chart():
    rng = np.random.default_rng(25)
    z = rng.uniform(0, 1, 180)
    angle = 8 * np.pi * z + rng.normal(0, 0.15, z.size)
    radius = 0.6 + 0.25 * z + rng.normal(0, 0.05, z.size)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection="3d")
    if using_theme():
        tm.style_3d(ax)
    points = ax.scatter(radius * np.cos(angle), radius * np.sin(angle), z, c=z, s=22, alpha=1.0, cmap=colormap(), depthshade=False)
    ax.set_title("3D scatter with sequential depth", pad=14)
    add_colorbar(fig, ax, points, shrink=0.65, pad=0.08)
    return fig


@chart("25-3d-surface", "3D surface")
def three_d_surface_chart():
    x = np.linspace(-3, 3, 80)
    y = np.linspace(-3, 3, 80)
    xx, yy = np.meshgrid(x, y)
    zz = np.sin(np.hypot(xx, yy)) * np.exp(-0.12 * (xx**2 + yy**2))
    fig = plt.figure(figsize=(8.5, 6))
    ax = fig.add_subplot(projection="3d")
    if using_theme():
        tm.style_3d(ax, elev=30)
    surface = ax.plot_surface(xx, yy, zz, cmap=colormap("diverging"), linewidth=0, antialiased=False, rcount=60, ccount=60)
    ax.set_title("A surface without heavy panes", pad=14)
    add_colorbar(fig, ax, surface, shrink=0.65, pad=0.08)
    return fig


@chart("26-3d-wireframe", "3D wireframe")
def three_d_wireframe_chart():
    x = np.linspace(-3, 3, 35)
    y = np.linspace(-3, 3, 35)
    xx, yy = np.meshgrid(x, y)
    zz = np.cos(xx) * np.sin(yy)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection="3d")
    if using_theme():
        tm.style_3d(ax, elev=30)
    options = {"color": tm.PRIMARY} if using_theme() else {}
    ax.plot_wireframe(xx, yy, zz, linewidth=0.75, rstride=2, cstride=2, **options)
    ax.set_title("A light 3D wireframe", pad=14)
    return fig


@chart("27-3d-bars", "3D bars")
def three_d_bar_chart():
    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(projection="3d")
    if using_theme():
        tm.style_3d(ax, elev=28, azim=-50)
    x = np.arange(5)
    y = np.arange(4)
    xx, yy = np.meshgrid(x, y)
    heights = (1 + np.sin(xx) + np.cos(yy)).ravel() + 1.2
    colors = [palette(8)[int(i) % 8] for i in xx.ravel()]
    ax.bar3d(xx.ravel(), yy.ravel(), 0, 0.58, 0.58, heights, color=colors, shade=True)
    ax.set_title("3D bars with shaded thematic faces", pad=14)
    ax.set_xticks(x)
    ax.set_yticks(y)
    return fig


def make_contact_sheet(records, output: Path):
    columns = 4
    cell_width = 820
    title_height = 48
    gap = 24
    margin = 36
    header = 92
    thumbnails = []
    for title, path in records:
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((cell_width, 10000), Image.Resampling.LANCZOS)
            thumbnails.append((title, image))

    row_heights = []
    for start in range(0, len(thumbnails), columns):
        row = thumbnails[start:start + columns]
        row_heights.append(max(image.height for _, image in row) + title_height + gap)
    width = 2 * margin + columns * cell_width + (columns - 1) * gap
    height = header + sum(row_heights) + margin
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    font_path = str(tm.font_paths()[tm.SANS_FONT])
    header_font = ImageFont.truetype(font_path, 42)
    title_font = ImageFont.truetype(font_path, 24)
    draw.text((margin, 22), "Default vs Teal Minimal · visual showcase", font=header_font, fill=tm.INK)

    y = header
    for row_index, start in enumerate(range(0, len(thumbnails), columns)):
        row = thumbnails[start:start + columns]
        for column, (title, image) in enumerate(row):
            x = margin + column * (cell_width + gap)
            bounds = draw.textbbox((0, 0), title, font=title_font)
            text_width = bounds[2] - bounds[0]
            draw.text((x + (cell_width - text_width) / 2, y + 4), title, font=title_font, fill=tm.INK)
            sheet.paste(image, (x + (cell_width - image.width) // 2, y + title_height))
        y += row_heights[row_index]
    sheet.save(output, dpi=(130, 130))
    for _, image in thumbnails:
        image.close()


def render_figure(build, themed: bool, dpi: int, vector_dir: Path, slug: str, figsize=None):
    context = tm.theme() if themed else style.context("default")
    with context:
        fig = build()
        if figsize is not None:
            fig.set_size_inches(figsize)
        fig.set_dpi(dpi)
        fig.canvas.draw()
        image = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())).convert("RGB")
        if themed and slug in {"01-line", "07-rounded-bars", "20-pills", "25-3d-surface"}:
            fig.savefig(vector_dir / f"{slug}.pdf")
            fig.savefig(vector_dir / f"{slug}.svg")
        plt.close(fig)
    return image


def compose_comparison(default_image, themed_image, dpi: int):
    if default_image.size != themed_image.size:
        raise RuntimeError(f"Comparison sizes differ: {default_image.size} != {themed_image.size}")
    width, height = default_image.size
    gap = round(dpi * 0.06)
    header = round(dpi * 0.34)
    comparison = Image.new("RGB", (2 * width + gap, height + header), "white")
    comparison.paste(default_image, (0, header))
    comparison.paste(themed_image, (width + gap, header))

    draw = ImageDraw.Draw(comparison)
    font = ImageFont.truetype(
        str(tm.font_paths()[tm.SANS_FONT]), size=round(14 * dpi / 72)
    )
    for center, label in ((width / 2, "Matplotlib default"), (width + gap + width / 2, "Teal Minimal")):
        bounds = draw.textbbox((0, 0), label, font=font)
        text_width = bounds[2] - bounds[0]
        text_height = bounds[3] - bounds[1]
        draw.text(
            (center - text_width / 2 - bounds[0], (header - text_height) / 2 - bounds[1]),
            label,
            font=font,
            fill=tm.INK,
        )
    return comparison


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/showcase"))
    parser.add_argument("--dpi", type=int, default=800, help="Final comparison PNG resolution")
    parser.add_argument("--preview-width", type=int, default=1800, help="Contact-sheet preview width in pixels")
    parser.add_argument("--only", nargs="+", help="Optional chart slugs to render")
    args = parser.parse_args()
    if args.dpi < 1 or args.preview_width < 100:
        parser.error("dpi must be positive and preview-width must be at least 100")

    comparison_dir = args.output / "comparisons"
    preview_dir = args.output / "previews"
    vector_dir = args.output / "vector"
    for directory in (comparison_dir, preview_dir, vector_dir):
        directory.mkdir(parents=True, exist_ok=True)

    selected = [entry for entry in CHARTS if not args.only or entry[0] in args.only]
    if not selected:
        parser.error("No charts matched --only")

    records = []
    for slug, title, build in selected:
        print(f"Rendering {slug} at {args.dpi} DPI...", flush=True)
        themed_image = render_figure(build, True, args.dpi, vector_dir, slug)
        figsize = (themed_image.width / args.dpi, themed_image.height / args.dpi)
        default_image = render_figure(build, False, args.dpi, vector_dir, slug, figsize=figsize)
        comparison = compose_comparison(default_image, themed_image, args.dpi)
        default_image.close()
        themed_image.close()

        comparison.save(comparison_dir / f"{slug}.png", dpi=(args.dpi, args.dpi))
        preview = comparison.copy()
        preview.thumbnail((args.preview_width, 10000), Image.Resampling.LANCZOS)
        preview_path = preview_dir / f"{slug}.png"
        preview.save(preview_path)
        records.append((title, preview_path))
        preview.close()
        comparison.close()
        gc.collect()

    with tm.theme():
        make_contact_sheet(records, args.output / "00-contact-sheet.png")
    print(f"Rendered {len(records)} comparisons to {comparison_dir.resolve()}")


if __name__ == "__main__":
    main()

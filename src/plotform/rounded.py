"""Exact capsule pills, squircles, and circularly rounded bar helpers."""

from __future__ import annotations

import numpy as np
from matplotlib.container import BarContainer
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.transforms import IdentityTransform

from .palette import PRIMARY, WHITE

# Cubic Bezier constant for a quarter circle.
_CIRCLE_KAPPA = 0.5522847498307936


def squircle_path(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    exponent: float = 4.0,
    points: int = 256,
) -> Path:
    """Return a closed superellipse path for rounded panels, not capsules."""
    if width < 0 or height < 0:
        raise ValueError("width and height must be nonnegative")
    if exponent < 2:
        raise ValueError("exponent must be at least 2")
    if points < 32:
        raise ValueError("points must be at least 32")

    theta = np.linspace(0.0, 2.0 * np.pi, points, endpoint=False)
    power = 2.0 / exponent
    cos = np.cos(theta)
    sin = np.sin(theta)
    px = x + width / 2 + width / 2 * np.sign(cos) * np.abs(cos) ** power
    py = y + height / 2 + height / 2 * np.sign(sin) * np.abs(sin) ** power
    vertices = np.column_stack((px, py))
    vertices = np.vstack((vertices, vertices[0]))
    codes = [Path.MOVETO] + [Path.LINETO] * (points - 1) + [Path.CLOSEPOLY]
    return Path(vertices, codes)


def _rectangle_path(t0, t1, baseline, end):
    vertices = [(t0, baseline), (t0, end), (t1, end), (t1, baseline), (t0, baseline)]
    codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
    return Path(vertices, codes)


def _vertical_rounded_path(t0, t1, baseline, end, radius, ends):
    """Build a bar from straight lines and exact circular Bezier arcs.

    With a full-width radius and ``ends='both'``, this is a stadium: two
    semicircles joined by straight sides. Every arc control point uses the
    standard cubic quarter-circle construction.
    """
    if radius <= 1e-9 or np.isclose(baseline, end) or np.isclose(t0, t1):
        return _rectangle_path(t0, t1, baseline, end)

    sign = 1.0 if end >= baseline else -1.0
    k = _CIRCLE_KAPPA
    start = (t0, baseline + sign * radius) if ends == "both" else (t0, baseline)
    vertices = [start]
    codes = [Path.MOVETO]

    def line(point):
        vertices.append(point)
        codes.append(Path.LINETO)

    def curve(control1, control2, point):
        vertices.extend((control1, control2, point))
        codes.extend((Path.CURVE4, Path.CURVE4, Path.CURVE4))

    # Left straight side, then the free-end left quarter circle.
    top_center_y = end - sign * radius
    line((t0, top_center_y))
    curve(
        (t0, top_center_y + sign * k * radius),
        (t0 + (1 - k) * radius, end),
        (t0 + radius, end),
    )

    # Straight free edge (zero length for a full semicircle), then the right arc.
    line((t1 - radius, end))
    curve(
        (t1 - (1 - k) * radius, end),
        (t1, top_center_y + sign * k * radius),
        (t1, top_center_y),
    )

    if ends == "both":
        bottom_center_y = baseline + sign * radius
        line((t1, bottom_center_y))
        curve(
            (t1, bottom_center_y - sign * k * radius),
            (t1 - (1 - k) * radius, baseline),
            (t1 - radius, baseline),
        )
        line((t0 + radius, baseline))
        curve(
            (t0 + (1 - k) * radius, baseline),
            (t0, bottom_center_y - sign * k * radius),
            (t0, bottom_center_y),
        )
    else:
        line((t1, baseline))

    vertices.append(start)
    codes.append(Path.CLOSEPOLY)
    return Path(vertices, codes)


def capsule_path(x: float, y: float, width: float, height: float) -> Path:
    """Return an exact capsule/stadium outline.

    The cap radius is exactly half the smaller dimension. Horizontal capsules
    have semicircular left/right ends; vertical capsules have semicircular
    top/bottom ends. Straight segments join the arcs at matching tangents.
    """
    if width < 0 or height < 0:
        raise ValueError("width and height must be nonnegative")
    if np.isclose(width, 0) or np.isclose(height, 0):
        return _rectangle_path(x, x + width, y, y + height)
    radius = min(width, height) / 2
    return _vertical_rounded_path(x, x + width, y, y + height, radius, "both")


class SquircleBox:
    """A Matplotlib annotation box style backed by a superellipse path."""

    def __init__(self, pad: float = 0.55, exponent: float = 4.0, points: int = 256):
        self.pad = pad
        self.exponent = exponent
        self.points = points

    def __call__(self, x0, y0, width, height, mutation_size):
        pad = mutation_size * self.pad
        return squircle_path(
            x0 - pad,
            y0 - pad,
            width + 2 * pad,
            height + 2 * pad,
            exponent=self.exponent,
            points=self.points,
        )


class CapsuleBox:
    """An exact capsule annotation box with UI-style text metrics.

    ``height`` is a multiple of the font mutation size. ``None`` derives the
    height from the text instead. Single-character labels expand to circles
    rather than becoming narrow vertical ovals.
    """

    def __init__(
        self,
        pad: float = 0.65,
        height: float | None = 1.9,
        min_aspect: float = 1.0,
        circle_threshold: float = 1.2,
    ):
        if pad < 0:
            raise ValueError("pad must be nonnegative")
        if height is not None and height <= 0:
            raise ValueError("height must be positive or None")
        if min_aspect <= 0 or circle_threshold < 1:
            raise ValueError("min_aspect must be positive and circle_threshold at least 1")
        self.pad = pad
        self.height = height
        self.min_aspect = min_aspect
        self.circle_threshold = circle_threshold

    def __call__(self, x0, y0, width, height, mutation_size):
        pad = mutation_size * self.pad
        center_x = x0 + width / 2
        center_y = y0 + height / 2
        capsule_width = width + 2 * pad
        capsule_height = (
            mutation_size * self.height if self.height is not None else height + 2 * pad
        )
        if capsule_width <= self.circle_threshold * capsule_height:
            capsule_width = capsule_height
        else:
            capsule_width = max(capsule_width, self.min_aspect * capsule_height)
        return capsule_path(
            center_x - capsule_width / 2,
            center_y - capsule_height / 2,
            capsule_width,
            capsule_height,
        )


def add_squircle(
    ax,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    exponent: float = 4.0,
    transform=None,
    **kwargs,
) -> PathPatch:
    """Add a superellipse panel in data coordinates by default."""
    patch = PathPatch(
        squircle_path(x, y, width, height, exponent=exponent),
        transform=transform or ax.transData,
        **kwargs,
    )
    ax.add_patch(patch)
    return patch


def add_pill(
    ax,
    x: float,
    y: float,
    text: str,
    *,
    transform=None,
    facecolor: str = PRIMARY,
    textcolor: str = WHITE,
    edgecolor: str = "none",
    pad: float = 0.65,
    height: float | None = 1.9,
    fontsize: float | None = None,
    **kwargs,
):
    """Add centered text in an exact capsule.

    Coordinates use data space by default. Pass ``transform=ax.transAxes`` for
    axes-fraction coordinates. ``height`` is relative to the font size; use
    ``height=None`` to derive it from the text metrics instead.
    """
    bbox = {
        "boxstyle": CapsuleBox(pad=pad, height=height),
        "facecolor": facecolor,
        "edgecolor": edgecolor,
        "linewidth": kwargs.pop("linewidth", 0.8),
    }
    return ax.annotate(
        text,
        (x, y),
        transform=transform or ax.transData,
        ha="center",
        va="center",
        color=textcolor,
        fontsize=fontsize,
        bbox=bbox,
        **kwargs,
    )


def _data_rectangle(center, length, thickness, baseline, orientation):
    t0 = center - thickness / 2
    t1 = center + thickness / 2
    end = baseline + length
    vertices = np.array([(t0, baseline), (t0, end), (t1, end), (t1, baseline), (t0, baseline)])
    if orientation == "horizontal":
        vertices = vertices[:, ::-1]
    return Path(vertices, [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])


class RoundedBarPatch(PathPatch):
    """A circularly rounded bar recalculated in display space at draw time."""

    def __init__(
        self,
        center,
        length,
        thickness,
        baseline,
        *,
        radius,
        ends,
        orientation,
        **kwargs,
    ):
        self.center = float(center)
        self.length = float(length)
        self.thickness = float(thickness)
        self.baseline = float(baseline)
        self.radius = radius
        self.ends = ends
        self.orientation = orientation
        self.strict_full = False
        self.data_path = _data_rectangle(
            self.center, self.length, self.thickness, self.baseline, self.orientation
        )
        super().__init__(self.data_path, transform=IdentityTransform(), **kwargs)

    def get_path(self):
        ax = getattr(self, "axes", None)
        if ax is None:
            return self.data_path

        if self.orientation == "vertical":
            corners = np.array(
                [
                    (self.center - self.thickness / 2, self.baseline),
                    (self.center + self.thickness / 2, self.baseline),
                    (self.center, self.baseline + self.length),
                    (self.center, self.baseline),
                    (self.center + 1, self.baseline),
                ]
            )
        else:
            corners = np.array(
                [
                    (self.baseline, self.center - self.thickness / 2),
                    (self.baseline, self.center + self.thickness / 2),
                    (self.baseline + self.length, self.center),
                    (self.baseline, self.center),
                    (self.baseline, self.center + 1),
                ]
            )
        pixels = ax.transData.transform(corners)
        if not np.isfinite(pixels).all():
            return self.data_path

        if self.orientation == "vertical":
            t0, t1 = sorted((pixels[0, 0], pixels[1, 0]))
            baseline, end = pixels[0, 1], pixels[2, 1]
            unit_scale = abs(pixels[4, 0] - pixels[3, 0])
        else:
            t0, t1 = sorted((pixels[0, 1], pixels[1, 1]))
            baseline, end = pixels[0, 0], pixels[2, 0]
            unit_scale = abs(pixels[4, 1] - pixels[3, 1])

        thickness = t1 - t0
        length = abs(end - baseline)
        if length <= 1e-9 or thickness <= 1e-9:
            path = _rectangle_path(t0, t1, baseline, end)
            return (
                Path(path.vertices[:, ::-1], path.codes)
                if self.orientation == "horizontal"
                else path
            )

        length_limit = length if self.ends == "free" else length / 2
        full_radius = thickness / 2
        if self.radius in {"full", "fit"}:
            if self.radius == "full" and self.strict_full and full_radius > length_limit + 1e-6:
                requirement = (
                    "bar length >= bar thickness"
                    if self.ends == "both"
                    else "bar length >= half the bar thickness"
                )
                raise ValueError(
                    f"An exact full capsule requires {requirement} in display units; "
                    "use radius='fit' to clamp short bars instead."
                )
            radius = full_radius if self.radius == "full" else min(full_radius, length_limit)
        else:
            radius = min(float(self.radius) * unit_scale, full_radius, length_limit)

        path = _vertical_rounded_path(t0, t1, baseline, end, radius, self.ends)
        if self.orientation == "horizontal":
            path = Path(path.vertices[:, ::-1], path.codes)
        return path


def _validate_bar_options(radius, ends):
    if isinstance(radius, str):
        if radius not in {"full", "fit"}:
            raise ValueError("radius must be 'full', 'fit', or a nonnegative number")
    else:
        value = float(radius)
        if not np.isfinite(value) or value < 0:
            raise ValueError("radius must be 'full', 'fit', or a nonnegative number")
    if ends not in {"free", "both"}:
        raise ValueError("ends must be 'free' or 'both'")


def _rounded_bars(
    ax,
    positions,
    lengths,
    *,
    thickness,
    baseline,
    radius,
    ends,
    orientation,
    color,
    label,
    **kwargs,
):
    _validate_bar_options(radius, ends)
    positions, lengths, baseline, thickness = np.broadcast_arrays(
        np.asarray(positions, dtype=float),
        np.asarray(lengths, dtype=float),
        np.asarray(baseline, dtype=float),
        np.asarray(thickness, dtype=float),
    )
    if np.any(thickness < 0):
        raise ValueError("bar thickness must be nonnegative")

    if color is not None and "facecolor" in kwargs:
        raise TypeError("pass either color or facecolor, not both")
    facecolor = color if color is not None else kwargs.pop("facecolor", None)
    if facecolor is None:
        facecolor = ax._get_patches_for_fill.get_next_color()

    if positions.size == 0:
        container = BarContainer([], datavalues=np.array([]), orientation=orientation, label=label)
        ax.add_container(container)
        return container

    patches = []
    for position, length, base, wide in zip(
        positions.ravel(), lengths.ravel(), baseline.ravel(), thickness.ravel(), strict=True
    ):
        patch = RoundedBarPatch(
            position,
            length,
            wide,
            base,
            radius=radius,
            ends=ends,
            orientation=orientation,
            facecolor=facecolor,
            **kwargs,
        )
        ax.add_patch(patch)
        patches.append(patch)

    container = BarContainer(
        patches,
        datavalues=lengths.ravel(),
        orientation=orientation,
        label=label,
    )
    ax.add_container(container)
    vertices = np.vstack([patch.data_path.vertices for patch in patches])
    ax.update_datalim(vertices)
    ax.autoscale_view()
    for patch in patches:
        patch.strict_full = True
    return container


def rounded_bar(
    ax,
    x,
    height,
    width=0.8,
    *,
    bottom=0.0,
    radius="full",
    ends="free",
    color=None,
    label=None,
    **kwargs,
):
    """Draw vertical bars with circular caps.

    ``radius='full'`` creates an exact semicircular free cap and requires enough
    display length. ``radius='fit'`` clamps short bars. Numeric radii produce
    circular rounded corners. ``ends='both'`` also rounds the baseline.
    """
    return _rounded_bars(
        ax,
        x,
        height,
        thickness=width,
        baseline=bottom,
        radius=radius,
        ends=ends,
        orientation="vertical",
        color=color,
        label=label,
        **kwargs,
    )


def rounded_barh(
    ax,
    y,
    width,
    height=0.8,
    *,
    left=0.0,
    radius="full",
    ends="free",
    color=None,
    label=None,
    **kwargs,
):
    """Draw horizontal bars with the same options as ``rounded_bar``."""
    return _rounded_bars(
        ax,
        y,
        width,
        thickness=height,
        baseline=left,
        radius=radius,
        ends=ends,
        orientation="horizontal",
        color=color,
        label=label,
        **kwargs,
    )


__all__ = [
    "CapsuleBox",
    "RoundedBarPatch",
    "SquircleBox",
    "add_pill",
    "add_squircle",
    "capsule_path",
    "rounded_bar",
    "rounded_barh",
    "squircle_path",
]

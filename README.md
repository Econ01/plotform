# Teal Minimal

A reusable Matplotlib theme built around pure white, **#008080 teal**, quiet
neutral decoration, Google-derived typography, and optional rounded chart
helpers. It works with ordinary Matplotlib code and with libraries that use
Matplotlib's `rcParams`.

## Quick start

Create an environment and install this directory in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

For normal use, the development extras are optional:

```bash
python -m pip install /path/to/matplotlib
```

Apply the theme before creating figures:

```python
import matplotlib.pyplot as plt
import teal_minimal as tm

tm.apply_theme()

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [2, 4, 3], label="Example")
ax.set(title="A minimal teal chart", xlabel="Time", ylabel="Signal")
tm.legend(ax)  # Optional: solid pill labels with adaptive text contrast.

fig.savefig("chart.png", dpi=800)
fig.savefig("chart.pdf")
```

`apply_theme()` resets Matplotlib's style to its defaults before applying Teal
Minimal. It changes process-global settings, so call it once during script or
application startup, not inside every plotting loop. Axes, labels, and ticks
are black by default while gridlines remain light. To restore the earlier
muted-gray axes and tick labels:

```python
tm.apply_theme(gray_decorations=True)
```

## Native-style helpers and optional fallback

The public helper names mirror familiar Matplotlib functions:

```python
tm.legend(ax)
tm.bar(x, height, ax=ax)
tm.barh(y, width, ax=ax)
tm.colorbar(image, ax=ax)
tm.annotate("Note", (0.5, 0.5), ax=ax)
```

`legend()` uses the current axes when `ax` is omitted; `colorbar()` uses the
current figure and axes. The older descriptive names (`pill_legend`,
`rounded_bar`, `rounded_barh`, `capsule_colorbar`, and `add_pill`) remain
available as aliases.

### Sharing code without installing the theme

Copy the root-level **`theme_compat.py`** file into your project and import it
with the same alias:

```python
import theme_compat as tm

with tm.theme():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [2, 4, 3], label="Example")
    tm.legend(ax)
    fig.savefig("plot.png")
```

“Compat” is short for **compatibility**. The module provides one API with two
implementations:

- If Teal Minimal is installed, its themed helpers are used.
- If it is missing, native Matplotlib helpers are used and the current style is
  left untouched.
- `tm.theme(enabled=False)` also preserves someone else's existing theme.

Use `plt.style.use("default")` yourself only when you specifically want
Matplotlib's default rather than the caller's current style. The compatibility
module catches only `ImportError`; genuine errors inside an installed theme are
not silently hidden. When copying the compatibility file, keep it alongside the
script or notebook that imports it so Python can find it.

Run the included example from the repository root:

```bash
python -m examples.optional_theme
```

## Fonts

The package registers its bundled fonts directly with Matplotlib. No operating
system installation or Matplotlib cache deletion is needed.

- **Teal Minimal Sans** is derived from Google Sans Flex with **roundness
  `ROND=100`**. Weight stays at the source default (400); the theme does not
  override font weight.
- **Teal Minimal Mono** is derived from Google Sans Code at its default weight.
- DejaVu fonts provide fallbacks for mathematical notation and missing glyphs.

Static derived instances avoid inconsistent variable-font support between
renderers. Font licenses and upstream attribution are included under
`src/teal_minimal/assets/fonts/`.

## Colors

The curated categorical cycle is:

| Order | Color | Hex |
| --- | --- | --- |
| 1 | Teal | `#008080` |
| 2 | Amber | `#E69F00` |
| 3 | Blue | `#0072B2` |
| 4 | Coral/vermillion | `#D55E00` |
| 5 | Purple | `#6A51A3` |
| 6 | Green | `#4C9A2A` |
| 7 | Rose | `#CC79A7` |
| 8 | Dark slate | `#4B5563` |

Use more colors without immediately repeating the first eight:

```python
tm.apply_theme(n_colors=14)       # Set a 14-color default cycle.
colors = tm.get_palette(14)       # Or retrieve them for manual use.
```

Extension is deterministic. Beyond roughly 8–12 categories, add direct labels,
markers, line styles, or small multiples; color alone cannot remain reliably
distinguishable for an unlimited number of categories.

Three registered continuous colormaps are available:

```python
ax.imshow(values, cmap=tm.SCALAR_CMAP)       # Full-range scalar default
ax.imshow(values, cmap=tm.DIVERGING_CMAP)    # Signed/diverging data
ax.imshow(values, cmap=tm.SEQUENTIAL_CMAP)   # Optional pale brand-teal map
```

`SCALAR_CMAP` uses navy → blue → teal → green → amber
(`#17324D → #0072B2 → #008080 → #4C9A2A → #C47F00`), avoiding invisible
near-white endpoints. Scalar markers should be fully opaque. For mplot3d
scatter plots, also disable Matplotlib's separate depth fading with
`depthshade=False`. Use `shade=True` for `bar3d` so face lighting preserves
3D depth cues.

## Rounded helpers

### Pills and annotations

```python
tm.annotate("New", (0.15, 0.85), ax=ax, transform=ax.transAxes)
```

The pill is an exact capsule/stadium: straight top and bottom segments joined
to **semicircular ends**, with radius exactly half its height. It uses cubic
Bezier quarter-circle geometry (`capsule_path`), not a superellipse. Pill height
is fixed relative to the font size by default; pass `height=None` to derive it
from the text. Near-square single-character badges become circles. Use
`tm.CapsuleBox` as an annotation `boxstyle`. `tm.add_squircle(...)` and
`tm.SquircleBox` remain separate rounded-panel primitives.

### Pill legends

```python
tm.legend(ax, ncols=3)
```

Each label replaces its separate handle with a **solid category-colored pill**.
Text adaptively uses white or black to target at least 4.5:1 contrast. Marker,
line, and error-bar handles are explicitly hidden rather than merely assigned
zero width, preventing overlap with the label.

Auxiliary uncertainty regions can use a tinted fill with darkened category
text through an explicit per-label override:

```python
tm.legend(ax, styles={"95% interval": "soft"})
```

Everything else defaults to `solid`. For dense plots, place the complete legend
above the axes or add a white group capsule:

```python
tm.legend(ax, outside=True)
tm.legend(ax, backdrop=True, backdrop_alpha=0.88)
```

Lines, patches, bar containers, scatter collections, and error-bar containers
are supported. Ordinary `ax.legend()` remains unchanged.

### Capsule colorbars

```python
image = ax.imshow(values, cmap=tm.SCALAR_CMAP)
colorbar = tm.colorbar(image, ax=ax)
```

The colorbar's visible gradient is clipped to an exact vertical capsule in
display space. Ticks and numeric labels remain outside. It supports image,
contour, streamplot, scatter, and surface mappables; standard rectangular
`fig.colorbar()` output remains available.

### Rounded bars

```python
import numpy as np

x = np.arange(4)

# Default: an exact semicircular free cap and a square baseline.
tm.bar(x, [3, 5, -2, 4], radius="full", ends="free", ax=ax)

# Subtle corner rounding instead of a full cap.
tm.bar(x, [3, 5, -2, 4], radius=0.16, ax=ax)

# Round the baseline too, creating a complete vertical capsule.
tm.bar(x, [3, 5, -2, 4], radius="full", ends="both", ax=ax)

tm.barh(x, [5, 3, 4, 2], radius="full", ax=ax)

# Explicitly clamp a bar too short for an exact full capsule.
tm.bar(x, [3, 5, -2, 4], radius="fit", ends="both", ax=ax)
```

Positive and negative values are supported. Full caps are true semicircles:
free-end mode requires display length of at least half the bar thickness, and
both-end mode requires length of at least the full thickness. If an exact full
capsule cannot fit, drawing raises a clear error rather than silently changing
the shape; use `radius="fit"` to opt into clamping. Numeric radii produce
circular rounded corners and use the bar-thickness axis's data units.

Geometry is calculated in display space, so caps remain circular across aspect
ratios and DPI settings. These helpers accept numeric positions and return a
standard `BarContainer`. Use `ax.set_xticks()` / `ax.set_yticks()` for
categorical labels. Stacked rounded bars are intentionally not automated: only
the outer end of a complete stack should normally be rounded.

## 3D plots

Most settings carry over automatically, but mplot3d panes and grids require a
small additional call:

```python
fig = plt.figure()
ax = fig.add_subplot(projection="3d")
tm.style_3d(ax)

ax.plot_surface(xx, yy, zz, cmap=tm.DIVERGING_CMAP)
```

`style_3d()` clears panes, softens grids, and sets a consistent view. Its axes
and ticks are black by default; pass `gray_decorations=True` for the muted
variant. It does not attempt unsupported rounded 3D panes.

## Scripts, notebooks, and web applications

- **Scripts:** call `tm.apply_theme()` after imports and before figure creation.
- **Jupyter:** install the package into the kernel's environment, restart the
  kernel after installation, then run the same import and `apply_theme()` once.
- **Web apps:** call it once at process startup. If an application switches
  between styles, use the scoped form below and create a separate figure for
  each request rather than sharing figures between threads.

```python
with tm.theme():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 2])
    fig.savefig("scoped.png")
# Previous rcParams are restored here.
```

For publication, PNG defaults to **800 DPI**, PDF embeds TrueType fonts, and SVG
converts text to paths for portability. Override `svg.fonttype` if editable SVG
text is more important than identical rendering on systems without the font.

## Visual showcase

```bash
python examples/showcase.py
```

This creates 27 side-by-side comparisons with **Matplotlib defaults on the
left and Teal Minimal on the right**, using identical data and canvas sizes.
Outputs are organized as:

- `artifacts/showcase/comparisons/`: final 800-DPI comparison PNGs.
- `artifacts/showcase/previews/`: smaller versions for quick review.
- `artifacts/showcase/vector/`: selected themed PDF/SVG exports.
- `artifacts/showcase/00-contact-sheet.png`: a lightweight overview.

The gallery includes lines, time series, scatter, error bars,
grouped/stacked/rounded bars, full capsules, histograms, boxplots, violins,
areas, heatmaps, contours, donut, polar, log, stem, quiver, streamplot,
exact capsules, pill legends, small multiples, palette extension, and 3D
line/scatter/surface/wireframe/bars. For a faster development render, use
`python examples/showcase.py --dpi 140 --output artifacts/showcase-check`.

## Capsule geometry reference

```bash
python examples/geometry_check.py
```

This creates `artifacts/capsule-geometry.png` at 800 DPI and a lightweight
preview. The board shows horizontal pills, a circular single-character badge,
semicircular free caps, and complete vertical capsules.

## Tests

```bash
pytest
```

The tests cover exact font resolution, default font weight, palette behavior,
global and scoped settings, exact capsule endpoints and tangents,
aspect-ratio-stable circular bar caps, hidden legend handles, adaptive text
contrast, uncertainty-region overrides, capsule colorbar clipping, scalar-map
visibility, 3D styling, and actual PNG/PDF/SVG rendering. Horizontal and
vertical capsules are also compared with analytic stadium masks to validate
their rendered silhouettes. Run the showcase as the visual regression review
when changing the design.

## Regenerating fonts

Bundled fonts work without `fontTools` or network access. To rebuild them from
upstream Google Fonts:

```bash
python -m pip install fonttools
python tools/prepare_fonts.py
```

## License

Python code is MIT licensed. The bundled font software remains under the SIL
Open Font License; see the font asset notices for details.

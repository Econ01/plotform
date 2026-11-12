# Changelog

All notable changes to Plotform are documented here. The project follows
[Semantic Versioning](https://semver.org/) while it remains pre-1.0.

## 0.1.0 — Initial public release

### Added

- Minimalist global and scoped Matplotlib themes.
- Vivid categorical palettes and three continuous colormaps.
- Native-style `legend`, `bar`, `barh`, `colorbar`, and `annotate` helpers.
- Exact capsule annotations, circular bar caps, and separate squircle geometry.
- Solid and soft pill legends with adaptive text contrast.
- Vertical capsule colorbars with external ticks.
- Minimal 3D styling and preserved face shading.
- Bundled Plotform Sans and Plotform Mono fonts with licenses and attribution.
- A 27-chart comparison gallery, geometry reference board, and native Matplotlib example.
- CI, package build checks, and trusted-publishing release workflows.

### Removed

- The optional compatibility layer. Use Plotform when themed output is wanted,
  or ordinary Matplotlib when a script must run without the package.

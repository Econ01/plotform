# Bundled font attributions

Teal Minimal includes derived, static font instances so plots render consistently
without requiring system-wide font installation or variable-font axis support.

## Teal Minimal Sans

- Source: **Google Sans Flex**, Google Sans Flex Authors
- Upstream: https://github.com/googlefonts/googlesans-flex
- Downloaded from: https://github.com/google/fonts/tree/main/ofl/googlesansflex
- Modification: instantiated with `ROND=100`; weight and every other variable
  axis were left at their source defaults. The font was then renamed to avoid
  collision with separately installed Google fonts.
- Result: `TealMinimalSans-Rounded.ttf`, regular weight 400
- License: `TealMinimalSans-OFL.txt` (SIL Open Font License 1.1)
- Trademark notice: `TealMinimalSans-TRADEMARKS.md`

## Teal Minimal Mono

- Source: **Google Sans Code**, Google Sans Code Project Authors
- Upstream: https://github.com/googlefonts/googlesans-code
- Downloaded from: https://github.com/google/fonts/tree/main/ofl/googlesanscode
- Modification: instantiated at the source default weight and renamed.
- Result: `TealMinimalMono-Regular.ttf`, regular weight 400
- License: `TealMinimalMono-OFL.txt` (SIL Open Font License 1.1)
- Trademark notice: `TealMinimalMono-TRADEMARKS.md`

Run `python tools/prepare_fonts.py` from the repository root to regenerate these
assets from Google Fonts. The generated documents and figures are not subject
to the font software license; the font files themselves remain under the OFL.

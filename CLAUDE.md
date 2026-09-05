# CLAUDE.md — img2badge

Images (or parts of them) to LED badge strip PNGs: mask what counts as
subject, scale it to the strip height, binarize, hand-tune. Read
`README.md` for the pipeline and flags, `examples/README.md` for real
logo conversions and their lessons.

## Layout

```
img2badge/            the library (CLI = thin wrapper, keep it that way)
  convert.py          pipeline: ink mask -> crop -> dilate -> bbox trim
                      -> LANCZOS scale -> binarize -> column trim;
                      also profile_ink, append_strips, save/load/zoom
  art.py              ●/· strip text-art (spaced on disk for square
                      editing aspect; parser strips spaces, compact
                      files stay valid)
  cli.py              img2badge <image|.txt> [-o -H -t --method --mask
                      --crop --invert --dilate --art --append --gap
                      --zoom --dots --profile]
examples/
  originals/          committed source logos (trademarks; demo-only)
  art/                editable ●/· strips, one per example
  *.png               badge-ready strips (README table = the recipes)
tests/                fixtures drawn with PIL in conftest — never vendor
                      image assets
```

Dev shell: `nix develop` (uv + numpy/Pillow). Run as `uv run img2badge`
or `uv run pytest`.

## Invariants — do not break these

- **Dilate happens BEFORE the bbox trim.** A trimmed ink map has no
  canvas left for strokes to thicken into (regression-tested).
- **The ink floor (>16) is shared** by `_bbox_trim` and `profile_ink` —
  that is what makes `--profile` honest: faint junk (watermarks) shows
  up exactly where it will distort the sizing. Change one, change both.
- **`.txt` input is verbatim.** A hand-edited art file rebuilds
  bit-for-bit; no scaling, trimming, or thresholding is applied to it.
- **Hand-tuned examples: the `art/*.txt` is the source of truth**
  (currently freebsd, fox, apple — marked † in examples/README.md).
  Re-running the conversion command overwrites the tuning; regenerate
  those PNGs only from their art files.
- **`print_dots` resolves stdout at call time** (`file=None` default) —
  a `file=sys.stdout` default binds the import-time stream and bypasses
  pytest capsys.
- `.gitignore` subtlety: `!examples/*.png` does not match
  subdirectories — `examples/originals/*.png` needs its own negation.

## Conversion cheat-sheet (for advising on quality issues)

- Pick the mask by what the subject *is*: dark-on-light -> `auto`;
  shape on transparency -> `alpha`; brand color -> `color=#RRGGBB,tol`;
  light-on-dark -> `luma --invert`. White marks on a colored disc:
  color-mask white and `--crop` inside the disc (the white background
  outside also matches).
- `luma --invert` traps: mid-luma fills (cyan ~127) pass the profile's
  ink floor and saturate the histogram; a color mask excludes them by
  RGB distance instead.
- Thin strokes need `--dilate` roughly equal to the downscale factor
  (source height / 11). Too much fuses loops shut — sweep and compare
  `--dots` output (quake 13, cyan-curl 5).
- The subject squashing vertically usually means faint junk stretched
  the bbox — run `--profile` (with the same mask/crop) and use its
  suggested `--crop`.
- Dithers (`fs`, `atkinson`, `bayer`) suit photos; logos and line art
  want the default threshold.
- Hand-tuning loop: convert with `--art`, edit the `.txt`, rebuild with
  `img2badge file.txt -o out.png --dots`.

## Working conventions

- Source logos beyond the committed demo set live in
  `../logo-sources/` (local-only, has a provenance README) — copy new
  originals there immediately; pasted-image caches are volatile.
- New examples earn their place with a *lesson* — the examples/README
  table row says what technique the logo demonstrates.
- Wordmark strips for `--append` come from font2badge
  (`font2badge k8x12.ttf "<Name>" --ppem 12 --mono`).
- Zoom copies (`--zoom`) are for viewing only; generate on demand, do
  not commit them.

## Commits & releases

- **Conventional Commits are required for PR titles** (enforced by
  `.github/workflows/pr-title.yml`). We squash-merge, so the PR title
  becomes the commit on main — write it as `type: summary`.
- **Only `feat:`/`fix:`/breaking bump the version;** docs/ci/test/chore
  land in the changelog only. Pre-1.0 flags in
  `release-please-config.json` downshift bumps: breaking -> minor,
  `feat:` -> patch.
- **Releases are automated by release-please**
  (`.github/workflows/cd.yaml`): merging the standing release PR tags
  `img2badge-vX.Y.Z`. Never bump the version by hand.
- **The version lives only in `pyproject.toml`** (seed:
  `.release-please-manifest.json`) — unlike pixelshaper there is no
  `__init__.py` annotation.
- CI (`ci.yml`): ruff + black on Linux; pytest matrix on
  ubuntu/windows/macos.

## Related (not in this repo)

- Siblings: `../font2badge/` (text -> strip, self-scaled),
  `../pixelshaper/` (hand-tunable pixel fonts) — the three share the
  spaced ●/· art convention and the CI/CD shape.
- Display consumer: `../led-name-badge-ls32/` (push via
  `lednamebadge.py -s 4 -m <modes> <pngs...>`; strips must be exactly
  11 px tall; mode 4 still-centered clips wider than 44 px, mode 0
  scrolls; a push rewrites all 8 slots).
- Slot inventory: `claude-workspace/domains/led-badge/outputs/
  badge-slots.md` — update it on every badge push.

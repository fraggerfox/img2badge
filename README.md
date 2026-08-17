# img2badge

> [!NOTE]
> **AI-generated code.** This repository was developed with
> [Claude Code](https://claude.com/claude-code): the code and
> documentation are largely AI-generated, working under human direction
> and review.

An image — or a masked/cropped **part** of one — to a badge-ready LED
strip PNG: white-on-black, exactly your badge's pixel height, ready for
[led-name-badge-ls32](https://github.com/fossasia/led-name-badge-ls32).

The third sibling in the badge family:
[font2badge](https://github.com/fraggerfox/font2badge) renders **text**,
[pixelshaper](https://github.com/fraggerfox/pixelshaper) builds crafted
**pixel fonts**, img2badge converts **images** — and because all three
emit same-height strips, they compose (`--append`) into one badge
message.

## Contents

- [Usage](#usage)
- [Flags](#flags)
- [The recipe that works for logos](#the-recipe-that-works-for-logos)
- [Hand-tuning round trip](#hand-tuning-round-trip)
- [Examples](#examples)
- [How it decides on/off](#how-it-decides-onoff)

## Usage

```sh
nix develop                          # uv dev shell, venv activated
img2badge <image> [flags]            # image -> strip PNG
img2badge <strip.txt>                # rebuild a hand-edited art strip
```

Output defaults to `<input>-badge.png`. Push to the badge with:

```sh
python3 lednamebadge.py -s 4 -m 4 strip.png   # mode 4 = still-centered
```

## Flags

| Flag | Default | Meaning |
|------|---------|---------|
| `-o`, `--out PATH` | `<input>-badge.png` | output PNG path |
| `-H`, `--height N` | 11 | strip height in px (ignored for `.txt` input) |
| `-t`, `--threshold F` | 0.5 | on/off cut as fraction of peak ink (threshold method) |
| `--method M` | threshold | `threshold` / `fs` / `atkinson` / `bayer` — dithers suit photos, not line art |
| `--mask M` | auto | what counts as ink: `auto` (dark + opaque), `luma`, `alpha`, `color=#RRGGBB[,tol]` |
| `--crop X,Y,W,H` | — | use only this region of the source |
| `--invert` | off | select light pixels instead of dark (auto/luma) |
| `--dilate N` | 0 | thicken source ink (N×N max filter) before scaling — rescues thin line art |
| `--art TXT` | — | also write the strip as editable ●/· text art |
| `--append PNG` | — | join same-height strips after this one (repeatable) |
| `--gap N` | 3 | dark columns between joined strips |
| `--zoom N` | 0 | also write an `@Nx` nearest-neighbour copy for viewing |
| `--dots` | off | print the strip as ●/· rows |

## The recipe that works for logos

Naively downscaling a whole logo to 11 px crushes everything — a wordmark
becomes noise. What survives is **isolate the iconic mark, render the
name as text**:

```sh
# 1. isolate the icon (by color, alpha, or crop) and scale it to 11 px
img2badge logo.png --mask "color=#e8541d,80" -o icon.png

# 2. render the wordmark as crisp pixel text with font2badge
font2badge k8x12.ttf "NetBSD" --ppem 12 --mono -o name.png

# 3. compose
img2badge icon.png --append name.png -o badge.png
```

Mask cheat-sheet, from real logos:

- **solid dark mark on transparency** (Quake, Unreal): `--mask auto` —
  darkness gated by alpha, the default just works.
- **colored mark next to a wordmark** (NetBSD flag, HelloFresh lemon):
  `--mask color=#RRGGBB,tol` picks the mark by its color.
- **a band of the image** (a flag across the top): `--crop X,Y,W,H`.
- **thin line art** (the Quake ring): add `--dilate 9` or the strokes
  break up at 11 px.

## Hand-tuning round trip

Auto-conversion gets a logo ~90% there; the last pixels want a human —
open a counter, reconnect a stroke, drop a stray dot. Emit the strip as
text art, edit it in any editor, rebuild:

```sh
img2badge logo.png --art logo.txt     # writes the PNG and the ●/· art
$EDITOR logo.txt                       # flip pixels by hand
img2badge logo.txt -o logo.png        # rebuild the PNG from your edit
```

The art format is the same ●/· grid pixelshaper uses for glyphs (`#`/`.`
are accepted as ASCII aliases), so edits diff cleanly in git.

## Examples

See [examples/](examples/) for real conversions (NetBSD, FreeBSD,
HelloFresh, Quake, Unreal) with their commands and outputs.

## How it decides on/off

The pipeline is: **mask** the source into a grayscale ink map (what
counts as subject) → **bbox-trim** → optional **dilate** → **LANCZOS**
scale to the strip height → **binarize**. The default binarization is a
hard threshold at a fraction of peak ink — the right call for logos and
line art, where dithering only adds noise. The dither methods
(Floyd–Steinberg, Atkinson, Bayer) exist for photographic sources where
faking tone with dot patterns is the point.

The one thing no converter can add is information: at 11 px every pixel
is load-bearing, and fine detail (thin rings, small text, interior
cutouts) needs either `--dilate`, a wider layout, or the hand-tuning
round trip above.

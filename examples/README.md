# Examples

Real logo conversions, regenerated with img2badge. Wordmark strips come
from [font2badge](https://github.com/fraggerfox/font2badge)
(`font2badge k8x12.ttf "<Name>" --ppem 12 --mono`) and are composed with
`--append`. The `@8x` copies are nearest-neighbour zooms for viewing.

Logo sources are the freely-hosted variants (Wikimedia/site assets);
they are trademarks of their respective owners, reproduced here only as
tiny 11 px conversion demos.

| Strip | Command (icon part) | Lesson |
|---|---|---|
| `netbsd.png` (58×11) | `img2badge netbsd-logo.png --crop 0,0,200,85 --mask 'color=#e87722,90' --append name.png` | crop the flag band, pick it by color — the wordmark is orange too |
| `freebsd.png` (42×11) | `img2badge horned-logo.png --dilate 61 --append name.png` | thin outline art needs a strong dilate (~87 source px per output px here) |
| `hellofresh.png` (57×11) | `img2badge hellofresh-logo.png --mask 'color=#91c11e,90' --append name.png` | color mask isolates the lemon from the dark wordmark |
| `quake.png` (9×11) | `img2badge quake-q.png --dilate 15` | the nail-through-ring survives as ring + crossbar + spike |
| `unreal.png` (7×11) | `img2badge ue-logo.png --crop 0,0,960,510` | crop the emblem out of a stacked emblem+wordmark lockup |

Every one of these is also a hand-tuning candidate: re-run with
`--art strip.txt`, fix pixels, rebuild with `img2badge strip.txt`.

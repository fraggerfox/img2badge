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
| `freebsd.png` (43×11) | `img2badge orb.png --crop 0,0,600,370 --mask 'color=#b5010f,80' --append name.png` | crop off the color-swatch bar; the solid orb needs no dilation |
| `hellofresh.png` (57×11) | `img2badge hellofresh-logo.png --mask 'color=#91c11e,90' --append name.png` | color mask isolates the lemon from the dark wordmark |
| `quake.png` (10×11) | `img2badge quake.png --crop 0,0,447,400 --mask luma --invert --dilate 13` | white-on-black wants --invert; crop the ™; dilate saves the thin crescent |
| `unreal.png` (11×11) | `img2badge ue-emblem.png` | the classic circle emblem converts square-on; the U survives in negative space |

Every one of these is also a hand-tuning candidate: re-run with
`--art strip.txt`, fix pixels, rebuild with `img2badge strip.txt`.

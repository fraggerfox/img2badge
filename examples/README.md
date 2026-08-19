# Examples

Real logo conversions, regenerated with img2badge. Wordmark strips come
from [font2badge](https://github.com/fraggerfox/font2badge)
(`font2badge k8x12.ttf "<Name>" --ppem 12 --mono`) and are composed with
`--append`. To view a strip at a readable size, generate a zoom copy
on demand (`img2badge <strip>.txt --zoom 8 -o /tmp/view.png`) — zoom
copies are not kept in the repo.

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
| `foxhound.png` (10×11) | `img2badge foxhound.png -t 0.35` | four overlapping shapes fuse at 11 px — the case where auto-conversion needs hand-tuning |
| `apple.png` (9×11) | `img2badge apple.png` | a solid square-ish mark just works with the defaults |

## Editable art

Each strip's ●/· text art is committed alongside it (`<name>.txt`) in
the space-separated format — one lit/dark cell per pixel, spaces as
visual separators so the art reads at true proportions in an editor.
Edit the `.txt`, then rebuild its PNG:

```sh
img2badge examples/quake.txt -o examples/quake.png --dots
```

The `.txt` is the source of truth once you start editing — re-running
the image conversion would overwrite your pixels.

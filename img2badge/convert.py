"""Image -> ink mask -> scale to strip height -> 1-bit strip.

The pipeline mirrors what the badge needs: select the part of the image
that is "subject" (the ink), scale that to the strip height, then decide
on/off per pixel. Selection is the part generic converters lack — a logo
wordmark crushed into a squeezed icon is unreadable, but the icon alone,
masked out and scaled, survives 11 px.
"""

import sys

import numpy as np
from PIL import Image, ImageFilter

# Ordered 4x4 Bayer matrix for the "bayer" method.
_BAYER4 = np.array(
    [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]],
    dtype=np.float32,
)


def parse_color(spec: str):
    """'#RRGGBB' or '#RRGGBB,tol' -> ((r, g, b), tol). Default tol 60."""
    body, _, tol = spec.partition(",")
    body = body.lstrip("#")
    if len(body) != 6:
        raise SystemExit(f"bad color spec {spec!r}: want #RRGGBB[,tol]")
    rgb = tuple(int(body[i : i + 2], 16) for i in (0, 2, 4))
    return rgb, float(tol) if tol else 60.0


def ink_from_image(img: Image.Image, mask: str = "auto", invert: bool = False):
    """Reduce an image to a grayscale ink map (255 = fully subject).

    mask:
      auto   — darkness gated by opacity: dark, opaque pixels are ink.
               Handles both dark-on-light logos and shapes on transparency.
      luma   — darkness only (ignores alpha).
      alpha  — opacity only (solid marks on transparent background).
      color=#RRGGBB[,tol] — pixels within RGB distance tol of the color.
    invert selects light pixels instead of dark (auto/luma only).
    """
    a = np.asarray(img.convert("RGBA"), dtype=np.float32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    luma = 0.299 * r + 0.587 * g + 0.114 * b
    dark = luma if invert else 255.0 - luma
    if mask == "alpha":
        ink = al
    elif mask == "luma":
        ink = dark
    elif mask.startswith("color="):
        rgb, tol = parse_color(mask[len("color=") :])
        dist = np.sqrt((r - rgb[0]) ** 2 + (g - rgb[1]) ** 2 + (b - rgb[2]) ** 2)
        ink = np.where((dist <= tol) & (al > 32), 255.0, 0.0)
    elif mask == "auto":
        ink = dark * (al / 255.0)
    else:
        raise SystemExit(f"unknown mask {mask!r}: want auto, luma, alpha or color=...")
    return np.clip(ink, 0, 255).astype(np.uint8)


def _bbox_trim(ink: np.ndarray) -> np.ndarray:
    """Crop the ink map to its bounding box (anything above faint noise)."""
    rows = np.where((ink > 16).any(axis=1))[0]
    cols = np.where((ink > 16).any(axis=0))[0]
    if not len(rows):
        raise SystemExit("no ink found — check --mask/--crop/--invert")
    return ink[rows.min() : rows.max() + 1, cols.min() : cols.max() + 1]


def _binarize(gray: np.ndarray, method: str, threshold: float) -> np.ndarray:
    """Scaled grayscale -> boolean strip. threshold is a fraction of peak
    (threshold method only); the dither methods normalize to peak and use
    the classic mid-gray comparisons."""
    peak = float(gray.max())
    if peak <= 0:
        raise SystemExit("strip is empty after scaling")
    norm = gray.astype(np.float32) * (255.0 / peak)
    h, w = norm.shape
    if method == "threshold":
        return gray >= max(int(peak * threshold), 1)
    if method == "bayer":
        cuts = _BAYER4[np.arange(h)[:, None] % 4, np.arange(w)[None, :] % 4] + 0.5
        return norm >= cuts * (255.0 / 16.0)
    if method in ("fs", "atkinson"):
        out = np.zeros((h, w), bool)
        buf = norm.copy()
        for y in range(h):
            for x in range(w):
                old = buf[y, x]
                on = old >= 128.0
                out[y, x] = on
                err = old - (255.0 if on else 0.0)
                if method == "fs":
                    spread = [
                        (0, 1, 7 / 16),
                        (1, -1, 3 / 16),
                        (1, 0, 5 / 16),
                        (1, 1, 1 / 16),
                    ]
                else:  # atkinson: 6 neighbours, 1/8 each (drops 2/8 of the error)
                    spread = [
                        (0, 1, 1 / 8),
                        (0, 2, 1 / 8),
                        (1, -1, 1 / 8),
                        (1, 0, 1 / 8),
                        (1, 1, 1 / 8),
                        (2, 0, 1 / 8),
                    ]
                for dy, dx, wgt in spread:
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w:
                        buf[yy, xx] += err * wgt
        return out
    raise SystemExit(
        f"unknown method {method!r}: want threshold, fs, atkinson or bayer"
    )


def convert(
    path,
    height: int = 11,
    threshold: float = 0.5,
    method: str = "threshold",
    mask: str = "auto",
    crop=None,
    invert: bool = False,
    dilate: int = 0,
):
    """Full pipeline: image file -> boolean (height x width) strip."""
    img = Image.open(path)
    if crop is not None:
        x, y, w, h = crop
        img = img.crop((x, y, x + w, y + h))
    ink = ink_from_image(img, mask=mask, invert=invert)
    if dilate:
        # Dilate BEFORE the bbox trim: a trimmed ink map has no canvas left
        # for the strokes to thicken into.
        size = dilate if dilate % 2 else dilate + 1  # MaxFilter wants odd
        ink = np.asarray(
            Image.fromarray(ink).filter(ImageFilter.MaxFilter(max(size, 3)))
        )
    src = Image.fromarray(_bbox_trim(ink))
    width = max(1, round(src.width * height / src.height))
    gray = np.asarray(src.resize((width, height), Image.LANCZOS))
    bits = _binarize(gray, method, threshold)
    cols = np.where(bits.any(axis=0))[0]
    if not len(cols):
        raise SystemExit("threshold erased all ink — try a lower --threshold")
    lo, hi = max(cols.min() - 1, 0), min(cols.max() + 2, bits.shape[1])
    return bits[:, lo:hi]


def append_strips(strips, gap: int = 3) -> np.ndarray:
    """Join same-height boolean strips left-to-right with dark gap columns."""
    heights = {s.shape[0] for s in strips}
    if len(heights) != 1:
        raise SystemExit(f"strip heights differ ({sorted(heights)}) — cannot join")
    h = heights.pop()
    parts = []
    for s in strips:
        parts.append(s)
        parts.append(np.zeros((h, gap), bool))
    return np.hstack(parts[:-1])


def load_strip(path) -> np.ndarray:
    """Load an existing strip PNG back into a boolean array."""
    return np.asarray(Image.open(path).convert("L")) > 127


def save_strip(bits: np.ndarray, path) -> None:
    """Boolean strip -> white-on-black PNG (True = lit)."""
    Image.fromarray(np.where(bits, 255, 0).astype(np.uint8), mode="L").save(path)


def save_zoom(bits: np.ndarray, path, factor: int) -> None:
    """Nearest-neighbour zoom copy for viewing (browsers blur-scale 11 px)."""
    img = Image.fromarray(np.where(bits, 255, 0).astype(np.uint8), mode="L")
    img.resize((bits.shape[1] * factor, bits.shape[0] * factor), Image.NEAREST).save(
        path
    )


def print_dots(bits: np.ndarray, file=None) -> None:
    # Resolve stdout at call time (a default arg would bind the import-time
    # stream and bypass pytest's capsys / any later redirection).
    # Two columns per pixel: terminal cells are ~2x taller than wide, so a
    # one-char-per-pixel grid renders horizontally squished.
    for row in bits:
        print(" ".join("●" if v else "·" for v in row), file=file or sys.stdout)

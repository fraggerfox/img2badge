"""●/· text-art strips: the hand-tuning round trip.

Auto-conversion gets a logo ~90% there; the last pixels want a human
(open a counter, reconnect a stroke). Emit the strip as editable text,
fix it in any editor, rebuild the PNG — same loop, same characters, as
pixelshaper's glyph files, minus the metrics header (a strip has none).
"""

import numpy as np

ON, OFF = "●", "·"
_ON_CHARS = {ON, "#", "@"}
_OFF_CHARS = {OFF, ".", " "}


def write_art(bits: np.ndarray, path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in bits:
            f.write("".join(ON if v else OFF for v in row) + "\n")


def read_art(path) -> np.ndarray:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            rows.append([_cell(ch, path) for ch in line])
    if not rows:
        raise SystemExit(f"{path}: empty art file")
    width = max(len(r) for r in rows)
    grid = np.zeros((len(rows), width), bool)
    for y, r in enumerate(rows):
        grid[y, : len(r)] = r
    return grid


def _cell(ch: str, path) -> bool:
    if ch in _ON_CHARS:
        return True
    if ch in _OFF_CHARS:
        return False
    raise SystemExit(f"{path}: unexpected character {ch!r} (use {ON}/{OFF} or #/.)")

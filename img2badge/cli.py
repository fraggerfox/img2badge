import argparse
from pathlib import Path

from img2badge.art import read_art, write_art
from img2badge.convert import (
    append_strips,
    convert,
    load_strip,
    print_dots,
    save_strip,
    save_zoom,
)


def _parse_crop(spec: str):
    try:
        x, y, w, h = (int(v) for v in spec.split(","))
    except ValueError:
        raise SystemExit(f"bad --crop {spec!r}: want X,Y,W,H")
    return x, y, w, h


def main():
    ap = argparse.ArgumentParser(
        description="Convert an image (or a masked/cropped part of it) into a "
        "badge-ready LED strip PNG. A .txt input rebuilds a hand-edited "
        "text-art strip instead."
    )
    ap.add_argument("input", type=Path, help="image file, or a ●/· .txt art strip")
    ap.add_argument(
        "-o", "--out", type=Path, help="output PNG (default: <input>-badge.png)"
    )
    ap.add_argument(
        "-H",
        "--height",
        type=int,
        default=11,
        help="strip height in px (default 11; ignored for .txt input)",
    )
    ap.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.5,
        help="on/off cut as fraction of peak ink (threshold method; default 0.5)",
    )
    ap.add_argument(
        "--method",
        choices=("threshold", "fs", "atkinson", "bayer"),
        default="threshold",
        help="binarization (default threshold; dithers suit photos, not line art)",
    )
    ap.add_argument(
        "--mask",
        default="auto",
        help="what counts as ink: auto (dark+opaque), luma, alpha, or "
        "color=#RRGGBB[,tol] (default auto)",
    )
    ap.add_argument(
        "--crop",
        type=_parse_crop,
        metavar="X,Y,W,H",
        help="use only this region of the source image",
    )
    ap.add_argument(
        "--invert",
        action="store_true",
        help="select light pixels instead of dark (auto/luma masks)",
    )
    ap.add_argument(
        "--dilate",
        type=int,
        default=0,
        metavar="N",
        help="thicken source ink with an NxN max filter before scaling "
        "(rescues thin line art; N is rounded up to odd)",
    )
    ap.add_argument(
        "--art",
        type=Path,
        metavar="TXT",
        help="also write the strip as editable ●/· text art",
    )
    ap.add_argument(
        "--append",
        type=Path,
        action="append",
        default=[],
        metavar="PNG",
        help="join these same-height strip PNGs after this one (repeatable)",
    )
    ap.add_argument(
        "--gap", type=int, default=3, help="dark columns between joined strips"
    )
    ap.add_argument(
        "--zoom",
        type=int,
        default=0,
        metavar="N",
        help="also write an @Nx nearest-neighbour copy for viewing",
    )
    ap.add_argument("--dots", action="store_true", help="print the strip as ●/· rows")
    args = ap.parse_args()

    if args.input.suffix == ".txt":
        bits = read_art(args.input)
    else:
        bits = convert(
            args.input,
            height=args.height,
            threshold=args.threshold,
            method=args.method,
            mask=args.mask,
            crop=args.crop,
            invert=args.invert,
            dilate=args.dilate,
        )

    if args.append:
        bits = append_strips([bits] + [load_strip(p) for p in args.append], args.gap)

    out = args.out or args.input.with_name(f"{args.input.stem}-badge.png")
    save_strip(bits, out)
    print(f"{out} ({bits.shape[1]}x{bits.shape[0]})")
    if args.art:
        write_art(bits, args.art)
        print(f"{args.art} (editable art — rebuild with: img2badge {args.art})")
    if args.zoom:
        zpath = out.with_name(f"{out.stem}@{args.zoom}x.png")
        save_zoom(bits, zpath, args.zoom)
        print(f"{zpath}")
    if args.dots:
        print_dots(bits)


if __name__ == "__main__":
    main()

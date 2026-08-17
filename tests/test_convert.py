"""convert(): masks, crop, dilate, methods, and failure modes."""

import numpy as np
import pytest

from img2badge.convert import append_strips, convert


def test_dark_on_light_fills_the_strip(dark_circle):
    bits = convert(dark_circle)
    assert bits.dtype == bool
    assert bits.shape[0] == 11
    # a circle scaled to the strip touches top and bottom rows
    assert bits[0].any() and bits[10].any()
    # roughly as wide as tall (square source, bbox-trimmed)
    assert 9 <= bits.shape[1] <= 14


def test_alpha_background_is_not_ink(alpha_mark):
    bits = convert(alpha_mark)  # auto mask gates darkness by opacity
    # the mark is 60x40 source px -> wider than tall; fully lit block
    assert bits.shape[0] == 11
    assert bits.all(axis=None) or bits.mean() > 0.9


def test_color_mask_isolates_the_icon(two_color_logo):
    red = convert(two_color_logo, mask="color=#c82828,80")
    both = convert(two_color_logo)  # auto: everything dark-ish
    # the red circle alone is ~square; icon+wordmark together is much wider
    assert red.shape[1] < both.shape[1] / 2


def test_crop_selects_a_region(two_color_logo):
    icon = convert(two_color_logo, crop=(0, 0, 100, 100))
    assert 9 <= icon.shape[1] <= 14  # just the circle


def test_dilate_thickens_ink(tmp_path):
    from PIL import Image, ImageDraw

    # a 1px vertical line, converted at native height so no downscale blurs
    # the comparison: dilate must strictly widen the lit area
    img = Image.new("RGB", (20, 20), "white")
    ImageDraw.Draw(img).line([10, 0, 10, 19], fill="black", width=1)
    p = tmp_path / "line.png"
    img.save(p)
    plain = convert(p, height=20)
    fat = convert(p, height=20, dilate=5)
    assert fat.sum() > plain.sum()
    assert fat.shape[1] > plain.shape[1]


def test_height_is_configurable(dark_circle):
    assert convert(dark_circle, height=16).shape[0] == 16


def test_methods_run_and_differ(dark_circle):
    outs = {
        m: convert(dark_circle, method=m)
        for m in ("threshold", "fs", "atkinson", "bayer")
    }
    for bits in outs.values():
        assert bits.shape[0] == 11 and bits.any()
    # dithers scatter differently from the hard threshold on the AA edge
    assert any(
        outs["threshold"].shape != o.shape or not np.array_equal(outs["threshold"], o)
        for k, o in outs.items()
        if k != "threshold"
    )


def test_invert_selects_light_pixels(tmp_path):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (100, 100), "black")
    ImageDraw.Draw(img).ellipse([20, 20, 80, 80], fill="white")
    p = tmp_path / "lightondark.png"
    img.save(p)
    bits = convert(p, invert=True)
    # the white circle becomes the subject: ~square, present
    assert bits.shape[0] == 11 and bits.any()
    assert 9 <= bits.shape[1] <= 14


def test_no_ink_fails_loudly(tmp_path):
    from PIL import Image

    p = tmp_path / "blank.png"
    Image.new("RGB", (50, 50), "white").save(p)
    with pytest.raises(SystemExit, match="no ink"):
        convert(p)


def test_append_joins_and_validates():
    a = np.ones((11, 5), bool)
    b = np.ones((11, 3), bool)
    joined = append_strips([a, b], gap=2)
    assert joined.shape == (11, 10)
    assert not joined[:, 5:7].any()  # the gap is dark
    with pytest.raises(SystemExit, match="heights differ"):
        append_strips([a, np.ones((9, 3), bool)])

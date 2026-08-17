"""Test images are drawn on the fly — the suite vendors no assets."""

import numpy as np
import pytest
from PIL import Image, ImageDraw


@pytest.fixture()
def dark_circle(tmp_path):
    """Solid black circle on white — the plain luma/auto case."""
    img = Image.new("RGB", (200, 200), "white")
    ImageDraw.Draw(img).ellipse([40, 40, 160, 160], fill="black")
    p = tmp_path / "circle.png"
    img.save(p)
    return p


@pytest.fixture()
def alpha_mark(tmp_path):
    """Black square on TRANSPARENT background — reads all-dark without alpha."""
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([20, 30, 80, 70], fill=(10, 10, 10, 255))
    p = tmp_path / "alpha.png"
    img.save(p)
    return p


@pytest.fixture()
def two_color_logo(tmp_path):
    """Red icon left, blue wordmark right, white bg — the isolation case."""
    img = Image.new("RGB", (300, 100), "white")
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, 90, 90], fill=(200, 40, 40))
    d.rectangle([120, 30, 290, 70], fill=(40, 40, 200))
    p = tmp_path / "logo.png"
    img.save(p)
    return p


def strip_of(path):
    """Load a written strip PNG back as a boolean array."""
    return np.asarray(Image.open(path).convert("L")) > 127

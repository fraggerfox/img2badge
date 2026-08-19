"""Art round-trip and the CLI surface."""

import numpy as np
import pytest
from PIL import Image

from img2badge import cli
from img2badge.art import read_art, write_art


def strip_of(path):
    return np.asarray(Image.open(path).convert("L")) > 127


def run(monkeypatch, tmp_path, *args):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["img2badge", *map(str, args)])
    cli.main()


def test_art_round_trip(tmp_path):
    rng = np.random.default_rng(7)
    bits = rng.random((11, 30)) > 0.6
    p = tmp_path / "strip.txt"
    write_art(bits, p)
    assert np.array_equal(read_art(p), bits)


def test_art_accepts_ascii_aliases(tmp_path):
    p = tmp_path / "s.txt"
    p.write_text("#.#\n.#.\n", encoding="utf-8")
    grid = read_art(p)
    assert grid.tolist() == [[True, False, True], [False, True, False]]


def test_spaced_and_compact_formats_read_identically(tmp_path):
    spaced = tmp_path / "spaced.txt"
    compact = tmp_path / "compact.txt"
    spaced.write_text("\u25cf \u00b7 \u25cf\n\u00b7 \u25cf \u00b7\n", encoding="utf-8")
    compact.write_text("\u25cf\u00b7\u25cf\n\u00b7\u25cf\u00b7\n", encoding="utf-8")
    assert np.array_equal(read_art(spaced), read_art(compact))


def test_art_rejects_junk(tmp_path):
    p = tmp_path / "bad.txt"
    p.write_text("●x●\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="unexpected character"):
        read_art(p)


def test_cli_image_to_png_and_art(monkeypatch, tmp_path, dark_circle, capsys):
    run(
        monkeypatch,
        tmp_path,
        dark_circle,
        "-o",
        "out.png",
        "--art",
        "out.txt",
        "--dots",
    )
    bits = strip_of(tmp_path / "out.png")
    assert bits.shape[0] == 11
    # the art file mirrors the PNG
    assert np.array_equal(read_art(tmp_path / "out.txt"), bits)
    out = capsys.readouterr().out
    assert "out.png" in out and "●" in out


def test_cli_rebuilds_edited_art(monkeypatch, tmp_path, dark_circle):
    run(monkeypatch, tmp_path, dark_circle, "-o", "a.png", "--art", "a.txt")
    art = (tmp_path / "a.txt").read_text(encoding="utf-8")
    edited = art.replace("●", "·", 1)  # hand-edit: clear the first lit pixel
    (tmp_path / "a.txt").write_text(edited, encoding="utf-8")
    run(monkeypatch, tmp_path, tmp_path / "a.txt", "-o", "b.png")
    a, b = strip_of(tmp_path / "a.png"), strip_of(tmp_path / "b.png")
    assert a.shape == b.shape
    assert a.sum() - b.sum() == 1  # exactly the edited pixel changed


def test_cli_append_and_zoom(monkeypatch, tmp_path, dark_circle, alpha_mark):
    run(monkeypatch, tmp_path, alpha_mark, "-o", "mark.png")
    run(
        monkeypatch,
        tmp_path,
        dark_circle,
        "-o",
        "combo.png",
        "--append",
        "mark.png",
        "--gap",
        "4",
        "--zoom",
        "3",
    )
    combo = strip_of(tmp_path / "combo.png")
    mark = strip_of(tmp_path / "mark.png")
    assert combo.shape[0] == 11
    assert combo.shape[1] > mark.shape[1]  # both parts present
    zoom = strip_of(tmp_path / "combo@3x.png")
    assert zoom.shape == (33, combo.shape[1] * 3)


def test_cli_default_output_name(monkeypatch, tmp_path, dark_circle):
    run(monkeypatch, tmp_path, dark_circle)
    assert (dark_circle.parent / f"{dark_circle.stem}-badge.png").exists()

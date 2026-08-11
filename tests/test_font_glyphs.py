import sys
from pathlib import Path

import pytest

FONT_DIR = Path(__file__).parents[1] / "firmware" / "font"
sys.path.insert(0, str(FONT_DIR))

import bdftohex  # pylint: disable=wrong-import-position
import hextokff  # pylint: disable=wrong-import-position


@pytest.mark.parametrize(
    "size,expected_bitmap",
    [
        (
            14,
            "F73C94249424F4BC00809BB86744674498A00478F35C94F894F8F3A4",
        ),
        (
            16,
            "F38F92099209F24F004000409DCE63B163B19C48023E023EF1B7927E927EF1C9",
        ),
        (
            24,
            "FE787FFE787FCE6073CE6073FE667FFE667FFE667F000600000600"
            "CF9E7CCF9E7C307983307983CF8670CF86700061FC0061FCFE198F"
            "FE198FFE198FCE67FCCE67FCFE1E73FE1E73",
        ),
    ],
)
def test_qr_glyph_bdf_contains_exact_bitmap(size, expected_bitmap):
    glyphs = bdftohex.bdftohex(str(FONT_DIR / ("qr-u%d.bdf" % size)))

    assert glyphs == ["E000:" + expected_bitmap]


def test_qr_glyph_is_selected_only_for_wide_fonts(monkeypatch, tmp_path):
    glyph_file = tmp_path / "qr.hex"
    glyph_file.write_text(
        "E000:F73C94249424F4BC00809BB86744674498A00478F35C94F894F8F3A4\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(FONT_DIR)

    narrow_font = hextokff.hextokff(str(glyph_file), 14, 14)
    wide_font = hextokff.hextokff(str(glyph_file), 14, 14, ["ko-KR", "zh-CN", "ja-JP"])

    assert 0xE000 in hextokff.CUSTOM_WIDE_CODEPOINTS
    assert 0xE000 not in hextokff.DEFAULT_CODEPOINTS
    assert "0xE0,0x00" not in narrow_font
    assert "0xE0,0x00" in wide_font

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
            "FCFCFCFCCCCCCCCCFCFCFCFC00000000FCCCFCCCCC30CC30FCCCFCCC",
        ),
        (
            16,
            "FC3FFC3FCC33CC33FC3FFC3F0000000000000000FC33FC33CC0CCC0CFC33FC33",
        ),
        (
            24,
            "FFC3FFFFC3FFFFC3FFE1C387E1C387E1C387E1C387FFC3FFFFC3FFFFC3FF"
            "000000000000000000000000FFC387FFC387FFC387E1C078E1C078E1C078"
            "E1C078FFC387FFC387FFC387",
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

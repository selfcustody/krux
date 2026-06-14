# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors

import pytest

EXPECTED_THEME_KEYS = {
    "background",
    "info_background",
    "foreground",
    "frame",
    "disabled",
    "go",
    "esc_no",
    "del",
    "toggle",
    "error",
    "highlight",
}


def _rgb565_to_rgb(color):
    color = ((color & 0xFF) << 8) | ((color >> 8) & 0xFF)
    return (
        ((color >> 11) & 0x1F) * 255 / 31,
        ((color >> 5) & 0x3F) * 255 / 63,
        (color & 0x1F) * 255 / 31,
    )


def _relative_luminance_component(value):
    value = value / 255
    if value <= 0.03928:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def _relative_luminance(color):
    red, green, blue = _rgb565_to_rgb(color)
    return (
        0.2126 * _relative_luminance_component(red)
        + 0.7152 * _relative_luminance_component(green)
        + 0.0722 * _relative_luminance_component(blue)
    )


def _contrast_ratio(color_a, color_b):
    luminance_a = _relative_luminance(color_a)
    luminance_b = _relative_luminance(color_b)
    lighter = max(luminance_a, luminance_b)
    darker = min(luminance_a, luminance_b)
    return (lighter + 0.05) / (darker + 0.05)


def test_all_themes_expose_same_keys(amigo):
    from krux.themes import THEMES

    for palette in THEMES.values():
        assert set(palette) == EXPECTED_THEME_KEYS


@pytest.mark.parametrize(
    "theme_name", ["Dark", "Light", "Orange", "CypherPink", "CypherPunk"]
)
def test_text_and_status_colors_meet_normal_text_contrast(amigo, theme_name):
    from krux.themes import THEMES

    palette = THEMES[theme_name]
    pairs = (
        ("foreground", "background"),
        ("foreground", "info_background"),
        ("go", "background"),
        ("error", "background"),
    )
    for foreground, background in pairs:
        assert _contrast_ratio(palette[foreground], palette[background]) >= 4.5


@pytest.mark.parametrize(
    "theme_name", ["Dark", "Light", "Orange", "CypherPink", "CypherPunk"]
)
def test_frames_meet_non_text_contrast(amigo, theme_name):
    from krux.themes import THEMES

    palette = THEMES[theme_name]
    assert _contrast_ratio(palette["frame"], palette["background"]) >= 3


@pytest.mark.parametrize(
    "theme_name", ["Dark", "Light", "Orange", "CypherPink", "CypherPunk"]
)
def test_network_colors_are_readable_on_theme_backgrounds(amigo, theme_name):
    from krux.themes import MAIN_TXT_COLOR, TEST_TXT_COLOR, THEMES

    background = THEMES[theme_name]["background"]
    assert _contrast_ratio(MAIN_TXT_COLOR, background) >= 4.5
    assert _contrast_ratio(TEST_TXT_COLOR, background) >= 4.5


@pytest.mark.parametrize(
    "theme_name", ["Dark", "Light", "Orange", "CypherPink", "CypherPunk"]
)
def test_amigo_uses_theme_info_background(amigo, theme_name):
    from krux.krux_settings import Settings
    from krux.themes import THEMES, Theme

    Settings().appearance.theme = theme_name

    assert Theme().info_bg_color == THEMES[theme_name]["info_background"]

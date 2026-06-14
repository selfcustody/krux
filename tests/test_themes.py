# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors

import pytest


@pytest.fixture
def rgb565_to_rgb():
    def _calc(color):
        color = ((color & 0xFF) << 8) | ((color >> 8) & 0xFF)
        return (
            ((color >> 11) & 0x1F) * 255 / 31,
            ((color >> 5) & 0x3F) * 255 / 63,
            (color & 0x1F) * 255 / 31,
        )

    return _calc


@pytest.fixture
def relative_luminance_component():
    def _calc(value):
        value = value / 255
        if value <= 0.03928:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    return _calc


@pytest.fixture
def relative_luminance(rgb565_to_rgb, relative_luminance_component):
    def _calc(color):
        red, green, blue = rgb565_to_rgb(color)
        return (
            0.2126 * relative_luminance_component(red)
            + 0.7152 * relative_luminance_component(green)
            + 0.0722 * relative_luminance_component(blue)
        )

    return _calc


@pytest.fixture
def contrast_ratio(relative_luminance):
    def _calc(color_a, color_b):
        luminance_a = relative_luminance(color_a)
        luminance_b = relative_luminance(color_b)
        lighter = max(luminance_a, luminance_b)
        darker = min(luminance_a, luminance_b)
        return (lighter + 0.05) / (darker + 0.05)

    return _calc


def test_text_and_status_colors_meet_normal_text_contrast(amigo, contrast_ratio):
    from krux.themes import THEMES

    cases = ("Dark", "Light", "Orange", "CypherPink", "CypherPunk")
    pairs = (
        ("foreground", "background"),
        ("foreground", "info_background"),
        ("go", "background"),
        ("error", "background"),
    )
    for case in cases:
        palette = THEMES[case]
        for foreground, background in pairs:
            assert contrast_ratio(palette[foreground], palette[background]) >= 4.5


def test_frames_meet_non_text_contrast(amigo, contrast_ratio):
    from krux.themes import THEMES

    cases = ("Dark", "Light", "Orange", "CypherPink", "CypherPunk")
    for case in cases:
        palette = THEMES[case]
        assert contrast_ratio(palette["frame"], palette["background"]) >= 3


def test_network_colors_are_readable_on_theme_backgrounds(amigo, contrast_ratio):
    from krux.themes import MAIN_TXT_COLOR, TEST_TXT_COLOR, THEMES

    cases = ("Dark", "Light", "Orange", "CypherPink", "CypherPunk")
    for case in cases:
        background = THEMES[case]["background"]
        assert contrast_ratio(MAIN_TXT_COLOR, background) >= 4.5
        assert contrast_ratio(TEST_TXT_COLOR, background) >= 4.5


def test_amigo_uses_theme_info_background(amigo):
    from krux.krux_settings import Settings
    from krux.themes import THEMES, Theme

    cases = ("Dark", "Light", "Orange", "CypherPink", "CypherPunk")
    for case in cases:
        Settings().appearance.theme = case

        assert Theme().info_bg_color == THEMES[case]["info_background"]

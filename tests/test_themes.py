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

    cases = (
        ("Dark", "foreground", "background"),
        ("Dark", "foreground", "info_background"),
        ("Dark", "go", "background"),
        ("Dark", "error", "background"),
        ("Light", "foreground", "background"),
        ("Light", "foreground", "info_background"),
        ("Light", "go", "background"),
        ("Light", "error", "background"),
        ("Orange", "foreground", "background"),
        ("Orange", "foreground", "info_background"),
        ("Orange", "go", "background"),
        ("Orange", "error", "background"),
        ("CypherPink", "foreground", "background"),
        ("CypherPink", "foreground", "info_background"),
        ("CypherPink", "go", "background"),
        ("CypherPink", "error", "background"),
        ("CypherPunk", "foreground", "background"),
        ("CypherPunk", "foreground", "info_background"),
        ("CypherPunk", "go", "background"),
        ("CypherPunk", "error", "background"),
    )
    for theme_name, foreground, background in cases:
        palette = THEMES[theme_name]
        assert contrast_ratio(palette[foreground], palette[background]) >= 4.5


def test_frames_meet_non_text_contrast(amigo, contrast_ratio):
    from krux.themes import THEMES

    cases = (
        "Dark",
        "Light",
        "Orange",
        "CypherPink",
        "CypherPunk",
    )
    for theme_name in cases:
        palette = THEMES[theme_name]
        assert contrast_ratio(palette["frame"], palette["background"]) >= 3


def test_cypherpink_frame_keeps_theme_identity(amigo, contrast_ratio):
    from krux.themes import THEMES

    palette = THEMES["CypherPink"]

    assert palette["frame"] != palette["disabled"]
    assert contrast_ratio(palette["frame"], palette["background"]) >= 4.5


def test_network_colors_use_light_theme_variants_only_on_light_theme(
    amigo, contrast_ratio
):
    from krux.krux_settings import Settings
    from krux.pages.utils import Utils
    from krux.themes import DARKERGREEN, DARKERORANGE, GREEN, ORANGE, THEMES

    cases = (
        ("Dark", ORANGE, GREEN),
        ("Light", DARKERORANGE, DARKERGREEN),
        ("Orange", ORANGE, GREEN),
        ("CypherPink", ORANGE, GREEN),
        ("CypherPunk", ORANGE, GREEN),
    )
    for theme_name, main_color, test_color in cases:
        Settings().appearance.theme = theme_name
        background = THEMES[theme_name]["background"]

        assert Utils.get_network_color("Mainnet") == main_color
        assert Utils.get_network_color("Testnet") == test_color
        assert contrast_ratio(main_color, background) >= 4.5
        assert contrast_ratio(test_color, background) >= 4.5


def test_amigo_uses_disabled_color_for_info_background(amigo):
    from krux.krux_settings import Settings
    from krux.themes import THEMES, Theme

    cases = (
        "Dark",
        "Light",
        "Orange",
        "CypherPink",
        "CypherPunk",
    )
    for theme_name in cases:
        Settings().appearance.theme = theme_name

        assert Theme().info_bg_color == THEMES[theme_name]["disabled"]

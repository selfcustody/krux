# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from .krux_settings import Settings, ThemeSettings

DEFAULT_THEME = ThemeSettings.DARK_THEME_NAME

# To create new colors from RGB values use firmware/scripts/rgbconv.py script

BLACK = 0x0000
WHITE = 0xFFFF
LIGHTBLACK = 0x0842
DARKGREY = 0xEF7B
LIGHTGREY = 0x38C6
LIGHT_GREEN = 0xEC9F
GREEN = 0xE007
DARKGREEN = 0x8005
RED = 0x00F8
LIGHT_PINK = 0xDFFC
PINK = 0x1FF8
PURPLE = 0x0F78
ORANGE = 0x20FD
DARKORANGE = 0xA0CA
YELLOW = 0x85F6
BLUE = 0xF800
LIGHTBLUE = 0xBD0E
CYAN = 0xFF07
MAGENTA = 0x1FF8  # Remove this color after logger is removed


THEMES = {
    ThemeSettings.DARK_THEME_NAME: {
        "background": BLACK,
        "foreground": WHITE,
        "frame": DARKGREY,
        "disabled": DARKGREY,
        "go": GREEN,
        "esc_no": RED,
        "del": YELLOW,
        "toggle": CYAN,
        "error": RED,
        "highlight": LIGHTBLUE,
    },
    ThemeSettings.LIGHT_THEME_NAME: {
        "background": WHITE,
        "foreground": BLACK,
        "frame": DARKGREY,
        "disabled": LIGHTGREY,
        "go": DARKGREEN,
        "esc_no": RED,
        "del": DARKORANGE,
        "toggle": BLUE,
        "error": RED,
        "highlight": BLUE,
    },
    ThemeSettings.ORANGE_THEME_NAME: {
        "background": LIGHTBLACK,
        "foreground": ORANGE,
        "frame": DARKORANGE,
        "disabled": DARKGREY,
        "go": GREEN,
        "esc_no": RED,
        "del": YELLOW,
        "toggle": CYAN,
        "error": RED,
        "highlight": YELLOW,
    },
    ThemeSettings.PINK_THEME_NAME: {
        "background": BLACK,
        "foreground": LIGHT_PINK,
        "frame": PURPLE,
        "disabled": DARKGREY,
        "go": PINK,
        "esc_no": RED,
        "del": YELLOW,
        "toggle": CYAN,
        "error": RED,
        "highlight": PINK,
    },
    ThemeSettings.GREEN_THEME_NAME: {
        "background": BLACK,
        "foreground": LIGHT_GREEN,
        "frame": DARKGREEN,
        "disabled": DARKGREY,
        "go": GREEN,
        "esc_no": RED,
        "del": YELLOW,
        "toggle": CYAN,
        "error": RED,
        "highlight": GREEN,
    },
}


class Theme:
    """Themes handler"""

    def __init__(self) -> None:
        self.update()

    def update(self):
        """Updates theme colors"""
        current_theme = Settings().appearance.theme
        if current_theme not in (list(ThemeSettings.THEME_NAMES.values())):
            # In case old version theme in use was deleted
            current_theme = ThemeSettings.DARK_THEME_NAME
            Settings().appearance.theme = current_theme
        self.bg_color = THEMES[current_theme]["background"]
        self.fg_color = THEMES[current_theme]["foreground"]
        self.frame_color = THEMES[current_theme]["frame"]
        self.disabled_color = THEMES[current_theme]["disabled"]
        self.go_color = THEMES[current_theme]["go"]
        self.no_esc_color = THEMES[current_theme]["esc_no"]
        self.del_color = THEMES[current_theme]["del"]
        self.toggle_color = THEMES[current_theme]["toggle"]
        self.error_color = THEMES[current_theme]["error"]
        self.highlight_color = THEMES[current_theme]["highlight"]


theme = Theme()

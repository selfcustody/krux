# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

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
import os

# avoids importing from flash VSF
os.chdir("/")

VERSION = "1.0"
NAME = "Example"

print("Print executed inside kapp", NAME)

from krux.pages import Page, Menu, MENU_CONTINUE, MENU_EXIT
from krux.krux_settings import t
from krux.display import STATUS_BAR_HEIGHT, FONT_HEIGHT, DEFAULT_PADDING
from krux.themes import theme
from krux.kboard import kboard

# -------------------


class KMenu(Menu):
    """Customizes the page's menu"""

    def __init__(
        self,
        ctx,
        menu,
        offset=None,
        disable_statusbar=False,
        back_label="Back",
        back_status=lambda: MENU_EXIT,
    ):
        super().__init__(ctx, menu, offset, disable_statusbar, back_label, back_status)
        self.disable_statusbar = False
        if offset is None:
            self.menu_offset = STATUS_BAR_HEIGHT
        else:
            # Always disable status bar if menu has non standard offset
            self.disable_statusbar = True
            self.menu_offset = offset if offset >= 0 else DEFAULT_PADDING

    def new_draw_wallet_indicator(self):
        """Customize the top bar"""
        if not kboard.is_m5stickv:
            self.ctx.display.draw_hcentered_text(
                NAME,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                theme.highlight_color,
                theme.info_bg_color,
            )
        else:
            self.ctx.display.draw_string(
                24,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                NAME,
                theme.highlight_color,
                theme.info_bg_color,
            )

    def new_draw_network_indicator(self):
        """Don't draw testnet"""

    # Overwrite Menu top bar functions to allow code reuse
    Menu.draw_wallet_indicator = new_draw_wallet_indicator
    Menu.draw_network_indicator = new_draw_network_indicator


# -------------------


class Kapp(Page):
    """Represents the page of the kapp"""

    def __init__(self, ctx):
        shtn_reboot_label = (
            t("Shutdown") if ctx.power_manager.has_battery() else t("Reboot")
        )
        super().__init__(
            ctx,
            KMenu(
                ctx,
                [
                    (t("About"), self.about),
                    (shtn_reboot_label, self.shutdown),
                ],
                back_label=None,
            ),
        )

    def about(self):
        """Handler for the 'about' menu item"""

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            "Kapp %s\n%s: %s\n\n" % (NAME, t("Version"), VERSION)
            + t("Use this as a model to implement new Kapps")
        )
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE


# -------------------


def run(ctx):
    """Runs this kapp"""
    print("run() function inside kapp", NAME)

    Kapp(ctx).run()

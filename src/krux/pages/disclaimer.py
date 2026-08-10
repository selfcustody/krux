# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors

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

from . import Page, Menu, MENU_EXIT, MENU_SHUTDOWN
from ..display import DEFAULT_PADDING, FONT_HEIGHT
from ..krux_settings import t, DISCLAIMER_PATH
from ..themes import theme


class Disclaimer(Page):
    """Research and development disclaimer, shown on the About page and,
    once per firmware version, before the application can be used
    """

    def __init__(self, ctx):
        super().__init__(ctx, None)

    def _pages(self, warning):
        """Splits the disclaimer text in as many pages as the display requires"""

        paragraphs = [
            t(
                "Krux is a research and development project, made by nerds building"
                " tools for their own interests, open to the world."
            ),
            t("Innovative features may have undiscovered flaws that endanger funds."),
        ]

        # Room left for the text, once the warning and its blank line are placed
        available_lines = (self.ctx.display.height() - DEFAULT_PADDING) // FONT_HEIGHT
        if warning:
            available_lines -= len(self.ctx.display.to_lines(warning)) + 1

        pages = ["\n\n".join(paragraphs)]
        if (
            len(self.ctx.display.to_lines(pages[0], available_lines + 1))
            > available_lines
        ):
            # Small displays show one paragraph per page
            pages = paragraphs
        return pages

    def show(self, acknowledge=False):
        """Displays the disclaimer. When acknowledging, a confirmation page is
        appended and the current version is stored, so it is not shown again
        """

        warning = t("Use it at your own risk.")
        # When acknowledging, the warning is shown on the confirmation page
        warning_lines = 0 if acknowledge else len(self.ctx.display.to_lines(warning))

        pages = self._pages(None if acknowledge else warning)
        for index, page in enumerate(pages):
            text_lines = len(self.ctx.display.to_lines(page))
            last_page = index == len(pages) - 1
            total_lines = text_lines
            if last_page and warning_lines:
                total_lines += warning_lines + 1
            offset_y = self.ctx.display.get_center_offset_y(total_lines)
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(page, offset_y)
            if last_page and warning_lines:
                self.ctx.display.draw_hcentered_text(
                    warning,
                    offset_y=offset_y + (text_lines + 1) * FONT_HEIGHT,
                    color=theme.highlight_color,
                )
            self.ctx.input.wait_for_button()

        if acknowledge:
            return self._acknowledge(warning)
        return True

    def _acknowledge(self, warning):
        """Requires the user to confirm the warning, then stores the acknowledgment.
        Returns False if the user chose to shut down instead
        """

        self.ctx.display.clear()
        warning_lines = self.ctx.display.draw_hcentered_text(
            warning, DEFAULT_PADDING, color=theme.highlight_color
        )
        menu_offset = DEFAULT_PADDING + (warning_lines + 1) * FONT_HEIGHT
        menu = Menu(
            self.ctx,
            [
                (t("I understand"), lambda: MENU_EXIT),
                (t("Shutdown"), self.shutdown),
            ],
            offset=menu_offset,
            back_label=None,
        )
        _, status = menu.run_loop()
        if status == MENU_SHUTDOWN:
            return False
        store_acknowledgment()
        return True


def acknowledged():
    """Returns True if the disclaimer was already acknowledged for this version"""

    from ..metadata import VERSION

    try:
        with open(DISCLAIMER_PATH, "r") as disclaimer_file:
            return disclaimer_file.read() == VERSION
    except OSError:
        return False


def store_acknowledgment():
    """Stores the version the disclaimer was acknowledged for"""

    from ..metadata import VERSION

    try:
        with open(DISCLAIMER_PATH, "w") as disclaimer_file:
            disclaimer_file.write(VERSION)
    except OSError:
        # Without storage the disclaimer will be shown again on the next boot
        pass

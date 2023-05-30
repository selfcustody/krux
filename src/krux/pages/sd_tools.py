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

from ..sd_card import SDHandler
import uos
import time
from ..krux_settings import t
from ..themes import theme
from . import (
    Page,
    MENU_CONTINUE,
    MENU_EXIT,
    SD_ROOT_PATH,
)


class SDTools(Page):
    """Toold to manage SD card"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def sd_check(self):
        """Handler for the 'SD Check' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Checking for SD card.."))
        try:
            # Check for SD hot-plug
            with SDHandler():
                sd_status = uos.statvfs(SD_ROOT_PATH)
                sd_total = int(sd_status[2] * sd_status[1] / 1024 / 1024)
                sd_free = int(sd_status[4] * sd_status[1] / 1024 / 1024)

                self.ctx.display.clear()
                self.ctx.display.draw_hcentered_text(
                    t("SD card")
                    + "\n\n"
                    + t("Size: ")
                    + "{:,}".format(sd_total)
                    + " MB"
                    + "\n\n"
                    + t("Used: ")
                    + "{:,}".format(sd_total - sd_free)
                    + " MB"
                    + "\n\n"
                    + t("Free: ")
                    + "{:,}".format(sd_free)
                    + " MB"
                )
                if self.prompt(
                    t("Explore files?"), self.ctx.display.bottom_prompt_line
                ):
                    self.select_file(select_file_handler=self._show_file_details)
        except OSError:
            self.ctx.display.flash_text(t("SD card not detected"), theme.error_color)

        return MENU_CONTINUE

    def _show_file_details(self, file):
        """Handler to print file info when selecting a file in the file explorer"""
        if SDHandler.dir_exists(file):
            return MENU_EXIT

        stats = uos.stat(file)
        size = stats[6] / 1024
        size_deximal_places = str(int(size * 100))[-2:]
        created = time.localtime(stats[9])
        modified = time.localtime(stats[8])
        file = file[4:]  # remove "/sd/" prefix
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            file
            + "\n\n"
            + t("Size: ")
            + "{:,}".format(int(size))
            + "."
            + size_deximal_places
            + " KB"
            + "\n\n"
            + t("Created: ")
            + "%s-%s-%s %s:%s"
            % (created[0], created[1], created[2], created[3], created[4])
            + "\n\n"
            + t("Modified: ")
            + "%s-%s-%s %s:%s"
            % (modified[0], modified[1], modified[2], modified[3], modified[4])
        )
        self.ctx.input.wait_for_button()
        # if self.prompt(t("Delete File?"), self.ctx.display.bottom_prompt_line):
        #     with SDHandler() as sd:
        #         sd.delete(file)
        #     return MENU_EXIT
        return MENU_CONTINUE

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

import board
import gc
from . import Page, Menu, MENU_EXIT, MENU_CONTINUE
from ..sd_card import SDHandler
from ..krux_settings import t, Settings

LIST_FILE_DIGITS = 9  # len on large devices per menu item
LIST_FILE_DIGITS_SMALL = 5  # len on small devices per menu item

SD_ROOT_PATH = "/sd"
THOUSANDS_SEPARATOR = " "


class FileManager(Page):
    """Helper class to handle files interface"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def select_file(
        self, select_file_handler=lambda *args: MENU_EXIT, file_extension=""
    ):
        """Starts a file explorer on the SD folder and returns the file selected"""
        import os

        custom_start_digits = LIST_FILE_DIGITS
        custom_end_digts = LIST_FILE_DIGITS + 4  # 3 more because of file type
        if board.config["type"] == "m5stickv":
            custom_start_digits = LIST_FILE_DIGITS_SMALL
            custom_end_digts = LIST_FILE_DIGITS_SMALL + 4  # 3 more because of file type

        path = SD_ROOT_PATH
        while True:
            # if is a dir then list all files in it
            if SDHandler.dir_exists(path):
                items = []
                menu_items = []

                if path != SD_ROOT_PATH:
                    items.append("..")
                    menu_items.append(("..", lambda: MENU_EXIT))

                dir_files = os.listdir(path)
                for filename in dir_files:
                    extension_match = False
                    if isinstance(file_extension, str):
                        # No extension filter or matches
                        extension_match = filename.endswith(file_extension)
                    else:
                        # Check for any matches for tuple / list
                        for ext in file_extension:
                            if filename.endswith(ext):
                                extension_match = True
                                break

                    if (
                        extension_match
                        # Is a directory
                        or SDHandler.dir_exists(path + "/" + filename)
                    ):
                        items.append(filename)
                        display_filename = filename
                        if len(filename) >= custom_start_digits + 2 + custom_end_digts:
                            display_filename = (
                                filename[:custom_start_digits]
                                + ".."
                                + filename[len(filename) - custom_end_digts :]
                            )
                        menu_items.append(
                            (
                                display_filename,
                                lambda file=filename: select_file_handler(
                                    path + "/" + file
                                ),
                            )
                        )

                # We need to add this option because /sd can be empty!
                items.append("Back")
                menu_items.append((t("Back"), lambda: MENU_EXIT))

                submenu = Menu(self.ctx, menu_items)
                index, _ = submenu.run_loop()

                # selected "Back"
                if index == len(items) - 1:
                    return ""
                # selected ".."
                if index == 0 and path != SD_ROOT_PATH:
                    path = path.split("/")
                    path.pop()
                    path = "/".join(path)
                else:
                    path += "/" + items[index]
            # it is a file!
            else:
                submenu, menu_items, items = (None, None, None)
                del submenu, menu_items, items
                gc.collect()
                return path

    def show_file_details(self, file):
        """Handler to print file info when selecting a file in the file explorer"""
        if SDHandler.dir_exists(file):
            return MENU_EXIT

        self.display_file(file)
        self.ctx.input.wait_for_button()
        # if self.prompt(t("Delete File?"), self.ctx.display.bottom_prompt_line):
        #     with SDHandler() as sd:
        #         sd.delete(file)
        #     return MENU_EXIT
        return MENU_CONTINUE

    def display_file(self, file):
        """Display the file details on the device's screen"""
        import uos
        import time

        stats = uos.stat(file)
        size_KB = stats[6] / 1024
        size_KB_fraction = str(int(size_KB * 100))[-2:]
        created = time.localtime(stats[9])
        modified = time.localtime(stats[8])
        file = file[4:]  # remove "/sd/" prefix
        decimal_separator = ","
        if Settings().i18n.locale == "en-US":
            decimal_separator = "."

        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            file
            + "\n\n"
            + t("Size: ")
            + "{:,}".format(int(size_KB)).replace(",", THOUSANDS_SEPARATOR)
            + decimal_separator
            + size_KB_fraction
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

        return file

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

import gc
from . import Page, Menu, MENU_EXIT, MENU_CONTINUE
from ..sd_card import SDHandler
from ..krux_settings import t
from ..format import generate_thousands_separator, render_decimal_separator
from ..display import BOTTOM_PROMPT_LINE
from ..kboard import kboard

LIST_FILE_DIGITS = 9  # len on large devices per menu item
LIST_FILE_DIGITS_SMALL = 5  # len on small devices per menu item

SD_ROOT_PATH = "/sd"


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
        if kboard.is_m5stickv:
            custom_start_digits = LIST_FILE_DIGITS_SMALL
            custom_end_digts = LIST_FILE_DIGITS_SMALL + 4  # 3 more because of file type

        path = SD_ROOT_PATH
        while True:
            # if is a dir then list all files in it
            if SDHandler.dir_exists(path):
                items = []  # simple reference for the files shown on the menu_items
                menu_items = []  # the user menu to interact

                if path != SD_ROOT_PATH:
                    items.append("..")
                    menu_items.append(("../", lambda: MENU_EXIT))

                # sorts by name ignorecase
                dir_files = sorted(os.listdir(path), key=str.lower)

                # separate directories from files
                directories = []
                files = []

                for filename in dir_files:
                    if SDHandler.file_exists(path + "/" + filename):
                        files.append(filename)
                    else:
                        directories.append(filename)

                del dir_files

                # show sorted folders first then sorted files
                for i, filename in enumerate(directories + files):
                    is_directory = i < len(directories)

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

                    if extension_match or is_directory:
                        items.append(filename)
                        display_filename = filename + "/" if is_directory else filename

                        if (
                            len(display_filename)
                            >= custom_start_digits + 2 + custom_end_digts
                        ):
                            display_filename = (
                                display_filename[:custom_start_digits]
                                + ".."
                                + display_filename[
                                    len(display_filename) - custom_end_digts :
                                ]
                            )
                        menu_items.append(
                            (
                                display_filename,
                                (
                                    (lambda: MENU_EXIT)
                                    if is_directory
                                    else (
                                        lambda file=filename: select_file_handler(
                                            path + "/" + file
                                        )
                                    )
                                ),
                            )
                        )

                # We need to add this option because /sd can be empty!
                items.append("Back")

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

        self.display_file(file)
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def load_file(self, file):
        """Handler to ask if will load selected file in the file explorer"""

        self.display_file(file)
        if self.prompt(t("Load?"), BOTTOM_PROMPT_LINE):
            return MENU_EXIT
        return MENU_CONTINUE

    def display_file(self, file):
        """Display the file details on the device's screen"""
        import uos
        import time
        from ..display import DEFAULT_PADDING, FONT_HEIGHT
        from ..themes import theme

        stats = uos.stat(file)
        size_KB = stats[6] / 1024
        size_KB_fraction = str(int(size_KB * 100))[-2:]
        created = time.localtime(stats[9])
        modified = time.localtime(stats[8])
        format_datetime = "%s-%02d-%02d %02d:%02d"
        file = file[4:]  # remove "/sd/" prefix

        self.ctx.display.clear()
        offset_y = DEFAULT_PADDING
        offset_y += (
            self.ctx.display.draw_hcentered_text(
                file
                + "\n\n"
                + t("Size:")
                + " "
                + generate_thousands_separator(int(size_KB))
                + render_decimal_separator()
                + size_KB_fraction
                + " KB",
                offset_y,
                highlight_prefix=":",
            )
            + 1
        ) * FONT_HEIGHT
        offset_y += (
            self.ctx.display.draw_hcentered_text(
                t("Created:"), offset_y, color=theme.highlight_color
            )
        ) * FONT_HEIGHT
        offset_y += (
            self.ctx.display.draw_hcentered_text(
                format_datetime % created[:5] + "\n\n", offset_y
            )
            * FONT_HEIGHT
        )
        offset_y += (
            self.ctx.display.draw_hcentered_text(
                t("Modified:"), offset_y, color=theme.highlight_color
            )
        ) * FONT_HEIGHT
        self.ctx.display.draw_hcentered_text(format_datetime % modified[:5], offset_y)

        return file

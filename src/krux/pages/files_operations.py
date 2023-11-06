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

from . import (
    Page,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
)
from ..krux_settings import t
from ..sd_card import SDHandler

FILE_SPECIAL = "0123456789()-.[]_~"


class SaveFile(Page):
    """File saver user interface"""

    def __init__(self, ctx):
        super().__init__(ctx, None)

    def save_file(
        self,
        data,
        empty_name,
        filename="",
        file_description="",
        file_extension="",
        file_suffix="",
        save_as_binary=True,
    ):
        """File saver handler page"""
        try:
            with SDHandler() as sd:
                # Wait until user defines a filename or select NO on the prompt
                filename_undefined = True
                while filename_undefined:
                    self.ctx.display.clear()
                    if self.prompt(
                        file_description + "\n" + t("Save to SD card?") + "\n\n",
                        self.ctx.display.height() // 2,
                    ):
                        filename, filename_undefined = self.set_filename(
                            filename,
                            empty_name,
                            file_suffix,
                            file_extension,
                        )

                        # if user defined a filename and it is ok, save!
                        if not filename_undefined:
                            if save_as_binary:
                                sd.write_binary(filename, data)
                            else:
                                sd.write(filename, data)
                            self.flash_text(t("Saved to SD card:\n%s") % filename)
                    else:
                        filename_undefined = False
        except:
            self.flash_text(t("SD card not detected."))

    def set_filename(
        self, curr_filename="", empty_filename="some_file", suffix="", file_extension=""
    ):
        """Helper to set the filename based on a suggestion and the user input"""
        started_filename = curr_filename
        filename_undefined = True

        # remove the file_extension if exists
        curr_filename = (
            curr_filename[: len(curr_filename) - len(file_extension)]
            if curr_filename.endswith(file_extension)
            else curr_filename
        )

        # remove the suffix if exists (because we will add it later)
        curr_filename = (
            curr_filename[: len(curr_filename) - len(suffix)]
            if curr_filename.endswith(suffix)
            else curr_filename
        )

        curr_filename = self.capture_from_keypad(
            t("Filename"),
            [LETTERS, UPPERCASE_LETTERS, FILE_SPECIAL],
            starting_buffer=("%s" + suffix) % curr_filename
            if curr_filename
            else empty_filename + suffix,
        )

        # Verify if user defined a filename and it is not just dots
        if (
            curr_filename
            and curr_filename != ESC_KEY
            and not all(c in "." for c in curr_filename)
        ):
            # add the extension ".psbt"
            curr_filename = (
                curr_filename
                if curr_filename.endswith(file_extension)
                else curr_filename + file_extension
            )
            # check and warn for overwrite filename
            # add the "/sd/" prefix
            if SDHandler.file_exists("/sd/" + curr_filename):
                self.ctx.display.clear()
                if self.prompt(
                    t("Filename %s exists on SD card, overwrite?") % curr_filename
                    + "\n\n",
                    self.ctx.display.height() // 2,
                ):
                    filename_undefined = False
            else:
                filename_undefined = False

        if curr_filename == ESC_KEY:
            curr_filename = started_filename

        return (curr_filename, filename_undefined)

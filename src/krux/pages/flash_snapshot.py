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

from . import Page, MENU_CONTINUE, DEFAULT_PADDING
from ..krux_settings import t
from ..themes import theme
from ..display import FONT_HEIGHT


class FlashSnapshot(Page):
    """Generate a human recognizable snapshot of the flash memory tied to a PIN"""

    def __init__(self, ctx, pin_hash):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.pin_hash = pin_hash

    def hash_pin_with_flash(self):
        """Hashes the pin, unique ID and flash memory together"""
        import hashlib
        import flash
        from ..firmware import FLASH_SIZE
        from machine import unique_id

        sha256 = hashlib.sha256()
        sha256.update(self.pin_hash)
        sha256.update(unique_id())
        counter = 0
        for address in range(0, FLASH_SIZE, 0x1000):
            counter += 1
            sha256.update(flash.read(address, 0x1000))
            if counter % 100 == 0:
                # Update progress
                print(counter // 41)
                self.ctx.display.draw_centered_text("%d%%" % (counter // 41))
        return sha256.digest()

    def hash_to_fingerprint(self, hash_bytes, y_offset=DEFAULT_PADDING):
        """Generates a 5x5 pixelated fingerprint based on a 256-bit hash."""

        # Create a 5x5 grid, but we'll only compute the first 3 columns
        block_size = self.ctx.display.width() // 7
        for row in range(5):
            for col in range(3):  # Only compute the left half and middle column
                byte_index = row * 3 + col
                bit_value = hash_bytes[byte_index] % 2  # 0 or 1

                # Set the color based on the bit value
                color = theme.fg_color if bit_value == 0 else theme.disabled_color

                # Calculate the position and draw the rectangle
                x = (col + 1) * block_size
                y = y_offset + row * block_size
                self.ctx.display.fill_rectangle(x, y, block_size, block_size, color)

                if col < 2:
                    # Draw the mirrored columns (0 and 1)
                    mirrored_col = 5 - col
                    x_mirror = mirrored_col * block_size
                    self.ctx.display.fill_rectangle(
                        x_mirror, y, block_size, block_size, color
                    )
        # Returns the size of the fingerprint
        return 5 * block_size

    def hash_to_words(self, hash_bytes):
        """Converts a hash to a list of words"""
        from embit.bip39 import mnemonic_from_bytes

        words = mnemonic_from_bytes(hash_bytes).split()
        return " ".join(words[:2])

    def generate(self):
        """Generates the flash snapshot"""
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(t("Generating Flash Snapshot.."))
        binary_flash_hash = self.hash_pin_with_flash()
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(t("Snapshot"))
        y_offset = DEFAULT_PADDING + 2 * FONT_HEIGHT
        y_offset += self.hash_to_fingerprint(binary_flash_hash, y_offset)
        y_offset += FONT_HEIGHT
        anti_tamper_words = self.hash_to_words(binary_flash_hash)
        self.ctx.display.draw_hcentered_text(anti_tamper_words, y_offset)
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

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
"""NFC card pages - tap prompt and card I/O.

The RF field is energized in exactly one place, NFCTapPage, and comes down on
every exit path. Outside these pages the reader is inert: with NFC switched off
the I2C bus is never opened, so a module left plugged in is untouched rather
than merely unused.

Only the KEF envelope crosses the antenna. The mnemonic is turned into entropy
and sealed before the reader is attached, and the reader is detached again
before the decryption password is asked for.
"""

from ..display import BOTTOM_PROMPT_LINE
from ..krux_settings import t, Settings
from ..themes import theme
from . import Page, MENU_CONTINUE

# Also how long a cancel keypress can wait, so it stays short
POLL_INTERVAL_MS = 200


class NFCTapPage(Page):
    """Card presence prompt and RF field lifecycle"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.nfc = None

    def open_reader(self):
        """Attaches the reader, reporting failure on screen.

        The menu entries that lead here are already gated on the setting, but
        the check is repeated at the hardware boundary so no future caller can
        reach the bus around it.
        """
        from ..nfc import NFC, NFCError

        if not Settings().hardware.nfc.enabled:
            self.flash_error(t("NFC reader not found"))
            return False
        nfc = NFC()
        try:
            nfc.init()
        except NFCError:
            self.flash_error(t("NFC reader not found"))
            return False
        self.nfc = nfc
        return True

    def close_reader(self):
        """Drops the field and detaches the reader"""
        if self.nfc is not None:
            self.nfc.deinit()
            self.nfc = None

    def wait_for_tag(self, title):
        """Energizes the field and polls until a card shows up or the user leaves"""
        from ..nfc import NFCError

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            title + "\n\n" + t("Hold a card to the reader")
        )
        self.ctx.display.draw_hcentered_text(
            t("Press PAGE to cancel."), BOTTOM_PROMPT_LINE, color=theme.highlight_color
        )
        try:
            self.nfc.field(True)
        except NFCError:
            self.flash_error(t("NFC reader not found"))
            return False

        while True:
            try:
                self.nfc.poll()
                return True
            except NFCError:
                # An empty field, two cards at once, and a family Krux does not
                # accept all look the same from here: keep waiting.
                pass
            if (
                self.ctx.input.wait_for_button(
                    block=False, wait_duration=POLL_INTERVAL_MS
                )
                is not None
            ):
                break

        try:
            self.nfc.field(False)
        except NFCError:
            pass
        return False

    def test_reader(self):
        """Probes for a reader and reports what it found, field never coming up"""
        if not self.open_reader():
            return MENU_CONTINUE
        self.close_reader()
        self.flash_success(t("Reader detected"))
        return MENU_CONTINUE


class StoreOnNFC(NFCTapPage):
    """Writes a KEF envelope to a card"""

    def _write(self, kef_envelope, record_type, failure_text):
        """Asks for a card and writes the envelope onto it, reporting success.

        The card dance is the same whatever the envelope holds; only the record
        type and what to say when it fails belong to the caller.
        """
        from ..nfc import NFCError, NFCSizeError

        if not self.open_reader():
            return False
        try:
            if not self.wait_for_tag(t("Store on NFC Card")):
                return False
            if self.nfc.has_record():
                # Say what is at stake before asking, as the SD card does when
                # a filename is already taken. "Overwrite?" on its own does not
                # tell anyone what they are about to lose.
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(
                    t("This card already holds a Krux record.")
                )
                if not self.prompt(t("Overwrite?"), BOTTOM_PROMPT_LINE):
                    return False
                # Ask for the card again rather than trusting the earlier poll:
                # the prompt was up in between, and the card only had to drift a
                # centimetre.
                if not self.wait_for_tag(t("Store on NFC Card")):
                    return False
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Processing…"))
            try:
                self.nfc.write_record(kef_envelope, record_type)
            except NFCSizeError:
                self.flash_error(t("Card too small"))
                return False
            except NFCError:
                self.flash_error(failure_text)
                return False
        finally:
            self.close_reader()
        return True

    def write(self, kef_envelope, mnemonic_id):
        """Stores an encrypted mnemonic"""
        from ..nfc import RECORD_KEF

        if self._write(kef_envelope, RECORD_KEF, t("Failed to store mnemonic")):
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Encrypted mnemonic stored with ID:") + " " + mnemonic_id,
                highlight_prefix=":",
            )
            self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def write_xpub(self, xpub):
        """Stores an extended public key.

        Plaintext, as the .pub file and the QR code from the same page already
        are, and with no checksum requirement: nothing consumes an xpub card
        automatically. A descriptor card is read straight into a wallet, so a
        flipped bit there has to be caught; an xpub card is read by a person.
        """
        from ..nfc import RECORD_XPUB

        if self._write(xpub, RECORD_XPUB, t("Failed to store public key")):
            self.flash_success(t("Public key stored on card"))
        return MENU_CONTINUE

    def write_datum(self, payload):
        """Stores whatever the datum tool is holding.

        Its own type, so a datum card walks into neither the mnemonic loader
        nor the wallet. The datum tool takes arbitrary bytes and gives no
        promise about them beyond that.
        """
        from ..nfc import RECORD_DATUM

        if self._write(payload, RECORD_DATUM, t("Failed to store datum")):
            self.flash_success(t("Datum stored on card"))
        return MENU_CONTINUE

    def write_descriptor(self, kef_envelope):
        """Stores an encrypted wallet output descriptor"""
        from ..nfc import RECORD_DESCRIPTOR

        if self._write(
            kef_envelope, RECORD_DESCRIPTOR, t("Failed to store descriptor")
        ):
            self.flash_success(t("Descriptor stored on card"))
        return MENU_CONTINUE


class EraseNFC(NFCTapPage):
    """Wipes the data area of a card"""

    def erase(self):
        """Asks for a card, confirms, and zeroes every data block on it"""
        from ..nfc import NFCError

        if not self.open_reader():
            return MENU_CONTINUE
        try:
            if not self.wait_for_tag(t("Erase NFC Card")):
                return MENU_CONTINUE

            # No has_record() probe first. Erasing takes the whole data area,
            # so "no Krux record here" would be the wrong thing to reassure
            # anyone with - the card may be carrying plenty that Krux cannot
            # see, and all of it is about to go.
            self.ctx.display.clear()
            if not self.prompt(
                t("Erase all data on this card?"), self.ctx.display.height() // 2
            ):
                return MENU_CONTINUE
            # The prompt was up in between, and the card only had to drift a
            # centimetre.
            if not self.wait_for_tag(t("Erase NFC Card")):
                return MENU_CONTINUE

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Processing…"))
            try:
                self.nfc.erase()
            except NFCError:
                # A card pulled away mid erase leaves part of the data area
                # written and part not, so this is not "nothing happened".
                self.flash_error(t("Failed to erase card"))
                return MENU_CONTINUE
        finally:
            self.close_reader()

        self.flash_success(t("Card erased"))
        return MENU_CONTINUE


class LoadFromNFC(NFCTapPage):
    """Reads a KEF envelope off a card"""

    def read(self, record_type=None):
        """Returns the envelope bytes, or None. Detaches the reader first, so
        the password is asked for with the antenna already down.

        record_type is what the caller can parse; a card holding anything else
        reports as empty rather than handing back a payload nobody asked for.
        """
        from ..nfc import NFCError, RECORD_KEF

        if record_type is None:
            record_type = RECORD_KEF

        if not self.open_reader():
            return None
        try:
            if not self.wait_for_tag(t("From NFC Card")):
                return None
            try:
                return self.nfc.read_record(record_type)
            except NFCError:
                # A card with no record, an unreadable one, one holding a record
                # of another type, and one whose header was refused all say the
                # same thing here on purpose.
                self.flash_error(t("No backup on this card"))
                return None
        finally:
            self.close_reader()

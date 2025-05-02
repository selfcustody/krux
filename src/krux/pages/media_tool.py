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

from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from ..display import FONT_HEIGHT, DEFAULT_PADDING
from ..krux_settings import t


def urobj_to_data(ur_obj):
    """returns flatened data from a UR object. belongs in qr or qr_capture???"""
    import urtypes

    print("type: {}, cbor: {}".format(ur_obj.type, ur_obj.cbor))
    if ur_obj.type == "crypto-bip39":
        data = urtypes.crypto.BIP39.from_cbor(ur_obj.cbor).words
    elif ur_obj.type == "crypto-account":
        data = (
            urtypes.crypto.Account.from_cbor(ur_obj.cbor)
            .output_descriptors[0]
            .descriptor()
        )
    elif ur_obj.type == "crypto-output":
        data = urtypes.crypto.Output.from_cbor(ur_obj.cbor).descriptor()
    elif ur_obj.type == "crypto-psbt":
        data = urtypes.crypto.PSBT.from_cbor(ur_obj.cbor).data
    elif ur_obj.type == "bytes":
        data = urtypes.bytes.Bytes.from_cbor(ur_obj.cbor).data
    else:
        data = None
    return data


def convert_encoding(contents, conversion):
    """encoding conversions to/from (hex, base58, base43, base64, utf8)"""
    from krux.baseconv import base_encode, base_decode
    from binascii import hexlify, unhexlify

    from_bytes = isinstance(contents, bytes)
    if conversion in (43, 58, 64):
        if from_bytes:
            return base_encode(contents, conversion)
        return base_decode(contents, conversion)
    if conversion == "hex":
        if from_bytes:
            return hexlify(contents).decode()
        return unhexlify(contents)
    if conversion == "utf8":
        if from_bytes:
            return contents.decode()
        return contents.encode()
    return None


class MediaToolMenu(Page):
    """Krux Media Tool Menu"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Scan a QR"), self.scan_qr),
                    (t("Text Entry"), self.text_entry),
                    (t("Read file"), self.read_file),
                ],
            ),
        )

    def scan_qr(self):
        """Handler for the 'Scan a QR' menu item"""

        from .qr_capture import QRCodeCapture

        qr_scanner = QRCodeCapture(self.ctx)
        contents, fmt = qr_scanner.qr_capture_loop()
        print(
            "\nscanned raw contents: {} {}, format: {}".format(
                type(contents), repr(contents), fmt
            )
        )
        title = "QR Contents"
        if isinstance(contents, str):
            if len(contents) != len(contents.encode()):
                # Must be in simulator; micropython has no latin-1
                contents = contents.encode("latin-1")
        if fmt == 2:
            title += ", UR:" + contents.type
            contents = urobj_to_data(contents)

        page = MediaTool(self.ctx)
        page.contents, page.title = contents, title
        return page.manipulate_contents()

    def text_entry(self):
        """Handler for the 'Text Entry' menu item"""
        text = self.capture_from_keypad(
            t("Text"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
        )
        if text in ("", ESC_KEY):
            return MENU_CONTINUE

        page = MediaTool(self.ctx)
        page.contents, page.title = text, t("Custom Text")
        return page.manipulate_contents()

    def read_file(self):
        """Handler for the 'Read SD File' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text("Todo: read file from sdcard")
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE


class MediaTool(Page):
    """Krux Media Tool"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.contents = None
        self.about = None
        self.title = None
        self.decrypted = False
        self.sensitive = False
        self.history = []

    def view_qr(self):
        """Reusable handler for viewing a QR code"""
        from .qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, data=self.contents, title=self.title)
        seed_qr_view.display_qr(allow_export=True)

        return MENU_CONTINUE

    def view_contents(self):
        """Displays infobox and contents"""
        from binascii import hexlify

        info_len = self._info_box()
        self.ctx.display.draw_hcentered_text(
            (
                '"' + self.contents + '"'
                if isinstance(self.contents, str)
                else "0x " + hexlify(self.contents).decode()
            ),
            offset_y=DEFAULT_PADDING + (info_len + 1) * FONT_HEIGHT,
        )
        self.ctx.input.wait_for_button()

    def _info_box(self):
        self.ctx.display.clear()
        return self.ctx.display.draw_hcentered_text(
            "\n".join(
                [
                    self.title,
                    " ".join(
                        [
                            t("decrypted") if self.decrypted else "",
                            t("sensitive") if self.sensitive else "",
                        ]
                    ),
                    self.about,
                ]
            ),
            info_box=True,
        )

    def _analyze_contents(self):
        """analyzes `.contents`, sets `.about`(type and length) and `.sensitivity` (if a secret)"""

        if isinstance(self.contents, bytes):
            self.about = t("binary: {} bytes").format(len(self.contents))

            # does it look like 128 or 256 bits of mnemonic entropy / CompactSeedQR?
            if len(self.contents) in (16, 32) and max((x for x in self.contents)) > 127:
                self.sensitive = True

        elif isinstance(self.contents, str):
            self.about = t("text: {} chars").format(len(self.contents))

            # does it look like a 12 or 24 word mnemonic / Mnemonic QR?
            if len(self.contents.split()) in (12, 24):
                self.sensitive = True

            # does it look like a 12 or 24 word decimal mnemonic / StandadardSeedQR?
            elif len(set((x in "0123456789" for x in self.contents))) == 1 and (
                len(self.contents) in (12 * 4, 24 * 4)
            ):
                self.sensitive = True

        # todo: can we know that it's psbt/xpub/xprv/addy/mnemonic/descriptor/etc

    def manipulate_contents(self, try_decrypt=True):
        """allows to view, convert, encrypt/decrypt, and export short str/bytes contents"""
        from binascii import unhexlify
        from krux.baseconv import base_decode
        from .encryption_ui import KEFEnvelope

        # print("into manipulate_contents(", contents, type(contents), history)

        # check if KEF wrapped
        if try_decrypt and isinstance(self.contents, bytes):
            while True:
                kef = KEFEnvelope(self.ctx)
                plaintext = kef.unseal_ui(self.contents)
                if plaintext is None:
                    break
                self.decrypted = True
                self.contents = plaintext
                self.history = []

        # analyze bytes contents
        self._analyze_contents()

        # build menu options
        todo_menu = []
        if isinstance(self.contents, bytes):
            todo_menu.append((t("to hex"), lambda: "hex"))
            todo_menu.append((t("to base43"), lambda: 43))
            todo_menu.append((t("to base58"), lambda: 58))
            todo_menu.append((t("to base64"), lambda: 64))
            try:
                self.contents.decode()
                todo_menu.append((t("to utf8"), lambda: "utf8"))
            except:
                pass

        elif isinstance(self.contents, str):
            try:
                unhexlify(self.contents)
                todo_menu.append((t("from hex"), lambda: "hex"))
            except:
                pass

            try:
                base_decode(self.contents, 43)
                todo_menu.append((t("from base43"), lambda: 43))
            except:
                pass

            try:
                base_decode(self.contents, 58)
                todo_menu.append((t("from base58"), lambda: 58))
            except:
                pass

            try:
                base_decode(self.contents, 64)
                todo_menu.append(("from base64", lambda: 64))
            except:
                pass

            try:
                self.contents.encode()
                todo_menu.append((t("from utf8"), lambda: "utf8"))
            except:
                pass

        todo_menu.append((t("Encrypt"), lambda: "encrypt"))
        if not (self.decrypted and self.sensitive):
            todo_menu.append((t("Export QR"), lambda: "export"))

        if self.history:
            for i, option in enumerate(todo_menu):
                if option[1]() == self.history[-1]:
                    todo_menu[i] = (option[0] + " (" + t("Undo") + ")", lambda: "undo")
                    break

        self.view_contents()

        # display infobox and run the todo_menu
        info_len = self._info_box()
        menu = Menu(
            self.ctx, todo_menu, offset=info_len * FONT_HEIGHT + DEFAULT_PADDING
        )
        idx, status = menu.run_loop()

        # if user chose to exit
        if idx == len(todo_menu) - 1:
            return MENU_CONTINUE

        # if user chose to convert data
        if status not in ("encrypt", "export"):
            if status == "undo":
                status = self.history.pop()
            else:
                self.history.append(status)
            self.contents = convert_encoding(self.contents, status)
            return self.manipulate_contents(try_decrypt=try_decrypt)

        # if user chose to encrypt
        if status == "encrypt":
            kef = KEFEnvelope(self.ctx)
            self.contents = (
                self.contents
                if isinstance(self.contents, bytes)
                else self.contents.encode()
            )
            self.contents = kef.seal_ui(self.contents, override_settings=True)
            self.title = kef.label if kef.label else ""
            return self.manipulate_contents(try_decrypt=False)

        # user chose to export
        return self.view_qr()

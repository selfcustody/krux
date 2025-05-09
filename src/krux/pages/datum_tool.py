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
    """encoding conversions to/from (hex/base58/base43/base64/utf8)"""
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


class DatumToolMenu(Page):
    """Krux Datum Tool Menu"""

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

        page = DatumTool(self.ctx)
        page.contents, page.title = contents, title
        return page.manipulate_contents()

    def text_entry(self):
        """Handler for the 'Text Entry' menu item"""
        text = self.capture_from_keypad(
            t("Text"),
            [
                LETTERS,
                UPPERCASE_LETTERS,
                NUM_SPECIAL_1,
                NUM_SPECIAL_2,
                "123456789abcdef0",
            ],
        )
        if text in ("", ESC_KEY):
            return MENU_CONTINUE

        page = DatumTool(self.ctx)
        page.contents, page.title = text, t("Custom Text")
        return page.manipulate_contents()

    def read_file(self):
        """Handler for the 'Read SD File' menu item"""
        from .utils import Utils

        if not self.has_sd_card():
            self.ctx.display.clear()
            self.flash_error(t("SD card not detected."))
            return MENU_CONTINUE

        utils = Utils(self.ctx)
        try:
            filename, contents = utils.load_file()
        except OSError:
            pass

        if not contents:
            return MENU_CONTINUE

        # utils.load_file() always returns binary, try as utf8 text
        try:
            contents = contents.decode()
        except:
            pass

        page = DatumTool(self.ctx)
        page.contents = contents
        # pylint: disable=C0207
        page.title = t("File Contents") + "\n" + filename.split("/")[-1]
        return page.manipulate_contents()


class DatumTool(Page):
    """Krux Datum Tool"""

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

    def save_sd(self):
        """Reusable handler for saving to SD file"""
        from .file_operations import SaveFile

        if isinstance(self.contents, bytes):
            extension = ".bin"
            binary = True
        else:
            extension = ".txt"
            binary = False

        save_page = SaveFile(self.ctx)
        save_page.save_file(
            self.contents,
            self.title.split()[-1],
            file_extension=extension,
            save_as_binary=binary,
            prompt=True,
        )

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
        """clears screen, displays info_box, returns height-in-lines"""
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

    def _decrypt_as_kef_envelope(self):
        """Assuming self.contents are encrypted, offer to decrypt"""
        from .encryption_ui import KEFEnvelope
        from binascii import hexlify

        while True:
            kef = KEFEnvelope(self.ctx)
            plaintext = kef.unseal_ui(self.contents)
            if plaintext is None:
                break
            try:
                self.title = kef.label.decode()
            except:
                self.title = "0x" + hexlify(kef.label).decode()

            self.decrypted = True
            self.contents = plaintext
            self.history = []

    def _build_options_menu(self):
        """Build a menu of how to manipulate contents"""
        from binascii import unhexlify
        from krux.baseconv import base_decode

        # build menu options
        menu = []
        if isinstance(self.contents, bytes):
            menu.append((t("to hex"), lambda: "hex"))
            menu.append((t("to base43"), lambda: 43))
            menu.append((t("to base58"), lambda: 58))
            menu.append((t("to base64"), lambda: 64))
            try:
                self.contents.decode()
                menu.append((t("to utf8"), lambda: "utf8"))
            except:
                pass

        elif isinstance(self.contents, str):
            try:
                unhexlify(self.contents)
                menu.append((t("from hex"), lambda: "hex"))
            except:
                pass

            try:
                base_decode(self.contents, 43)
                menu.append((t("from base43"), lambda: 43))
            except:
                pass

            try:
                base_decode(self.contents, 58)
                menu.append((t("from base58"), lambda: 58))
            except:
                pass

            try:
                base_decode(self.contents, 64)
                menu.append(("from base64", lambda: 64))
            except:
                pass

            try:
                self.contents.encode()
                menu.append((t("from utf8"), lambda: "utf8"))
            except:
                pass

        if isinstance(self.contents, bytes):
            menu.append((t("Encrypt"), lambda: "encrypt"))

        if not (self.decrypted and self.sensitive):
            menu.append((t("Export to QR"), lambda: "export_qr"))
            menu.append((t("Export to SD"), lambda: "export_sd"))

        if self.history:
            for i, option in enumerate(menu):
                if option[1]() == self.history[-1]:
                    menu[i] = (option[0] + " (" + t("Undo") + ")", lambda: "undo")
                    break

        return menu

    def manipulate_contents(self, try_decrypt=True):
        """allows to view, convert, encrypt/decrypt, and export short str/bytes contents"""

        # print("into manipulate_contents(", contents, type(contents), history)

        # check if KEF wrapped
        if try_decrypt and isinstance(self.contents, bytes):
            self._decrypt_as_kef_envelope()

        # analyze bytes contents
        self._analyze_contents()

        # get menu of what can be done to contents
        todo_menu = self._build_options_menu()

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
        if status not in ("encrypt", "export_qr", "export_sd"):
            if status == "undo":
                status = self.history.pop()
            else:
                self.history.append(status)
            self.contents = convert_encoding(self.contents, status)
            return self.manipulate_contents()

        # if user chose to encrypt
        if status == "encrypt":
            from .encryption_ui import KEFEnvelope

            kef = KEFEnvelope(self.ctx)
            kef.label = self.title
            self.contents = kef.seal_ui(self.contents, override_defaults=True)
            self.title = kef.label if kef.label else ""
            self.decrypted = False
            return self.manipulate_contents(try_decrypt=False)

        # if user chose to export_qr
        if status == "export_qr":
            return self.view_qr()

        # user chose export_sd
        return self.save_sd()

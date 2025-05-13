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
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from ..display import FONT_WIDTH, FONT_HEIGHT, DEFAULT_PADDING, TOTAL_LINES
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
    """encoding conversions to/from (hex/base43/base58/base64/utf8)"""
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
                    (t("Read File"), self.read_file),
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
        return page.view_contents()

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
        return page.view_contents()

    def read_file(self):
        """Handler for the 'Read File' menu item"""
        from .utils import Utils

        if not self.has_sd_card():
            self.ctx.display.clear()
            self.flash_error(t("SD card not detected."))
            return MENU_CONTINUE

        utils = Utils(self.ctx)
        try:
            filename, contents = utils.load_file(prompt=False)
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
        return page.view_contents()


class DatumTool(Page):
    """Krux Datum Tool"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.contents = None
        self.about = None
        self.title = None
        self.datum = None
        self.decrypted = False
        self.sensitive = False
        self.history = []
        self.oneline_viewable = None

    def view_qr(self):
        """Reusable handler for viewing a QR code"""
        from ..qr import QR_CAPACITY_BYTE, QR_CAPACITY_ALPHANUMERIC

        if isinstance(self.contents, bytes):
            seedqrview_thresh = QR_CAPACITY_BYTE[3]
        else:
            seedqrview_thresh = QR_CAPACITY_ALPHANUMERIC[3]

        if len(self.contents) <= seedqrview_thresh:
            from .qr_view import SeedQRView

            seed_qr_view = SeedQRView(self.ctx, data=self.contents, title=self.title)
            seed_qr_view.display_qr(allow_export=True)
        else:
            from ..qr import FORMAT_NONE, FORMAT_PMOFN, FORMAT_BBQR, FORMAT_UR

            idx, _ = Menu(
                self.ctx,
                (
                    (t("Static"), lambda: None),
                    (t("Part M of N"), lambda: None),
                    (t("Fountain UR"), lambda: None),
                    (t("BBQr"), lambda: None),
                ),
                back_label=None,
            ).run_loop()
            if idx == 0:
                qrfmt = FORMAT_NONE
            elif idx == 1:
                qrfmt = FORMAT_PMOFN
            elif idx == 2:
                qrfmt = FORMAT_UR
            else:
                qrfmt = FORMAT_BBQR

            try:
                self.display_qr_codes(self.contents, qrfmt, title=self.title)
            except Exception as err:
                self.flash_error("TODO: UR, BBQr\n" + str(err))
                self.view_qr()

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

    def _info_box(self, preview=True):
        """clears screen, displays info_box, returns height-in-lines"""
        from binascii import hexlify

        self.ctx.display.clear()
        num_lines = self.ctx.display.draw_hcentered_text(
            "\n".join(
                [
                    self.title,
                    " ".join(
                        [
                            self.datum if self.datum else "",
                            t("decrypted") if self.decrypted else "",
                            t("sensitive") if self.sensitive else "",
                        ]
                    ),
                    self.about,
                ]
            ),
            info_box=True,
        )
        if preview:
            num_lines += 1
            self.ctx.display.draw_hcentered_text(
                (
                    '"' + self.contents + '"'
                    if isinstance(self.contents, str)
                    else "0x" + hexlify(self.contents).decode()
                ),
                offset_y=DEFAULT_PADDING + num_lines * FONT_HEIGHT,
                max_lines=1,
                info_box=True,
            )

        return num_lines

    def _show_contents(self):
        """Displays infobox and contents"""
        from binascii import hexlify

        print("_show_contents()", self.contents)

        info_len = self._info_box(preview=False)
        self.ctx.display.draw_hcentered_text(
            (
                '"' + self.contents + '"'
                if isinstance(self.contents, str)
                else "0x" + hexlify(self.contents).decode()
            ),
            offset_y=DEFAULT_PADDING + (info_len + 1) * FONT_HEIGHT,
            max_lines=TOTAL_LINES - (info_len + 2),
        )
        self.ctx.input.wait_for_button()

    def _analyze_contents(self):
        """
        analyzes `.contents`, sets:
        * .about (type and length)
        * .datum is the "recognized" datum_type, ie: xpub/psbt/descriptor/etc
        * .sensitivity (bool) if secret,
        * .oneline_viewable (bool) if short enough for one-line display
        """

        if isinstance(self.contents, bytes):
            self.about = t("binary: {} bytes").format(len(self.contents))

            # datum
            if self.contents[:5] == b"psbt\xff":
                self.datum = "PSBT"

            # does it look like 128 or 256 bits of mnemonic entropy / CompactSeedQR?
            if len(self.contents) in (16, 32) and max((x for x in self.contents)) > 127:
                self.sensitive = True

            # fits on one line in info_box
            if (len(self.contents) * 2 + 2) * FONT_WIDTH <= self.ctx.display.width():
                self.oneline_viewable = True
            else:
                self.oneline_viewable = False

        elif isinstance(self.contents, str):
            self.about = t("text: {} chars").format(len(self.contents))

            # datum
            if self.contents[:7] == "cHNidP8":
                self.datum = "PSBT"
            elif (
                self.contents[:1] in "xyzYZtuvUV" and self.contents[1:4] == "pub"
            ) or (
                self.contents[:1] == "["
                and self.contents.split("]")[1][:1] in "xyzYZtuvUV"
                and self.contents.split("]")[1][1:4] == "pub"
            ):
                self.datum = "XPUB"
            elif self.contents.split("(")[0] in ("pkh", "sh", "wpkh", "wsh", "tr"):
                self.datum = "DESCR"

            # does it look like a 12 or 24 word mnemonic / Mnemonic QR?
            if len(self.contents.split()) in (12, 24):
                self.sensitive = True

            # does it look like a 12 or 24 word decimal mnemonic / StandadardSeedQR?
            elif len(set((x in "0123456789" for x in self.contents))) == 1 and (
                len(self.contents) in (12 * 4, 24 * 4)
            ):
                self.sensitive = True

            # fits on one line in info_box
            if (len(self.contents) + 2) * FONT_WIDTH <= self.ctx.display.width():
                self.oneline_viewable = True
            else:
                self.oneline_viewable = False

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

    def _build_options_menu(self, offer_convert=False, offer_show=True):
        """Build a menu list of what to do with contents, possibly w/ conversions"""
        from binascii import unhexlify
        from krux.baseconv import base_decode

        # build menu options
        menu = []

        if offer_show:
            menu.append((t("Show Datum"), lambda: "show"))

        if not offer_convert:
            menu.append((t("Convert Datum"), lambda: "convert_begin"))

            if not (self.decrypted and self.sensitive):
                menu.append((t("Export to QR"), lambda: "export_qr"))
                menu.append((t("Export to SD"), lambda: "export_sd"))

        else:
            if isinstance(self.contents, bytes):
                menu.append((t("to hex"), lambda: "hex"))
                menu.append((t("to base43"), lambda: 43))
                menu.append((t("to base64"), lambda: 64))
                try:
                    self.contents.decode()
                    menu.append((t("to utf8"), lambda: "utf8"))
                except:
                    pass
                menu.append((t("Encrypt"), lambda: "encrypt"))

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
                    base_decode(self.contents, 64)
                    menu.append(("from base64", lambda: 64))
                except:
                    pass

                try:
                    self.contents.encode()
                    menu.append((t("from utf8"), lambda: "utf8"))
                except:
                    pass

            if self.history:
                for i, option in enumerate(menu):
                    if option[1]() == self.history[-1]:
                        menu[i] = (option[0] + " (" + t("Undo") + ")", lambda: "undo")
                        break

            menu.append((t("Done Converting"), lambda: "convert_end"))

        return menu

    def view_contents(self, try_decrypt=True, offer_convert=False):
        """allows to view, convert, encrypt/decrypt, and export short str/bytes contents"""
        from .encryption_ui import KEFEnvelope

        argv = {
            "try_decrypt": try_decrypt,
            "offer_convert": offer_convert,
        }

        # check if KEF wrapped
        if try_decrypt and isinstance(self.contents, bytes):
            self._decrypt_as_kef_envelope()

        # analyze contents
        self._analyze_contents()

        # get menu of what can be done to contents
        todo_menu = self._build_options_menu(
            offer_convert=offer_convert, offer_show=not self.oneline_viewable
        )

        # display infobox
        info_len = self._info_box()

        # run todo_menu
        back_status = {}
        if offer_convert:
            back_status = {"back_label": None}
        menu = Menu(
            self.ctx,
            todo_menu,
            offset=(info_len + 1) * FONT_HEIGHT + DEFAULT_PADDING,
            **back_status
        )
        _, status = menu.run_loop()

        if status == MENU_EXIT:
            # if user chose to exit
            return MENU_CONTINUE

        if status == "show":
            # if user wants to view data
            self._show_contents()
        elif status == "convert_begin":
            # if user wants to convert data
            argv["offer_convert"] = True
        elif status == "convert_end":
            # if user is done converting data
            argv["offer_convert"] = False
        elif status in ("undo", "hex", 43, 64, "utf8"):
            # if user chose a particular conversion
            if status == "undo":
                status = self.history.pop()
            else:
                self.history.append(status)
            self.contents = convert_encoding(self.contents, status)
        elif status == "encrypt":
            # if user chose to encrypt
            kef = KEFEnvelope(self.ctx)
            kef.label = self.title
            self.contents = kef.seal_ui(self.contents, override_defaults=True)
            self.title = kef.label if kef.label else ""
            self.decrypted = False
            argv["try_decrypt"] = False
        elif status == "export_qr":
            # if user chose to export_qr
            self.view_qr()
        else:
            # user chose export_sd
            self.save_sd()

        return self.view_contents(**argv)

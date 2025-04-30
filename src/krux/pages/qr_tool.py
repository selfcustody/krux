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


class QRTool(Page):
    """Krux QR Tools"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Scan a QR"), self.scan_qr),
                    (t("New Text QR"), self.create_qr),
                    (t("New Encrypted QR"), self.create_encrypted_qr),
                ],
            ),
        )
        self.ctx = ctx

    def scan_qr(self):
        """Handler for the 'Scan a QR' menu item"""

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
        return self.manipulate_contents(contents, title)

    def create_qr(self, text=None):
        """Handler for the 'New Text QR' menu item"""
        if text is None:
            if not self.prompt(
                t("Create QR code from text?"),
                self.ctx.display.height() // 2,
            ):
                return MENU_CONTINUE
            text = self.capture_from_keypad(
                t("Text"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
            )
            if text in ("", ESC_KEY):
                return MENU_CONTINUE
        return self.view_qr(contents=text, title=t("Text QR Code"))

    def create_encrypted_qr(self, text=None):
        """Handler for the 'New Encrypted QR' menu item"""
        if text is None:
            if not self.prompt(
                t("Create QR code from text?"),
                self.ctx.display.height() // 2,
            ):
                return MENU_CONTINUE
            text = self.capture_from_keypad(
                t("Text"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
            )
            if text in ("", ESC_KEY):
                return MENU_CONTINUE

        from .encryption_ui import KEFEnvelope

        kef = KEFEnvelope(self.ctx)
        text = text if isinstance(text, bytes) else text.encode()
        contents = kef.seal_ui(text, override_settings=True)
        return self.view_qr(contents=contents, title=t("Encrypted QR Code"))

    def view_qr(self, contents, title=None):
        """Reusable handler for viewing a QR code"""
        from .qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, data=contents, title=title)
        seed_qr_view.display_qr(allow_export=True)

        return MENU_CONTINUE

    def manipulate_contents(
        self,
        contents,
        title,
        history=None,
        try_decrypt=True,
        decrypted=False,
        sensitive=False,
    ):
        """allows to view, convert, encrypt/decrypt, and export short str/bytes contents"""
        # pylint: disable=R0912,R0915
        from binascii import hexlify, unhexlify
        from krux.baseconv import base_encode, base_decode
        from .encryption_ui import KEFEnvelope

        def convert(contents, conversion):
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

        def info_box(title, decrypted, sensitive, type_len):
            self.ctx.display.clear()
            return self.ctx.display.draw_hcentered_text(
                "\n".join(
                    [
                        title,
                        " ".join(
                            [
                                t("decrypted") if decrypted else "",
                                t("sensitive") if sensitive else "",
                            ]
                        ),
                        type_len,
                    ]
                ),
                info_box=True,
            )

        # print("into manipulate_contents(", contents, type(contents), history)
        type_len = None
        if history is None:
            history = []

        # check if KEF wrapped
        if try_decrypt and isinstance(contents, bytes):
            while True:
                kef = KEFEnvelope(self.ctx)
                plaintext = kef.unseal_ui(contents)
                if plaintext is None:
                    break
                decrypted = True
                contents = plaintext
                history = []

        # analyze bytes contents, build menu options
        todo_menu = []
        if isinstance(contents, bytes):
            type_len = t("binary: {} bytes").format(len(contents))
            if len(contents) in (16, 32) and max((x for x in contents)) > 127:
                sensitive = True
            todo_menu.append((t("to hex"), lambda: "hex"))
            todo_menu.append((t("to base43"), lambda: 43))
            todo_menu.append((t("to base58"), lambda: 58))
            todo_menu.append((t("to base64"), lambda: 64))
            try:
                contents.decode()
                todo_menu.append((t("to utf8"), lambda: "utf8"))
            except:
                pass

        # analyze string contents, build menu options
        elif isinstance(contents, str):
            type_len = t("text: {} chars").format(len(contents))
            if len(contents.split()) in (12, 24):
                sensitive = True
            elif len(set((x in "0123456789" for x in contents))) == 1 and (
                len(contents) in (12 * 4, 24 * 4)
            ):
                sensitive = True

            try:
                unhexlify(contents)
                todo_menu.append((t("from hex"), lambda: "hex"))
            except:
                pass

            try:
                base_decode(contents, 43)
                todo_menu.append((t("from base43"), lambda: 43))
            except:
                pass

            try:
                base_decode(contents, 58)
                todo_menu.append((t("from base58"), lambda: 58))
            except:
                pass

            try:
                base_decode(contents, 64)
                todo_menu.append(("from base64", lambda: 64))
            except:
                pass

            try:
                contents.encode()
                todo_menu.append((t("from utf8"), lambda: "utf8"))
            except:
                pass

        todo_menu.append((t("Encrypt"), lambda: "encrypt"))
        if not (decrypted and sensitive):
            todo_menu.append((t("Export QR"), lambda: "export"))

        if len(history):
            for i, option in enumerate(todo_menu):
                if option[1]() == history[-1]:
                    todo_menu[i] = (option[0] + " (" + t("Undo") + ")", lambda: "undo")
                    break

        # display infobox and contents
        info_len = info_box(title, decrypted, sensitive, type_len)
        self.ctx.display.draw_hcentered_text(
            (
                '"' + contents + '"'
                if isinstance(contents, str)
                else "0x " + hexlify(contents).decode()
            ),
            offset_y=DEFAULT_PADDING + (info_len + 1) * FONT_HEIGHT,
        )
        self.ctx.input.wait_for_button()

        # display infobox and run the todo_menu
        info_len = info_box(title, decrypted, sensitive, type_len)
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
                status = history.pop()
            else:
                history.append(status)
            contents = convert(contents, status)
            return self.manipulate_contents(
                contents,
                title,
                history=history,
                try_decrypt=try_decrypt,
                decrypted=decrypted,
                sensitive=sensitive,
            )

        # if user chose to encrypt
        if status == "encrypt":
            kef = KEFEnvelope(self.ctx)
            contents = contents if isinstance(contents, bytes) else contents.encode()
            contents = kef.seal_ui(contents, override_settings=True)
            title = kef.label if kef.label else ""
            return self.manipulate_contents(
                contents, title, try_decrypt=False, sensitive=sensitive
            )

        # user chose to export
        return self.view_qr(contents, title)

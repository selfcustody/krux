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
from krux.wdt import wdt
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
from .encryption_ui import (
    OVERRIDE_ITERATIONS,
    OVERRIDE_VERSION,
    OVERRIDE_LABEL,
)
from ..display import FONT_WIDTH, FONT_HEIGHT, DEFAULT_PADDING, TOTAL_LINES
from ..krux_settings import t
from ..input import (
    BUTTON_TOUCH,
    BUTTON_ENTER,
    FAST_FORWARD,
    FAST_BACKWARD,
    BUTTON_PAGE,
    SWIPE_LEFT,
    SWIPE_UP,
    BUTTON_PAGE_PREV,
    SWIPE_RIGHT,
    SWIPE_DOWN,
)

DATUM_DESCRIPTOR = "DESC"
DATUM_PSBT = "PSBT"
DATUM_XPUB = "XPUB"
DATUM_ADDRESS = "ADDR"

DATUM_UR_TYPES = {
    # DATUM_DESCRIPTOR: ["crypto-account", "crypto-output"],
    DATUM_PSBT: ["crypto-psbt"],
    # DATUM_XPUB: ["crypto-account"],
    # DATUM_ADDRESS: ["crypto-account"],
}
DATUM_BBQR_TYPES = {
    DATUM_DESCRIPTOR: ["U"],
    DATUM_PSBT: ["P"],
    DATUM_XPUB: ["U"],
    DATUM_ADDRESS: ["U"],
}

STATIC_QR_MAX_SIZE = 4  # version 5 - 37x37
SUFFICIENT_SAMPLE_SIZE = 512  # to truncate large contents for sampling
SLOW_ENCODING_MAX_SIZE = 2**14  # base43,base58,bech32 not offered above this size


def urobj_to_data(ur_obj):
    """returns flatened data from a UR object. belongs in qr or qr_capture???"""
    import urtypes

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
    """encoding conversions to/from (hex/HEX/base43/base58/base64/shift_case/utf8)"""
    from krux.baseconv import base_encode, base_decode
    from binascii import hexlify, unhexlify

    from_bytes = isinstance(contents, bytes)
    try:
        if conversion in (32, 43, 58, 64):
            if from_bytes:
                return base_encode(contents, conversion)
            return base_decode(contents, conversion)
        if conversion == "hex":
            if from_bytes:
                return hexlify(contents).decode()
            return unhexlify(contents)
        if conversion == "HEX":
            if from_bytes:
                return hexlify(contents).decode().upper()
            return unhexlify(contents)
        if conversion == "utf8":
            if from_bytes:
                return contents.decode()
            return contents.encode()
        if conversion == "shift_case":
            if isinstance(contents, str):
                if contents == contents.lower():
                    return contents.upper()
                if contents == contents.upper():
                    return contents.lower()
    except:
        pass
    return None


def identify_datum(data, encodings=None):
    """Determine which "datum" type this is; ie: PSBT, XPUB, DESC, ADDR"""

    # TODO: more samples and fewer false-positives
    datum = None
    if isinstance(data, bytes):
        if data[:5] == b"psbt\xff":
            datum = DATUM_PSBT
    elif len(data) > 33:
        if encodings is None:
            encodings = detect_encodings(data)

        if data[:1] in "xyzYZtuvUV" and data[1:4] == "pub" and 58 in encodings:
            datum = DATUM_XPUB
        elif (
            data[:1] == "["
            and data.split("]")[1][:1] in "xyzYZtuvUV"
            and data.split("]")[1][1:4] == "pub"
        ):
            datum = DATUM_XPUB
        elif data.split("(")[0] in ("pkh", "sh", "wpkh", "wsh", "tr"):
            datum = DATUM_DESCRIPTOR
        elif (data[:1] in ("1", "3", "n", "2", "m") and 58 in encodings) or (
            data[:4].lower() in ("bc1p", "bc1q", "tb1p", "tb1q")
            and "bech32" in [x.lower()[:6] for x in encodings if isinstance(x, str)]
        ):
            datum = DATUM_ADDRESS

    return datum


def detect_encodings(str_data, verify=True):
    """
    Detect which encodings this data str might be, returns list

    A more-efficient/reduced version of this function exists in baseconv, this one
    remains/used here to identify potentially useful-but-missing encodings
    """
    # pylint: disable=R0912,R0915
    from binascii import unhexlify
    from krux.baseconv import base_decode, base_encode
    from embit.bech32 import bech32_decode, Encoding

    encodings = []

    if not isinstance(str_data, str):
        raise TypeError("detect_encodings() expected str")

    str_len = len(str_data)

    # get min and max characters (sorted by ordinal value)
    # then check most restrictive encodings first
    min_chr = min(str_data[:SUFFICIENT_SAMPLE_SIZE])
    max_chr = max(str_data[:SUFFICIENT_SAMPLE_SIZE])

    # might it be hex
    if str_len % 2 == 0 and "0" <= min_chr:
        if max_chr <= "F":
            if verify:
                try:
                    unhexlify(str_data)
                    encodings.append("HEX")
                except:
                    pass
            else:
                encodings.append("HEX")
        elif max_chr <= "f":
            if verify:
                try:
                    unhexlify(str_data)
                    encodings.append("hex")
                except:
                    pass
            else:
                encodings.append("hex")

    # might it be base32
    if "2" <= min_chr and max_chr <= "Z":
        if verify:
            try:
                base_decode(str_data, 32)
                encodings.append(32)
            except:
                pass
        else:
            encodings.append(32)

    # might it be bech32
    if str_len <= SLOW_ENCODING_MAX_SIZE and "0" <= min_chr:
        encoding = None
        if max_chr <= "Z":
            if verify:
                encoding, _, _ = bech32_decode(str_data)
                wdt.feed()
            if encoding == Encoding.BECH32:
                encodings.append("BECH32")
            elif encoding == Encoding.BECH32M:
                encodings.append("BECH32M")
        elif max_chr <= "z":
            if verify:
                encoding, _, _ = bech32_decode(str_data)
            if encoding == Encoding.BECH32:
                encodings.append("bech32")
            elif encoding == Encoding.BECH32M:
                encodings.append("bech32m")

    # might it be base43
    if str_len <= SLOW_ENCODING_MAX_SIZE and "$" <= min_chr and max_chr <= "Z":
        if verify:
            try:
                base_decode(str_data, 43)
                wdt.feed()
                encodings.append(43)
            except:
                pass
        else:
            encodings.append(43)

    # might it be base58
    if str_len <= SLOW_ENCODING_MAX_SIZE and "1" <= min_chr and max_chr <= "z":
        if verify:
            try:
                base_decode(str_data, 58)
                wdt.feed()
                encodings.append(58)
            except:
                pass
        else:
            encodings.append(58)

    # might it be base64
    if "+" <= min_chr and max_chr <= "z":
        if verify:
            try:
                # binascii.a2b_base64 is NOT strict
                as_bytes = base_decode(str_data, 64)
                if base_encode(as_bytes, 64) == str_data:
                    encodings.append(64)
                del as_bytes
            except:
                pass
        else:
            encodings.append(64)

    # might it be ascii
    if ord(max_chr) <= 127:
        encodings.append("ascii")

    # might it be latin-1
    if 128 <= ord(max_chr) <= 255:
        encodings.append("latin-1")

    # assume utf8
    encodings.append("utf8")

    gc.collect()

    return encodings


class DatumToolMenu(Page):
    """Krux Datum Tool Menu"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Via Camera"), self.scan_qr),
                    (t("Via Manual Input"), self.text_entry),
                    (t("From Storage"), self.read_file),
                ],
            ),
        )

    def scan_qr(self):
        """Handler for the 'Scan a QR' menu item"""

        from .qr_capture import QRCodeCapture

        qr_scanner = QRCodeCapture(self.ctx)
        contents, fmt = qr_scanner.qr_capture_loop()
        if contents is None:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE

        title = "QR Contents"
        if fmt == 2:
            title += ", UR:" + contents.type
            contents = urobj_to_data(contents)

        if isinstance(contents, bytes):
            try:
                contents = contents.decode()
            except:
                pass

        page = DatumTool(self.ctx)
        page.contents, page.title = contents, title
        return page.view_contents()

    def text_entry(self):
        """Handler for the 'Text Entry' menu item"""
        from .encryption_ui import prompt_for_text_update

        text = ""
        while True:
            updated = prompt_for_text_update(
                self.ctx,
                text if text else "",
                t("Proceed?"),
                prompt_highlight_prefix="?",
                title=t("Custom Text"),
                keypads=[
                    LETTERS,
                    UPPERCASE_LETTERS,
                    NUM_SPECIAL_1,
                    NUM_SPECIAL_2,
                ],
            )
            if updated == text:
                break
            text = updated
        if text in ("", ESC_KEY):
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE

        page = DatumTool(self.ctx)
        page.contents, page.title = text, t("Custom Text")
        return page.view_contents()

    def read_file(self):
        """Handler for the 'Read File' menu item"""
        from .utils import Utils

        if not self.has_sd_card():
            self.flash_error(t("SD card not detected."))
            return MENU_CONTINUE

        utils = Utils(self.ctx)
        try:
            filename, contents = utils.load_file(prompt=False)
        except OSError:
            pass

        if not contents:
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing…"))

        # utils.load_file() always returns binary
        try:
            contents = contents.decode()
            if contents[-1:] == "\n":
                contents = contents[:-1]
        except:
            pass

        page = DatumTool(self.ctx)
        page.contents = contents
        # pylint: disable=C0207
        page.title = filename.split("/")[-1]
        return page.view_contents()


class DatumTool(Page):
    """Krux Datum Tool"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.contents = None
        self.encodings = []
        self.about_prefix = None
        self.about = None
        self.title = None
        self.datum = None
        self.decrypted = False
        self.sensitive = False
        self.history = []
        self.oneline_viewable = None

    def view_qr(self):
        """Reusable handler for viewing a QR code"""
        from ..qr import QR_CAPACITY_BYTE, QR_CAPACITY_ALPHANUMERIC, QR_CAPACITY_NUMERIC
        from ..bbqr import encode_bbqr
        import urtypes
        from ur.ur import UR

        # Helper function to check if character is alphanumeric
        def is_alnum(c):
            return ("A" <= c <= "Z") or ("0" <= c <= "9") or c in (" $%*+-./:")

        seedqrview_thresh = QR_CAPACITY_BYTE[STATIC_QR_MAX_SIZE]
        if not isinstance(self.contents, bytes):
            if all(c.isdigit() for c in self.contents[:SUFFICIENT_SAMPLE_SIZE]):
                seedqrview_thresh = QR_CAPACITY_NUMERIC[STATIC_QR_MAX_SIZE]
            elif all(is_alnum(c) for c in self.contents[:SUFFICIENT_SAMPLE_SIZE]):
                seedqrview_thresh = QR_CAPACITY_ALPHANUMERIC[STATIC_QR_MAX_SIZE]

        if len(self.contents) <= seedqrview_thresh:
            from .encryption_ui import prompt_for_text_update
            from .qr_view import SeedQRView

            # for transcribable qr, allow updating title
            while True:
                updated = prompt_for_text_update(
                    self.ctx,
                    self.title,
                    t("Update QR Label?"),
                    dflt_affirm=False,
                    prompt_highlight_prefix="?",
                    title=t("QR Label"),
                    keypads=[
                        LETTERS,
                        UPPERCASE_LETTERS,
                        NUM_SPECIAL_1,
                        NUM_SPECIAL_2,
                    ],
                )
                if updated == self.title:
                    break
                self.title = updated

            kvargs = {}
            # when not sensitive, allow export to sd
            if not self.sensitive:
                kvargs["allow_export"] = True

            seed_qr_view = SeedQRView(self.ctx, data=self.contents, title=self.title)
            seed_qr_view.display_qr(**kvargs)

        else:
            from ..qr import FORMAT_NONE, FORMAT_PMOFN, FORMAT_BBQR, FORMAT_UR

            menu_opts = []
            if len(self.contents) <= seedqrview_thresh * 4:
                menu_opts.append((t("Static"), (FORMAT_NONE,)))
            menu_opts.append((t("Part M of N"), (FORMAT_PMOFN,)))

            if self.datum in DATUM_BBQR_TYPES:
                menu_opts.extend(
                    [
                        ("BBQr " + v, (FORMAT_BBQR, v))
                        for v in DATUM_BBQR_TYPES[self.datum]
                    ]
                )

            curr_datum = identify_datum(self.contents, self.encodings)
            if curr_datum:
                if curr_datum in DATUM_UR_TYPES:
                    menu_opts.extend(
                        [
                            ("UR " + v, (FORMAT_UR, v))
                            for v in DATUM_UR_TYPES[curr_datum]
                        ]
                    )

            if isinstance(self.contents, bytes):
                menu_opts.append(("UR bytes", (FORMAT_UR, "bytes")))

            idx, _ = Menu(
                self.ctx,
                [(x[0], lambda: None) for x in menu_opts],
                back_label=None,
            ).run_loop()

            qr_fmt = menu_opts[idx][1][0]

            encoded = None
            if qr_fmt in (FORMAT_BBQR, FORMAT_UR):
                encoded = self.contents

                if qr_fmt == FORMAT_BBQR:
                    encoded = encode_bbqr(encoded, file_type=menu_opts[idx][1][1])

                elif qr_fmt == FORMAT_UR:
                    ur_type = menu_opts[idx][1][1]
                    if ur_type == "bytes":
                        encoded = UR(ur_type, urtypes.Bytes(encoded).to_cbor())
                    elif ur_type == "crypto-psbt":
                        encoded = UR(ur_type, urtypes.PSBT(encoded).to_cbor())
                    # TODO: other urtypes

            try:
                self.display_qr_codes(
                    encoded if encoded else self.contents, qr_fmt, title=self.title
                )
            except Exception as err:
                self.flash_error(
                    "Failed encoding ({}), try as bytes. {}".format(
                        repr(menu_opts[idx]),
                        str(err),
                    )
                )

        return MENU_CONTINUE

    def save_sd(self):
        """Reusable handler for saving to SD file"""
        from .file_operations import SaveFile

        save_page = SaveFile(self.ctx)
        save_page.save_file(
            self.contents,
            self.title.split(",")[-1].replace(" ", "_"),
            save_as_binary=isinstance(self.contents, bytes),
            prompt=False,
        )

    def _info_box(self, preview=True, about_suffix=""):
        """clears screen, displays info_box, returns height-in-lines"""
        from binascii import hexlify

        self.ctx.display.clear()
        parts = [
            self.title,
            "".join(
                [
                    "wasKEF " if self.decrypted else "",
                    "secret " if self.sensitive else "",
                    ",".join([str(x) for x in self.encodings]),
                ]
            ),
            " ".join(
                [
                    x
                    for x in [
                        self.about,
                        self.datum,
                        about_suffix,
                    ]
                    if x
                ]
            ),
        ]
        if preview:
            preview_contents = self.contents[:SUFFICIENT_SAMPLE_SIZE]
            parts.append(
                self.fit_to_line(
                    (
                        '"' + preview_contents + '"'
                        if isinstance(preview_contents, str)
                        else "0x" + hexlify(preview_contents).decode()
                    ),
                    crop_middle=False,
                )
            )
        num_lines = self.ctx.display.draw_hcentered_text(
            "\n".join(p for p in parts if p),
            info_box=True,
            highlight_prefix=self.about_prefix,
        )

        return num_lines

    def _show_contents(self):
        """Displays infobox and contents"""
        from binascii import hexlify
        from ..settings import ELLIPSIS
        from ..kboard import kboard

        page_indicator = "p.%d"
        max_lines = 0
        offset_x = (
            DEFAULT_PADDING
            if not kboard.is_m5stickv
            else (self.ctx.display.width() % FONT_WIDTH) // 2
        )
        content_len = len(self.contents)

        def _update_infobox(curr_page):
            info_len = self._info_box(
                preview=False, about_suffix=page_indicator % (curr_page)
            )
            max_lines = TOTAL_LINES - (info_len + 1)
            return info_len, max_lines

        curr_page, pages = 0, [0]
        start_index = 0
        info_len, max_lines = _update_infobox(curr_page + 1)

        while True:
            info_len, max_lines = _update_infobox(curr_page + 1)
            chars_per_page = self.ctx.display.width() // FONT_WIDTH * max_lines
            contents = self.contents[start_index : start_index + chars_per_page + 1]
            if isinstance(contents, bytes):
                contents = hexlify(contents).decode()[: chars_per_page + 1]
            lines, endpos = self.ctx.display.to_lines_endpos(contents, max_lines)
            if isinstance(self.contents, bytes):
                if endpos % 2:
                    endpos -= 1
                    if lines[-1][-1] == ELLIPSIS:
                        lines[-1] = lines[-1][:-2] + ELLIPSIS * 2
                endpos = endpos // 2
            endpos += start_index
            if pages[-1] < endpos < content_len:
                pages.append(endpos)

            offset_y = DEFAULT_PADDING + info_len * FONT_HEIGHT + 1
            for line in lines:
                self.ctx.display.draw_string(offset_x, offset_y, line)
                offset_y += FONT_HEIGHT

            btn = self.ctx.input.wait_for_fastnav_button()
            if btn in (BUTTON_PAGE, FAST_FORWARD, SWIPE_UP, SWIPE_LEFT):
                if curr_page + 1 < len(pages):
                    curr_page += 1
            elif btn in (BUTTON_PAGE_PREV, FAST_BACKWARD, SWIPE_DOWN, SWIPE_RIGHT):
                if curr_page > 0:
                    curr_page -= 1
            elif btn in (BUTTON_ENTER, BUTTON_TOUCH):
                break
            start_index = pages[curr_page]

    def _analyze_contents(self):
        """
        analyzes `.contents`, sets:
        * .about (type and length)
        * .encodings (list)
        * .sensitivity (bool) if secret,
        * .oneline_viewable (bool) if short enough for one-line display
        * .datum is the "recognized" datum_type, ie: xpub/psbt/descriptor/etc
        """

        if isinstance(self.contents, bytes):
            self.about_prefix = t("binary:")
            self.about = self.about_prefix + " " + t("%s bytes") % len(self.contents)
            try:
                as_str = self.contents.decode()
                suggestion = str(detect_encodings(as_str, False)[0])
                del as_str
                gc.collect()
                if suggestion != "utf8":
                    suggestion = suggestion + "_via_utf8"
                self.encodings = [suggestion + "?"]
            except:
                self.encodings = []

            # does it look like 128 or 256 bits of mnemonic entropy / CompactSeedQR?
            if len(self.contents) in (16, 32) and max((x for x in self.contents)) > 127:
                self.sensitive = True

            # fits on one line in info_box
            if (len(self.contents) * 2 + 2) * FONT_WIDTH <= self.ctx.display.width():
                self.oneline_viewable = True
            else:
                self.oneline_viewable = False

        elif isinstance(self.contents, str):
            self.about_prefix = t("text:")
            self.about = self.about_prefix + " " + t("%s chars") % len(self.contents)
            self.encodings = detect_encodings(self.contents)

            # does it look like a 12 or 24 word mnemonic / Mnemonic QR?
            if len(self.contents[:256].split()) in (12, 24):
                self.sensitive = True

            # does it look like a 12 or 24 word decimal mnemonic / StandadardSeedQR?
            elif (
                len(self.contents) in (12 * 4, 24 * 4)
                and len(set((x in "0123456789" for x in self.contents))) == 1
            ):
                self.sensitive = True

            # fits on one line in info_box
            if (len(self.contents) + 2) * FONT_WIDTH <= self.ctx.display.width():
                self.oneline_viewable = True
            else:
                self.oneline_viewable = False

        # datum
        if not self.datum:
            self.datum = identify_datum(self.contents, self.encodings)

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

            self.title = self.fit_to_line(self.title)
            self.decrypted = True
            self.contents = plaintext
            self.history = []

    def _build_options_menu(self, offer_convert=False, offer_show=True):
        """Build a menu list of what to do with contents, possibly w/ conversions"""

        menu = []

        if offer_show:
            menu.append((t("Show Datum"), lambda: "show"))

        if not offer_convert:
            menu.append((t("Convert Datum"), lambda: "convert_begin"))
            menu.append((t("QR Code"), lambda: "export_qr"))

            # when not sensitive, allow export to sd
            if not self.sensitive:
                menu.append((t("Save to SD card"), lambda: "export_sd"))

        else:
            if isinstance(self.contents, bytes):
                if self.history and self.history[-1] == "HEX":
                    menu.append((t("to HEX"), lambda: "HEX"))
                else:
                    menu.append((t("to hex"), lambda: "hex"))
                menu.append((t("to base32"), lambda: 32))
                if len(self.contents) <= SLOW_ENCODING_MAX_SIZE * 5.42 / 8:
                    # 5.42 slightly less than log2(43); adjusts for base43 bloat
                    menu.append((t("to base43"), lambda: 43))
                menu.append((t("to base64"), lambda: 64))
                try:
                    self.contents.decode()
                    menu.append((t("to utf8"), lambda: "utf8"))
                except:
                    pass
                menu.append((t("Encrypt"), lambda: "encrypt"))

            elif isinstance(self.contents, str):
                if "HEX" in self.encodings:
                    menu.append((t("from HEX"), lambda: "HEX"))
                if "hex" in self.encodings:
                    menu.append((t("from hex"), lambda: "hex"))
                if set(self.encodings).intersection(
                    ["hex", "HEX", "bech32", "BECH32", "bech32m", "BECH32M"]
                ):
                    menu.append((t("shift case"), lambda: "shift_case"))
                if 32 in self.encodings:
                    menu.append((t("from base32"), lambda: 32))
                if 43 in self.encodings:
                    menu.append((t("from base43"), lambda: 43))
                if 64 in self.encodings:
                    menu.append((t("from base64"), lambda: 64))
                if "utf8" in self.encodings:
                    menu.append((t("from utf8"), lambda: "utf8"))

            if self.history:
                for i, option in enumerate(menu):
                    if (
                        option[1]() in ("HEX", "hex")
                        and self.history[-1] in ("HEX", "hex")
                    ) or option[1]() == self.history[-1]:
                        menu[i] = (option[0] + " (" + t("Undo") + ")", lambda: "undo")
                        break

            menu.append((t("Done Converting"), lambda: "convert_end"))

        return menu

    def view_contents(self, try_decrypt=True, offer_convert=False):
        """allows to view, convert, encrypt/decrypt, and export short str/bytes contents"""
        from .encryption_ui import KEFEnvelope

        gc.collect()

        kvargs = {
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
            offset=info_len * FONT_HEIGHT + DEFAULT_PADDING,
            **back_status
        )
        _, status = menu.run_loop()

        if status == MENU_EXIT:
            # if user chose to exit
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing…"))

        if status == "show":
            # if user wants to view data
            self._show_contents()
        elif status == "convert_begin":
            # if user wants to convert data
            kvargs["offer_convert"] = True
        elif status == "convert_end":
            # if user is done converting data
            kvargs["offer_convert"] = False
        elif status in ("undo", "hex", "HEX", 32, 43, 64, "utf8", "shift_case"):
            # if user chose a particular conversion
            undo = False
            if status == "undo":
                undo = True
                status = self.history.pop()
            new_contents = convert_encoding(self.contents, status)
            if new_contents is not None:
                self.contents = new_contents
                if not undo:
                    self.history.append(status)
                del new_contents
            else:
                if undo:
                    self.history.append(status)
                self.flash_error(t("Failed to convert"))

        elif status == "encrypt":
            # if user chose to encrypt
            kef = KEFEnvelope(self.ctx)
            kef.label = self.datum if self.datum else self.title
            encrypted = kef.seal_ui(
                self.contents,
                overrides=[OVERRIDE_VERSION, OVERRIDE_ITERATIONS, OVERRIDE_LABEL],
            )
            if encrypted:
                # now in "hiding secrets" mode
                self.contents = encrypted
                self.title = kef.label + " KEF" if kef.label else "KEF"
                self.sensitive = False
                self.decrypted = False
                self.history = []
                kvargs["try_decrypt"] = False
        elif status == "export_qr":
            # if user chose to export_qr
            self.view_qr()
        else:
            # user chose export_sd
            self.save_sd()

        return self.view_contents(**kvargs)

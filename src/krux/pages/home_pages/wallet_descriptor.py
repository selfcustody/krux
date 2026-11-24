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

from krux.pages import (
    Page,
    Menu,
    MENU_CONTINUE,
    LOAD_FROM_CAMERA,
    LOAD_FROM_SD,
)
from krux.display import (
    DEFAULT_PADDING,
    BOTTOM_PROMPT_LINE,
    FONT_HEIGHT,
    FONT_WIDTH,
    MINIMAL_PADDING,
)
from krux.krux_settings import t
from krux.qr import FORMAT_NONE, FORMAT_PMOFN
from krux.sd_card import (
    DESCRIPTOR_FILE_EXTENSION,
    JSON_FILE_EXTENSION,
)
from krux.themes import theme
from krux.key import FINGERPRINT_SYMBOL, DERIVATION_PATH_SYMBOL, P2TR
from krux.kboard import kboard


class WalletDescriptor(Page):
    """Page to load and export wallet descriptor"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def wallet(self):
        """Handler for the 'wallet descriptor' menu item"""
        title = t("Wallet output descriptor")
        self.ctx.display.clear()
        if self.ctx.wallet.key is None:
            # No key loaded, so it's being called from tools -> descriptor addresses
            text = t("Load a trusted wallet descriptor to view addresses?")
            text += "\n" + t("(watch-only)")
            if self.prompt(text, self.ctx.display.height() // 2):
                return self._load_wallet()
        elif not self.ctx.wallet.is_loaded():
            text = t("Wallet output descriptor not found.")
            self.ctx.display.draw_centered_text(text)
            if self.prompt(t("Load?"), BOTTOM_PROMPT_LINE):
                return self._load_wallet()
        else:
            qr_type_menu = [
                ("Plaintext", lambda: "P"),
                ("Encrypted", lambda: "E"),
            ]
            idx, qr_type = Menu(self.ctx, qr_type_menu).run_loop()
            if idx == len(qr_type_menu) - 1:
                return MENU_CONTINUE

            is_encrypted = qr_type == "E"
            if is_encrypted:
                from krux.pages.encryption_ui import KEFEnvelope
                from krux.pages.qr_view import SeedQRView

                # simple descriptor string encoded to bytes, rather than what was loaded
                wallet_data = self.ctx.wallet.descriptor.to_string().encode()

                kef = KEFEnvelope(self.ctx)
                kef.label = self.ctx.wallet.label
                wallet_data = kef.seal_ui(wallet_data)
                if not wallet_data:
                    # User cancelled the encryption
                    return MENU_CONTINUE
                qr_format = "binary"
                title = "KEF " + kef.label
                sqr = SeedQRView(self.ctx, binary=True, data=wallet_data, title=title)
                sqr.display_qr(allow_export=True, transcript_tools=False)
            else:
                self.display_wallet(self.ctx.wallet)
                wallet_data, qr_format = self.ctx.wallet.wallet_qr()
            from krux.pages.utils import Utils

            utils = Utils(self.ctx)
            utils.print_standard_qr(wallet_data, qr_format, title)

            # Try to save the Wallet output descriptor on the SD card
            if self.has_sd_card() and not self.ctx.wallet.persisted:
                from krux.pages.file_operations import SaveFile

                save_page = SaveFile(self.ctx)
                if is_encrypted:
                    file_content = wallet_data
                else:
                    file_content = self.ctx.wallet.descriptor.to_string()
                self.ctx.wallet.persisted = save_page.save_file(
                    file_content,
                    self.ctx.wallet.label,
                    self.ctx.wallet.label,
                    title + ":",
                    DESCRIPTOR_FILE_EXTENSION,
                    save_as_binary=is_encrypted,
                )

        return MENU_CONTINUE

    def _load_wallet_data(self):
        """Loads and decrypts wallet data from camera or SD card"""
        persisted = False
        wallet_data = None

        load_method = self.load_method()
        if load_method == LOAD_FROM_CAMERA:
            from krux.pages.qr_capture import QRCodeCapture

            qr_capture = QRCodeCapture(self.ctx)
            wallet_data, qr_format = qr_capture.qr_capture_loop()
            if wallet_data is None:
                return None  # user left the QR scanner
        elif load_method == LOAD_FROM_SD:
            # Try to read the wallet output descriptor from a file on the SD card
            qr_format = FORMAT_NONE
            from krux.pages.utils import Utils

            utils = Utils(self.ctx)
            filename, wallet_data = utils.load_file(
                (
                    DESCRIPTOR_FILE_EXTENSION,
                    JSON_FILE_EXTENSION,
                ),
                prompt=False,
            )
            if not filename:
                # Cancelled, or load_file already reported the failure
                return None
            persisted = True
        else:  # Cancel
            return None

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing…"))

        # Decrypt if needed
        from krux.pages.encryption_ui import decrypt_kef

        try:
            wallet_data = decrypt_kef(self.ctx, wallet_data)

            # Cpython raises UnicodeDecodeError, MaixPy raises TypeError
            try:
                wallet_data = wallet_data.decode()
            except:
                self.flash_error(t("Failed to load"))
                return None
        except KeyError:
            self.flash_error(t("Failed to decrypt"))
            return None
        except ValueError:
            # ValueError=not KEF or declined to decrypt
            pass

        return wallet_data, qr_format, persisted

    def _build_mismatch_warning(
        self,
        current_policy_type,
        required_policy_type,
        current_network,
        required_network,
        current_script_type=None,
        required_script_type=None,
    ):
        """Builds warning text for policy/network/script type mismatch"""
        from krux.key import get_policy_type_name, get_network_name

        offset_y = DEFAULT_PADDING + 2 * FONT_HEIGHT

        # Check if policy changed
        if current_policy_type != required_policy_type:
            self.ctx.display.draw_hcentered_text(
                "{}:".format(t("Policy Type")), offset_y, theme.highlight_color
            )
            offset_y += FONT_HEIGHT
            offset_y += (
                self.ctx.display.draw_hcentered_text(
                    "{} > {}".format(
                        get_policy_type_name(current_policy_type),
                        get_policy_type_name(required_policy_type),
                    ),
                    offset_y,
                )
                * FONT_HEIGHT
            )
            offset_y += 2 * FONT_HEIGHT

        # Check if script type changed
        if (
            required_script_type
            and current_script_type
            and current_script_type != required_script_type
        ):
            self.ctx.display.draw_hcentered_text(
                "{}:".format(t("Script Type")), offset_y, theme.highlight_color
            )
            offset_y += FONT_HEIGHT
            offset_y += (
                self.ctx.display.draw_hcentered_text(
                    "{} > {}".format(
                        current_script_type.upper(),
                        required_script_type.upper(),
                    ),
                    offset_y,
                )
                * FONT_HEIGHT
            )
            offset_y += 2 * FONT_HEIGHT

        # Check if network changed
        if required_network and current_network != required_network:
            self.ctx.display.draw_hcentered_text(
                "{}:".format(t("Network")), offset_y, theme.highlight_color
            )
            offset_y += FONT_HEIGHT
            offset_y += (
                self.ctx.display.draw_hcentered_text(
                    "{} > {}".format(
                        get_network_name(current_network),
                        get_network_name(required_network),
                    ),
                    offset_y,
                )
                * FONT_HEIGHT
            )

    def _handle_policy_mismatch(self, exception, wallet_data, qr_format, persisted):
        """Handles policy/network mismatch by prompting user and re-deriving key"""
        from krux.wallet import Wallet
        from krux.key import Key

        required_policy_type = exception.args[0]
        required_script_type = exception.args[1]
        current_policy_type = exception.args[2]
        required_network = exception.args[3] if len(exception.args) > 3 else None
        current_network = exception.args[4] if len(exception.args) > 4 else None
        current_script_type = self.ctx.wallet.key.script_type

        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            t("Wallet mismatch:"), DEFAULT_PADDING, theme.error_color
        )

        self._build_mismatch_warning(
            current_policy_type,
            required_policy_type,
            current_network,
            required_network,
            current_script_type,
            required_script_type,
        )

        if not self.prompt(t("Change wallet?"), BOTTOM_PROMPT_LINE):
            return None, None

        # Re-derive key with correct policy type, script type, and network
        updated_key = Key(
            self.ctx.wallet.key.mnemonic,
            required_policy_type,
            network=(
                required_network if required_network else self.ctx.wallet.key.network
            ),
            passphrase=self.ctx.wallet.key.passphrase,
            account_index=self.ctx.wallet.key.account_index,
            script_type=required_script_type,
        )

        wallet = Wallet(updated_key)
        wallet.persisted = persisted
        try:
            wallet.load(wallet_data, qr_format)
            return wallet, None
        except Exception as e:
            return wallet, e

    def _attempt_wallet_load(self, wallet_data, qr_format, persisted):
        """Attempts to load wallet with exception handling"""
        from krux.wallet import Wallet, PolicyMismatchWarning

        wallet = Wallet(self.ctx.wallet.key)
        wallet.persisted = persisted
        wallet_load_exception = None

        try:
            wallet.load(wallet_data, qr_format)
        except PolicyMismatchWarning as e:
            return self._handle_policy_mismatch(e, wallet_data, qr_format, persisted)
        except Exception as e:
            wallet_load_exception = e

        return wallet, wallet_load_exception

    def _load_wallet(self):
        """Load a wallet output descriptor from the camera or SD card"""
        # Load wallet data
        loaded = self._load_wallet_data()
        if loaded is None:  # user chose Back, or the load already reported itself
            return MENU_CONTINUE
        wallet_data, qr_format, persisted = loaded

        # Attempt to load the wallet with exception handling
        wallet, wallet_load_exception = self._attempt_wallet_load(
            wallet_data, qr_format, persisted
        )

        # Handle loading errors
        if wallet_load_exception:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Invalid wallet:") + "\n%s" % repr(wallet_load_exception),
                theme.error_color,
            )
            self.ctx.input.wait_for_button()
            return MENU_CONTINUE

        # Check if wallet was successfully loaded
        if not wallet or not wallet.is_loaded():
            return MENU_CONTINUE

        # Warn about missing change address if needed
        if not wallet.has_change_addr():
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Could not determine change address."), theme.error_color
            )
            if not self.prompt(t("Proceed anyway?"), BOTTOM_PROMPT_LINE):
                return MENU_CONTINUE

        # Display wallet and confirm loading
        self.ctx.display.clear()
        self.display_loading_wallet(wallet)
        if self.prompt(t("Load?"), BOTTOM_PROMPT_LINE):
            self.ctx.wallet = wallet
            self.flash_success(t("Wallet output descriptor loaded!"))

        return MENU_CONTINUE

    def display_wallet(self, wallet):
        """Try to show the wallet output descriptor as a QRCode"""
        try:
            w_data, qr_format = wallet.wallet_qr()
            if qr_format == FORMAT_NONE:
                qr_format = FORMAT_PMOFN
                w_data = w_data.decode() if not isinstance(w_data, str) else w_data
            self.display_qr_codes(w_data, qr_format, title=wallet.label)
        except Exception as e:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Error:") + "\n%s" % repr(e), theme.error_color
            )
            self.ctx.input.wait_for_button()

    def _draw_loading_header(self, wallet):
        """Clears the screen, draws the label and the computed policy of the
        wallet being loaded and returns the y offset for what follows"""
        self.ctx.display.clear()
        # The label can come from the file being loaded: cap its height, so
        # it can't push what Krux computed from the descriptor off the screen
        offset_y = DEFAULT_PADDING
        offset_y += (
            self.ctx.display.draw_hcentered_text(wallet.label, offset_y, max_lines=2)
            * FONT_HEIGHT
        )
        if wallet.is_multisig():
            # Quorum, script type and whether keys are sorted
            policy_text = "%d of %d %s %s" % (
                wallet.policy["m"],
                wallet.policy["n"],
                wallet.policy["type"].upper(),
                "sortedmulti" if wallet.descriptor.is_sorted else "multi",
            )
            offset_y += (
                self.ctx.display.draw_hcentered_text(
                    policy_text, offset_y, theme.highlight_color
                )
                * FONT_HEIGHT
            )
        return offset_y + FONT_HEIGHT // 2

    def _next_loading_page(self, wallet):
        """Waits for a button, then starts a new page of the wallet being loaded"""
        self.ctx.input.wait_for_button()
        return self._draw_loading_header(wallet)

    def _is_tr_internal_key(self, wallet, i, key):
        """Tells if key is the provably unspendable TR internal key"""
        return (
            not key.origin
            and i == 0
            and wallet.is_miniscript()
            and wallet.policy.get("type") == P2TR
        )

    def _is_our_key(self, wallet, key):
        """Tells if key, from a wallet with many keys, is the one loaded"""
        return (
            self.ctx.wallet.key
            and len(wallet.descriptor.keys) > 1
            and key.fingerprint == self.ctx.wallet.key.fingerprint
        )

    def _loading_key_lines(self, wallet, i, key):
        """Returns the lines, as (x, text, color), that describe a key of the
        wallet being loaded"""
        from krux.settings import THIN_SPACE

        padding = MINIMAL_PADDING if kboard.has_minimal_display else DEFAULT_PADDING
        indent = 0 if kboard.has_minimal_display else 3
        sub_padding = padding + indent * FONT_WIDTH
        sub_width = self.ctx.display.ascii_chars_per_line() - indent
        is_tr_internal = self._is_tr_internal_key(wallet, i, key)

        color = theme.fg_color
        if self._is_our_key(wallet, key):
            color = theme.highlight_color
        elif is_tr_internal:
            color = theme.disabled_color

        title = " " * indent
        if wallet.is_multisig() or wallet.is_miniscript():
            title = "{}: ".format(chr(65 + i))
        if is_tr_internal:
            title += t("TR internal key")
        else:
            title += FINGERPRINT_SYMBOL + THIN_SPACE
            title += str(key.origin)[:8] if key.origin else t("unknown")
        lines = [(padding, line, color) for line in self.ctx.display.to_lines(title)]

        if key.origin:
            derivation = "{} m{}".format(DERIVATION_PATH_SYMBOL, str(key.origin)[8:])
            lines.append((sub_padding, derivation, color))
        elif is_tr_internal:
            for line in self.ctx.display.to_lines(t("Provably unspendable")):
                lines.append((sub_padding, line, color))

        xpub = key.key.to_base58()
        # The derivation applied after the xpub decides every address.
        # Show it whenever it is not the standard receive/change pair.
        if key.suffix != "/<0;1>/*":
            suffix = xpub[:4] + (key.suffix or " (fixed)")
            for start in range(0, len(suffix), sub_width):
                lines.append(
                    (sub_padding, suffix[start : start + sub_width], theme.error_color)
                )

        # Full xpub, wrapped: a cropped one can be matched by another key
        for start in range(0, len(xpub), sub_width):
            lines.append((sub_padding, xpub[start : start + sub_width], color))
        return lines

    def display_loading_wallet(self, wallet):
        """Displays wallet descriptor attributes while loading"""
        from krux.settings import ELLIPSIS

        padding = MINIMAL_PADDING if kboard.has_minimal_display else DEFAULT_PADDING
        page_top = offset_y = self._draw_loading_header(wallet)
        our_key_indexes_chars = []
        unused_key_index = None
        for i, key in enumerate(wallet.descriptor.keys):
            if self._is_tr_internal_key(wallet, i, key):
                unused_key_index = chr(65 + i)
            if self._is_our_key(wallet, key):
                our_key_indexes_chars.append(chr(65 + i))

            lines = self._loading_key_lines(wallet, i, key)
            # Keys go whole on a page, above the prompt, whenever they fit
            if (
                offset_y > page_top
                and offset_y + len(lines) * FONT_HEIGHT > BOTTOM_PROMPT_LINE
            ):
                offset_y = self._next_loading_page(wallet)
            for x, text, color in lines:
                if offset_y + FONT_HEIGHT > BOTTOM_PROMPT_LINE:
                    # Key is taller than a page, continue it on the next one
                    offset_y = self._next_loading_page(wallet)
                self.ctx.display.draw_string(x, offset_y, text, color)
                offset_y += FONT_HEIGHT
            offset_y += FONT_HEIGHT // 2

        # Display miniscript policies if available
        if wallet.is_miniscript():
            from krux.pages.home_pages.miniscript_indenter import MiniScriptIndenter

            max_width = self.ctx.display.width() // FONT_WIDTH
            miniscript_policy = MiniScriptIndenter().indent(
                wallet.descriptor.full_policy, max_width
            )
            lines_left = (BOTTOM_PROMPT_LINE - offset_y) // FONT_HEIGHT

            if len(miniscript_policy) > lines_left:
                self.ctx.input.wait_for_button()
                offset_y = self._draw_loading_header(wallet)

            for line in miniscript_policy:
                self.ctx.display.draw_string(padding, offset_y, line)
                for idx, char in enumerate(line):
                    char_x = padding + idx * FONT_WIDTH
                    if char == unused_key_index:
                        self.ctx.display.draw_string(
                            char_x, offset_y, char, theme.disabled_color
                        )
                    elif char in our_key_indexes_chars:
                        self.ctx.display.draw_string(
                            char_x, offset_y, char, theme.highlight_color
                        )
                offset_y += FONT_HEIGHT
                if offset_y >= BOTTOM_PROMPT_LINE:
                    self.ctx.display.draw_hcentered_text(ELLIPSIS, offset_y)
                    self.ctx.input.wait_for_button()
                    offset_y = self._draw_loading_header(wallet)

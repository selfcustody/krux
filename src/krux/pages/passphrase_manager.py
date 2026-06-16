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
import json
from ...krux_settings import t, Settings
from ...sd_card import JSON_FILE_EXTENSION
from .. import (
    Page,
    Menu,
    MENU_CONTINUE,
)

PASSPHRASE_FILE = "/flash/passphrases.json"
MAX_PASSPHRASES = 10


class PassphraseManager(Page):
    """UI for managing multiple BIP39 passphrases"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.passphrases = self._load_passphrases()

    def _load_passphrases(self):
        """Load passphrases from flash storage"""
        try:
            with open(PASSPHRASE_FILE, "r") as f:
                return json.loads(f.read())
        except (OSError, ValueError):
            return []

    def _save_passphrases(self):
        """Save passphrases to flash storage"""
        try:
            with open(PASSPHRASE_FILE, "w") as f:
                f.write(json.dumps(self.passphrases))
        except OSError as e:
            self.flash_error(t("Failed to save") + ": " + str(e))

    def manager_menu(self):
        """Passphrase manager main menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("List Passphrases"), self.list_passphrases),
                (t("Add Passphrase"), self.add_passphrase),
                (t("Delete Passphrase"), self.delete_passphrase),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def list_passphrases(self):
        """List all stored passphrases"""
        if not self.passphrases:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("No passphrases stored"))
            self.ctx.input.wait_for_button()
            return MENU_CONTINUE

        for i, pp in enumerate(self.passphrases):
            self.ctx.display.clear()
            info = t("Passphrase") + " %d/%d:\n\n" % (i + 1, len(self.passphrases))
            info += pp.get("name", "Unnamed") + "\n"
            info += t("Fingerprint") + ": " + pp.get("fingerprint", "?")
            self.ctx.display.draw_hcentered_text(info, info_box=True)
            self.ctx.input.wait_for_button()

        return MENU_CONTINUE

    def add_passphrase(self):
        """Add a new passphrase"""
        if len(self.passphrases) >= MAX_PASSPHRASES:
            self.flash_error(t("Maximum passphrases reached") + ": %d" % MAX_PASSPHRASES)
            return MENU_CONTINUE

        from ..utils import Utils

        utils = Utils(self.ctx)
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Enter passphrase name"))
        name = utils.capture_from_keypad(
            t("Name"),
            keysets=[],
            starting_buffer="",
        )
        if not name:
            return MENU_CONTINUE

        from .wallet_settings import PassphraseEditor

        passphrase_editor = PassphraseEditor(self.ctx)
        passphrase = passphrase_editor.load_passphrase_menu(
            self.ctx.wallet.key.mnemonic
        )
        if passphrase is None:
            return MENU_CONTINUE

        from ...key import Key

        fingerprint = Key.extract_fingerprint(
            self.ctx.wallet.key.mnemonic, passphrase
        )

        self.passphrases.append({
            "name": name,
            "passphrase": passphrase,
            "fingerprint": fingerprint,
        })
        self._save_passphrases()

        self.flash_text(t("Passphrase added") + ": " + name)
        return MENU_CONTINUE

    def delete_passphrase(self):
        """Delete a stored passphrase"""
        if not self.passphrases:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("No passphrases stored"))
            self.ctx.input.wait_for_button()
            return MENU_CONTINUE

        menu_items = []
        for i, pp in enumerate(self.passphrases):
            label = pp.get("name", "Unnamed") + " (" + pp.get("fingerprint", "?") + ")"
            menu_items.append((label, lambda idx=i: self._delete_at(idx)))

        submenu = Menu(self.ctx, menu_items)
        submenu.run_loop()
        return MENU_CONTINUE

    def _delete_at(self, index):
        """Delete passphrase at given index"""
        if index < len(self.passphrases):
            name = self.passphrases[index].get("name", "Unnamed")
            if self.prompt(t("Delete") + " " + name + "?"):
                del self.passphrases[index]
                self._save_passphrases()
                self.flash_text(t("Passphrase deleted"))
        return MENU_CONTINUE

    def apply_passphrase(self):
        """Apply a stored passphrase to the current wallet"""
        if not self.passphrases:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("No passphrases stored"))
            self.ctx.input.wait_for_button()
            return MENU_CONTINUE

        menu_items = []
        for i, pp in enumerate(self.passphrases):
            label = pp.get("name", "Unnamed") + " (" + pp.get("fingerprint", "?") + ")"
            menu_items.append((label, lambda idx=i: self._apply_at(idx)))

        submenu = Menu(self.ctx, menu_items)
        submenu.run_loop()
        return MENU_CONTINUE

    def _apply_at(self, index):
        """Apply passphrase at given index"""
        if index < len(self.passphrases):
            passphrase = self.passphrases[index].get("passphrase", "")
            from ...key import Key
            from ...wallet import Wallet

            key = Key(
                self.ctx.wallet.key.mnemonic,
                self.ctx.wallet.key.policy_type,
                self.ctx.wallet.key.network,
                passphrase=passphrase,
            )
            self.ctx.wallet = Wallet(key)
            self.flash_text(
                t("%s: loaded!") % key.fingerprint_hex_str(True),
                highlight_prefix=":",
            )
        return MENU_CONTINUE

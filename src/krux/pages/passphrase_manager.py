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
from ..krux_settings import t, Settings
from ..sd_card import JSON_FILE_EXTENSION
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
)

PASSPHRASE_FILENAME = "passphrases.json"
PASSPHRASE_FILE = "/flash/" + PASSPHRASE_FILENAME
LOCATION_FLASH = "flash"
LOCATION_SD = "sd"
MAX_PASSPHRASES = 10


class PassphraseManager(Page):
    """UI for managing multiple BIP39 passphrases"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.passphrases = self._load_passphrases()

    def _read_flash(self):
        with open(PASSPHRASE_FILE, "r") as f:
            data = json.loads(f.read())
            if isinstance(data, list):
                return data
        return None

    def _read_sd(self):
        from ..sd_card import SDHandler

        with SDHandler() as sd:
            data = json.loads(sd.read(PASSPHRASE_FILENAME))
            if isinstance(data, list):
                return data
        return None

    def _load_passphrases(self):
        result = []
        for loader in [self._read_flash, self._read_sd]:
            try:
                data = loader()
                if data:
                    result.extend(data)
            except (OSError, ValueError, KeyError):
                pass
        return result

    def _save_passphrases(self):
        flash_pp = [p for p in self.passphrases if p.get("location", LOCATION_FLASH) == LOCATION_FLASH]
        sd_pp = [p for p in self.passphrases if p.get("location") == LOCATION_SD]
        saved = False
        try:
            with open(PASSPHRASE_FILE, "w") as f:
                f.write(json.dumps(flash_pp))
                saved = True
        except (OSError, ValueError):
            pass
        if sd_pp:
            try:
                from ..sd_card import SDHandler

                with SDHandler() as sd:
                    sd.write(PASSPHRASE_FILENAME, json.dumps(sd_pp))
                    saved = True
            except (OSError, ValueError, KeyError):
                pass
        if not saved:
            self.flash_error(t("Failed to save"))

    def _choose_storage(self):
        location = LOCATION_FLASH

        def _set(loc):
            nonlocal location
            location = loc
            return MENU_EXIT

        items = [(t("Internal Flash"), lambda: _set(LOCATION_FLASH))]
        if self.has_sd_card():
            items.append((t("SD Card"), lambda: _set(LOCATION_SD)))

        if len(items) == 1:
            return LOCATION_FLASH

        menu = Menu(self.ctx, items)
        menu.run_loop()
        return location

    def manager_menu(self):
        """Passphrase manager main menu — 3 items"""
        submenu = Menu(
            self.ctx,
            [
                (t("Passphrases"), self._passphrases_screen),
                (t("Type New"), self._type_new),
                (t("Clear"), self._clear),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def _passphrases_screen(self):
        """Unified screen: list stored passphrases + add new"""
        from . import LETTERS
        from .utils import Utils
        from ..key import Key

        while True:
            items = []
            for i, pp in enumerate(self.passphrases):
                name = pp.get("name", "Unnamed")
                fp = pp.get("fingerprint", "?")[:8]
                label = "%s [%s]" % (name, fp)
                items.append((label, lambda idx=i: self._passphrase_action(idx)))

            items.append((t("Add New"), lambda: self._add_new()))

            submenu = Menu(self.ctx, items)
            result = submenu.run_loop()

            if result == MENU_EXIT or result == ESC_KEY:
                break

        return MENU_CONTINUE

    def _passphrase_action(self, index):
        """Show action submenu for a stored passphrase"""
        if index >= len(self.passphrases):
            return MENU_CONTINUE

        pp = self.passphrases[index]
        name = pp.get("name", "Unnamed")

        action = None

        def _do(act):
            nonlocal action
            action = act
            return MENU_EXIT

        submenu = Menu(
            self.ctx,
            [
                (t("Apply"), lambda: _do("apply")),
                (t("View"), lambda: _do("view")),
                (t("Delete"), lambda: _do("delete")),
            ],
        )
        submenu.run_loop()

        if action == "apply":
            self._apply_at(index)
        elif action == "view":
            self._view_passphrase(index)
        elif action == "delete":
            self._delete_at(index)

        return MENU_CONTINUE

    def _view_passphrase(self, index):
        """Show details of a stored passphrase"""
        if index >= len(self.passphrases):
            return MENU_CONTINUE

        pp = self.passphrases[index]
        self.ctx.display.clear()
        info = pp.get("name", "Unnamed") + "\n"
        info += t("Fingerprint") + ": " + pp.get("fingerprint", "?") + "\n"
        pp_type = pp.get("type", "normal")
        info += t("Type") + ": " + t(pp_type.capitalize()) + "\n"
        loc = pp.get("location", LOCATION_FLASH)
        info += t("Storage") + ": " + ("Flash" if loc == LOCATION_FLASH else "SD")
        self.ctx.display.draw_hcentered_text(info, info_box=True)
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def _add_new(self):
        """Add a new passphrase — name, type, passphrase, storage"""
        if len(self.passphrases) >= MAX_PASSPHRASES:
            self.flash_error(t("Maximum passphrases reached") + ": %d" % MAX_PASSPHRASES)
            return MENU_CONTINUE

        from .utils import Utils
        from . import LETTERS
        from .wallet_settings import PassphraseEditor
        from ..key import Key

        utils = Utils(self.ctx)
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Enter passphrase name"))
        name = utils.capture_from_keypad(
            t("Name"),
            keysets=[LETTERS],
            starting_buffer="",
        )
        if name in (ESC_KEY, None) or not name:
            return MENU_CONTINUE

        pp_type = "normal"

        def _set_type(new_type):
            nonlocal pp_type
            pp_type = new_type
            return MENU_EXIT

        type_menu = Menu(
            self.ctx,
            [
                (t("Normal"), lambda: _set_type("normal")),
                (t("Duress"), lambda: _set_type("duress")),
            ],
        )
        type_menu.run_loop()

        passphrase_editor = PassphraseEditor(self.ctx)
        passphrase = passphrase_editor.load_passphrase_menu(
            self.ctx.wallet.key.mnemonic
        )
        if passphrase is None:
            return MENU_CONTINUE

        location = self._choose_storage()
        if location is None:
            return MENU_CONTINUE

        fingerprint = Key.extract_fingerprint(
            self.ctx.wallet.key.mnemonic, passphrase
        )

        self.passphrases.append({
            "name": name,
            "passphrase": passphrase,
            "fingerprint": fingerprint,
            "type": pp_type,
            "location": location,
        })
        self._save_passphrases()
        self.flash_text(t("Passphrase added") + ": " + name)
        return MENU_CONTINUE

    def _type_new(self):
        """Type and apply a new passphrase without storing"""
        from .wallet_settings import PassphraseEditor
        from ..key import Key
        from ..wallet import Wallet

        if not self.prompt(
            t("Add or change wallet passphrase?"), self.ctx.display.height() // 2
        ):
            return MENU_CONTINUE

        passphrase_editor = PassphraseEditor(self.ctx)
        passphrase = passphrase_editor.load_passphrase_menu(
            self.ctx.wallet.key.mnemonic
        )
        if passphrase is None:
            return MENU_CONTINUE

        self.ctx.wallet = Wallet(
            Key(
                self.ctx.wallet.key.mnemonic,
                self.ctx.wallet.key.policy_type,
                self.ctx.wallet.key.network,
                passphrase,
                self.ctx.wallet.key.account_index,
                self.ctx.wallet.key.script_type,
            )
        )
        return MENU_CONTINUE

    def _clear(self):
        """Reset wallet to empty passphrase"""
        if not self.prompt(
            t("Clear passphrase?"), self.ctx.display.height() // 2
        ):
            return MENU_CONTINUE

        from ..key import Key
        from ..wallet import Wallet

        self.ctx.wallet = Wallet(
            Key(
                self.ctx.wallet.key.mnemonic,
                self.ctx.wallet.key.policy_type,
                self.ctx.wallet.key.network,
                "",
                self.ctx.wallet.key.account_index,
                self.ctx.wallet.key.script_type,
            )
        )
        self.flash_text(t("Passphrase cleared"))
        return MENU_CONTINUE

    def _apply_at(self, index):
        """Apply passphrase at given index"""
        if index >= len(self.passphrases):
            return MENU_CONTINUE

        pp = self.passphrases[index]
        passphrase = pp.get("passphrase", "")
        pp_type = pp.get("type", "normal")

        from ..key import Key
        from ..wallet import Wallet

        key = Key(
            self.ctx.wallet.key.mnemonic,
            self.ctx.wallet.key.policy_type,
            self.ctx.wallet.key.network,
            passphrase=passphrase,
            account_index=self.ctx.wallet.key.account_index,
            script_type=self.ctx.wallet.key.script_type,
        )
        self.ctx.wallet = Wallet(key)

        if pp_type == "duress":
            self.ctx.duress_mode = True
            from ..krux_settings import Settings
            settings = Settings()
            wipe_delay = settings.duress.wipe_delay
            self.flash_text(
                t("Duress wallet loaded") + " - "
                + t("Wipe in") + " %ds" % wipe_delay,
                highlight_prefix=":",
            )
            import time
            time.sleep(wipe_delay)
            from ..duress import panic_wipe
            panic_wipe(self.ctx)
        else:
            self.flash_text(
                t("%s: loaded!") % key.fingerprint_hex_str(True),
                highlight_prefix=":",
            )
        return MENU_CONTINUE

    def _delete_at(self, index):
        """Delete passphrase at given index"""
        if index >= len(self.passphrases):
            return MENU_CONTINUE

        name = self.passphrases[index].get("name", "Unnamed")
        if self.prompt(t("Delete") + " " + name + "?"):
            del self.passphrases[index]
            self._save_passphrases()
            self.flash_text(t("Passphrase deleted"))
        return MENU_CONTINUE

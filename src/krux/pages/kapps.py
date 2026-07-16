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

"""Krux apps (kapps) manager: install, verify and run developer-signed apps.

Kapp contract
-------------
A kapp is a single ``.mpy`` module (compiled with the firmware's ``mpy-cross``)
accompanied by a detached ``.mpy.sig`` signature. A kapp must expose:

- ``run(ctx)``  -- entry point; receives the Krux ``ctx`` and returns when done.

and may optionally expose:

- ``ALLOW_STARTUP``  -- truthy to permit being set as a boot startup kapp;
- ``NAME`` / ``VERSION``  -- human-readable metadata.

Security model
--------------
- Kapps are verified against the dedicated ``KAPP_SIGNER_PUBKEYS`` (never the
  firmware signer key). A kapp is accepted only if a trusted key signed the
  exact bytes present in flash.
- The signature is re-verified against the flash copy on *every* execution
  (menu and startup paths alike): flash content is never trusted from an
  earlier check.
- A kapp's module-level code runs on import. This only happens after signature
  verification, so importing is gated on the kapp being trusted.
- Imports are sandboxed (``vfs.exec_allowed`` and a chdir into flash) and the
  sandbox is always torn down afterwards, dropping the module from
  ``sys.modules`` so nothing it patched survives into the session.
- The device reboots after any kapp exits, so a misbehaving kapp cannot leave
  poisoned state driving login, tamper checks or wallet handling.
"""

from krux.pages import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
)
from krux.krux_settings import t
from krux.display import BOTTOM_PROMPT_LINE
from krux.sd_card import MPY_FILE_EXTENSION, SIGNATURE_FILE_EXTENSION, SD_PATH
from krux.settings import FLASH_PATH, STARTUP_APPS_FILE
import os

READABLEBUFFER_SIZE = 128
# Kapp module contract
RUN_ATTR = "run"  # required: run(ctx) entry point
STARTUP_ATTR = "ALLOW_STARTUP"  # optional: may be set as a startup kapp
# Refuse .mpy files larger than this before copying to flash
MAX_KAPP_SIZE = 256 * 1024


class Kapps(Page):
    """Krux standalone apps manager"""

    def __init__(self, ctx):
        self.ctx = ctx

        items = []
        signed_apps = self.parse_all_flash_apps()
        for app_name in signed_apps:
            clean_name = app_name[:-4]
            items += [
                (clean_name, lambda name=clean_name: self.execute_flash_kapp(name))
            ]
        items += [
            (
                t("Load from SD card"),
                None if not self.has_sd_card() else self.load_sd_kapp,
            )
        ]

        super().__init__(
            ctx,
            Menu(ctx, items),
        )

    def parse_all_flash_apps(self):
        """Check if any .mpy app present in flash is signed.
        If not, ask for deletion to prevent importing and executing malicious code"""

        from krux.firmware import sha256

        unsigned_apps = []
        signed_apps = []
        flash_path_prefix = "/%s/" % FLASH_PATH
        for file in os.listdir(flash_path_prefix):
            if file.endswith(MPY_FILE_EXTENSION):
                # Check if signature file exists for the .mpy file.
                # Only a missing/unreadable file means "unsigned"; a failure
                # inside signature verification is an error and must surface,
                # not silently classify the app as unsigned.
                try:
                    with open(
                        flash_path_prefix + file + SIGNATURE_FILE_EXTENSION,
                        "rb",
                        buffering=0,
                    ) as sigfile:
                        sig_data = sigfile.read()
                except OSError:
                    unsigned_apps += [file]
                    continue
                if self.valid_signature(sig_data, sha256(flash_path_prefix + file)):
                    signed_apps += [file]
                else:
                    unsigned_apps += [file]

        if len(unsigned_apps) > 0:
            # Prompts user about deleting as it will change flash memory and TC hash
            self.ctx.display.clear()
            if not self.prompt(
                t("Unsigned apps found in flash will be deleted.")
                + "\n\n"
                + t("Proceed?"),
                self.ctx.display.height() // 2,
            ):
                raise ValueError("Unsigned apps found in flash")

            # Delete any .mpy files from flash VFS to avoid malicious code import/execution
            for app in unsigned_apps:
                os.remove(flash_path_prefix + app)
                self._remove_from_startup(app[: -len(MPY_FILE_EXTENSION)])

        return signed_apps

    def valid_signature(self, sig, data_hash):
        """Return if any trusted kapp signer key signed data_hash"""

        from krux.firmware import get_kapp_pubkeys, check_signature

        pubkeys = get_kapp_pubkeys()
        if not pubkeys:
            # No kapp key provisioned or all malformed: fail closed
            raise ValueError("Invalid public key")

        for pubkey in pubkeys:
            if check_signature(pubkey, sig, data_hash):
                return True

        return False

    def _verify_flash_kapp(self, app_name):
        """Verify the signature of a kapp as it exists in flash right now.
        Called on every execution so flash content is never trusted from an
        earlier check (boot, install or menu listing)."""

        from krux.firmware import sha256

        flash_path_prefix = "/%s/" % FLASH_PATH
        mpy_path = flash_path_prefix + app_name + MPY_FILE_EXTENSION
        try:
            with open(mpy_path + SIGNATURE_FILE_EXTENSION, "rb", buffering=0) as f:
                sig_data = f.read()
        except OSError:
            return False
        return self.valid_signature(sig_data, sha256(mpy_path))

    def _load_startup_apps(self):
        """Reads the set of startup apps from flash (empty on any error)"""

        import ujson as json

        try:
            with open("/%s/%s" % (FLASH_PATH, STARTUP_APPS_FILE), "r") as f:
                return set(json.load(f))
        except (OSError, ValueError):
            return set()

    def _save_startup_apps(self, startup_apps):
        """Persists the set of startup apps to flash"""

        import ujson as json

        with open("/%s/%s" % (FLASH_PATH, STARTUP_APPS_FILE), "w") as f:
            json.dump(list(startup_apps), f)

    def _add_to_startup(self, app_name):
        """Registers an app as a startup kapp"""

        startup_apps = self._load_startup_apps()
        if app_name not in startup_apps:
            startup_apps.add(app_name)
            self._save_startup_apps(startup_apps)

    def _remove_from_startup(self, app_name):
        """Drops an app from the startup apps file, if present"""

        startup_apps = self._load_startup_apps()
        if app_name in startup_apps:
            startup_apps.discard(app_name)
            self._save_startup_apps(startup_apps)

    def _with_flash_kapp(self, app_name, callback):
        """Import a signature-verified kapp from flash, run callback(module),
        and always tear the import sandbox down afterwards.

        The kapp's module-level code runs on import; callers must verify the
        signature first. The sandbox (flash import + chdir) and sys.modules are
        restored in a finally block even if import or the callback raises, so
        nothing the kapp loaded or patched survives this call."""

        import vfs
        import sys
        import gc

        vfs.exec_allowed(True)
        os.chdir("/" + FLASH_PATH)
        try:
            module = __import__(app_name)
            return callback(module)
        finally:
            vfs.exec_allowed(False)
            os.chdir("/")
            sys.modules.pop(app_name, None)
            gc.collect()

    def _invoke_kapp(self, module):
        """Validate the kapp contract and run its entry point"""

        entry = getattr(module, RUN_ATTR, None)
        if not callable(entry):
            raise ValueError("Not a Krux app")
        entry(self.ctx)

    def _flash_copy_matches(self, expected_hash, actual_hash):
        """Return if the hash of the bytes written to flash matches the hash
        the user approved (guards the SD->flash copy against TOCTOU/corruption)"""
        return expected_hash == actual_hash

    def execute_flash_kapp(self, app_name, from_sd=False, prompt=True):
        """Prompt user to load and 'execute' a .mpy Krux app"""

        self.ctx.display.clear()
        if prompt and not self.prompt(
            t("Execute %s Krux app?") % app_name, self.ctx.display.height() // 2
        ):
            return MENU_EXIT if from_sd else MENU_CONTINUE

        # Re-verify the signature of the flash copy on every execution, on the
        # menu path and the startup path alike. Anyone with flash write access
        # could have swapped the .mpy since it was last checked.
        if not self._verify_flash_kapp(app_name):
            self.flash_error(t("Bad signature"))
            return MENU_EXIT if from_sd else MENU_CONTINUE

        # Import and run inside the flash sandbox; the helper always tears the
        # sandbox down and drops the module afterwards, even on error.
        try:
            self._with_flash_kapp(app_name, self._invoke_kapp)
        except Exception as e:
            import sys

            sys.print_exception(e)
            from krux.themes import theme

            self.ctx.display.to_portrait()
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Error:") + "\n" + "Could not execute %s" % app_name,
                theme.error_color,
            )
            self.ctx.input.wait_for_button()

        # After any execution reboot Krux (better safe than sorry) - startup
        # kapps included: a misbehaving kapp must not leave a poisoned module
        # state driving login, TC checks and wallet handling.
        from ..power import power_manager

        power_manager.shutdown()
        return None

    def load_sd_kapp(self):
        """Loads kapp from SD to flash, then executes"""

        # Prompt user for .mpy file
        from krux.pages.utils import Utils

        filename, _ = Utils(self.ctx).load_file(
            MPY_FILE_EXTENSION, prompt=False, only_get_filename=True
        )

        if not filename:
            return MENU_CONTINUE

        from krux.firmware import sha256
        import binascii

        sd_path_prefix = "/%s/" % SD_PATH

        # Refuse oversized files before hashing or copying anything
        try:
            file_size = os.stat(sd_path_prefix + filename)[6]
        except OSError:
            file_size = 0
        if file_size > MAX_KAPP_SIZE:
            self.flash_error(t("File too large"))
            return MENU_CONTINUE

        data_hash = sha256(sd_path_prefix + filename)

        # Confirm hash string
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            filename + "\n\n" + "SHA256:\n\n" + binascii.hexlify(data_hash).decode(),
            highlight_prefix=":",
        )
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE

        # Check signature of .mpy file in SD
        sig_data = None
        try:
            with open(
                sd_path_prefix + filename + SIGNATURE_FILE_EXTENSION, "rb", buffering=0
            ) as sigfile:
                sig_data = sigfile.read()
        except OSError:
            self.flash_error(t("Missing signature file"))
            return MENU_CONTINUE

        if not self.valid_signature(sig_data, data_hash):
            self.flash_error(t("Bad signature"))
            return MENU_CONTINUE

        # Check if app is already installed in flash
        found_in_flash_vfs = False
        filename_flash = ""
        flash_path_prefix = "/%s/" % FLASH_PATH
        for file in os.listdir(flash_path_prefix):
            if file.endswith(MPY_FILE_EXTENSION):
                if sha256(flash_path_prefix + file) == data_hash:
                    found_in_flash_vfs = True
                    filename_flash = file
                    break

        # Copy kapp + sig from SD to flash VFS, if app not found
        install_from_sd = False
        if not found_in_flash_vfs:
            install_from_sd = True

            # Warns user about changing users's flash internal memory region
            self.ctx.display.clear()
            if not self.prompt(
                t("App will be stored internally on flash.") + "\n\n" + t("Proceed?"),
                self.ctx.display.height() // 2,
            ):
                return MENU_CONTINUE

            # Save APP .mpy
            filename_flash = filename.rsplit("/", 1)[-1]
            with open(
                flash_path_prefix + filename_flash,
                "wb",
                buffering=0,
            ) as flash_file:
                with open(sd_path_prefix + filename, "rb", buffering=0) as sd_file:
                    while True:
                        chunk = sd_file.read(READABLEBUFFER_SIZE)
                        if not chunk:
                            break
                        flash_file.write(chunk)

            # Verify the bytes actually written to flash against the hash the
            # user approved: the SD file could have changed between the hash
            # prompt and this copy (TOCTOU), or the copy could be corrupted.
            if not self._flash_copy_matches(
                data_hash, sha256(flash_path_prefix + filename_flash)
            ):
                os.remove(flash_path_prefix + filename_flash)
                self.flash_error(t("Bad signature"))
                return MENU_CONTINUE

            # Save SIG .mpy.sig
            with open(
                flash_path_prefix + filename_flash + SIGNATURE_FILE_EXTENSION,
                "wb",
                buffering=0,
            ) as kapp_sig_file:
                kapp_sig_file.write(sig_data)

            # Register the app as a startup kapp if it opts in (ALLOW_STARTUP).
            # The flash copy is signature-verified above, so importing it in the
            # sandbox to read the flag is gated on the kapp being trusted.
            app_name = filename_flash[:-4]
            try:
                self._with_flash_kapp(
                    app_name,
                    lambda module: self._register_startup_flag(module, app_name),
                )
            except Exception as e:
                import sys

                sys.print_exception(e)

        del sig_data
        import gc

        gc.collect()

        return self.execute_flash_kapp(filename_flash[:-4], install_from_sd)

    def _register_startup_flag(self, module, app_name):
        """Records the app as a startup kapp when it declares ALLOW_STARTUP"""

        if getattr(module, STARTUP_ATTR, False):
            self._add_to_startup(app_name)

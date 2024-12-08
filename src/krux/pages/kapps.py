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
    MENU_CONTINUE,
)
from krux.krux_settings import t
from krux.display import BOTTOM_PROMPT_LINE

READABLEBUFFER_SIZE = 128


class Kapps(Page):
    """Krux standalone apps manager"""

    def _check_signature(self, sig, data_hash):
        from embit import ec
        from ..metadata import SIGNER_PUBKEY

        pubkey = None
        try:
            pubkey = ec.PublicKey.from_string(SIGNER_PUBKEY)
        except:
            raise ValueError("Invalid public key")

        try:
            # Parse, serialize, and reparse to ensure signature is compact prior to verification
            sig = ec.Signature.parse(ec.Signature.parse(sig).serialize())

            if not pubkey.verify(sig, data_hash):
                self.flash_error(t("Bad signature"))
                return False
        except:
            self.flash_error(t("Bad signature"))
            return False

        return True

    def load_kapp(self):  # pylint: disable=R1710
        """Prompt user to load and 'execute' a .mpy Krux app"""
        if not self.prompt(
            t("Execute a signed Krux app?"), self.ctx.display.height() // 2
        ):
            return MENU_CONTINUE

        # Check if Krux app is enabled
        from krux.krux_settings import Settings

        if not Settings().security.allow_kapp:
            self.flash_error(t("Allow in settings first!"))
            return MENU_CONTINUE

        if not self.has_sd_card():
            self.flash_error(t("SD card not detected."))
            return MENU_CONTINUE

        # Prompt user for .mpy file
        from krux.pages.utils import Utils
        from krux.sd_card import MPY_FILE_EXTENSION, SIGNATURE_FILE_EXTENSION, SD_PATH

        filename, _ = Utils(self.ctx).load_file(
            MPY_FILE_EXTENSION, prompt=False, only_get_filename=True
        )

        if not filename:
            return MENU_CONTINUE

        # Confirm hash string
        sd_path_prefix = "/%s/" % SD_PATH
        from krux.firmware import sha256

        data_hash = sha256(sd_path_prefix + filename)

        import binascii

        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            filename + "\n\n" + "SHA256:\n" + binascii.hexlify(data_hash).decode()
        )
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE

        # Check signature of .mpy file in SD
        sig_data = None
        try:
            sig_data = open(
                sd_path_prefix + filename + SIGNATURE_FILE_EXTENSION, "rb"
            ).read()
        except:
            self.flash_error(t("Missing signature file"))
            return MENU_CONTINUE

        if not self._check_signature(sig_data, data_hash):
            return MENU_CONTINUE

        # Warns user about changing users's flash internal memory region
        self.ctx.display.clear()
        if not self.prompt(
            t("App will be stored internally on flash.") + "\n\n" + t("Proceed?"),
            self.ctx.display.height() // 2,
        ):
            return MENU_CONTINUE

        # Delete any .mpy files from flash VFS to avoid malicious code import/execution
        import os
        from krux.settings import FLASH_PATH

        found_in_flash_vfs = False
        flash_path_prefix = "/%s/" % FLASH_PATH
        for file in os.listdir(flash_path_prefix):
            if file.endswith(MPY_FILE_EXTENSION):
                # Only remove .mpy different from what was loaded from SD
                if sha256(flash_path_prefix + file) != data_hash:
                    os.remove(flash_path_prefix + file)
                else:
                    found_in_flash_vfs = True

        # Copy kapp + sig from SD to flash VFS if not found
        # sig file will allow the check and execution of the kapp at startup (opsec)
        kapp_filename = "kapp"
        if not found_in_flash_vfs:
            with open(
                flash_path_prefix + kapp_filename + MPY_FILE_EXTENSION,
                "wb",
                buffering=0,
            ) as kapp_file:
                with open(sd_path_prefix + filename, "rb", buffering=0) as file:
                    while True:
                        chunk = file.read(READABLEBUFFER_SIZE)
                        if not chunk:
                            break
                        kapp_file.write(chunk)

            with open(
                flash_path_prefix
                + kapp_filename
                + MPY_FILE_EXTENSION
                + SIGNATURE_FILE_EXTENSION,
                "wb",
            ) as kapp_sig_file:
                kapp_sig_file.write(sig_data)

        del sig_data
        import gc

        gc.collect()

        # Allows import of files in flash VFS
        # TODO: Dinamically enable vsf->execution
        os.chdir("/" + FLASH_PATH)

        # Import and exec the kapp
        i_kapp = None
        try:
            i_kapp = __import__(kapp_filename)
            i_kapp.run(self.ctx)
        except:
            # avoids importing from flash VSF
            os.chdir("/")

            # unimport module
            import sys

            del i_kapp
            del sys.modules[kapp_filename]

            raise ValueError("Could not execute %s" % filename)

        # avoids importing from flash VSF
        os.chdir("/")

        # After execution restart Krux (better safe than sorry)
        from ..power import power_manager

        power_manager.shutdown()

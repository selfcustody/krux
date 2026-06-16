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
    # ESC_KEY,
    # LETTERS,
    # UPPERCASE_LETTERS,
    # NUM_SPECIAL_1,
    # NUM_SPECIAL_2,
)
from ..krux_settings import t

# TODO: re-enable "Create a QR Code" (and keypads ^^^) once encryption is possible w/o Datum Tool


class Tools(Page):
    """Krux generic tools"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("QR Benchmark"), self.qr_benchmark),
                    (t("Datum Tool"), self.datum_tool),
                    (t("Descriptor Addresses"), self.descriptor_addresses),
                    (t("Nostr Keys"), self.nostr_keys),
                    (t("Device Tests"), self.device_tests),
                    (t("Flash Tools"), self.flash_tools),
                    (t("Security"), self.security_menu),
                    (t("Remove Mnemonic"), self.rm_stored_mnemonic),
                ],
            ),
        )
        self.ctx = ctx

    def flash_tools(self):
        """Handler for the 'Flash Tools' menu item"""

        from .flash_tools import FlashTools

        flash_tools = FlashTools(self.ctx)
        flash_tools.flash_tools_menu()
        return MENU_CONTINUE

    def security_menu(self):
        """Handler for the 'Security' menu item"""
        from .anti_tamper import AntiTamper

        anti_tamper = AntiTamper(self.ctx)
        return anti_tamper.security_menu()

    def nostr_keys(self):
        """Handler for the 'Nostr Keys' menu item"""
        from .nostr_keys import NostrKeys

        nostr = NostrKeys(self.ctx)
        return nostr.nostr_menu()

    def rm_stored_mnemonic(self):
        """Lists and allow deletion of stored mnemonics"""
        from .encryption_ui import LoadEncryptedMnemonic

        encrypted_mnemonics = LoadEncryptedMnemonic(self.ctx)
        while True:
            ret = encrypted_mnemonics.load_from_storage(remove_opt=True)
            if ret == MENU_CONTINUE:
                del encrypted_mnemonics
                return ret

    def datum_tool(self):
        """Handler for the 'Datum Tool' menu item"""
        import sys
        from .datum_tool import DatumToolMenu

        while True:
            if DatumToolMenu(self.ctx).run() == MENU_EXIT:
                break

        sys.modules.pop("krux.pages.datum_tool")
        del sys.modules["krux.pages"].datum_tool
        return MENU_CONTINUE

    # def create_qr(self):
    #    """Handler for the 'Create QR Code' menu item"""
    #    if self.prompt(
    #        t("Create QR code from text?"),
    #        self.ctx.display.height() // 2,
    #    ):
    #        text = self.capture_from_keypad(
    #            t("Text"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
    #        )
    #        if text in ("", ESC_KEY):
    #            return MENU_CONTINUE
    #
    #        from .qr_view import SeedQRView
    #
    #        title = t("Custom QR Code")
    #        seed_qr_view = SeedQRView(self.ctx, data=text, title=title)
    #        return seed_qr_view.display_qr(allow_export=True)
    #    return MENU_CONTINUE

    def descriptor_addresses(self):
        """Handler for the 'Descriptor Addresses' menu item"""
        from .home_pages.wallet_descriptor import WalletDescriptor
        from .home_pages.addresses import Addresses
        from ..wallet import Wallet

        self.ctx.wallet = Wallet(None)
        menu_result = WalletDescriptor(self.ctx).wallet()
        if self.ctx.wallet.is_loaded():
            menu_result = Addresses(self.ctx).addresses_menu()
        return menu_result

    def device_tests(self):
        """Handler for the 'Device Tests' menu item"""
        import sys
        from .device_tests import DeviceTests

        page = DeviceTests(self.ctx)
        page.run()
        sys.modules.pop("krux.pages.device_tests")
        del sys.modules["krux.pages"].device_tests
        return MENU_CONTINUE

    def qr_benchmark(self):
        """Handler for the 'QR Benchmark' menu item"""
        import time
        import sensor

        FRAME_COUNT = 30
        results = []

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("QR Benchmark") + "\n\n" + t("Starting..."))

        # Test 1: find_qrcodes() per frame
        sensor.reset()
        sensor.set_pixformat(sensor.RGB565)
        sensor.set_framesize(sensor.QVGA)
        sensor.run(1)
        time.sleep_ms(500)

        times = []
        for i in range(FRAME_COUNT):
            img = sensor.snapshot()
            start = time.ticks_us()
            img.find_qrcodes()
            elapsed = time.ticks_diff(time.ticks_us(), start)
            times.append(elapsed)

        avg_rgb = sum(times) // len(times)
        results.append("RGB565: %d ms" % (avg_rgb // 1000))

        # Test 2: GRAYSCALE
        sensor.reset()
        sensor.set_pixformat(sensor.GRAYSCALE)
        sensor.set_framesize(sensor.QVGA)
        sensor.run(1)
        time.sleep_ms(500)

        times = []
        for i in range(FRAME_COUNT):
            img = sensor.snapshot()
            start = time.ticks_us()
            img.find_qrcodes()
            elapsed = time.ticks_diff(time.ticks_us(), start)
            times.append(elapsed)

        avg_gray = sum(times) // len(times)
        results.append("GRAYSCALE: %d ms" % (avg_gray // 1000))

        # Calculate improvement
        if avg_rgb > 0:
            improvement = (avg_rgb - avg_gray) * 100 // avg_rgb
            results.append("Improvement: %d%%" % improvement)

        # Test 3: Mode switch time
        from krux.camera import Camera, QR_SCAN_MODE, ANTI_GLARE_MODE

        cam = Camera()
        start = time.ticks_ms()
        cam.initialize_run(QR_SCAN_MODE)
        t1 = time.ticks_diff(time.ticks_ms(), start)

        start = time.ticks_ms()
        cam.initialize_run(ANTI_GLARE_MODE)
        t2 = time.ticks_diff(time.ticks_ms(), start)

        results.append("Mode switch: %d ms" % t1)

        # Show results
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("QR Benchmark") + "\n\n" + "\n".join(results)
        )
        time.sleep(5)

        return MENU_CONTINUE

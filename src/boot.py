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
# pylint: disable=C0103

import sys
import time
import gc
import os

from krux.power import power_manager
from krux.display import display
from krux.context import ctx

MIN_SPLASH_WAIT_TIME = 1000


def draw_splash(display_splash):
    """Display splash while loading modules"""
    from krux.display import SPLASH

    display_splash.clear()
    display_splash.draw_centered_text(SPLASH)


def check_for_updates():
    """Checks SD card, if a valid firmware is found asks if user wants to update the device"""

    # Check if the SD card is inserted and contains a firmware before loading the firmware module
    try:
        os.stat("/sd/firmware.bin")
    except OSError:
        return

    from krux import firmware

    if firmware.upgrade():
        power_manager.shutdown()

    # Unimport firware
    sys.modules.pop("krux.firmware")
    del sys.modules["krux"].firmware
    del firmware


def tc_code_verification(ctx_pin):
    """Loads and run the Pin Verification page"""
    from krux.krux_settings import Settings, TC_CODE_PATH

    # Checks if there is a pin set
    try:
        if not (os.stat(TC_CODE_PATH)[0] & 0x4000) == 0:
            raise OSError
    except OSError:
        print("No pin set")
        return True

    ctx_pin.tc_code_enabled = True

    if not Settings().security.boot_flash_hash:
        return True

    from krux.pages.tc_code_verification import TCCodeVerification

    pin_verification_page = TCCodeVerification(ctx_pin)
    pin_hash = pin_verification_page.capture(return_hash=True)
    if not pin_hash:
        return False

    from krux.pages.flash_tools import FlashHash

    flash_hash = FlashHash(ctx_pin, pin_hash)
    flash_hash.generate()

    # Unimport FlashHash the free memory
    sys.modules.pop("krux.pages.flash_tools")
    del sys.modules["krux"].pages.flash_tools
    del FlashHash

    # Unimport TCCodeVerification the free memory
    sys.modules.pop("krux.pages.tc_code_verification")
    del sys.modules["krux"].pages.tc_code_verification
    del TCCodeVerification
    return True


def login(ctx_login):
    """Loads and run the Login page"""
    from krux.pages.login import Login

    start_from = None
    while True:
        if not Login(ctx_login).run(start_from):
            # Exited for shutdown
            break

        if ctx_login.wallet is not None:
            # Exited for Home menu
            break

        # Exited for change in Settings
        start_from = Login.SETTINGS_MENU_INDEX

    # Unimport Login the free memory
    sys.modules.pop("krux.pages.login")
    del sys.modules["krux"].pages.login
    del Login


def home(ctx_home):
    """Loads and run the Login page"""
    from krux.pages.home_pages.home import Home

    if ctx_home.is_logged_in():
        while True:
            if not Home(ctx_home).run():
                break


def startup_kapp(ctx_app):
    """Check for startup kapp needs to run before firmware"""
    from krux.krux_settings import Settings

    app_name = Settings().security.startup_kapp
    if app_name == "none":
        return False

    from krux.pages.kapps import Kapps

    kapps = Kapps(ctx_app)
    kapps.execute_flash_kapp(app_name, prompt=False)

    return True


# ------
# Boot initialization
# ------

display.initialize_lcd()

if not startup_kapp(ctx):
    preimport_ticks = time.ticks_ms()
    draw_splash(display)
    check_for_updates()
    gc.collect()

    # If importing happened too fast, sleep the difference so the logo
    # will be shown
    postimport_ticks = time.ticks_ms()
    if preimport_ticks + MIN_SPLASH_WAIT_TIME > postimport_ticks:
        time.sleep_ms(preimport_ticks + MIN_SPLASH_WAIT_TIME - postimport_ticks)


from krux.auto_shutdown import auto_shutdown

ctx.power_manager = power_manager
auto_shutdown.add_ctx(ctx)

if not tc_code_verification(ctx):
    power_manager.shutdown()
login(ctx)
gc.collect()
home(ctx)

ctx.clear()
power_manager.shutdown()

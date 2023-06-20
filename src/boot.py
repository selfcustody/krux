# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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

import sys
import gc

sys.path.append("")
sys.path.append(".")

SPLASH = """
                
                
                
    ██         
    ██         
    ██         
  ██████       
    ██         
    ██  ██     
    ██ ██      
    ████       
    ██ ██      
    ██  ██     
    ██   ██    
                
                
                
"""[
    1:-1
]

from krux.power import power_manager


def check_for_updates():
    """Checks SD card, if a valid firmware is found asks if user wants to update the device"""
    from krux import firmware

    if firmware.upgrade():
        power_manager.shutdown()

    # Unimport firware
    sys.modules.pop("krux.firmware")
    del sys.modules["krux"].firmware
    del firmware


def login(ctx_login):
    """Loads and run the Login page"""
    from krux.pages.login import Login

    login_start_from = None
    while True:
        if not Login(ctx_login).run(login_start_from):
            break

        if ctx_login.wallet is not None:
            # Have a loaded wallet
            break
        # Login closed due to change of locale at Settings
        login_start_from = 2  # will start Login again from Settings

    # Unimport Login the free memory
    sys.modules.pop("krux.pages.login")
    del sys.modules["krux"].pages.login
    del Login


def home(ctx_home):
    """Loads and run the Login page"""
    from krux.pages.home import Home

    if ctx_home.wallet is not None:
        while True:
            if not Home(ctx_home).run():
                break


check_for_updates()
gc.collect()

from krux.context import Context

ctx = Context()
ctx.power_manager = power_manager
# Display splash while loading pages
ctx.display.clear()
ctx.display.draw_centered_text(SPLASH.split("\n"))
login(ctx)
gc.collect()
home(ctx)

ctx.clear()
power_manager.shutdown()

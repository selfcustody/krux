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
import time

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

SPLASH_ALT = """
          /|         
         /_|         
 ________| |         
<_|_.'   " |         
    / O . O \,--,    
    | .---. |/ /     
    \* \_/ */ /      
 ____\     / /______ 
/           / \     |
'---.       |__\  __|
    |       |\ __|   
   /        \__\     
   \        /        
    ;-.--.-:_        
   <__;   '__>       
     Pokémon!        
"""[
    1:-1
]

from krux import firmware
from krux.power import power_manager

if firmware.upgrade():
    power_manager.shutdown()

# Unimport firware
sys.modules.pop("krux.firmware")
del sys.modules["krux"].firmware
del firmware

# Note: These imports come after the firmware upgrade check
#       to allow it to have more memory to work with
import lcd
from krux.context import Context

ctx = Context()
ctx.power_manager = power_manager

# Check for the correct SPLASH
try:
    import ujson as json
except ImportError:
    import json

settings = {}
file_location = "/flash/"
filename = "settings.json"

# Check for the correct settings persist location
try:
    with open(file_location + filename, "r") as f:
        settings = json.loads(f.read())
except:
    pass

file_location = (
    settings.get("settings", {}).get("persist", {}).get("location", "undefined")
)

# Settings file not found on flash, or key is missing
if file_location != "flash":
    file_location = "/sd/"
    try:
        with open(file_location + filename, "r") as f:
            settings = json.loads(f.read())
    except:
        pass

# Check if locale is set to pokemon to change SPLASH
if settings.get("settings", {}).get("i18n", {}).get("locale", "undefined") == "pokemon":
    SPLASH = SPLASH_ALT

del settings, file_location, filename

# Display splash while loading pages
ctx.display.draw_centered_text(SPLASH.split("\n"), color=lcd.WHITE)

preimport_ticks = time.ticks_ms()
from krux.pages.login import Login
from krux.pages.home import Home

postimport_ticks = time.ticks_ms()

# If importing happened in under 1s, sleep the difference so the logo
# will be shown
MIN_LOGO_TIME = 1000  # 1s
if preimport_ticks + MIN_LOGO_TIME > postimport_ticks:
    time.sleep_ms(preimport_ticks + MIN_LOGO_TIME - postimport_ticks)
del preimport_ticks, postimport_ticks, MIN_LOGO_TIME

login_start_from = None
while True:
    if not Login(ctx).run(login_start_from):
        break

    if ctx.wallet is None:
        # Login closed due to change of locale at Settings
        login_start_from = 2  # will start Login again from Settings
        continue

    if not Home(ctx).run():
        break
from krux.krux_settings import t

ctx.display.flash_text(t("Shutting down.."))

ctx.clear()
power_manager.shutdown()

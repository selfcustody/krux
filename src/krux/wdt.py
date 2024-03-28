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
import machine
from .settings import FLASH_PATH, SETTINGS_FILENAME

try:
    import ujson as json
except ImportError:
    import json

RESET_TIMEOUT = 30000
WDT_CONF_NAME = "WATCHDOG_DISABLE"

# Create a watchdog timer that resets the device if not fed for 30s
wdt = machine.WDT(id=0, timeout=RESET_TIMEOUT)

# Check if user wanted to disable the watchdog!
try:
    with open("/" + FLASH_PATH + "/" + SETTINGS_FILENAME, "r") as f:
        conf_dict = json.loads(f.read())
        if conf_dict.get(WDT_CONF_NAME, False):
            print("Watchdog disabled!")
            wdt.stop()
        del conf_dict
except:
    pass

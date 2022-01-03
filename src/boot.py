# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

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
sys.path.append('')
sys.path.append('.')

from krux import firmware
from krux.power import PowerManager

pmu = PowerManager()
if firmware.upgrade():
    pmu.shutdown()

# Note: These imports come after the firmware upgrade check
#       to allow it to have more memory to work with
import lcd
from krux.context import Context
from krux.pages.login import Login
from krux.pages.home import Home

SPLASH = """
BTCBTCBTCBTCBTCB
TCBTC      BTCBT
CBTCB      TCBTC
BTCBT      CBTCB
TCBTC      BTCBT
CBTCB      TCBTC
B              T
C  K  r  u  x  B
T              C
BTCBT      CBTCB
TCBTC      BTCBT
CBTCB      TCBTC
BTCBT      CBTCB
TCBTC      BTCBT
CBTCB      TCBTC
BTCBT      CBTCB
TCBTCBTCBTCBTCBT
"""

ctx = Context()

ctx.display.flash_text(SPLASH, color=lcd.WHITE, word_wrap=False, padding=8)

while True:
    if not Login(ctx).run():
        break

    if not Home(ctx).run():
        break

ctx.display.flash_text(( 'Shutting down..' ))

ctx.clear()

pmu.shutdown()

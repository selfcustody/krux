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

# Create a watchdog timer that shuts down the device if in inactivity
import machine
from .krux_settings import Settings

ONE_MINUTE = 60000
from .power import power_manager


def wdt_shutdown(_):
    """Watchdog timer callback to shutdown the device"""
    auto_shutdown.shutdown()


class AutoShutdown:
    """Uses an watchdog timer to shutdown the device if inactivity is detected"""

    def __init__(self):
        self.auto_shutdown_timer = None
        self.shutdown_time = Settings().security.auto_shutdown * ONE_MINUTE
        self.ctx = None
        if self.shutdown_time > 0:
            self.auto_shutdown_timer = machine.WDT(
                id=1, timeout=self.shutdown_time, callback=wdt_shutdown
            )

    def add_ctx(self, ctx):
        """Add a context to the auto_shutdown object"""
        self.ctx = ctx

    def shutdown(self):
        """Clear context and shutdown the device"""
        if self.ctx:
            self.ctx.clear()
        if self.auto_shutdown_timer:
            power_manager.shutdown()

    def feed(self):
        """Feed the auto_shutdown timer"""
        if self.auto_shutdown_timer:
            self.auto_shutdown_timer.feed()


auto_shutdown = AutoShutdown()  # Singleton

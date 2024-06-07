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

from machine import Timer
from .krux_settings import Settings

ONE_SECOND = 1000
from .power import power_manager


def seconds_counter(_):
    """Timer callback to increment seconds counter"""
    auto_shutdown.seconds_counter()


class AutoShutdown:
    """Uses a timer to shutdown the device if inactivity is detected"""

    def __init__(self):
        self.auto_shutdown_timer = None
        self.shutdown_time = 0
        self.time_out = 0
        self.ctx = None
        self.init_timer(Settings().security.auto_shutdown)

    def init_timer(self, value=None):
        """Initializes the timer 1 with a 1 second period"""
        self.shutdown_time = value * 60
        self.time_out = self.shutdown_time
        if self.shutdown_time and self.auto_shutdown_timer is None:
            # Creates a timer in case it does not exist
            self.auto_shutdown_timer = Timer(
                Timer.TIMER1,
                Timer.CHANNEL0,
                mode=Timer.MODE_PERIODIC,
                period=ONE_SECOND,
                callback=seconds_counter,
            )

    def add_ctx(self, ctx):
        """Add a context to the auto_shutdown object"""
        self.ctx = ctx

    def seconds_counter(self):
        """Counts the seconds and shuts down the device if threshold is reached"""
        if self.time_out > 0:
            self.time_out -= 1
        elif self.shutdown_time > 0:
            if self.ctx:
                self.ctx.clear()
            if self.auto_shutdown_timer:
                power_manager.shutdown()

    def feed(self):
        """Feed the auto_shutdown timer"""
        if self.auto_shutdown_timer:
            self.time_out = self.shutdown_time


auto_shutdown = AutoShutdown()  # Singleton

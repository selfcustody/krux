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
import machine
import sys
import board


class PowerManager:
    """PowerManager is a singleton interface for controlling the device's power management unit"""

    def __init__(self):
        self.pmu = None
        if board.config["type"].startswith("amigo"):
            try:
                from pmu import axp173

                self.pmu = axp173()
                self.pmu.enablePMICSleepMode(False)
                # Amigo already have a dedicated reset button
                # Will only enable button checking when in sleep mode
            except:
                pass
        else:
            try:
                from pmu import axp192

                self.pmu = axp192()
                self.pmu.enablePMICSleepMode(True)
            except:
                pass

    def batt_voltage(self):
        """Returns the battery voltage of the device"""
        if self.pmu is not None:
            return self.pmu.getVbatVoltage()
        return None

    def shutdown(self):
        """Shuts down the device"""
        if self.pmu is not None:
            # Enable button checking before shutdown
            self.pmu.enablePMICSleepMode(True)
            self.pmu.setEnterSleepMode()
        machine.reset()
        sys.exit()

    def reboot(self):
        """Reboots the device"""
        if self.pmu is not None:
            self.pmu.enablePMICSleepMode(False)
        machine.reset()
        sys.exit()


power_manager = PowerManager()  # Singleton

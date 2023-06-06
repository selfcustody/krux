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

# https://github.com/m5stack/M5StickC/blob/0527606d9e56c956ab17b278c25e3d07d7664f5e/src/AXP192.cpp#L20
MAX_BATTERY_MV = 4200
# https://github.com/m5stack/M5StickC/blob/0527606d9e56c956ab17b278c25e3d07d7664f5e/src/AXP192.cpp#L56
MIN_BATTERY_MV = 3000


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

    def has_battery(self):
        """Returns if the device has a battery"""
        try:
            assert int(self.pmu.getVbatVoltage()) > 0
        except:
            return False
        return True

    def battery_charge_remaining(self):
        """Returns the state of charge of the device's battery"""
        mv = int(self.pmu.getVbatVoltage())
        if board.config["type"].startswith("amigo"):
            charge = max(0, (mv - 3394.102415024943) / 416.73204356)
        elif board.config["type"] == "m5stickv":
            charge = max(0, (mv - 3131.427782118631) / 790.56172897)
        else:
            charge = max(0, ((mv - MIN_BATTERY_MV) / (MAX_BATTERY_MV - MIN_BATTERY_MV)))
        return min(1, charge)


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

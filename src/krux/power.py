# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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
from .i2c import i2c_bus

# https://github.com/m5stack/M5StickC/blob/0527606d9e56c956ab17b278c25e3d07d7664f5e/src/AXP192.cpp#L20
MAX_BATTERY_MV = 4200
# https://github.com/m5stack/M5StickC/blob/0527606d9e56c956ab17b278c25e3d07d7664f5e/src/AXP192.cpp#L56
MIN_BATTERY_MV = 3000


class PowerManager:
    """PowerManager is a singleton interface for controlling the device's power management unit"""

    def __init__(self):
        self.pmu = None
        try:
            from pmu import PMUController

            self.pmu = PMUController(i2c_bus)
            self.pmu.enable_adcs(True)
            if board.config["type"] == "m5stickv":
                self.pmu.enable_pek_button_monitor()
        except Exception as e:
            print(e)

    def has_battery(self):
        """Returns if the device has a battery"""
        try:
            assert int(self.pmu.get_battery_voltage()) > 0
        except:
            return False
        return True

    def battery_charge_remaining(self):
        """Returns the state of charge of the device's battery"""
        mv = int(self.pmu.get_battery_voltage())
        if board.config["type"].startswith("amigo"):
            charge = max(0, (mv - 3394.102415024943) / 416.73204356)
        elif board.config["type"] == "m5stickv":
            charge = max(0, (mv - 3131.427782118631) / 790.56172897)
        else:
            charge = max(0, ((mv - MIN_BATTERY_MV) / (MAX_BATTERY_MV - MIN_BATTERY_MV)))

        # Dirty trick to avoid showing 100% when battery is not fully charged
        if self.pmu.charging():
            charge -= 0.35  # compensates for the batt voltage raise when charging
            # limits in 90% when still charging to let user know it's not fully charged
            charge = min(0.9, charge)

        return min(1, charge)

    def usb_connected(self):
        """Returns True if USB connected, False otherwise"""
        return self.pmu.usb_connected()

    def set_screen_brightness(self, value):
        """Sets the screen brightness by modifying the backlight voltage"""
        # Accpeted values range from 0 to 8
        # pmu register allow values from 0 to 15, but values below 7 result in no backlight
        value += 7
        self.pmu.set_screen_brightness(value)

    def shutdown(self):
        """Shuts down the device"""
        if self.pmu is not None:
            self.pmu.enable_adcs(False)
            self.pmu.enter_sleep_mode()
        machine.reset()
        sys.exit()

    def reboot(self):
        """Reboots the device"""
        machine.reset()
        sys.exit()


power_manager = PowerManager()  # Singleton

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

# CST816S specs:
# I2C address: 0x15
# Single-point capacitive touch controller with gesture recognition

import time
from Maix import GPIO
from fpioa_manager import fm
from . import Touchscreen
from ..i2c import i2c_bus

# CST816S Register addresses
CST816S_TOUCH_DATA = 0x01
CST816S_VERSION = 0x15
CST816S_VERSION_INFO = 0xA7
CST816S_STANDBY = 0xA5
CST816S_AUTO_SLEEP_TIME = 0xF9
CST816S_AUTO_SLEEP_MODE = 0xFE
CST816S_DOUBLE_CLICK_EN = 0xEC

CST816S_ADDR = 0x15
ACTIVITY_THRESHOLD = 100  # Minimum time between touch events (ms)
SCREEN_WIDTH = 240  # Screen width for Y coordinate mirroring (page mode)
# Modify this in case of different screens show up

# # Gesture constants
# GESTURE_NONE = 0x00
# GESTURE_SWIPE_UP = 0x01
# GESTURE_SWIPE_DOWN = 0x02
# GESTURE_SWIPE_LEFT = 0x03
# GESTURE_SWIPE_RIGHT = 0x04
# GESTURE_SINGLE_CLICK = 0x05
# GESTURE_DOUBLE_CLICK = 0x0B
# GESTURE_LONG_PRESS = 0x0C

# # Touch event constants
# EVENT_TOUCH_DOWN = 0x00
# EVENT_TOUCH_UP = 0x01
EVENT_TOUCH_CONTACT = 0x02


def __handler__(pin_num=None):
    # pylint: disable=unused-argument
    """GPIO interrupt handler for touch events"""
    touch_control.trigger_event()


class CST816(Touchscreen):
    """CST816S capacitive touchscreen controller driver

    Provides I2C communication interface for CST816S touch IC
    with interrupt-driven touch event detection and gesture recognition.
    """

    def __init__(self):
        self.irq_pin = None
        self.event_flag = False
        self.irq_point = None
        self.last_touch_time = 0

    def _init_pins(self, irq_pin):
        """Initialize interrupt and reset pins with proper timing sequence"""
        fm.register(irq_pin, fm.fpioa.GPIOHS1)
        self.irq_pin = GPIO(GPIO.GPIOHS1, GPIO.IN, GPIO.PULL_UP)

    def _init_cst816(self):
        """Configure CST816S registers for touch detection"""
        try:
            # Verify device communication
            version = self.read_reg(CST816S_VERSION, 1)
            if version is not None:
                print("CST816S touchscreen found")

            self.write_reg(CST816S_AUTO_SLEEP_MODE, bytearray([0x00]))

        except Exception as e:
            print("CST816S initialization error:", e)

    def activate(self, irq_pin):
        """Enable touchscreen with interrupt handling"""
        self._init_pins(irq_pin)
        self._init_cst816()
        self.irq_pin.irq(__handler__, GPIO.IRQ_FALLING)

    def write_reg(self, reg_addr, buf):
        """Write data to CST816S register"""
        if i2c_bus is not None:
            try:
                # Send 8-bit register address + data
                payload = bytearray([reg_addr])
                payload.extend(bytearray(buf))
                i2c_bus.writeto(CST816S_ADDR, payload)
            except Exception as e:
                print("CST816S write error:", e)

    def read_reg(self, reg_addr, buf_len):
        """Read data from CST816S register"""
        if i2c_bus is not None:
            try:
                addr_bytes = bytearray([reg_addr])
                i2c_bus.writeto(CST816S_ADDR, addr_bytes)
                return i2c_bus.readfrom(CST816S_ADDR, buf_len)
            except Exception as e:
                print("CST816S read error:", e)
        return None

    def _read_touch_data(self):
        """Read complete touch data including coordinates and gesture"""
        try:
            touch_data = self.read_reg(CST816S_TOUCH_DATA, 6)
            if touch_data is not None and len(touch_data) >= 6:
                points = touch_data[1]
                event = touch_data[2] >> 6
                x = ((touch_data[2] & 0x0F) << 8) | touch_data[3]
                y = ((touch_data[4] & 0x0F) << 8) | touch_data[5]

                # Return coordinates if touch is active
                if points > 0 and event == EVENT_TOUCH_CONTACT:
                    x = max(0, SCREEN_WIDTH - x)
                    return (x, y)

        except Exception as e:
            print("CST816S touch data read error:", e)
        return None

    def current_point_validate(self):
        """Check touch status and return coordinates if valid touch detected"""
        try:
            # CST816S provides touch data directly without status check
            return self._read_touch_data()
        except Exception as e:
            print("CST816S current_point error:", e)
        return None

    def current_point(self):
        """Return touch coordinates if within activity threshold"""
        if time.ticks_ms() - self.last_touch_time <= ACTIVITY_THRESHOLD:
            return self._read_touch_data()
        return None

    def trigger_event(self):
        """Process touch interrupt and update event state"""
        current_time = time.ticks_ms()

        # Debounce: ignore rapid successive touches
        if current_time - self.last_touch_time <= ACTIVITY_THRESHOLD:
            self.last_touch_time = current_time
            return

        # Capture new touch event
        irq_point = self.current_point_validate()
        if irq_point is not None:
            self.irq_point = irq_point
            self.event_flag = True
            self.last_touch_time = current_time

    def event(self):
        """Return and clear touch event flag"""
        flag = self.event_flag
        self.event_flag = False
        return flag

    def threshold(self, _):
        """CST816S doesn't have configurable threshold - this is a placeholder for compatibility"""
        # CST816S has fixed internal threshold, but we keep this method for API compatibility
        print("CST816S: Threshold setting not supported")


touch_control = CST816()

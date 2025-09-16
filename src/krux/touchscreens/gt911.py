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

# GT911 specs:
# I2C addresses: 0x5D (primary), 0x14 (secondary)

import time
from Maix import GPIO
from fpioa_manager import fm
from . import Touchscreen
from ..i2c import i2c_bus

# GT911 Register addresses
GT911_PRODUCT_ID = 0x8140
GT911_CONFIG_DATA = 0x8047
GT911_COORD_ADDR = 0x814E
GT911_CHECK_SUM = 0x80FF
GT911_COMMAND = 0x8040
GT911_CONFIG_TRIGGER = 0x8057

GT911_ADDR = 0x5D
TOUCH_THRESHOLD = 40
ACTIVITY_THRESHOLD = 100  # Minimum time between touch events (ms)


def __handler__(pin_num=None):
    # pylint: disable=unused-argument
    """GPIO interrupt handler for touch events"""
    touch_control.trigger_event()


class GT911(Touchscreen):
    """GT911 capacitive touchscreen controller driver

    Provides I2C communication interface for GT911 touch IC
    with interrupt-driven touch event detection.
    """

    def __init__(self):
        self.irq_pin = None
        self.reset_pin = None
        self.event_flag = False
        self.irq_point = None
        self.addr = GT911_ADDR
        self.last_touch_time = 0

    def _init_pins(self, irq_pin, reset_pin):
        """Initialize interrupt and reset pins with proper timing sequence"""
        fm.register(irq_pin, fm.fpioa.GPIOHS1)
        fm.register(reset_pin, fm.fpioa.GPIOHS2)

        # Configure pins (INT as pull-down sets I2C address to 0x5D)
        self.irq_pin = GPIO(GPIO.GPIOHS1, GPIO.IN, GPIO.PULL_DOWN)
        self.reset_pin = GPIO(GPIO.GPIOHS2, GPIO.OUT)

        # Power-on reset sequence
        self.reset_pin.value(0)
        time.sleep_ms(10)
        self.reset_pin.value(1)
        time.sleep_ms(50)

    def _init_gt911(self):
        """Configure GT911 registers for touch detection"""
        try:
            # Verify device communication
            product_id = self.read_reg(GT911_PRODUCT_ID, 4)
            if product_id is not None:
                print("GT911 found. Product ID:", product_id)

            # Configure interrupt trigger mode and touch sensitivity
            self.write_reg(GT911_CONFIG_TRIGGER, bytearray([0x02]))
            self.write_reg(GT911_CONFIG_DATA, bytearray([TOUCH_THRESHOLD]))
            self.write_reg(GT911_COMMAND, bytearray([0x00]))

        except Exception as e:
            print("GT911 initialization error:", e)

    def activate(self, irq_pin, res_pin):
        """Enable touchscreen with interrupt handling"""
        self._init_pins(irq_pin, res_pin)
        self._init_gt911()
        self.irq_pin.irq(__handler__, GPIO.IRQ_RISING)

    def write_reg(self, reg_addr, buf):
        """Write data to GT911 register"""
        if i2c_bus is not None:
            try:
                # Send 16-bit register address + data
                payload = bytearray([reg_addr >> 8, reg_addr & 0xFF])
                payload.extend(bytearray(buf))
                i2c_bus.writeto(self.addr, payload)
            except Exception as e:
                print("GT911 write error:", e)

    def read_reg(self, reg_addr, buf_len):
        """Read data from GT911 register"""
        if i2c_bus is not None:
            try:
                addr_bytes = bytearray([reg_addr >> 8, reg_addr & 0xFF])
                i2c_bus.writeto(self.addr, addr_bytes)
                return i2c_bus.readfrom(self.addr, buf_len)
            except Exception as e:
                print("GT911 read error:", e)
        return None

    def _read_touch_coordinates(self):
        """Extract X,Y coordinates from touch data and clear interrupt flag"""
        try:
            touch_data = self.read_reg(GT911_COORD_ADDR + 1, 8)
            if touch_data is not None and len(touch_data) >= 8:
                x = touch_data[1] | (touch_data[2] << 8)
                y = touch_data[3] | (touch_data[4] << 8)
                return (x, y)
        except Exception as e:
            print("GT911 coordinate read error:", e)
        return None

    def current_point_validate(self):
        """Check touch status and return coordinates if valid touch detected"""
        try:
            status = self.read_reg(GT911_COORD_ADDR, 1)
            if status is not None and (status[0] & 0x80) and (status[0] & 0x0F) >= 1:
                return self._read_touch_coordinates()
        except Exception as e:
            print("GT911 current_point error:", e)
        return None

    def current_point(self):
        """Return touch coordinates if within activity threshold"""
        if time.ticks_ms() - self.last_touch_time <= ACTIVITY_THRESHOLD:
            return self._read_touch_coordinates()
        return None

    def trigger_event(self):
        """Process touch interrupt and update event state"""
        current_time = time.ticks_ms()

        # Debounce: ignore rapid successive touches
        if current_time - self.last_touch_time <= ACTIVITY_THRESHOLD:
            self.last_touch_time = current_time
            self.write_reg(GT911_COORD_ADDR, bytearray([0x00]))  # Clear irq flag
            return

        # Capture new touch event
        irq_point = self.current_point_validate()
        if irq_point is not None:
            self.irq_point = irq_point
            self.event_flag = True
            self.last_touch_time = current_time
        self.write_reg(GT911_COORD_ADDR, bytearray([0x00]))  # Clear irq flag

    def event(self):
        """Return and clear touch event flag"""
        flag = self.event_flag
        self.event_flag = False
        return flag

    def threshold(self, value):
        """Update touch sensitivity threshold"""
        try:
            config_data = bytearray([value])
            self.write_reg(GT911_CONFIG_DATA, config_data)
        except Exception as e:
            print("GT911 threshold error", e)


touch_control = GT911()

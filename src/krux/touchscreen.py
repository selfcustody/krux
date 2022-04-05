# This file is part of MaixUI
# Copyright (c) sipeed.com
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php
#

import time
import board
from machine import I2C

FT_DEVIDE_MODE = 0x00
FT_ID_G_MODE = 0xA4
FT_ID_G_THGROUP = 0x80
FT_ID_G_PERIODACTIVE = 0x88
FT6X36_ADDR = 0x38


class TouchLow:
    """TouchLow is a driver with methods to interact with touch IC(FT6X36) using I2C"""

    def __init__(self):
        self.i2c3 = None
        self.addr = 0

    def config(self, i2c3, addr=FT6X36_ADDR):
        """Defines which I2C bus and I2C address will be used"""
        self.i2c3 = i2c3
        self.addr = addr

    def write_reg(self, reg_addr, buf):
        """Writes buffer content to a register address"""
        self.i2c3.writeto_mem(self.addr, reg_addr, buf, mem_size=8)

    def read_reg(self, reg_addr, buf_len):
        """Reads from a register address"""
        return self.i2c3.readfrom_mem(self.addr, reg_addr, buf_len, mem_size=8)

    def config_ft6x36(self):
        """Writes and setup touchscreen IC"""
        self.write_reg(FT_DEVIDE_MODE, 0)
        self.write_reg(FT_ID_G_THGROUP, 12)
        self.write_reg(FT_DEVIDE_MODE, 14)

    def get_point(self):
        """Get y and x touch points from IC's I2C registers"""
        if self.i2c3 is not None:
            data = self.read_reg(0x02, 1)
            if data is not None and data[0] == 0x1:
                data_buf = self.read_reg(0x03, 4)
                y = ((data_buf[0] & 0x0F) << 8) | (data_buf[1])
                x = ((data_buf[2] & 0x0F) << 8) | (data_buf[3])
                if (data_buf[0] & 0xC0) == 0x80:
                    return (y, x)
        return None


class Touch:
    """Touch is a singleton API to interact with touchscreen driver"""

    idle, press, release = 0, 1, 2

    def __init__(self, width, height, cycle=1000):
        """Touch API init - width and height are in Landscape mode
        For Krux width = max_y, height = max_x
        """
        self.cycle = cycle
        self.last_time = 0
        self.points = (0, 0)
        self.y_regions = []
        self.x_regions = []
        self.index = 0
        self.state = Touch.idle
        self.width, self.height = width, height
        self.touchlow = TouchLow()
        self.init_i2c()

    def init_i2c(self):
        """Setup I2C bus"""
        self.i2c = I2C(
            I2C.I2C0,
            freq=400000,
            scl=board.config["krux.pins"]["I2C_SCL"],
            sda=board.config["krux.pins"]["I2C_SDA"],
        )
        self.touchlow.config(self.i2c, FT6X36_ADDR)

    def clear_regions(self):
        """Remove previously stored buttons map"""
        self.y_regions = []
        self.x_regions = []

    def add_y_delimiter(self, region):
        """Adds a y button delimiter to be mapped as a array by touchscreen"""
        if region > self.width:
            raise ValueError("Touch region added outside display area")
        self.y_regions.append(region)

    def add_x_delimiter(self, region):
        """Adds a x button delimiter to be mapped as a array by touchscreen"""
        if region > self.height:
            raise ValueError("Touch region added outside display area")
        self.x_regions.append(region)

    def extract_index(self, data):
        """Gets an index from touched points, y and x delimiters"""
        y, x = data
        if self.state != Touch.press:
            self.state = Touch.press
            self.points = (y, x)
            self.index = 0
            if self.y_regions:
                for region in self.y_regions:
                    if self.points[1] > region:
                        self.index += 1
                if self.index == 0 or self.index >= len(
                    self.y_regions
                ):  # outside y areas
                    self.state = Touch.idle
                else:
                    self.index -= 1
                    if self.x_regions:  # if 2D array
                        self.index *= len(self.x_regions) - 1
                        x_index = 0
                        for x_region in self.x_regions:
                            if self.points[0] > x_region:
                                x_index += 1
                        if x_index == 0 or x_index >= len(
                            self.x_regions
                        ):  # outside x areas
                            self.state = Touch.idle
                        else:
                            x_index -= 1
                        self.index += x_index
            else:
                self.index = 0

    def get_state(self):
        """Returns the touchscreen state"""
        if time.ticks_ms() > self.last_time + self.cycle:
            self.last_time = time.ticks_ms()
            data = self.touchlow.get_point()
            if data is not None:
                self.extract_index(data)
            else:  # gets realease than return to ilde.
                if self.state == Touch.release:
                    self.state = Touch.idle
                    self.points = (0, 0)
                elif self.state == Touch.press:
                    self.state = Touch.release
        return self.state

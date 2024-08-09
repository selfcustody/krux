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
# pylint: disable=W0212

import gc
import sensor
import board

OV2640_ID = 0x2642  # Lenses, vertical flip - Bit
OV5642_ID = 0x5642  # Lenses, horizontal flip - Bit
OV7740_ID = 0x7742  # No lenses, no Flip - M5sitckV, Amigo
GC0328_ID = 0x9D  # Dock
GC2145_ID = 0x45  # Yahboom


class Camera:
    """Camera is a singleton interface for interacting with the device's camera"""

    def __init__(self):
        self.initialized = False
        self.cam_id = None
        self.antiglare_enabled = False
        self.initialize_sensor()

    def initialize_sensor(self, grayscale=False):
        """Initializes the camera"""
        self.initialized = False
        self.antiglare_enabled = False
        self.cam_id = sensor.get_id()
        if self.cam_id in (OV7740_ID, GC2145_ID):
            sensor.reset(freq=18200000)
            if board.config["type"] == "cube":
                # Rotate camera 180 degrees on Cube
                sensor.set_hmirror(1)
                sensor.set_vflip(1)
        else:
            sensor.reset()
        if grayscale and self.cam_id != GC2145_ID:
            # GC2145 does not support grayscale
            sensor.set_pixformat(sensor.GRAYSCALE)
        else:
            sensor.set_pixformat(sensor.RGB565)
        if self.cam_id == OV5642_ID:
            sensor.set_hmirror(1)
        if self.cam_id == OV2640_ID:
            sensor.set_vflip(1)
        if board.config["type"] == "bit":
            # CIF mode will use central pixels and discard darker periphery
            sensor.set_framesize(sensor.CIF)
        else:
            sensor.set_framesize(sensor.QVGA)
        if self.cam_id == OV7740_ID:
            self.config_ov_7740()
        if self.cam_id == OV2640_ID:
            self.config_ov_2640()
        sensor.skip_frames()

    def config_ov_7740(self):
        """Specialized config for OV7740 sensor"""
        # Allowed luminance thresholds:
        # luminance high threshold, default=0x78
        sensor.__write_reg(0x24, 0x70)
        # luminance low threshold, default=0x68
        sensor.__write_reg(0x25, 0x60)

        # Average-based sensing window definition
        # Ingnore periphery and measure luminance only on central area
        # Regions 1,2,3,4
        sensor.__write_reg(0x56, 0x0)
        # Regions 5,6,7,8
        sensor.__write_reg(0x57, 0b00111100)
        # Regions 9,10,11,12
        sensor.__write_reg(0x58, 0b00111100)
        # Regions 13,14,15,16
        sensor.__write_reg(0x59, 0x0)

    def config_ov_2640(self):
        """Specialized config for OV2640 sensor"""
        # Set register bank 0
        sensor.__write_reg(0xFF, 0x00)
        # Enable AEC
        sensor.__write_reg(0xC2, 0x8C)
        # Set register bank 1
        sensor.__write_reg(0xFF, 0x01)
        sensor.__write_reg(0x03, 0xCF)
        # Allowed luminance thresholds:
        # luminance high threshold, default=0x78
        sensor.__write_reg(0x24, 0x70)
        # luminance low threshold, default=0x68
        sensor.__write_reg(0x25, 0x60)

        # Average-based sensing window definition
        # Ingnore periphery and measure luminance only on central area
        # Regions 1,2,3,4
        sensor.__write_reg(0x5D, 0xFF)
        # Regions 5,6,7,8
        sensor.__write_reg(0x5E, 0b11000011)
        # Regions 9,10,11,12
        sensor.__write_reg(0x5F, 0b11000011)
        # Regions 13,14,15,16
        sensor.__write_reg(0x60, 0xFF)

    def has_antiglare(self):
        """Returns whether the camera has anti-glare functionality"""
        return self.cam_id in (OV7740_ID, OV2640_ID, GC2145_ID)

    def enable_antiglare(self):
        """Enables anti-glare mode"""
        if self.cam_id == OV2640_ID:
            # Set register bank 1
            sensor.__write_reg(0xFF, 0x01)
            # luminance high level, default=0x78
            sensor.__write_reg(0x24, 0x28)
            # luminance low level, default=0x68
            sensor.__write_reg(0x25, 0x20)
        elif self.cam_id == OV7740_ID:
            # luminance high level, default=0x78
            sensor.__write_reg(0x24, 0x38)
            # luminance low level, default=0x68
            sensor.__write_reg(0x25, 0x20)
            # Disable frame integrtation (night mode)
            sensor.__write_reg(0x15, 0x00)
        elif self.cam_id == GC2145_ID:
            # Set register bank 1
            sensor.__write_reg(0xFE, 0x01)
            # Expected luminance level, default=0x50
            sensor.__write_reg(0x13, 0x25)
            # luminance high level, default=0xF2
            sensor.__write_reg(0x0E, 0x40)
            # luminance low level, default=0x20
            sensor.__write_reg(0x0F, 0x15)
        sensor.skip_frames()
        self.antiglare_enabled = True

    def disable_antiglare(self):
        """Disables anti-glare mode"""
        if self.cam_id in (OV7740_ID, OV2640_ID):
            if self.cam_id == OV2640_ID:
                # Set register bank 1
                sensor.__write_reg(0xFF, 0x01)
            # luminance high level, default=0x78
            sensor.__write_reg(0x24, 0x70)
            # luminance low level, default=0x68
            sensor.__write_reg(0x25, 0x60)
        elif self.cam_id == GC2145_ID:
            # Set register bank 1
            sensor.__write_reg(0xFE, 0x01)
            # Expected luminance level, default=0x50
            sensor.__write_reg(0x13, 0x50)
            # luminance high level, default=0xF2
            sensor.__write_reg(0x0E, 0xF2)
            # luminance low level, default=0x20
            sensor.__write_reg(0x0F, 0x20)
        sensor.skip_frames()
        self.antiglare_enabled = False

    def toggle_antiglare(self):
        """Toggles anti-glare mode and returns the new state"""
        if self.antiglare_enabled:
            self.disable_antiglare()
            return False
        self.enable_antiglare()
        return True

    def snapshot(self):
        """Helper to take a customized snapshot from sensor"""
        img = sensor.snapshot()
        if board.config["type"] == "bit":
            img.lens_corr(strength=1.1)
            img.rotation_corr(z_rotation=180)
        return img

    def initialize_run(self):
        """Initializes and runs sensor"""
        self.initialize_sensor()
        sensor.run(1)

    def stop_sensor(self):
        """Stops capturing from sensor"""
        gc.collect()
        sensor.run(0)

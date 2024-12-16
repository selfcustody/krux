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

QR_SCAN_MODE = 0
ANTI_GLARE_MODE = 1
ENTROPY_MODE = 2
BINARY_GRID_MODE = 3


class Camera:
    """Camera is a singleton interface for interacting with the device's camera"""

    # Luminosity thresholds for each camera and mode
    lum_th = {
        OV2640_ID: {
            QR_SCAN_MODE: (0x60, 0x70),
            ANTI_GLARE_MODE: (0x20, 0x28),
            ENTROPY_MODE: (0x68, 0x78),
            BINARY_GRID_MODE: (0x44, 0x48),
        },
        OV7740_ID: {
            QR_SCAN_MODE: (0x60, 0x70),
            ANTI_GLARE_MODE: (0x20, 0x28),
            ENTROPY_MODE: (0x68, 0x78),
            BINARY_GRID_MODE: (0x44, 0x48),
        },
        GC2145_ID: {
            QR_SCAN_MODE: (0x30, 0x55),
            ANTI_GLARE_MODE: (0x25, 0x40),
            ENTROPY_MODE: (0x20, 0xF2),
            BINARY_GRID_MODE: (0x30, 0x50),
        },
        GC0328_ID: {
            QR_SCAN_MODE: 0x70,
            ANTI_GLARE_MODE: 0x40,
            ENTROPY_MODE: 0x80,
            BINARY_GRID_MODE: 0x70,
        },
    }

    def __init__(self):
        self.cam_id = None
        self.mode = None
        try:
            self.initialize_sensor(mode=QR_SCAN_MODE)
            sensor.run(0)
        except Exception as e:
            print("Camera not found:", e)

    def initialize_sensor(self, mode=QR_SCAN_MODE):
        """Initializes the camera"""
        sensor.reset(freq=18200000)
        self.cam_id = sensor.get_id()
        if board.config["type"] == "cube":
            # Rotate camera 180 degrees on Cube
            sensor.set_hmirror(1)
            sensor.set_vflip(1)
        self.mode = mode
        if mode == BINARY_GRID_MODE and self.cam_id != GC2145_ID:
            # Binary grid mode uses grayscale except for GC2145
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
        if mode != ENTROPY_MODE:
            if self.cam_id == OV7740_ID:
                self.config_ov_7740()
            if self.cam_id == OV2640_ID:
                self.config_ov_2640()
            if self.cam_id == GC2145_ID:
                self.config_gc_2145()
            self.luminosity_threshold()

    def config_ov_7740(self):
        """Specialized config for OV7740 sensor"""

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

    def config_gc_2145(self):
        """Specialized config for GC2145 sensor"""
        # Set register bank 1
        sensor.__write_reg(0xFE, 0x01)
        # Center weight mode = 7, default=0x01 (center mode = 0)
        sensor.__write_reg(0x0C, 0x71)

    def has_antiglare(self):
        """Returns whether the camera has anti-glare functionality"""
        return self.cam_id in (OV7740_ID, OV2640_ID, GC2145_ID, GC0328_ID)

    def luminosity_threshold(self):
        """Set luminosity thresholds for cameras"""

        if self.cam_id == GC0328_ID:
            target = self.lum_th.get(self.cam_id, {}).get(self.mode, 0x80)
            # Set register bank 1
            sensor.__write_reg(0xFE, 0x01)
            # Expected luminance level, default=0x50
            sensor.__write_reg(0x13, target)
            return

        (low, high) = self.lum_th.get(self.cam_id, {}).get(self.mode, (0, 0))
        if low < 0x10 or high > 0xF0:
            return

        if self.cam_id == OV2640_ID:
            # Set register bank 1
            sensor.__write_reg(0xFF, 0x01)
        if self.cam_id in (OV7740_ID, OV2640_ID):
            # luminance high level, default=0x78
            sensor.__write_reg(0x24, high)
            # luminance low level, default=0x68
            sensor.__write_reg(0x25, low)
            vpt_low = (low - 0x10) >> 4
            vpt_high = (high + 0x10) >> 4
            vpt = (vpt_high << 4) | vpt_low
            # VPT - fast convergence zone, default=0xD4
            sensor.__write_reg(0x26, vpt)
            if self.mode in (QR_SCAN_MODE, ANTI_GLARE_MODE):
                # Disable frame integration (bad for animated QR codes)
                sensor.__write_reg(0x15, 0x00)  # pylint: disable=W0212
        elif self.cam_id == GC2145_ID:
            # Set register bank 1
            sensor.__write_reg(0xFE, 0x01)
            # luminance high level, default=0xF2
            sensor.__write_reg(0x0E, high)
            # luminance low level, default=0x20
            sensor.__write_reg(0x0F, low)
            # Expected luminance level, default=0x50
            sensor.__write_reg(0x13, (low + high) // 2)
        sensor.skip_frames()

    def toggle_antiglare(self):
        """Toggles anti-glare mode and returns the new state"""
        if self.mode == ANTI_GLARE_MODE:
            self.mode = QR_SCAN_MODE
            self.luminosity_threshold()
            return False
        self.mode = ANTI_GLARE_MODE
        self.luminosity_threshold()
        return True

    def snapshot(self):
        """Helper to take a customized snapshot from sensor"""
        img = sensor.snapshot()
        if board.config["type"] == "bit":
            img.lens_corr(strength=1.1)
            img.rotation_corr(z_rotation=180)
        return img

    def initialize_run(self, mode=QR_SCAN_MODE):
        """Initializes and runs sensor"""
        if self.mode is None:
            raise ValueError("No camera found")
        if self.mode != mode:
            self.initialize_sensor(mode=mode)
        sensor.run(1)

    def stop_sensor(self):
        """Stops capturing from sensor"""
        gc.collect()
        sensor.run(0)

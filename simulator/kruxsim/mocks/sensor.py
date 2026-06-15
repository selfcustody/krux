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
import sys
import platform
import threading
from unittest import mock
import cv2
from cv2 import split, VideoCapture, cvtColor, COLOR_BGR2RGB, COLOR_BGR2LAB
from numpy import std
from PIL import Image
import time

THREAD_DROP_PERIOD = 0.01

sequence_executor = None
camera_index = None
capturer = None

IS_MACOS = platform.system() == "Darwin"


def register_sequence_executor(s):
    global sequence_executor
    sequence_executor = s


def set_camera_index(index):
    """Set camera index for webcam capture"""
    global camera_index
    camera_index = index


def _try_read(cap):
    """Try to read a frame in a thread with timeout (macOS workaround)"""
    result = [None, None]

    def _read():
        try:
            result[0], result[1] = cap.read()
        except Exception:
            pass

    t = threading.Thread(target=_read, daemon=True)
    t.start()
    t.join(timeout=3.0)
    if t.is_alive():
        return False, None
    return result[0], result[1]


def _try_open_and_read(index):
    """Try to open camera and read a frame in current thread. Returns (cap, ret)"""
    if IS_MACOS:
        cap = VideoCapture(index, cv2.CAP_AVFOUNDATION)
    else:
        cap = VideoCapture(index)
    if not cap.isOpened():
        cap.release()
        return None, False
    ret, _ = cap.read()
    return cap, ret


def find_available_cameras(max_test=4):
    """Probe for available cameras and return list of working indices.
    On macOS wraps open+read in thread with timeout to avoid VideoCapture hangs."""
    available = []
    for i in range(max_test):
        try:
            if IS_MACOS:
                result = [None, False]
                def _probe(idx=i):
                    cap, ret = _try_open_and_read(idx)
                    result[0] = cap
                    result[1] = ret
                t = threading.Thread(target=_probe)
                t.daemon = True
                t.start()
                t.join(timeout=4)
                if t.is_alive():
                    continue
                cap, ret = result
                if cap is None:
                    continue
                if ret:
                    available.append(i)
                cap.release()
            else:
                cap, ret = _try_open_and_read(i)
                if cap is not None:
                    if ret:
                        available.append(i)
                    cap.release()
        except Exception:
            pass
    return available


def init_camera(index=None):
    """Initialize camera with auto-detection or specified index.
    On macOS wraps VideoCapture creation in thread with timeout."""
    global capturer

    if index is not None:
        target_idx = index
    else:
        available = find_available_cameras()
        if not available:
            return False
        target_idx = available[0]

    if IS_MACOS:
        result = [None, False]
        def _init(idx=target_idx):
            cap, ret = _try_open_and_read(idx)
            result[0] = cap
            result[1] = ret
        t = threading.Thread(target=_init)
        t.daemon = True
        t.start()
        t.join(timeout=4)
        if t.is_alive() or result[0] is None:
            return False
        capturer = result[0]
        return True
    else:
        cap, _ = _try_open_and_read(target_idx)
        if cap is not None:
            capturer = cap
            return True
    return False


class MockStatistics:
    """
    Used to mock openMV the statistics object returned by the sensor module
    """

    def __init__(self, img):
        self.img = img  # LAB image
        # Split the LAB image into L, a, and b channels
        lab_l, lab_a, lab_b = split(img)

        # Calculate the standard deviation of each channel
        self.std_L = std(lab_l)
        self.std_a = std(lab_a)
        self.std_b = std(lab_b)

    def l_stdev(self):
        return self.std_L

    def a_stdev(self):
        return self.std_a

    def b_stdev(self):
        return self.std_b

    def median(self):
        return 10


class Mockqrcode:
    def __init__(self, data):
        self.data = data

    def payload(self):
        return self.data


def reset(freq=None, dual_buff=False):
    pass


def run(on):
    global capturer
    if sequence_executor:
        return

    if on:
        if capturer is None or not capturer.isOpened():
            init_camera(camera_index)
    else:
        if capturer:
            capturer.release()
            capturer = None


def find_qrcodes(img):
    codes = []
    try:
        from pyzbar.pyzbar import decode as zbar_decode
        data = zbar_decode(img)
        if data:
            codes.append(Mockqrcode(data[0].data.decode()))
    except ImportError:
        pass
    return codes


def create_empty_frame():
    """Create a blank frame when camera is not available"""
    m = mock.MagicMock()
    m.get_frame.return_value = None
    m.find_qrcodes.return_value = None
    m.to_bytes.return_value = b""
    stats = mock.MagicMock()
    stats.l_stdev.return_value = 0
    stats.a_stdev.return_value = 0
    stats.b_stdev.return_value = 0
    stats.median.return_value = 0
    m.get_statistics.return_value = stats
    m.width.return_value = 320
    m.height.return_value = 240
    m.lens_corr.return_value = m
    return m


def snapshot():
    # Temporarily yield execution to allow other threads to run
    time.sleep(THREAD_DROP_PERIOD)

    m = mock.MagicMock()
    m.find_qrcodes.return_value = None
    if sequence_executor:
        if sequence_executor.camera_image is not None:
            frame = sequence_executor.camera_image
            frame = cvtColor(frame, COLOR_BGR2RGB)
            img = sequence_executor.camera_image
            rgb_frame = cvtColor(img, COLOR_BGR2RGB)
            lab_frame = cvtColor(rgb_frame, COLOR_BGR2LAB)
            m.get_frame.return_value = frame
            m.find_qrcodes.return_value = find_qrcodes(img)
            m.to_bytes.return_value = frame.tobytes()
            m.get_statistics.return_value = MockStatistics(lab_frame)
            m.width.return_value = frame.shape[1]
            m.height.return_value = frame.shape[0]
            m.lens_corr.return_value = m
            if m.find_qrcodes.return_value:
                sequence_executor.camera_image = None
    else:
        if capturer is None or not capturer.isOpened():
            return create_empty_frame()

        if IS_MACOS:
            ret, frame = _try_read(capturer)
        else:
            ret, frame = capturer.read()

        if not ret or frame is None:
            return create_empty_frame()

        try:
            rgb_frame = cvtColor(frame, COLOR_BGR2RGB)
            lab_frame = cvtColor(frame, COLOR_BGR2LAB)
            img = Image.fromarray(rgb_frame)

            m.get_frame.return_value = rgb_frame
            m.find_qrcodes.return_value = find_qrcodes(img)
            m.to_bytes.return_value = frame.tobytes()
            m.get_statistics.return_value = MockStatistics(lab_frame)
            m.width.return_value = frame.shape[1]
            m.height.return_value = frame.shape[0]
            m.lens_corr.return_value = m
        except Exception:
            return create_empty_frame()
    return m


if "sensor" not in sys.modules:
    sys.modules["sensor"] = mock.MagicMock(
        reset=reset,
        run=run,
        snapshot=snapshot,
    )

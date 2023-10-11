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
from unittest import mock
import pyzbar.pyzbar
import cv2
import numpy as np
import PIL
import PIL.Image

sequence_executor = None


def register_sequence_executor(s):
    global sequence_executor
    sequence_executor = s


class Mockhistogram_threshold:
    def value(self):
        return 1


class Mockhistogram:
    def get_threshold(self):
        return Mockhistogram_threshold()


class Mockqrcode:
    def __init__(self, data):
        self.data = data

    def payload(self):
        return self.data


capturer = None


def reset(freq=None, dual_buff=False):
    pass


def run(on):
    global capturer
    if sequence_executor:
        return

    if on:
        capturer = cv2.VideoCapture(0)
    else:
        capturer.release()


def find_qrcodes(img):
    codes = []
    data = pyzbar.pyzbar.decode(img)
    if data:
        try:
            test_encoding = data[0].data.decode().encode('shift-jis').decode()
            # Send data as string
            codes.append(Mockqrcode(data[0].data.decode()))
        except:
            # If fails re-decode test send re-encoded bytes
            codes.append(Mockqrcode(data[0].data.decode().encode('shift-jis')))
    return codes


def snapshot():
    m = mock.MagicMock()
    if sequence_executor:
        if sequence_executor.camera_image is not None:
            frame = sequence_executor.camera_image
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            img = sequence_executor.camera_image

            m.get_frame.return_value = frame
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = find_qrcodes(img)

            sequence_executor.camera_image = None
        else:
            m.get_histogram.return_value = "failed"
    else:
        _, frame = capturer.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        img = PIL.Image.fromarray(frame)

        m.get_frame.return_value = frame
        m.get_histogram.return_value = Mockhistogram()
        m.find_qrcodes.return_value = find_qrcodes(img)
        m.to_bytes.return_value = frame.tobytes()
    return m


if "sensor" not in sys.modules:
    sys.modules["sensor"] = mock.MagicMock(
        reset=reset,
        run=run,
        snapshot=snapshot,
    )

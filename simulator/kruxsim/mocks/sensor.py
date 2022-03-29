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


def reset():
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
        codes.append(Mockqrcode(data[0].data.decode()))
    return codes


def snapshot():
    m = mock.MagicMock()
    if sequence_executor:
        if sequence_executor.camera_image is not None:
            frame = np.array(sequence_executor.camera_image)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            img = sequence_executor.camera_image

            m.get_frame.return_value = frame
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = find_qrcodes(img)

            sequence_executor.camera_image = None
        else:
            m.get_histogram.return_value = "failed"
    else:
        _, frame = capturer.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame)

        m.get_frame.return_value = frame
        m.get_histogram.return_value = Mockhistogram()
        m.find_qrcodes.return_value = find_qrcodes(img)
    return m


if "sensor" not in sys.modules:
    sys.modules["sensor"] = mock.MagicMock(
        reset=reset,
        run=run,
        snapshot=snapshot,
    )

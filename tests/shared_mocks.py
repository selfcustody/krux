from unittest import mock
import pyqrcode


def encode_to_string(data):
    """
    Properly encode some qrcode data
    to a string

    :param data: data to be encoded
    """
    try:
        code_str = pyqrcode.create(data, error="L", mode="binary").text()
    except:
        # pre-decode if binary (SeedQR)
        data = data.decode("latin-1")
        code_str = pyqrcode.create(data, error="L", mode="binary").text()
    size = 0
    while code_str[size] != "\n":
        size += 1
    i = 0
    padding = 0
    while code_str[i] != "1":
        if code_str[i] == "\n":
            padding += 1
        i += 1
    code_str = code_str[(padding) * (size + 1) : -(padding) * (size + 1)]
    size -= 2 * padding

    new_code_str = ""
    for i in range(size):
        for j in range(size + 2 * padding + 1):
            if padding <= j < size + padding:
                index = i * (size + 2 * padding + 1) + j
                new_code_str += code_str[index]
        new_code_str += "\n"

    return new_code_str


def get_mock_open(files: dict[str, str]):
    """
    Mock the process of open a files

    :return the mocked files
    """

    # pylint: disable=unused-argument
    def open_mock(filename, *args, **kwargs):
        for expected_filename, content in files.items():
            if filename == expected_filename:
                if content == "Exception":
                    raise Exception()  # pylint: disable=broad-exception-raised
                return mock.mock_open(read_data=content).return_value
        raise OSError("(mock) Unable to open {filename}")

    return mock.MagicMock(side_effect=open_mock)


def statvfs(_):
    """
    TODO: proper documentation
    """
    return (8192, 8192, 1896512, 1338303, 1338303, 0, 0, 0, 0, 255)


class TimeMocker:
    """
    A simple mocked timer
    """

    def __init__(self, increment) -> None:
        self.increment = increment
        self.time = 0

    def tick(self):
        """
        Increment the mocked timer
        """
        self.time += self.increment
        return self.time


class MockPrinter:
    """
    A simple mocked printer
    """

    def __init__(self):
        pass

    def qr_data_width(self):
        """
        Default size of a qrcode data
        """
        return 33

    # pylint: disable=missing-function-docstring
    def clear(self):
        pass

    # pylint: disable=missing-function-docstring
    def print_qr_code(self, qr_code):
        pass

    # pylint: disable=missing-function-docstring
    def print_string(self, string):
        pass

    # pylint: disable=missing-function-docstring
    def set_bitmap_mode(self, x_size, y_size, mode):
        pass

    # pylint: disable=missing-function-docstring
    def print_bitmap_line(self, line):
        pass

    # pylint: disable=missing-function-docstring
    def feed(self, amount):
        pass


class MockQRPartParser:
    """
    A simple mocked parser of
    a qrcode's part
    """

    TOTAL = 10
    FORMAT = 0

    def __init__(self):
        self.count = 0
        self.parts = []
        self.format = MockQRPartParser.FORMAT

    def total_count(self):
        """
        Get the total data count of QRPart

        :return MockQRPartParser.TOTAL
        """
        return MockQRPartParser.TOTAL

    def parsed_count(self):
        """
        Get the total length of parts on QRPart
        """
        return len(self.parts)

    def parse(self, part):
        """
        If can be parsed, append a part on QRPart
        """
        if part not in self.parts:
            self.parts.append(part)

    def is_complete(self):
        """
        The part is complete

        :return boolean
        """
        return len(self.parts) == self.total_count()

    def result(self):
        """
        Get the joined parts of QRPart
        """
        return "".join(self.parts)


class MockhistogramThreshold:
    """
    A simple mocked threshold's histogram
    """

    def value(self):
        """
        Get 1 as threshold

        :return int
        """
        return 1


class Mockhistogram:
    """
    A simple mocked histogram
    """

    def get_threshold(self):
        """
        Get the :class:`MockhistogramThreshold`

        :return Mockhistogram_threshold
        """
        return MockhistogramThreshold()


class Mockqrcode:
    """
    A simple mocked qrcode
    """

    def __init__(self, data):
        self.data = data

    def payload(self):
        """
        Get the mocked qrcode's associated data

        :return some data
        """
        return self.data


class MockBlob:
    """
    A simple mocked blob data
    """

    def rect(self):
        """
        Return a tuple with len(4)

        :return tuple[4]
        """
        return (10, 10, 125, 100)


class MockStats:
    """Mock the luminosity of dots of a TinySeed on which the words
    abandon...(x11) + about mnemonic is punched"""

    def __init__(self) -> None:
        self.counter = 0
        self.word_counter = 0

    def median(self):
        """
        Get a mocked median
        (20, 50 or 60)

        :return int
        """
        if self.word_counter == 0:
            self.word_counter += 1
            return 50
        self.counter += 1
        if self.word_counter == 12 and self.counter == 10:
            return 20
        if self.counter == 12:
            self.counter = 0
            self.word_counter += 1
            if self.word_counter > 12:
                self.word_counter = 0
                return 60
            return 20
        return 60


SNAP_SUCCESS = 0
SNAP_HISTOGRAM_FAIL = 1
SNAP_FIND_QRCODES_FAIL = 2
SNAP_REPEAT_QRCODE = 3
DONT_FIND_ANYTHING = 4

IMAGE_TO_HASH = b"\x12\x04"  # Dummy bytes


def snapshot_generator(outcome=SNAP_SUCCESS):
    """
    Generate a function that create a set of mocked
    histogram, qrcode and/or blobs/stats

    :param outcome: int
    :return function<mock.MagicMock>
    """
    count = 0

    def snapshot():
        nonlocal count
        count += 1
        m = mock.MagicMock()
        if outcome == SNAP_HISTOGRAM_FAIL and count == 2:
            m.get_histogram.return_value = "failed"
            m.find_qrcodes.return_value = [Mockqrcode(str(count))]
        elif outcome == SNAP_FIND_QRCODES_FAIL and count == 2:
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = []
        elif outcome == SNAP_REPEAT_QRCODE and count == 2:
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = [Mockqrcode(str(count - 1))]
        elif outcome == DONT_FIND_ANYTHING:
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = []
        else:
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = [Mockqrcode(str(count))]
            m.to_bytes.return_value = IMAGE_TO_HASH
            m.find_blobs.return_value = [MockBlob()]
            m.width.return_value = 320
            m.height.return_value = 240
            m.get_statistics.return_value = MockStats()
        return m

    return snapshot


def board_m5stickv():
    """
    Return a mocked m5stack m5stickv device

    :return mockMagicMock
    """
    return mock.MagicMock(
        config={
            "type": "m5stickv",
            "lcd": {"height": 135, "width": 240, "invert": 0, "dir": 40, "lcd_type": 3},
            "sdcard": {"sclk": 30, "mosi": 33, "miso": 31, "cs": 32},
            "board_info": {
                "ISP_RX": 4,
                "ISP_TX": 5,
                "WIFI_TX": 39,
                "WIFI_RX": 38,
                "CONNEXT_A": 35,
                "CONNEXT_B": 34,
                "MPU_SDA": 29,
                "MPU_SCL": 28,
                "MPU_INT": 23,
                "SPK_LRCLK": 14,
                "SPK_BCLK": 15,
                "SPK_DIN": 17,
                "SPK_SD": 25,
                "MIC_LRCLK": 10,
                "MIC_DAT": 12,
                "MIC_CLK": 13,
                "LED_W": 7,
                "LED_R": 6,
                "LED_G": 9,
                "LED_B": 8,
                "BUTTON_A": 36,
                "BUTTON_B": 37,
            },
            "krux": {
                "pins": {
                    "BUTTON_A": 36,
                    "BUTTON_B": 37,
                    "LED_W": 7,
                    "UART2_TX": 35,
                    "UART2_RX": 34,
                    "I2C_SCL": 28,
                    "I2C_SDA": 29,
                },
                "display": {
                    "touch": False,
                    "font": [8, 14],
                    "inverted_coordinates": False,
                    "qr_colors": [16904, 61307],
                },
            },
        }
    )


def board_amigo_tft():
    """
    Return a mocked sipeed amigo-tft device

    :return mockMagicMock
    """
    return mock.MagicMock(
        config={
            "type": "amigo_tft",
            "lcd": {"height": 320, "width": 480, "invert": 0, "dir": 40, "lcd_type": 1},
            "sdcard": {"sclk": 11, "mosi": 10, "miso": 6, "cs": 26},
            "board_info": {
                "BOOT_KEY": 23,
                "LED_R": 14,
                "LED_G": 15,
                "LED_B": 17,
                "LED_W": 32,
                "BACK": 23,
                "ENTER": 16,
                "NEXT": 20,
                "WIFI_TX": 6,
                "WIFI_RX": 7,
                "WIFI_EN": 8,
                "I2S0_MCLK": 13,
                "I2S0_SCLK": 21,
                "I2S0_WS": 18,
                "I2S0_IN_D0": 35,
                "I2S0_OUT_D2": 34,
                "I2C_SDA": 27,
                "I2C_SCL": 24,
                "SPI_SCLK": 11,
                "SPI_MOSI": 10,
                "SPI_MISO": 6,
                "SPI_CS": 12,
            },
            "krux": {
                "pins": {
                    "BUTTON_A": 16,
                    "BUTTON_B": 20,
                    "BUTTON_C": 23,
                    "LED_W": 32,
                    "I2C_SDA": 27,
                    "I2C_SCL": 24,
                },
                "display": {
                    "touch": True,
                    "font": [12, 24],
                    "inverted_coordinates": True,
                    "qr_colors": [0, 6342],
                },
            },
        }
    )


def board_dock():
    """
    Return a mocked sipeed dock device

    :return mockMagicMock
    """
    return mock.MagicMock(
        config={
            "type": "dock",
            "lcd": {"height": 240, "width": 320, "invert": 0, "lcd_type": 0},
            "sdcard": {"sclk": 27, "mosi": 28, "miso": 26, "cs": 29},
            "board_info": {
                "BOOT_KEY": 16,
                "LED_R": 13,
                "LED_G": 12,
                "LED_B": 14,
                "MIC0_WS": 19,
                "MIC0_DATA": 20,
                "MIC0_BCK": 18,
            },
            "krux": {
                "pins": {"BUTTON_A": 9, "ENCODER": [10, 11]},
                "display": {
                    "touch": False,
                    "font": [8, 16],
                    "inverted_coordinates": False,
                    "qr_colors": [0, 6342],
                },
            },
        }
    )


def mock_context(mocker):
    """
    Create a mocked context to return a properly krux device

    :param mocker: the mocker
    :return mocker.MagicMock of device
    :raise ValueError
    """
    import board

    # Avoid pylint `inconsistent-return-statments`:
    # (Either all return statements in a function should return
    # an expression, or none of them should).
    # assign a variable to mocked device
    device = None

    if board.config["type"] == "m5stickv":
        device = mocker.MagicMock(
            input=mocker.MagicMock(touch=None),
            display=mocker.MagicMock(
                font_width=8,
                font_height=14,
                width=mocker.MagicMock(return_value=135),
                height=mocker.MagicMock(return_value=240),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
    elif board.config["type"] == "dock":
        device = mocker.MagicMock(
            input=mocker.MagicMock(touch=None),
            display=mocker.MagicMock(
                font_width=8,
                font_height=16,
                width=mocker.MagicMock(return_value=240),
                height=mocker.MagicMock(return_value=320),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
    elif board.config["type"].startswith("amigo"):
        device = mocker.MagicMock(
            display=mocker.MagicMock(
                font_width=12,
                font_height=24,
                width=mocker.MagicMock(return_value=320),
                height=mocker.MagicMock(return_value=480),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
    else:
        type_device = board.config["type"]
        raise ValueError(f"Invalid board.config['type'] == {type_device}")

    return device

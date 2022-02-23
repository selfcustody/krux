import sys
import time
from unittest import mock
import importlib

def get_mock_open(files: dict[str, str]):
    def open_mock(filename, *args, **kwargs):
        for expected_filename, content in files.items():
            if filename == expected_filename:
                if content == 'Exception':
                    raise Exception()
                return mock.mock_open(read_data=content).return_value
        raise FileNotFoundError('(mock) Unable to open {filename}')
    return mock.MagicMock(side_effect=open_mock)

class MockPrinter:
    def __init__(self):
        pass
    
    def qr_data_width(self):
        return 33

    def clear(self):
        pass

    def print_qr_code(self, qr_code):
        pass
    
class MockQRPartParser:
    TOTAL = 10
    FORMAT = 0
    
    def __init__(self):
        self.count = 0
        self.parts = []
        self.format = MockQRPartParser.FORMAT

    def total_count(self):
        return MockQRPartParser.TOTAL

    def parsed_count(self):
        return len(self.parts)

    def parse(self, part):
        if part not in self.parts:
            self.parts.append(part)

    def is_complete(self):
        return len(self.parts) == self.total_count()

    def result(self):
        return ''.join(self.parts)

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

SNAP_SUCCESS = 0
SNAP_HISTOGRAM_FAIL = 1
SNAP_FIND_QRCODES_FAIL = 2
SNAP_REPEAT_QRCODE = 3
def snapshot_generator(outcome=SNAP_SUCCESS):
    count = 0
    def snapshot():
        nonlocal count
        count += 1
        m = mock.MagicMock()
        if outcome == SNAP_HISTOGRAM_FAIL and count == 2:
            m.get_histogram.return_value = 'failed'
            m.find_qrcodes.return_value = [Mockqrcode(str(count))]
        elif outcome == SNAP_FIND_QRCODES_FAIL and count == 2:
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = []
        elif outcome == SNAP_REPEAT_QRCODE and count == 2:
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = [Mockqrcode(str(count-1))]
        else:
            m.get_histogram.return_value = Mockhistogram()
            m.find_qrcodes.return_value = [Mockqrcode(str(count))]
        return m
    return snapshot

def board_m5stickv():
    return mock.MagicMock(config={
        'type': 'm5stickv',
        'lcd': {
            'height': 135,
            'width': 240,
            'invert': 0,
            'dir': 40,
            'lcd_type': 3
        },
        'sdcard': {
            'sclk': 30,
            'mosi': 33,
            'miso': 31,
            'cs': 32
        },
        'board_info': {
            'ISP_RX': 4,
            'ISP_TX': 5,
            'WIFI_TX': 39,
            'WIFI_RX': 38,
            'CONNEXT_A': 35,
            'CONNEXT_B': 34,
            'MPU_SDA': 29,
            'MPU_SCL': 28,
            'MPU_INT': 23,
            'SPK_LRCLK': 14,
            'SPK_BCLK': 15,
            'SPK_DIN': 17,
            'SPK_SD': 25,
            'MIC_LRCLK': 10,
            'MIC_DAT': 12,
            'MIC_CLK': 13,
            'LED_W': 7,
            'LED_R': 6,
            'LED_G': 9,
            'LED_B': 8,
            'BUTTON_A': 36,
            'BUTTON_B': 37
        },
        'krux.pins': {
            'BUTTON_A': 36,
            'BUTTON_B': 37,
            'LED_W': 7,
            'UART2_TX': 35,
            'UART2_RX': 34,
            'I2C_SCL': 28,
            'I2C_SDA': 29
        }
    })

def board_amigo():
    return mock.MagicMock(config={
        'type': 'amigo_tft',
        'lcd': {
            'height': 320,
            'width': 480,
            'invert': 0,
            'dir': 40,
            'lcd_type': 1
        },
        'sdcard': {
            'sclk': 11,
            'mosi': 10,
            'miso': 6,
            'cs': 26
        },
        'board_info': {
            'BOOT_KEY': 23,
            'LED_R': 14,
            'LED_G': 15,
            'LED_B': 17,
            'LED_W': 32,
            'BACK': 31,
            'ENTER': 23,
            'NEXT': 20,
            'WIFI_TX': 6,
            'WIFI_RX': 7,
            'WIFI_EN': 8,
            'I2S0_MCLK': 13,
            'I2S0_SCLK': 21,
            'I2S0_WS': 18,
            'I2S0_IN_D0': 35,
            'I2S0_OUT_D2': 34,
            'I2C_SDA': 27,
            'I2C_SCL': 24,
            'SPI_SCLK': 11,
            'SPI_MOSI': 10,
            'SPI_MISO': 6,
            'SPI_CS': 12
        },
        'krux.pins': {
            'BUTTON_A': 23,
            'BUTTON_B': 20,
            'LED_W': 32
        }
    })

# Create mock modules for all the micropython-specific modules
# that are not available in regular python
importlib.invalidate_caches()

if 'flash' in sys.modules:
    del sys.modules['flash']
sys.modules['flash'] = mock.MagicMock()

if 'secp256k1' in sys.modules:
    del sys.modules['secp256k1']
from embit.util import secp256k1
sys.modules['secp256k1'] = mock.MagicMock(wraps=secp256k1)

if 'machine' in sys.modules:
    del sys.modules['machine']
sys.modules['machine'] = mock.MagicMock()

if 'sensor' in sys.modules:
    del sys.modules['sensor']
sys.modules['sensor'] = mock.MagicMock()

if 'lcd' in sys.modules:
    del sys.modules['lcd']
sys.modules['lcd'] = mock.MagicMock()

if 'Maix' in sys.modules:
    del sys.modules['Maix']
sys.modules['Maix'] = mock.MagicMock()

if 'fpioa_manager' in sys.modules:
    del sys.modules['fpioa_manager']
sys.modules['fpioa_manager'] = mock.MagicMock()

if 'qrcode' in sys.modules:
    del sys.modules['qrcode']
sys.modules['qrcode'] = mock.MagicMock(
    encode_to_string=lambda data: ('0' * (len(data)-10)) + '\n'
)

if 'board' in sys.modules:
    del sys.modules['board']
sys.modules['board'] = board_m5stickv()

if 'urandom' in sys.modules:
    del sys.modules['urandom']
sys.modules['urandom'] = sys.modules['random']

setattr(time, 'sleep_ms', getattr(time, 'sleep_ms', mock.MagicMock()))
setattr(time, 'ticks_ms', getattr(time, 'ticks_ms', mock.MagicMock()))

setattr(sys, 'print_exception', getattr(sys, 'print_exception', mock.MagicMock()))

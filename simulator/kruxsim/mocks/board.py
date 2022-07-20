import sys
from unittest import mock
from kruxsim import devices

BOARD_CONFIG = None
BUTTON_A = None
BUTTON_B = None
BUTTON_C = None

def register_device(device):
    global BOARD_CONFIG
    global BUTTON_A
    global BUTTON_B
    global BUTTON_C
    if device == devices.M5STICKV:
        BOARD_CONFIG = {
            "type": "m5stickv",
            "lcd": {
                "height": 135,
                "width": 240,
                "invert": 0,
                "dir": 40,
                "lcd_type": 3
            },
            "sdcard": {
                "sclk": 30,
                "mosi": 33,
                "miso": 31,
                "cs": 32
            },
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
                "BUTTON_B": 37
            },
            "krux": {
                "pins":{
                    "BUTTON_A": 36,
                    "BUTTON_B": 37,
                    # "LED_W": 7,
                    "UART2_TX": 35,
                    "UART2_RX": 34,
                    # "I2C_SCL": 28,
                    # "I2C_SDA": 29
                },
                "display": {
                    "touch": False,
                    "font": [8, 14],
                    "orientation": [1, 2],
                    "qr_colors": [16904, 61307]
                },
                "sensor": {
                    "flipped": False,
                    "lenses": False
                }
            }
        }
    elif device == devices.AMIGO:
        BOARD_CONFIG = {
            "type": "amigo_ips",
            "lcd": {
                "height": 320,
                "width": 480,
                "invert": 1,
                "dir": 40,
                "lcd_type": 2
            },
            "sdcard": {
                "sclk": 11,
                "mosi": 10,
                "miso": 6,
                "cs": 26
            },
            "board_info": {
                "BOOT_KEY": 16,
                "LED_R": 14,
                "LED_G": 15,
                "LED_B": 17,
                "LED_W": 32,
                "BACK": 31,
                "ENTER": 23,
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
                "SPI_CS": 12
            },
            "krux": {
                "pins":{
                    "BUTTON_A": 16,
                    "BUTTON_B": 20,
                    "BUTTON_C": 23,
                    # "LED_W": 32,
                    "I2C_SDA": 27,
                    "I2C_SCL": 24
                },
                "display": {
                    "touch": True,
                    "font": [12, 24],
                    "orientation":[1, 0],
                },
                "sensor": {
                    "flipped": True,
                    "lenses": False
                }
            }
        }
    elif device == devices.PC:
        BOARD_CONFIG = {
            "type": "pc",
            "lcd": {
                "height": devices.WINDOW_SIZES[device][0],
                "width": devices.WINDOW_SIZES[device][1],
                "invert": 0,
                "dir": 40,
                "lcd_type": 2
            },
            "sdcard": {
                "sclk": 11,
                "mosi": 10,
                "miso": 6,
                "cs": 26
            },
            "board_info": {
                "BOOT_KEY": 16,
                "LED_R": 14,
                "LED_G": 15,
                "LED_B": 17,
                "LED_W": 32,
                "BACK": 31,
                "ENTER": 23,
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
                "SPI_CS": 12
            },
            "krux": {
                "pins":{
                    "BUTTON_A": 16,
                    "BUTTON_B": 20,
                    "BUTTON_C": 23,
                    # "LED_W": 32,
                    "I2C_SDA": 27,
                    "I2C_SCL": 24
                },
                "display": {
                    "touch": True,
                    "font": [12, 24],
                    "orientation": [1, 0]
                },
                "sensor": {
                    "flipped": True,
                    "lenses": False
                }
            }
        }

    sys.modules["board"] = mock.MagicMock(config=BOARD_CONFIG)

    BUTTON_A = BOARD_CONFIG["krux"]["pins"]["BUTTON_A"]
    BUTTON_B = BOARD_CONFIG["krux"]["pins"]["BUTTON_B"]
    if "BUTTON_C" in BOARD_CONFIG["krux"]["pins"]:
        BUTTON_C = BOARD_CONFIG["krux"]["pins"]["BUTTON_C"]
        

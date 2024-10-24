from Crypto.Cipher import AES
import pytest
from .shared_mocks import (
    DeflateIO,
    board_amigo,
    board_dock,
    board_cube,
    board_m5stickv,
    board_wonder_mv,
    encode_to_string,
    encode,
    statvfs,
)


def reset_krux_modules():
    import sys

    for name in list(sys.modules.keys()):
        if name.startswith("krux"):
            del sys.modules[name]


@pytest.fixture
def mp_modules(mocker, monkeypatch):
    from embit.util import secp256k1
    import random
    import time
    import sys

    monkeypatch.setitem(
        sys.modules,
        "qrcode",
        mocker.MagicMock(encode_to_string=encode_to_string, encode=encode),
    )
    monkeypatch.setitem(sys.modules, "secp256k1", mocker.MagicMock(wraps=secp256k1))
    monkeypatch.setitem(sys.modules, "urandom", random)
    monkeypatch.setitem(sys.modules, "flash", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "machine", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "sensor", mocker.MagicMock())
    lcd_mock = mocker.MagicMock()
    lcd_mock.string_width_px.side_effect = lambda s: len(s) * 8  # Assume 8px per char
    monkeypatch.setitem(sys.modules, "lcd", lcd_mock)
    monkeypatch.setitem(sys.modules, "Maix", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "fpioa_manager", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "pmu", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "image", mocker.MagicMock())
    monkeypatch.setitem(
        sys.modules,
        "ucryptolib",
        mocker.MagicMock(aes=AES.new, MODE_ECB=AES.MODE_ECB, MODE_CBC=AES.MODE_CBC),
    )
    monkeypatch.setitem(sys.modules, "shannon", mocker.MagicMock())
    monkeypatch.setattr(time, "sleep_ms", mocker.MagicMock(), raising=False)
    monkeypatch.setattr(time, "ticks_ms", mocker.MagicMock(), raising=False)
    monkeypatch.setattr(sys, "print_exception", mocker.MagicMock(), raising=False)
    monkeypatch.setitem(
        sys.modules,
        "uos",
        mocker.MagicMock(statvfs=statvfs),
    )
    monkeypatch.setitem(sys.modules, "deflate", mocker.MagicMock(DeflateIO=DeflateIO))


@pytest.fixture
def m5stickv(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_m5stickv())
    reset_krux_modules()


@pytest.fixture
def amigo(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_amigo())
    reset_krux_modules()


@pytest.fixture
def dock(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_dock())
    monkeypatch.setitem(sys.modules, "pmu", None)
    reset_krux_modules()


@pytest.fixture
def cube(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_cube())
    reset_krux_modules()


@pytest.fixture
def wonder_mv(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_wonder_mv())
    reset_krux_modules()


@pytest.fixture(params=["amigo", "m5stickv", "dock", "cube"])
def multiple_devices(request):
    return request.getfixturevalue(request.param)

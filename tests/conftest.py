from Crypto.Cipher import AES
import pytest
from .shared_mocks import (
    DeflateIO,
    board_amigo,
    board_dock,
    board_cube,
    board_m5stickv,
    board_wonder_mv,
    board_yahboom,
    board_bit,
    board_wonder_k,
    board_embed_fire,
    encode_to_string,
    encode,
    statvfs,
    pbkdf2_hmac_sha256_wrapper,
    base32_decode,
    base32_encode,
    base43_decode,
    base43_encode,
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
    import hashlib

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
        mocker.MagicMock(
            aes=AES.new,
            MODE_ECB=AES.MODE_ECB,
            MODE_CBC=AES.MODE_CBC,
            MODE_CTR=AES.MODE_CTR,
            MODE_GCM=AES.MODE_GCM,
        ),
    )
    monkeypatch.setitem(sys.modules, "shannon", mocker.MagicMock())
    monkeypatch.setattr(time, "sleep_ms", mocker.MagicMock(), raising=False)
    monkeypatch.setattr(
        time, "ticks_ms", mocker.MagicMock(return_value=1), raising=False
    )
    monkeypatch.setattr(sys, "print_exception", mocker.MagicMock(), raising=False)
    monkeypatch.setitem(
        sys.modules,
        "uos",
        mocker.MagicMock(statvfs=statvfs),
    )
    monkeypatch.setitem(sys.modules, "deflate", mocker.MagicMock(DeflateIO=DeflateIO))
    monkeypatch.setitem(
        sys.modules,
        "uhashlib_hw",
        mocker.MagicMock(
            pbkdf2_hmac_sha256=pbkdf2_hmac_sha256_wrapper,
            sha256=hashlib.sha256,
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "base32",
        mocker.MagicMock(
            decode=base32_decode,
            encode=base32_encode,
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "base43",
        mocker.MagicMock(
            decode=base43_decode,
            encode=base43_encode,
        ),
    )
    import json

    monkeypatch.setitem(sys.modules, "ujson", json)
    monkeypatch.setitem(sys.modules, "vfs", mocker.MagicMock())


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
def yahboom(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_yahboom())
    monkeypatch.setitem(sys.modules, "pmu", None)
    reset_krux_modules()


@pytest.fixture
def wonder_mv(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_wonder_mv())
    monkeypatch.setitem(sys.modules, "pmu", None)
    reset_krux_modules()


@pytest.fixture
def bit(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_bit())
    monkeypatch.setitem(sys.modules, "pmu", None)
    reset_krux_modules()


@pytest.fixture
def wonder_k(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_wonder_k())
    monkeypatch.setitem(sys.modules, "pmu", None)
    reset_krux_modules()


@pytest.fixture
def embed_fire(monkeypatch, mp_modules):
    import sys

    monkeypatch.setitem(sys.modules, "board", board_embed_fire())
    monkeypatch.setitem(sys.modules, "pmu", None)
    reset_krux_modules()


@pytest.fixture(
    params=[
        "amigo",
        "m5stickv",
        "dock",
        "cube",
        "yahboom",
        "wonder_mv",
        "bit",
        "wonder_k",
    ]
)
def multiple_devices(request):
    return request.getfixturevalue(request.param)

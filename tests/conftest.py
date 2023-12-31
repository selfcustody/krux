import pytest
from .shared_mocks import (
    board_amigo_tft,
    board_dock,
    board_m5stickv,
    encode_to_string,
    statvfs,
)


def reset_krux_modules():
    """
    Delete all related krux modules that
    the current shell has imported
    """
    import sys

    for name in list(sys.modules.keys()):
        if name.startswith("krux"):
            del sys.modules[name]


@pytest.fixture
def mp_modules(mocker, monkeypatch):
    """
    Suppress the default behavior of some modules
    without changing its original source code.

    :param mocker: the mocker
    :param monkeypatch: the monkey patcher
    """
    from embit.util import secp256k1
    import random
    import time
    import sys

    monkeypatch.setitem(
        sys.modules,
        "qrcode",
        mocker.MagicMock(encode_to_string=encode_to_string),
    )
    monkeypatch.setitem(sys.modules, "secp256k1", mocker.MagicMock(wraps=secp256k1))
    monkeypatch.setitem(sys.modules, "urandom", random)
    monkeypatch.setitem(sys.modules, "flash", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "machine", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "sensor", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "lcd", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "Maix", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "fpioa_manager", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "pmu", mocker.MagicMock())
    monkeypatch.setitem(sys.modules, "image", mocker.MagicMock())
    monkeypatch.setattr(time, "sleep_ms", mocker.MagicMock(), raising=False)
    monkeypatch.setattr(time, "ticks_ms", mocker.MagicMock(), raising=False)
    monkeypatch.setattr(sys, "print_exception", mocker.MagicMock(), raising=False)
    monkeypatch.setitem(
        sys.modules,
        "uos",
        mocker.MagicMock(statvfs=statvfs),
    )


@pytest.fixture
# pylint: disable=unused-argument
def m5stickv(monkeypatch, mp_modules): # pylint: disable=redefined-outer-name
    """
    Suppress the default behavior of :module:`board`
    for m5stickV device

    :param monkeypatch: the monkey patcher
    :param mp_modules: the mp_modules function
    """
    import sys

    monkeypatch.setitem(sys.modules, "board", board_m5stickv())
    reset_krux_modules()


@pytest.fixture
# pylint: disable=unused-argument
def amigo_tft(monkeypatch, mp_modules): # pylint: disable=redefined-outer-name
    """
    Suppress the default behavior of :module:`board`
    for amigo_tft device

    :param monkeypatch: the monkey patcher
    :param mp_modules: the mp_modules function
    """
    import sys

    monkeypatch.setitem(sys.modules, "board", board_amigo_tft())
    reset_krux_modules()


@pytest.fixture
# pylint: disable=unused-argument
def dock(monkeypatch, mp_modules): # pylint: disable=redefined-outer-name
    """
    Suppress the default behavior of :module:`board`
    for dock device

    :param monkeypatch: the monkey patcher
    :param mp_modules: the mp_modules function
    """
    import sys

    monkeypatch.setitem(sys.modules, "board", board_dock())
    reset_krux_modules()

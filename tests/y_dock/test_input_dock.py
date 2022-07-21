from ..shared_mocks import *
from krux.input import (
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    BUTTON_TOUCH,
    SWIPE_LEFT,
    SWIPE_RIGHT,
    PRESSED,
    RELEASED,
)
import threading
import sys
import pytest


def mock_modules(mocker):
    mocker.patch("krux.input.fm.register", new=mock.MagicMock())
    mocker.patch("krux.input.GPIO", new=mock.MagicMock())


def test_init_dock(mocker):
    mock_modules(mocker)

    import krux
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)
    krux.input.fm.register.assert_has_calls(
        [
            mock.call(board.config["krux"]["pins"]["BUTTON_A"], mock.ANY),
        ]
    )
    krux.rotary.fm.register.assert_has_calls(
        [
            mock.call(board.config["krux"]["pins"]["ENCODER"][0], mock.ANY),
            mock.call(board.config["krux"]["pins"]["ENCODER"][1], mock.ANY),
        ]
    )
    assert (
        krux.input.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS21"
    )
    assert (
        krux.rotary.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert (
        krux.rotary.fm.register.call_args_list[2].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS0"
    )
    assert input.enter is not None
    assert input.page is not None
    assert input.page_prev is not None

    assert krux.input.GPIO.call_count == 1
    assert krux.rotary.GPIO.call_count == 2
    assert (
        krux.input.GPIO.call_args_list[0].args[0]._extract_mock_name()
        == "mock.GPIOHS21"
    )
    assert (
        krux.rotary.GPIO.call_args_list[0].args[0]._extract_mock_name()
        == "mock.GPIO.GPIOHS22"
    )
    assert (
        krux.rotary.GPIO.call_args_list[1].args[0]._extract_mock_name()
        == "mock.GPIO.GPIOHS0"
    )


def test_encoder_spin_right(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)

    def spin():
        mocker.patch.object(time, "ticks_ms", new=lambda: 0)

        # Here it will count a PAGE press
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 200)
        krux.rotary.encoder.process((0, 1))

        # Keep spining through all modes
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 400)
        krux.rotary.encoder.process((1, 1))

        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 600)
        krux.rotary.encoder.process((1, 0))

        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 800)
        krux.rotary.encoder.process((0, 0))

    t = threading.Thread(target=spin)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_encoder_spin_left(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)

    def spin():
        mocker.patch.object(time, "ticks_ms", new=lambda: 0)

        # Here it will change direction to Left
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1000)
        krux.rotary.encoder.process((1, 0))

        # Here it will count a PAGE_PREV press
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1200)
        krux.rotary.encoder.process((1, 1))

        # Keep spining through all modes
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1400)
        krux.rotary.encoder.process((0, 1))

        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1600)
        krux.rotary.encoder.process((0, 0))

    t = threading.Thread(target=spin)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE_PREV
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()

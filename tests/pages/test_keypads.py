from . import create_ctx
import pytest


def test_button_turbo(mocker, m5stickv):
    from krux.pages.keypads import Keypad
    from krux.input import FAST_FORWARD, FAST_BACKWARD, PRESSED

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, "abc")
    mocker.spy(keypad, "_next_key")
    mocker.spy(keypad, "_previous_key")
    ctx.input.page_value = mocker.MagicMock(side_effect=[PRESSED, None])

    keypad.navigate(FAST_FORWARD)
    keypad._next_key.assert_called()

    ctx.input.page_value = mocker.MagicMock(side_effect=None)
    ctx.input.page_prev_value = mocker.MagicMock(side_effect=[PRESSED, None])
    keypad.navigate(FAST_BACKWARD)
    keypad._previous_key.assert_called()


def test_invalid_touch_index(mocker, amigo):
    from krux.pages.keypads import Keypad
    from krux.input import BUTTON_TOUCH

    ctx = create_ctx(mocker, [BUTTON_TOUCH], touch_seq=[-1])
    keypad = Keypad(ctx, "abc")
    btn = keypad.touch_to_physical()
    assert keypad.cur_key_index == 0

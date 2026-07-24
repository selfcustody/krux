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


def test_scan_key_uses_last_keyset_empty_cell(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["a" * 26, "b" * 23], has_scan_key=True)

    assert keypad.scan_index is None
    keypad.next_keyset()

    assert keypad.layout.width == 5
    assert keypad.layout.height == 6
    assert keypad.scan_index == 25
    assert keypad.more_index == 26
    assert keypad.del_index == 27
    assert keypad.esc_index == 28
    assert keypad.go_index == 29


def test_scan_key_is_reachable_with_buttons(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["a" * 26, "b" * 23], has_scan_key=True)
    keypad.next_keyset()
    keypad.cur_key_index = len(keypad.keys) - 1

    keypad._next_key()
    assert keypad.cur_key_index == keypad.scan_index

    keypad._previous_key()
    assert keypad.cur_key_index == len(keypad.keys) - 1


def test_draw_scan_key_glyph(mocker, m5stickv):
    import sys
    import lcd
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["a" * 26, "b" * 23], has_scan_key=True)
    keypad.next_keyset()

    keypad.draw_keys()
    keypad.draw_keys()

    sys.modules["image"].Image.assert_called_once()
    assert sys.modules["image"].Image.return_value.draw_rectangle.call_count > 1
    assert lcd.display.call_count == 2
    ctx.display.fill_rectangle.assert_not_called()

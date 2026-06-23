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


def test_toggle_case_abc_to_numbers(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC", "123", "!@#"])
    assert keypad.keyset_index == 0
    keypad.toggle_case()
    assert keypad.keyset_index == 1


def test_toggle_case_numbers_to_symbols(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC", "123", "!@#"])
    keypad.keyset_index = 2
    keypad.toggle_case()
    assert keypad.keyset_index == 0


def test_toggle_case_symbols_to_abc(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC", "123", "!@#"])
    keypad.keyset_index = 3
    keypad.toggle_case()
    assert keypad.keyset_index == 0


def test_toggle_case_no_change_single_keyset(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc"])
    keypad.toggle_case()
    assert keypad.keyset_index == 0


def test_build_key_cache_updates_on_toggle(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC"])
    first_label = keypad._key_labels[0]
    keypad.toggle_case()
    second_label = keypad._key_labels[0]
    assert first_label != second_label


def test_draw_keyset_index_three_bars(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC", "123", "!@#"])
    mocker.patch.object(ctx.display, "fill_rectangle")
    keypad.draw_keyset_index()
    assert ctx.display.fill_rectangle.call_count == 4


def test_draw_keyset_index_single_keyset(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc"])
    mocker.patch.object(ctx.display, "fill_rectangle")
    keypad.draw_keyset_index()
    ctx.display.fill_rectangle.assert_not_called()


def test_next_keyset_skips_letters(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC", "123", "!@#"])
    keypad.keyset_index = 2
    keypad.next_keyset()
    assert keypad.keyset_index == 3
    keypad.next_keyset()
    assert keypad.keyset_index == 2


def test_previous_keyset_skips_letters(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC", "123", "!@#"])
    keypad.keyset_index = 3
    keypad.previous_keyset()
    assert keypad.keyset_index == 2
    keypad.previous_keyset()
    assert keypad.keyset_index == 3


def test_next_keyset_wraps_around(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC", "123", "!@#"])
    keypad.keyset_index = 3
    keypad.next_keyset()
    assert keypad.keyset_index == 2


def test_previous_keyset_wraps_around(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "ABC", "123", "!@#"])
    keypad.keyset_index = 2
    keypad.previous_keyset()
    assert keypad.keyset_index == 3


def test_cell_positions_precomputed(mocker, m5stickv):
    from krux.pages.keypads import Keypad

    ctx = create_ctx(mocker, [])
    keypad = Keypad(ctx, ["abc", "123"])
    assert len(keypad.layout.cell_positions) == keypad.layout.max_index

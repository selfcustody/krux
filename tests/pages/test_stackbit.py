from .home_pages.test_home import tdata, create_ctx


def test_export_mnemonic_stackbit_standard(mocker, m5stickv, tdata):
    """Standard layout: 6 words per page, 4 pages for 24-word mnemonic"""
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    case = [
        Wallet(tdata.SINGLESIG_24_WORD_KEY),
        None,
        [
            *([BUTTON_PAGE] * 2),  # Go to "Other Formats"
            BUTTON_ENTER,  # Select "Other Formats"
            *([BUTTON_PAGE] * 2),  # Go to "Open Stackbit"
            *(
                [BUTTON_ENTER] * 6
            ),  # Select "Open Stackbit", "Standard", PG2, PG3, PG4, leave
            *([BUTTON_PAGE] * 2),  # Go to "Back" in Stackbit submenu
            BUTTON_ENTER,  # Select "Back" from Stackbit submenu
            *([BUTTON_PAGE] * 2),  # Go to "Back" in Other Formats
            BUTTON_ENTER,  # Select "Back" from Other Formats
            BUTTON_PAGE,  # Go to "Back" in mnemonic menu
            BUTTON_ENTER,  # Select "Back"
        ],
    ]
    ctx = create_ctx(mocker, case[2], case[0], case[1])
    mnemonics = MnemonicsView(ctx)
    mocker.spy(mnemonics, "stackbit")
    mocker.spy(mnemonics, "_stackbit_standard")
    mocker.spy(mnemonics, "_stackbit_vertical_compact")
    mnemonics.mnemonic()
    mnemonics.stackbit.assert_called_once()
    mnemonics._stackbit_standard.assert_called_once()
    mnemonics._stackbit_vertical_compact.assert_not_called()
    assert ctx.input.wait_for_button.call_count == len(case[2])


def test_export_mnemonic_stackbit_standard_amigo(mocker, amigo, tdata):
    """Standard layout on Amigo: 6 words per page, 4 pages for 24-word mnemonic"""
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    case = [
        Wallet(tdata.SINGLESIG_24_WORD_KEY),
        None,
        [
            *([BUTTON_PAGE] * 2),  # Go to "Other Formats"
            BUTTON_ENTER,  # Select "Other Formats"
            *([BUTTON_PAGE] * 2),  # Go to "Open Stackbit"
            *(
                [BUTTON_ENTER] * 6
            ),  # Select "Open Stackbit", "Standard", PG2, PG3, PG4, leave
            *([BUTTON_PAGE] * 2),  # Go to "Back" in Stackbit submenu
            BUTTON_ENTER,  # Select "Back" from Stackbit submenu
            *([BUTTON_PAGE] * 2),  # Go to "Back" in Other Formats
            BUTTON_ENTER,  # Select "Back" from Other Formats
            BUTTON_PAGE,  # Go to "Back" in mnemonic menu
            BUTTON_ENTER,  # Select "Back"
        ],
    ]
    ctx = create_ctx(mocker, case[2], case[0], case[1])
    mnemonics = MnemonicsView(ctx)
    mocker.spy(mnemonics, "stackbit")
    mocker.spy(mnemonics, "_stackbit_standard")
    mnemonics.mnemonic()
    mnemonics.stackbit.assert_called_once()
    mnemonics._stackbit_standard.assert_called_once()
    assert ctx.input.wait_for_button.call_count == len(case[2])


def test_export_mnemonic_stackbit_vertical(mocker, amigo, tdata):
    """Grouped layout on Amigo: 2 words/group, 4 words/page, 6 pages for 24-word mnemonic."""
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    case = [
        Wallet(tdata.SINGLESIG_24_WORD_KEY),
        None,
        [
            *([BUTTON_PAGE] * 2),  # Go to "Other Formats"
            BUTTON_ENTER,  # Select "Other Formats"
            *([BUTTON_PAGE] * 2),  # Go to "Open Stackbit"
            BUTTON_ENTER,  # Select "Open Stackbit"
            BUTTON_PAGE,  # Go to "Vertical"
            BUTTON_ENTER,  # Select "Vertical"
            *([BUTTON_ENTER] * 6),  # Advance 6 pages
            BUTTON_PAGE,  # Go to "Back" in Stackbit submenu
            BUTTON_ENTER,  # Select "Back" from Stackbit submenu
            *([BUTTON_PAGE] * 2),  # Go to "Back" in Other Formats
            BUTTON_ENTER,  # Select "Back" from Other Formats
            BUTTON_PAGE,  # Go to "Back" in mnemonic menu
            BUTTON_ENTER,  # Select "Back"
        ],
    ]
    ctx = create_ctx(mocker, case[2], case[0], case[1])
    mnemonics = MnemonicsView(ctx)
    mocker.spy(mnemonics, "stackbit")
    mocker.spy(mnemonics, "_stackbit_vertical")
    mocker.spy(mnemonics, "_stackbit_vertical_default")
    mnemonics.mnemonic()
    mnemonics.stackbit.assert_called_once()
    mnemonics._stackbit_vertical.assert_called_once()
    mnemonics._stackbit_vertical_default.assert_called_once()
    assert ctx.input.wait_for_button.call_count == len(case[2])


def test_export_mnemonic_stackbit_vertical_compact(mocker, m5stickv, tdata):
    """Dense layout on M5StickV: 6 words per page, 4 pages for 24-word mnemonic."""
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    case = [
        Wallet(tdata.SINGLESIG_24_WORD_KEY),
        None,
        [
            *([BUTTON_PAGE] * 2),  # Go to "Other Formats"
            BUTTON_ENTER,  # Select "Other Formats"
            *([BUTTON_PAGE] * 2),  # Go to "Open Stackbit"
            BUTTON_ENTER,  # Select "Open Stackbit"
            BUTTON_PAGE,  # Go to "Vertical"
            BUTTON_ENTER,  # Select "Vertical"
            *([BUTTON_ENTER] * 4),  # Advance 4 pages
            BUTTON_PAGE,  # Go to "Back" in Stackbit submenu
            BUTTON_ENTER,  # Select "Back" from Stackbit submenu
            *([BUTTON_PAGE] * 2),  # Go to "Back" in Other Formats
            BUTTON_ENTER,  # Select "Back" from Other Formats
            BUTTON_PAGE,  # Go to "Back" in mnemonic menu
            BUTTON_ENTER,  # Select "Back"
        ],
    ]
    ctx = create_ctx(mocker, case[2], case[0], case[1])
    mnemonics = MnemonicsView(ctx)
    mocker.spy(mnemonics, "stackbit")
    mocker.spy(mnemonics, "_stackbit_vertical")
    mocker.spy(mnemonics, "_stackbit_vertical_compact")
    mnemonics.mnemonic()
    mnemonics.stackbit.assert_called_once()
    mnemonics._stackbit_vertical.assert_called_once()
    mnemonics._stackbit_vertical_compact.assert_called_once()
    assert ctx.input.wait_for_button.call_count == len(case[2])


def test_enter_stackbit(m5stickv, mocker):
    from krux.pages.stack_1248 import Stackbit
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # Toggle "2" of first digit
        [BUTTON_PAGE]
        + [BUTTON_ENTER]
        # Toggle "1" of first digit (and disable "2" through sanity check)
        + [BUTTON_PAGE_PREV]
        + [BUTTON_ENTER]
        # Toggle "1" of second digit
        + [BUTTON_PAGE] * 2
        + [BUTTON_ENTER]
        # Toggle "2" of second digit
        + [BUTTON_PAGE]
        + [BUTTON_ENTER]
        # Toggle "8" of second digit (and disable "2" and "1" through sanity check)
        + [BUTTON_PAGE] * 2
        + [BUTTON_ENTER]
        # Proceed to second word
        + [BUTTON_PAGE_PREV] * 6
        + [BUTTON_ENTER] * 2
        # Cycle forward and toggle "2" of first digit
        + [BUTTON_PAGE] * 17
        + [BUTTON_ENTER]
        # Cycle backward and toggle "8" of fourth digit
        + [BUTTON_PAGE_PREV] * 4
        + [BUTTON_ENTER]
        # Proceed to third word
        + [BUTTON_PAGE] * 2
        + [BUTTON_ENTER] * 2
        # Give up on third word
        + [BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER, BUTTON_PAGE]
        # Enter 11 more words (language)
        + [BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER, BUTTON_ENTER] * 10
        + [BUTTON_ENTER]
    )
    TEST_12_WORDS = "thought wife language language language language language language language language language language"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert " ".join(words) == TEST_12_WORDS


def test_enter_stackbit_touch(amigo, mocker):
    from krux.pages.stack_1248 import Stackbit, STACKBIT_GO_INDEX
    from krux.input import BUTTON_TOUCH

    YES = 1
    BTN_SEQUENCE = [BUTTON_TOUCH] * 3 * 12 + [BUTTON_TOUCH]
    TOUCH_SEQUENCE = [0, STACKBIT_GO_INDEX + 1, YES] * 12 + [YES]
    TEST_12_WORDS = "language language language language language language language language language language language language"

    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert " ".join(words) == TEST_12_WORDS


def test_esc_entering_stackbit(amigo, mocker):
    from krux.pages.stack_1248 import Stackbit
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # Move to ESC
        [BUTTON_PAGE_PREV] * 2
        + [BUTTON_ENTER]
        # Confirm
        + [BUTTON_ENTER]
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words == None


def test_enter_stackbit_vertical(m5stickv, mocker, tdata):
    """Button navigation: enter 'abandon'*11+'about' on a vertical 1248 grid."""
    from krux.pages.stack_1248 import Stackbit
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    ABANDON_SEQ = (
        # Move to fourth digit, toggle "1"
        [BUTTON_PAGE] * 3
        + [BUTTON_ENTER]
        # Go, confirm word "abandon"
        + [BUTTON_PAGE_PREV] * 4
        + [BUTTON_ENTER] * 2
    )
    ABOUT_SEQ = (
        # Move to fourth digit, toggle "4" (cell 8 is skipped as invalid)
        [BUTTON_PAGE] * 10
        + [BUTTON_ENTER]
        # Go, confirm word "about", confirm done
        + [BUTTON_PAGE_PREV] * 11
        + [BUTTON_ENTER] * 3
    )
    BTN_SEQUENCE = ABANDON_SEQ * 11 + ABOUT_SEQ

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248_vertical()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert " ".join(words) == tdata.SIGNING_MNEMONIC


def test_enter_stackbit_vertical_touch(amigo, mocker, tdata):
    """Touch navigation: enter 'abandon'*11+'about' via touch screen on vertical grid."""
    from krux.pages.stack_1248 import Stackbit, VERT_GO_INDEX
    from krux.input import BUTTON_TOUCH

    YES = 1
    # 1st "abandon": touch "1" of fourth digit, touch invalid cell 8 (no-op), Go, confirm
    # 10x "abandon": touch "1" of fourth digit, Go, confirm
    # 1x  "about":   touch "4" of fourth digit, Go, confirm, done
    BTN_SEQUENCE = [BUTTON_TOUCH] * 4 + [BUTTON_TOUCH] * 3 * 10 + [BUTTON_TOUCH] * 4
    TOUCH_SEQUENCE = (
        [3, 8, VERT_GO_INDEX, YES]
        + [3, VERT_GO_INDEX, YES] * 10
        + [11, VERT_GO_INDEX, YES, YES]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248_vertical()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert " ".join(words) == tdata.SIGNING_MNEMONIC


def test_esc_entering_stackbit_vertical(amigo, mocker):
    """Pressing Esc from the vertical input grid returns None."""
    from krux.pages.stack_1248 import Stackbit
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # Move to Esc
        [BUTTON_PAGE_PREV] * 3
        + [BUTTON_ENTER]  # Select "Esc"
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248_vertical()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words is None


def test_enter_stackbit_vertical_reject_word(m5stickv, mocker):
    """Rejecting a word confirmation returns to input without advancing word_index."""
    from krux.pages.stack_1248 import Stackbit
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # toggle bit at index 0 (col 0, weight 1)
        + [BUTTON_PAGE_PREV]  # wrap to Go
        + [BUTTON_ENTER]  # press Go
        + [BUTTON_PAGE]  # prompt: No — reject word
        # continue: digits reset, index reset to 0
        + [BUTTON_PAGE_PREV] * 3  # navigate 0 -> Go(18) -> 17 -> Esc(16)
        + [BUTTON_ENTER]  # press Esc
        + [BUTTON_ENTER]  # confirm "Are you sure?"
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248_vertical()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words is None


def test_load_key_from_1248_standard_cancel(m5stickv, mocker):
    """Selecting Standard then Esc dispatches to enter_1248 and returns MENU_CONTINUE without loading."""
    from krux.pages.mnemonic_loader import MnemonicLoader
    from krux.pages.stack_1248 import Stackbit
    from krux.pages import MENU_CONTINUE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # submenu: select Standard (idx 0)
        *([BUTTON_PAGE_PREV] * 2),  # in grid: navigate to Esc
        *([BUTTON_ENTER] * 2),  # select Esc, confirm; callback returns MENU_CONTINUE
        *([BUTTON_PAGE] * 2),  # submenu: idx 0 → 1 → 2 (Back)
        BUTTON_ENTER,  # select Back → MENU_EXIT
    ]
    spy_std = mocker.spy(Stackbit, "enter_1248")
    spy_vert = mocker.spy(Stackbit, "enter_1248_vertical")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    loader = MnemonicLoader(ctx)
    spy_load = mocker.spy(loader, "_load_key_from_words")

    result = loader.load_key_from_1248()

    assert result == MENU_CONTINUE
    spy_std.assert_called_once()
    assert spy_std.spy_return is None
    spy_vert.assert_not_called()
    spy_load.assert_not_called()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_load_key_from_1248_vertical_cancel(amigo, mocker):
    """Selecting Vertical then Esc dispatches to enter_1248_vertical and returns MENU_CONTINUE without loading."""
    from krux.pages.mnemonic_loader import MnemonicLoader
    from krux.pages.stack_1248 import Stackbit
    from krux.pages import MENU_CONTINUE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_PAGE,  # submenu: move idx 0 → 1 (Vertical)
        BUTTON_ENTER,  # select Vertical
        *([BUTTON_PAGE_PREV] * 3),  # in vertical grid: navigate to Esc
        BUTTON_ENTER,  # select Esc
        BUTTON_ENTER,  # confirm Esc; callback returns MENU_CONTINUE
        BUTTON_PAGE,  # submenu: idx 1 → 2 (Back)
        BUTTON_ENTER,  # select Back → MENU_EXIT
    ]
    spy_std = mocker.spy(Stackbit, "enter_1248")
    spy_vert = mocker.spy(Stackbit, "enter_1248_vertical")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    loader = MnemonicLoader(ctx)
    spy_load = mocker.spy(loader, "_load_key_from_words")

    result = loader.load_key_from_1248()

    assert result == MENU_CONTINUE
    spy_vert.assert_called_once()
    assert spy_vert.spy_return is None
    spy_std.assert_not_called()
    spy_load.assert_not_called()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_load_key_from_1248_vertical_loads_words(m5stickv, mocker, tdata):
    """Vertical: real 12-word entry produces tdata.SIGNING_MNEMONIC, piped into _load_key_from_words."""
    from krux.pages.mnemonic_loader import MnemonicLoader
    from krux.pages.stack_1248 import Stackbit
    from krux.pages import MENU_CONTINUE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    ABANDON_SEQ = (
        # Move to fourth digit, toggle "1"
        [BUTTON_PAGE] * 3
        + [BUTTON_ENTER]
        # Go, confirm word "abandon"
        + [BUTTON_PAGE_PREV] * 4
        + [BUTTON_ENTER] * 2
    )
    ABOUT_SEQ = (
        # Move to fourth digit, toggle "4" (cell 8 is skipped as invalid)
        [BUTTON_PAGE] * 10
        + [BUTTON_ENTER]
        # Go, confirm word "about", confirm done
        + [BUTTON_PAGE_PREV] * 11
        + [BUTTON_ENTER] * 3
    )
    BTN_SEQUENCE = (
        [BUTTON_PAGE, BUTTON_ENTER]  # submenu: move idx 0 → 1 (Vertical), select
        + ABANDON_SEQ * 11
        + ABOUT_SEQ
        + [BUTTON_PAGE, BUTTON_ENTER]  # submenu: idx 1 → 2 (Back), select
    )
    spy_std = mocker.spy(Stackbit, "enter_1248")
    spy_vert = mocker.spy(Stackbit, "enter_1248_vertical")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    loader = MnemonicLoader(ctx)
    mocker.patch.object(loader, "_load_key_from_words", return_value=MENU_CONTINUE)

    result = loader.load_key_from_1248()

    expected_words = tdata.SIGNING_MNEMONIC.split()
    assert result == MENU_CONTINUE
    spy_vert.assert_called_once()
    spy_std.assert_not_called()
    assert spy_vert.spy_return == expected_words
    loader._load_key_from_words.assert_called_once_with(expected_words)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_entering_stackbit_buttons_turbo(mocker, m5stickv):
    from krux.pages.stack_1248 import Stackbit
    from krux.input import PRESSED, FAST_FORWARD, FAST_BACKWARD, Input
    import pytest

    ctx = create_ctx(mocker, [])
    input = Input()
    input.wait_for_button = ctx.input.wait_for_button
    ctx.input.wait_for_fastnav_button = input.wait_for_fastnav_button
    stackbit = Stackbit(ctx)
    stackbit.index = mocker.MagicMock(side_effect=ValueError)

    # fast forward
    input.page_value = mocker.MagicMock(return_value=PRESSED)

    with pytest.raises(ValueError):
        stackbit.enter_1248()

    stackbit.index.assert_called_with(0, FAST_FORWARD)

    # fast backward
    input.page_value = mocker.MagicMock(return_value=None)
    input.page_prev_value = mocker.MagicMock(return_value=PRESSED)

    with pytest.raises(ValueError):
        stackbit.enter_1248()

    stackbit.index.assert_called_with(0, FAST_BACKWARD)


def test_enter_stackbit_vertical_navigation_skips_invalid_cells(m5stickv, mocker):
    """Forward and backward sweeps over the vertical grid skip cells 8 and 12."""
    from krux.pages.stack_1248 import Stackbit, VERT_INVALID_CELLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_PAGE] * 11  # 0 → 9 (skip 8) → 13 (skip 12)
        + [BUTTON_PAGE_PREV] * 4  # 13 → 11 (skip 12) → 7 (skip 8)
        + [BUTTON_PAGE] * 7  # 7 → 16 (skip 8, 12); lands on Esc
        + [BUTTON_ENTER] * 2  # select Esc, confirm
    )
    spy_index = mocker.spy(Stackbit, "_index_vertical")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248_vertical()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words is None
    assert spy_index.call_count == len(BTN_SEQUENCE) - 2  # ENTERs don't navigate
    for return_value in spy_index.spy_return_list:
        assert return_value not in VERT_INVALID_CELLS, (
            "navigation landed on invalid cell %d" % return_value
        )
    forward_returns = [
        spy_index.spy_return_list[i]
        for i, call in enumerate(spy_index.call_args_list)
        if call.args[-1] == BUTTON_PAGE
    ]
    backward_returns = [
        spy_index.spy_return_list[i]
        for i, call in enumerate(spy_index.call_args_list)
        if call.args[-1] == BUTTON_PAGE_PREV
    ]
    assert 9 in forward_returns and 13 in forward_returns
    assert 11 in backward_returns and 7 in backward_returns


def test_enter_stackbit_vertical_clamps_digit_on_overflow(m5stickv, mocker):
    """Toggling a bit that would push col-0 above 2 (or any other col above 9) clamps the digit to 0."""
    from krux.pages.stack_1248 import Stackbit
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # col 0 overflow path
        [BUTTON_ENTER]  # cell 0: digits=[1,0,0,0]
        + [BUTTON_PAGE] * 4  # 0 → 4 (col 0, row 1, weight 2)
        + [BUTTON_ENTER]  # cell 4: 1^2=3 > 2 → clamp digits[0] to 0
        # col 1 overflow path
        + [BUTTON_PAGE] * 7  # 4 → 13 (col 1, row 3, weight 8); skips 8 and 12
        + [BUTTON_ENTER]  # cell 13: digits=[0,8,0,0]
        + [BUTTON_PAGE_PREV] * 6  # 13 → 5 (col 1, row 1, weight 2); skips 12 and 8
        + [BUTTON_ENTER]  # cell 5: 8^2=10 > 9 → clamp digits[1] to 0
        # exit
        + [BUTTON_PAGE] * 9  # 5 → 16 (Esc); skips 8 and 12
        + [BUTTON_ENTER] * 2  # select Esc, confirm
    )
    snapshots = []
    real_toggle = Stackbit._toggle_bit_vertical

    def snap_toggle(self, digits, index):
        result = real_toggle(self, digits, index)
        snapshots.append((index, list(result)))
        return result

    mocker.patch.object(Stackbit, "_toggle_bit_vertical", new=snap_toggle)
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248_vertical()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words is None
    assert snapshots == [
        (0, [1, 0, 0, 0]),  # cell 0: set bit-1 in col 0
        (4, [0, 0, 0, 0]),  # cell 4: col-0 overflow (3 > 2) → clamp to 0
        (13, [0, 8, 0, 0]),  # cell 13: set bit-8 in col 1
        (5, [0, 0, 0, 0]),  # cell 5: col-1 overflow (10 > 9) → clamp to 0
    ]


def test_enter_stackbit_vertical_index_wraps_at_grid_boundaries(m5stickv, mocker):
    """PAGE_PREV at index 0 wraps to VERT_GO_INDEX; PAGE at VERT_GO_INDEX wraps to 0."""
    from krux.pages.stack_1248 import Stackbit, VERT_GO_INDEX
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_PAGE_PREV]  # 0 → VERT_GO_INDEX (backward wrap)
        + [BUTTON_PAGE]  # VERT_GO_INDEX → 0 (forward wrap)
        + [BUTTON_PAGE_PREV] * 3  # 0 → 18 → 17 → 16 (Esc)
        + [BUTTON_ENTER] * 2  # select Esc, confirm
    )
    spy_index = mocker.spy(Stackbit, "_index_vertical")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248_vertical()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert words is None
    assert spy_index.spy_return_list[0] == VERT_GO_INDEX  # backward wrap from 0
    assert spy_index.spy_return_list[1] == 0  # forward wrap from VERT_GO_INDEX

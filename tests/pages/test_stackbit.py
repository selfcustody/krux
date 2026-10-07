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
    """Grouped layout on Amigo: 2 words/group, 4 words/page, 6 pages for 24-word mnemonic.

    Amigo uses FONT_WIDTH=12, so 3 words/group would overflow the word name text.
    The layout auto-selects 2 words/group → 4 words/page → 6 pages.
    """
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
    """Dense layout on M5StickV: 6 words per page, 4 pages for 24-word mnemonic.

    2 words side-by-side × 3 rows, no word names or BIP39 codes.
    """
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
    BTN_SEQUENCE = [BUTTON_TOUCH] * 4 * 12 + [BUTTON_TOUCH]
    TOUCH_SEQUENCE = [0, -1, STACKBIT_GO_INDEX + 1, YES] * 12 + [
        YES
    ]  # negative values (invalid touches) should not change the result
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


def test_stackbit_index_ignore_swipe(mocker, amigo):
    from krux.pages.stack_1248 import Stackbit
    from krux.input import SWIPE_LEFT, SWIPE_RIGHT, SWIPE_DOWN, SWIPE_UP, SWIPE_FAIL

    ctx = create_ctx(mocker, [])
    stackbit = Stackbit(ctx)
    tmp = 10
    for swipe in (SWIPE_LEFT, SWIPE_RIGHT, SWIPE_DOWN, SWIPE_UP, SWIPE_FAIL):
        new_index = stackbit.index(tmp, swipe)
        assert new_index == tmp

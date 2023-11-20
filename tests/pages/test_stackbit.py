from .test_home import tdata, create_ctx


def test_export_mnemonic_stackbit(mocker, m5stickv, tdata):
    from krux.pages.mnemonic_view import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    case = [
        Wallet(tdata.SINGLESIG_24_WORD_KEY),
        None,
        [
            BUTTON_PAGE,
            BUTTON_PAGE,
            BUTTON_PAGE,
            BUTTON_PAGE,
            BUTTON_PAGE,
            BUTTON_ENTER,  # Open Stackbit
            BUTTON_ENTER,  # PG2
            BUTTON_ENTER,  # PG3
            BUTTON_ENTER,  # PG4
            BUTTON_ENTER,  # Leave
            BUTTON_PAGE,  # Go to "Back"
            BUTTON_PAGE,
            BUTTON_ENTER,  # click on back to return to home init screen
        ],
    ]
    ctx = create_ctx(mocker, case[2], case[0], case[1])
    mnemonics = MnemonicsView(ctx)
    mocker.spy(mnemonics, "stackbit")
    mnemonics.mnemonic()
    mnemonics.stackbit.assert_called_once()
    assert ctx.input.wait_for_button.call_count == len(case[2])


def test_export_mnemonic_stackbit_amigo(mocker, amigo_tft, tdata):
    from krux.pages.mnemonic_view import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    case = [
        Wallet(tdata.SINGLESIG_24_WORD_KEY),
        None,
        [
            BUTTON_PAGE,
            BUTTON_PAGE,
            BUTTON_PAGE,
            BUTTON_PAGE,
            BUTTON_PAGE,
            BUTTON_ENTER,  # Open Stackbit
            BUTTON_ENTER,  # PG2
            BUTTON_ENTER,  # PG3
            BUTTON_ENTER,  # PG4
            BUTTON_ENTER,  # Leave
            BUTTON_PAGE,  # Go to "Back"
            BUTTON_PAGE,
            BUTTON_ENTER,  # click on back to return to home init screen
        ],
    ]
    ctx = create_ctx(mocker, case[2], case[0], case[1])
    mnemonics = MnemonicsView(ctx)
    mocker.spy(mnemonics, "stackbit")
    mnemonics.mnemonic()
    mnemonics.stackbit.assert_called_once()
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


def test_enter_stackbit_touch(amigo_tft, mocker):
    from krux.pages.stack_1248 import Stackbit, STACKBIT_GO_INDEX
    from krux.input import BUTTON_TOUCH

    YES = 0
    BTN_SEQUENCE = [BUTTON_TOUCH] * 3 * 12 + [BUTTON_TOUCH]
    TOUCH_SEQUENCE = [0, STACKBIT_GO_INDEX + 1, YES] * 12 + [0]
    TEST_12_WORDS = "language language language language language language language language language language language language"

    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQUENCE)
    stackbit = Stackbit(ctx)
    words = stackbit.enter_1248()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert " ".join(words) == TEST_12_WORDS


def test_esc_entering_stackbit(amigo_tft, mocker):
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

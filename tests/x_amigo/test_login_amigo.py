from krux.settings import I18n
from ..shared_mocks import *
from krux.input import (
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    BUTTON_TOUCH,
    SWIPE_RIGHT,
    SWIPE_LEFT,
)


def test_new_key_from_d6(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login, D6_MIN_ROLLS

    cases = [
        (
            # Yes and proceed
            [BUTTON_PAGE, BUTTON_ENTER] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # Done? Yes and proceed
            [BUTTON_PAGE, BUTTON_ENTER] +
            # Confirm SHA, Move to Yes, Loading key, Skip passphrase, Single-key
            [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "diet glad hat rural panther lawsuit act drop gallery urge where fit",
        ),
        (
            # Yes and proceed
            [BUTTON_PAGE, BUTTON_ENTER] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # Done? No and proceed
            [BUTTON_ENTER] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # Confirm SHA, Move to Yes, Loading key, Skip passphrase, Single-key
            [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "day fog body unfold two filter bundle obey pause pattern penalty sweet shell quantum critic bridge stage patch purpose reflect flat domain post produce",
        ),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case[0])),
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)

        login.new_key_from_d6()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        assert ctx.wallet.key.mnemonic == case[1]

    # Leaving keypad
    esc_keypad = [
        # Move to Yes
        BUTTON_PAGE,
        # Enter Keypad
        BUTTON_ENTER,
        # Go to ESC position
        BUTTON_PAGE_PREV,
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
        # Move to Yes
        BUTTON_PAGE,
        # Leave
        BUTTON_ENTER,
    ]
    ctx = mock.MagicMock(
        input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=esc_keypad)),
        display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
    )
    login = Login(ctx)
    login.new_key_from_d6()
    assert ctx.input.wait_for_button.call_count == len(esc_keypad)


def test_load_key_from_text(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login

    cases = [
        (
            [BUTTON_PAGE, BUTTON_ENTER]
            + (
                # A
                [BUTTON_ENTER]
                +
                # B
                [BUTTON_ENTER]
                +
                # I
                [BUTTON_ENTER]
                +
                # Go + Confirm
                [BUTTON_ENTER, BUTTON_ENTER]
            )
            * 11
            + (
                # N
                [BUTTON_TOUCH]  # index 13 -> "n"
                +
                # Touch on del
                [BUTTON_TOUCH]  # index 26 -> "Del"
                +
                # N
                [BUTTON_TOUCH]  # index 13 -> "n"
                +
                # O
                [BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_ENTER]
                +
                # R going back
                [BUTTON_PAGE_PREV for _ in range(11)]
                + [BUTTON_ENTER]
                +
                # T
                [BUTTON_ENTER]
                +
                # Invalid Position
                [BUTTON_TOUCH]  # index 29 "empty"
                +
                # Go
                [BUTTON_TOUCH]  # index 28 -> "Go"
                +
                # Confirm word <north>
                [BUTTON_TOUCH]
            )
            +
            # Done? Move to Yes, Confirm, Words correct? Move to Yes, Confirm, No passphrase, Single-key
            [
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "ability ability ability ability ability ability ability ability ability ability ability north",
            [13, 26, 13, 29, 28],
        ),
        (
            [BUTTON_PAGE, BUTTON_ENTER]
            + (
                # A
                [BUTTON_ENTER]
                +
                # B
                [BUTTON_ENTER]
                +
                # I
                [BUTTON_ENTER]
                +
                # Go + Confirm
                [BUTTON_ENTER, BUTTON_ENTER]
            )
            * 11
            +
            # Move to Go, press Go, confirm word
            [BUTTON_PAGE_PREV] + [BUTTON_ENTER] + [BUTTON_ENTER] +
            # Done? Move to Yes, Confirm, Words correct? Move to Yes, Confirm, No passphrase, Single-key
            [
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "ability ability ability ability ability ability ability ability ability ability ability",
            [0],
        ),
    ]

    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(
                wait_for_button=mock.MagicMock(side_effect=case[0]),
                touch=mock.MagicMock(current_index=mock.MagicMock(side_effect=case[2])),
            ),
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)
        login.load_key_from_text()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_leaving_keypad(mocker):
    from krux.pages.login import Login

    esc_keypad = [
        BUTTON_PAGE,  # Yes
        BUTTON_ENTER,  # Proceed
        BUTTON_PAGE_PREV,  # Move to Go
        BUTTON_PAGE_PREV,  # Move to ESC
        BUTTON_ENTER,  # Press ESC
        BUTTON_PAGE,  # Move to Yes
        BUTTON_ENTER,  # Leave
    ]
    ctx = mock.MagicMock(
        input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=esc_keypad)),
        display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
    )
    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(esc_keypad)


def test_passphrase_give_up(mocker):
    from krux.pages.login import Login

    case = (
        [BUTTON_PAGE, BUTTON_ENTER]
        + (
            # A
            [BUTTON_ENTER]
            +
            # B
            [BUTTON_ENTER]
            +
            # I
            [BUTTON_ENTER]
            +
            # Go + Confirm
            [BUTTON_ENTER, BUTTON_ENTER]
        )
        * 11
        +
        # Move to Go, press Go, confirm word
        [BUTTON_PAGE_PREV]
        + [BUTTON_ENTER]
        + [BUTTON_ENTER]
        +
        # Done? Move to Yes, Confirm
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # Words correct? Move to Yes, Confirm
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # Passphrase, Move to Yes, confirm
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # In passphrase keypad:
        [
            BUTTON_PAGE_PREV,  # Move to Go
            BUTTON_PAGE_PREV,  # Move to ESC
            BUTTON_ENTER,  # Press ESC
            BUTTON_PAGE,  # Move to Yes
            BUTTON_ENTER,  # Leave
        ]
    )

    ctx = mock.MagicMock(
        input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case)),
        display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
    )
    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(case)


def test_passphrase(mocker):
    from krux.pages.login import Login

    case = (
        [BUTTON_PAGE, BUTTON_ENTER]
        + (
            # A
            [BUTTON_ENTER]
            +
            # B
            [BUTTON_ENTER]
            +
            # I
            [BUTTON_ENTER]
            +
            # Go + Confirm
            [BUTTON_ENTER, BUTTON_ENTER]
        )
        * 11
        +
        # Move to Go, press Go, confirm word
        [BUTTON_PAGE_PREV]
        + [BUTTON_ENTER]
        + [BUTTON_ENTER]
        +
        # Done? Move to Yes, Confirm
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # Words correct? Move to Yes, Confirm
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # Passphrase, Move to Yes, confirm
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # In passphrase keypad:
        [
            SWIPE_RIGHT,  # Test keypad swaping
            BUTTON_ENTER,  # Add "+" character
            SWIPE_LEFT,  #
            BUTTON_ENTER,  # Add "a" character
            BUTTON_PAGE_PREV,  # Move to Go
            BUTTON_ENTER,  # Press Go
            BUTTON_ENTER,  # Single key
        ]
    )

    ctx = mock.MagicMock(
        input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case)),
        display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
    )
    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(case)


def test_network(mocker):
    import krux
    from krux.pages.login import Login

    # page, page_prev, enter
    index_s_e = (2, 0, 1)
    ctx = mock.MagicMock(
        input=mock.MagicMock(
            touch=mock.MagicMock(current_index=mock.MagicMock(side_effect=index_s_e)),
            wait_for_button=mock.MagicMock(return_value=BUTTON_TOUCH),
        )
    )
    mocker.patch.object(ctx.input.touch, "x_regions", (0, 100, 200, 300))
    mocker.patch.object(ctx.input.touch, "y_regions", (100, 200))

    login = Login(ctx)

    login.network()

    assert ctx.input.wait_for_button.call_count == len(index_s_e)
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mock.call("Network\nmainnet"),
            mock.call("Network\ntestnet"),
            mock.call("Network\nmainnet"),
        ]
    )
    assert krux.pages.login.settings.network == "main"


def test_printer(mocker):
    import krux

    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login

    # page, page_prev, enter
    index_s_e = (2, 0, 1)
    ctx = mock.MagicMock(
        input=mock.MagicMock(
            touch=mock.MagicMock(current_index=mock.MagicMock(side_effect=index_s_e)),
            wait_for_button=mock.MagicMock(return_value=BUTTON_TOUCH),
        )
    )
    login = Login(ctx)

    login.printer()

    assert ctx.input.wait_for_button.call_count == len(index_s_e)
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mock.call("Baudrate\n9600"),
            mock.call("Baudrate\n19200"),
            mock.call("Baudrate\n9600"),
        ]
    )
    assert krux.pages.login.settings.printer.thermal.baudrate == 9600


def test_locale(mocker):
    import krux
    from krux.pages.login import Login

    cases = [
        (
            {"Locale\n%s": "Locale\n%s"},
            [
                I18n.locales[(I18n.locales.index("en-US") + i) % len(I18n.locales)]
                for i in range(len(I18n.locales))
            ],
        ),
        (None, ["en-US" for _ in range(len(I18n.locales))]),
    ]
    for case in cases:
        mocker.patch(
            "krux.pages.login.translations", new=mock.MagicMock(return_value=case[0])
        )

        # page_prev, page, enter
        index_s_e = (0, 2, 1)
        ctx = mock.MagicMock(
            input=mock.MagicMock(
                touch=mock.MagicMock(
                    current_index=mock.MagicMock(side_effect=index_s_e)
                ),
                wait_for_button=mock.MagicMock(return_value=BUTTON_TOUCH),
            )
        )
        login = Login(ctx)

        login.locale()

        assert ctx.input.wait_for_button.call_count == len(index_s_e)
        # asser if locales were called already done with m5stickV
        assert krux.pages.login.settings.i18n.locale == "en-US"


def test_debug(mocker):
    import krux
    from krux.pages.login import Login
    from krux.logging import NONE

    # page_prev, page, enter
    index_s_e = (0, 2, 1)
    ctx = mock.MagicMock(
        input=mock.MagicMock(
            touch=mock.MagicMock(current_index=mock.MagicMock(side_effect=index_s_e)),
            wait_for_button=mock.MagicMock(return_value=BUTTON_TOUCH),
        )
    )
    login = Login(ctx)

    login.debug()

    assert ctx.input.wait_for_button.call_count == len(index_s_e)
    # assert run over all debug levels already done with m5stickV
    assert krux.pages.login.settings.log.level == NONE

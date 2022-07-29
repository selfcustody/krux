def test_new_key_from_d6(mocker, m5stickv):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login, D6_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    cases = [
        (
            # 1 press to proceed
            [BUTTON_ENTER] +
            # 1 presses per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # 1 press to be done at min rolls
            [BUTTON_ENTER] +
            # 1 press to confirm roll string, 1 press to confirm SHA, 1 press to continue loading key, 1 press to skip passphrase, 1 press to select single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "diet glad hat rural panther lawsuit act drop gallery urge where fit",
        ),
        (
            # 1 press to proceed
            [BUTTON_ENTER] +
            # 1 presses per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # 1 press to continue rolling to max rolls
            [BUTTON_PAGE] +
            # 1 presses per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # 1 press to confirm roll string, 1 press to confirm SHA, 1 press to see last 12 words, 1 press to continue loading key, 1 press to skip passphrase, 1 press to select single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
            ],
            "day fog body unfold two filter bundle obey pause pattern penalty sweet shell quantum critic bridge stage patch purpose reflect flat domain post produce",
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[0])
            ),
            display=mocker.MagicMock(
                font_width=8,
                width=mocker.MagicMock(return_value=135),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
        login = Login(ctx)

        login.new_key_from_d6()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        assert ctx.wallet.key.mnemonic == case[1]


def test_new_key_from_d6_on_amigo_without_touch(mocker, amigo):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login, D6_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    cases = [
        (
            # Yes and proceed
            [BUTTON_PAGE, BUTTON_ENTER] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # Done? Yes and proceed
            [BUTTON_PAGE, BUTTON_ENTER] +
            # Confirm roll string, Confirm SHA, Move to Yes, Loading key, Skip passphrase, Single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
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
            # Confirm roll string, Confirm SHA, Move to Yes, Loading key, Skip passphrase, Single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "day fog body unfold two filter bundle obey pause pattern penalty sweet shell quantum critic bridge stage patch purpose reflect flat domain post produce",
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[0])
            ),
            display=mocker.MagicMock(
                font_width=12,
                width=mocker.MagicMock(return_value=480),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
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
    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            wait_for_button=mocker.MagicMock(side_effect=esc_keypad)
        ),
        display=mocker.MagicMock(
            font_width=12,
            width=mocker.MagicMock(return_value=480),
            to_lines=mocker.MagicMock(return_value=[""]),
        ),
    )
    login = Login(ctx)
    login.new_key_from_d6()
    assert ctx.input.wait_for_button.call_count == len(esc_keypad)


def test_new_key_from_d20(mocker, m5stickv):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login, D20_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    cases = [
        (
            # 1 press to proceed
            [BUTTON_ENTER] +
            # 2 roll presses
            [BUTTON_ENTER] + [BUTTON_ENTER] +
            # 2 deletions
            [BUTTON_PAGE_PREV for _ in range(3)]
            + [BUTTON_ENTER]
            + [BUTTON_PAGE_PREV for _ in range(3)]
            + [BUTTON_ENTER]
            +
            # 1 presses per roll
            [BUTTON_ENTER for _ in range(D20_MIN_ROLLS)] +
            # 1 press to be done at min rolls
            [BUTTON_ENTER] +
            # 1 press to confirm roll string, 1 press to confirm SHA, 1 press to continue loading key, 1 press to skip passphrase, 1 press to select single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "erupt remain ride bleak year cabin orange sure ghost gospel husband oppose",
        ),
        (
            # 1 press to proceed
            [BUTTON_ENTER] +
            # 1 presses per roll
            [BUTTON_ENTER for _ in range(D20_MIN_ROLLS)] +
            # 1 press to continue rolling to max rolls
            [BUTTON_PAGE] +
            # 1 presses per roll
            [BUTTON_ENTER for _ in range(D20_MIN_ROLLS)] +
            # 1 press to confirm roll string, 1 press to confirm SHA, 1 press to see last 12 words, 1 press to continue loading key, 1 press to skip passphrase, 1 press to select single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
            ],
            "fun island vivid slide cable pyramid device tuition only essence thought gain silk jealous eternal anger response virus couple faculty ozone test key vocal",
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[0])
            ),
            display=mocker.MagicMock(
                font_width=8,
                width=mocker.MagicMock(return_value=135),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
        login = Login(ctx)

        login.new_key_from_d20()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_qr_code(mocker, m5stickv):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    import binascii
    from ur.ur import UR
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_UR, FORMAT_NONE

    cases = [
        (
            # 12 word confirm, No passphrase, Single-key
            (BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER),
            FORMAT_NONE,
            "olympic term tissue route sense program under choose bean emerge velvet absurd",
            "olympic term tissue route sense program under choose bean emerge velvet absurd",
        ),
        (
            # 12 word confirm, 24 word confirm, No passphrase, Single-key
            (BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER),
            FORMAT_NONE,
            "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major",
            "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major",
        ),
        (
            # 12 word confirm, No passphrase, Single-key
            (BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER),
            FORMAT_NONE,
            "123417871814150815661375189403220156058119360008",
            "olympic term tissue route sense program under choose bean emerge velvet absurd",
        ),
        (
            # 12 word confirm, 24 word confirm, No passphrase, Single-key
            (BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER),
            FORMAT_NONE,
            "023301391610171019391278098413310856127602420628160203911717091708861236056502660800183118111075",
            "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major",
        ),
        (
            # 12 word confirm, No passphrase, Single-key
            (BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER),
            FORMAT_UR,
            UR(
                "crypto-bip39",
                bytearray(
                    binascii.unhexlify(
                        "A2018C66736869656C646567726F75706565726F6465656177616B65646C6F636B6773617573616765646361736865676C6172656477617665646372657765666C616D6565676C6F76650262656E"
                    )
                ),
            ),
            "shield group erode awake lock sausage cash glare wave crew flame glove",
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[0])
            ),
            display=mocker.MagicMock(to_lines=mocker.MagicMock(return_value=[""])),
        )
        login = Login(ctx)
        mocker.patch.object(
            login, "capture_qr_code", mocker.MagicMock(return_value=(case[2], case[1]))
        )

        login.load_key_from_qr_code()

        assert ctx.wallet.key.mnemonic == case[3]


def test_load_key_from_text(mocker, m5stickv):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    cases = [
        (
            [BUTTON_ENTER]
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
                [BUTTON_PAGE for _ in range(13)]
                + [BUTTON_ENTER]
                +
                # O
                [BUTTON_ENTER]
                +
                # R
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # T
                [BUTTON_ENTER]
                +
                # Go
                [BUTTON_ENTER]
            )
            +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability north",
        ),
        (
            [BUTTON_ENTER]
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
            # Go
            [BUTTON_PAGE for _ in range(28)] + [BUTTON_ENTER] +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[0])
            ),
            display=mocker.MagicMock(
                font_width=8,
                width=mocker.MagicMock(return_value=135),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
        login = Login(ctx)

        login.load_key_from_text()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_text_on_amigo_with_touch(mocker, amigo):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH

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
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[0]),
                touch=mocker.MagicMock(
                    current_index=mocker.MagicMock(side_effect=case[2])
                ),
            ),
            display=mocker.MagicMock(
                font_width=12,
                width=mocker.MagicMock(return_value=480),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
        login = Login(ctx)
        login.load_key_from_text()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_digits(mocker, m5stickv):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    cases = [
        (
            [BUTTON_ENTER]
            + (
                # 2
                [BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER]
                +
                # Go + Confirm
                [BUTTON_PAGE for _ in range(10)]
                + [BUTTON_ENTER, BUTTON_ENTER]
            )
            * 11
            + (
                # 1
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # 2
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # 0
                [BUTTON_PAGE for _ in range(11)]
                + [BUTTON_ENTER]
                +
                # 3
                [BUTTON_PAGE, BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER]
                +
                # Go
                [BUTTON_PAGE for _ in range(9)]
                + [BUTTON_ENTER]
            )
            +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability north",
        ),
        (
            [BUTTON_ENTER]
            + (
                # 2
                [BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER]
                +
                # Go + Confirm
                [BUTTON_PAGE for _ in range(10)]
                + [BUTTON_ENTER, BUTTON_ENTER]
            )
            * 11
            +
            # Go
            [BUTTON_PAGE for _ in range(12)] + [BUTTON_ENTER] +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[0])
            ),
            display=mocker.MagicMock(
                font_width=8,
                width=mocker.MagicMock(return_value=135),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
        login = Login(ctx)

        login.load_key_from_digits()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_bits(mocker, m5stickv):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    cases = [
        (
            [BUTTON_ENTER]
            + (
                # 1
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # Go + Confirm
                [BUTTON_PAGE for _ in range(3)]
                + [BUTTON_ENTER, BUTTON_ENTER]
            )
            * 11
            + (
                # 100 10 11 00 10
                # 1
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # 00
                [BUTTON_PAGE for _ in range(4)]
                + [BUTTON_ENTER, BUTTON_ENTER]
                +
                # 1
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # 0
                [BUTTON_PAGE for _ in range(4)]
                + [BUTTON_ENTER]
                +
                # 11
                [BUTTON_PAGE, BUTTON_ENTER, BUTTON_ENTER]
                +
                # 00
                [BUTTON_PAGE for _ in range(4)]
                + [BUTTON_ENTER, BUTTON_ENTER]
                +
                # 1
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # 0
                [BUTTON_PAGE for _ in range(4)]
                + [BUTTON_ENTER]
                +
                # Go
                [BUTTON_PAGE for _ in range(4)]
                + [BUTTON_ENTER]
            )
            +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability north",
        ),
        (
            [BUTTON_ENTER]
            + (
                # 1
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # Go + Confirm
                [BUTTON_PAGE for _ in range(3)]
                + [BUTTON_ENTER, BUTTON_ENTER]
            )
            * 11
            +
            # Go
            [BUTTON_PAGE for _ in range(4)] + [BUTTON_ENTER] +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[0])
            ),
            display=mocker.MagicMock(
                font_width=8,
                width=mocker.MagicMock(return_value=135),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        )
        login = Login(ctx)

        login.load_key_from_bits()

        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_leaving_keypad(mocker, amigo):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    esc_keypad = [
        BUTTON_PAGE,  # Yes
        BUTTON_ENTER,  # Proceed
        BUTTON_PAGE_PREV,  # Move to Go
        BUTTON_PAGE_PREV,  # Move to ESC
        BUTTON_ENTER,  # Press ESC
        BUTTON_PAGE,  # Move to Yes
        BUTTON_ENTER,  # Leave
    ]
    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            wait_for_button=mocker.MagicMock(side_effect=esc_keypad)
        ),
        display=mocker.MagicMock(
            font_width=12,
            width=mocker.MagicMock(return_value=480),
            to_lines=mocker.MagicMock(return_value=[""]),
        ),
    )
    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(esc_keypad)


def test_passphrase_give_up(mocker, amigo):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

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

    ctx = mocker.MagicMock(
        input=mocker.MagicMock(wait_for_button=mocker.MagicMock(side_effect=case)),
        display=mocker.MagicMock(
            font_width=12,
            width=mocker.MagicMock(return_value=480),
            to_lines=mocker.MagicMock(return_value=[""]),
        ),
    )
    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(case)


def test_passphrase(mocker, amigo):
    from krux.pages.login import Login
    from krux.input import (
        BUTTON_ENTER,
        BUTTON_PAGE,
        BUTTON_PAGE_PREV,
        SWIPE_LEFT,
        SWIPE_RIGHT,
    )

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

    ctx = mocker.MagicMock(
        input=mocker.MagicMock(wait_for_button=mocker.MagicMock(side_effect=case)),
        display=mocker.MagicMock(
            font_width=12,
            width=mocker.MagicMock(return_value=480),
            to_lines=mocker.MagicMock(return_value=[""]),
        ),
    )
    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(case)


def test_network(mocker, m5stickv):
    import krux

    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            wait_for_button=mocker.MagicMock(
                side_effect=(BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER)
            )
        ),
        display=mocker.MagicMock(to_lines=mocker.MagicMock(return_value=[""])),
    )
    login = Login(ctx)

    login.network()

    assert ctx.input.wait_for_button.call_count == 3
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call("Network\nmainnet"),
            mocker.call("Network\ntestnet"),
            mocker.call("Network\nmainnet"),
        ]
    )
    assert krux.pages.login.settings.network == "main"


def test_network_on_amigo(mocker, amigo):
    import krux
    from krux.pages.login import Login
    from krux.input import BUTTON_TOUCH

    # page, page_prev, enter
    index_s_e = (2, 0, 1)
    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            touch=mocker.MagicMock(
                current_index=mocker.MagicMock(side_effect=index_s_e)
            ),
            wait_for_button=mocker.MagicMock(return_value=BUTTON_TOUCH),
        )
    )
    mocker.patch.object(ctx.input.touch, "x_regions", (0, 100, 200, 300))
    mocker.patch.object(ctx.input.touch, "y_regions", (100, 200))

    login = Login(ctx)

    login.network()

    assert ctx.input.wait_for_button.call_count == len(index_s_e)
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call("Network\nmainnet"),
            mocker.call("Network\ntestnet"),
            mocker.call("Network\nmainnet"),
        ]
    )
    assert krux.pages.login.settings.network == "main"


def test_printer(mocker, m5stickv):
    import krux

    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            wait_for_button=mocker.MagicMock(
                side_effect=(BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER)
            )
        ),
        display=mocker.MagicMock(to_lines=mocker.MagicMock(return_value=[""])),
    )
    login = Login(ctx)

    login.printer()

    assert ctx.input.wait_for_button.call_count == 3
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call("Baudrate\n9600"),
            mocker.call("Baudrate\n19200"),
            mocker.call("Baudrate\n9600"),
        ]
    )
    assert krux.pages.login.settings.printer.thermal.baudrate == 9600


def test_printer_on_amigo(mocker, amigo):
    import krux

    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login
    from krux.input import BUTTON_TOUCH

    # page, page_prev, enter
    index_s_e = (2, 0, 1)
    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            touch=mocker.MagicMock(
                current_index=mocker.MagicMock(side_effect=index_s_e)
            ),
            wait_for_button=mocker.MagicMock(return_value=BUTTON_TOUCH),
        )
    )
    login = Login(ctx)

    login.printer()

    assert ctx.input.wait_for_button.call_count == len(index_s_e)
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call("Baudrate\n9600"),
            mocker.call("Baudrate\n19200"),
            mocker.call("Baudrate\n9600"),
        ]
    )
    assert krux.pages.login.settings.printer.thermal.baudrate == 9600


def test_locale(mocker, m5stickv):
    import krux

    from krux.pages.login import Login
    from krux.settings import I18n
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

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
            "krux.pages.login.translations", new=mocker.MagicMock(return_value=case[0])
        )

        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(
                    side_effect=(
                        BUTTON_PAGE,
                        BUTTON_PAGE,
                        BUTTON_PAGE,
                        BUTTON_PAGE,
                        BUTTON_PAGE,
                        BUTTON_PAGE,
                        BUTTON_ENTER,
                    )
                )
            ),
            display=mocker.MagicMock(to_lines=mocker.MagicMock(return_value=[""])),
        )
        login = Login(ctx)

        login.locale()

        assert ctx.input.wait_for_button.call_count == 7
        ctx.display.draw_centered_text.assert_has_calls(
            [mocker.call("Locale\n%s" % locale) for locale in case[1]]
        )
        assert krux.pages.login.settings.i18n.locale == "en-US"


def test_locale_on_amigo(mocker, amigo):
    import krux
    from krux.pages.login import Login
    from krux.input import BUTTON_TOUCH
    from krux.settings import I18n

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
            "krux.pages.login.translations", new=mocker.MagicMock(return_value=case[0])
        )

        # page_prev, page, enter
        index_s_e = (0, 2, 1)
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                touch=mocker.MagicMock(
                    current_index=mocker.MagicMock(side_effect=index_s_e)
                ),
                wait_for_button=mocker.MagicMock(return_value=BUTTON_TOUCH),
            )
        )
        login = Login(ctx)

        login.locale()

        assert ctx.input.wait_for_button.call_count == len(index_s_e)
        # asser if locales were called already done with m5stickV
        assert krux.pages.login.settings.i18n.locale == "en-US"


def test_debug(mocker, m5stickv):
    import krux

    from krux.pages.login import Login
    from krux.logging import NONE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            wait_for_button=mocker.MagicMock(
                side_effect=(
                    BUTTON_PAGE,
                    BUTTON_PAGE,
                    BUTTON_PAGE,
                    BUTTON_PAGE,
                    BUTTON_PAGE,
                    BUTTON_ENTER,
                )
            )
        ),
        display=mocker.MagicMock(to_lines=mocker.MagicMock(return_value=[""])),
    )
    login = Login(ctx)

    login.debug()

    assert ctx.input.wait_for_button.call_count == 6
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call("Log Level\nNONE"),
            mocker.call("Log Level\nDEBUG"),
            mocker.call("Log Level\nINFO"),
            mocker.call("Log Level\nWARN"),
            mocker.call("Log Level\nERROR"),
            mocker.call("Log Level\nNONE"),
        ]
    )
    assert krux.pages.login.settings.log.level == NONE


def test_debug_on_amigo(mocker, amigo):
    import krux
    from krux.pages.login import Login
    from krux.logging import NONE
    from krux.input import BUTTON_TOUCH

    # page_prev, page, enter
    index_s_e = (0, 2, 1)
    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            touch=mocker.MagicMock(
                current_index=mocker.MagicMock(side_effect=index_s_e)
            ),
            wait_for_button=mocker.MagicMock(return_value=BUTTON_TOUCH),
        )
    )
    login = Login(ctx)

    login.debug()

    assert ctx.input.wait_for_button.call_count == len(index_s_e)
    # assert run over all debug levels already done with m5stickV
    assert krux.pages.login.settings.log.level == NONE


def test_about(mocker, m5stickv):
    import krux

    from krux.pages.login import Login
    from krux.metadata import VERSION
    from krux.input import BUTTON_ENTER

    ctx = mocker.MagicMock(
        input=mocker.MagicMock(
            wait_for_button=mocker.MagicMock(return_value=BUTTON_ENTER)
        ),
        display=mocker.MagicMock(to_lines=mocker.MagicMock(return_value=[""])),
    )
    login = Login(ctx)

    login.about()

    ctx.input.wait_for_button.assert_called_once()
    ctx.display.draw_centered_text.assert_called_with("Krux\n\n\nVersion\n" + VERSION)

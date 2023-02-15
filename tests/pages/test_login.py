from ..shared_mocks import mock_context


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
        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])

        login = Login(ctx)

        login.new_key_from_d6()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        assert ctx.wallet.key.mnemonic == case[1]


def test_new_key_from_d6_on_amigo_tft_without_touch(mocker, amigo_tft):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login, D6_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    cases = [
        (
            # Yes and proceed
            [BUTTON_ENTER] +
            # 1 press per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # Done? Yes and proceed
            [BUTTON_ENTER] +
            # Confirm roll string, Confirm SHA, Yes, Skip passphrase, Single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "diet glad hat rural panther lawsuit act drop gallery urge where fit",
        ),
        (
            # Yes and proceed
            [BUTTON_ENTER] +
            # 1 press per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # Done? No and proceed
            [BUTTON_PAGE, BUTTON_ENTER] +
            # 1 press per roll
            [BUTTON_ENTER for _ in range(D6_MIN_ROLLS)] +
            # Confirm roll string, Confirm SHA, Yes, Skip passphrase, Single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "day fog body unfold two filter bundle obey pause pattern penalty sweet shell quantum critic bridge stage patch purpose reflect flat domain post produce",
        ),
    ]
    for case in cases:
        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])

        login = Login(ctx)

        login.new_key_from_d6()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        assert ctx.wallet.key.mnemonic == case[1]

    # Leaving keypad
    esc_keypad = [
        # Enter Keypad
        BUTTON_ENTER,
        # Go to ESC position
        BUTTON_PAGE_PREV,
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
        # Leave
        BUTTON_ENTER,
    ]
    ctx = mock_context(mocker)
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=esc_keypad)

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
        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])

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
            # 12 word confirm, 24 word confirm, No passphrase, Single-key
            (BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER),
            FORMAT_NONE,
            b"[\xbd\x9dq\xa8\xecy\x90\x83\x1a\xff5\x9dBeE",
            "forum undo fragile fade shy sign arrest garment culture tube off merit",
        ),
        (
            # 12 word confirm, 24 word confirm, No passphrase, Single-key
            (BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER),
            FORMAT_NONE,
            b"\x0et\xb6A\x07\xf9L\xc0\xcc\xfa\xe6\xa1=\xcb\xec6b\x15O\xecg\xe0\xe0\t\x99\xc0x\x92Y}\x19\n",
            "attack pizza motion avocado network gather crop fresh patrol unusual wild holiday candy pony ranch winter theme error hybrid van cereal salon goddess expire",
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
    case_num = 0
    for case in cases:
        print("test_load_key_from_qr_code cases[" + str(case_num) + "]")
        case_num = case_num + 1

        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])

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
                # Confirm
                [BUTTON_ENTER]
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
            # Done?, 12 word confirm, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
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
                # Confirm
                [BUTTON_ENTER]
            )
            * 11
            +
            # Go + Confirm word
            [BUTTON_PAGE for _ in range(28)] + [BUTTON_ENTER] + [BUTTON_ENTER] +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    for case in cases:
        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])

        login = Login(ctx)

        login.load_key_from_text()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_text_on_amigo_tft_with_touch(mocker, amigo_tft):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH

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
                # Confirm
                [BUTTON_ENTER]
            )
            * 11
            + (
                # N
                [BUTTON_TOUCH]  # index 13 -> "n"
                +
                # Touch on del
                [BUTTON_TOUCH]  # index 26 -> "Del"
                +
                # Invalid Position
                [BUTTON_TOUCH]  # index 29 "empty"
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
                # Confirm word <north> -> index 0 (Yes)
                [BUTTON_TOUCH]
            )
            +
            # Done? Confirm, Words correct? Confirm, No passphrase, Single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "ability ability ability ability ability ability ability ability ability ability ability north",
            [13, 26, 29, 13, 0],
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
                # Confirm
                [BUTTON_ENTER]
            )
            * 11
            +
            # Move to Go, press Go, confirm word
            [BUTTON_PAGE_PREV] + [BUTTON_ENTER] + [BUTTON_ENTER] +
            # Done? Confirm, Words correct? Confirm, No passphrase, Single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "ability ability ability ability ability ability ability ability ability ability ability",
            [0],
        ),
    ]

    for case in cases:
        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])
        ctx.input.touch = mocker.MagicMock(
            current_index=mocker.MagicMock(side_effect=case[2])
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
                # Confirm
                + [BUTTON_ENTER]
            )
            +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
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
            # Go + Confirm
            [BUTTON_PAGE for _ in range(12)] + [BUTTON_ENTER] + [BUTTON_ENTER] +
            # Done?, 12 word confirm, Continue?, No passphrase, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    for case in cases:
        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])

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
        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])

        login = Login(ctx)

        login.load_key_from_bits()

        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_leaving_keypad(mocker, amigo_tft):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    esc_keypad = [
        BUTTON_ENTER,  # Proceed
        BUTTON_PAGE_PREV,  # Move to Go
        BUTTON_PAGE_PREV,  # Move to ESC
        BUTTON_ENTER,  # Press ESC
        BUTTON_ENTER,  # Leave
    ]
    ctx = mock_context(mocker)
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=esc_keypad)

    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(esc_keypad)


def test_passphrase_give_up(mocker, amigo_tft):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    case = (
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
            # Confirm
            [BUTTON_ENTER]
        )
        * 11
        +
        # Move to Go, press Go, confirm word
        [BUTTON_PAGE_PREV]
        + [BUTTON_ENTER]
        + [BUTTON_ENTER]
        +
        # Done? Confirm
        [BUTTON_ENTER]
        +
        # Words correct? Confirm
        [BUTTON_ENTER]
        +
        # Passphrase, confirm
        [BUTTON_ENTER]
        +
        # In passphrase keypad:
        [
            BUTTON_PAGE_PREV,  # Move to Go
            BUTTON_PAGE_PREV,  # Move to ESC
            BUTTON_ENTER,  # Press ESC
            BUTTON_ENTER,  # Leave
        ]
    )

    ctx = mock_context(mocker)
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=case)

    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(case)


def test_passphrase(mocker, amigo_tft):
    from krux.pages.login import Login
    from krux.input import (
        BUTTON_ENTER,
        BUTTON_PAGE_PREV,
        SWIPE_LEFT,
        SWIPE_RIGHT,
    )

    case = (
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
            # Confirm
            [BUTTON_ENTER]
        )
        * 11
        +
        # Move to Go, press Go, confirm word
        [BUTTON_PAGE_PREV]
        + [BUTTON_ENTER]
        + [BUTTON_ENTER]
        +
        # Done? Confirm
        [BUTTON_ENTER]
        +
        # Words correct? Confirm
        [BUTTON_ENTER]
        +
        # Passphrase, confirm
        [BUTTON_ENTER]
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

    ctx = mock_context(mocker)
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=case)

    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(case)


# import unittest
# tc = unittest.TestCase()
# tc.assertEqual(Settings().i18n.locale, 'b')


def test_settings(mocker, m5stickv):
    import krux

    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.settings import Settings, CategorySetting, NumberSetting
    from krux.translations import translation_table

    tlist = list(translation_table)
    index_en = tlist.index("en-US")
    index_next = (index_en + 1) % (len(tlist))
    text_en = translation_table[tlist[index_en]][1177338798] + "\n" + tlist[index_en]
    text_next = (
        translation_table[tlist[index_next]][1177338798] + "\n" + tlist[index_next]
    )

    cases = [
        (
            (
                # Bitcoin
                BUTTON_ENTER,
                # Change network
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Network\nmain"),
                mocker.call("Network\ntest"),
            ],
            lambda: Settings().bitcoin.network == "test",
            CategorySetting,
        ),
        (
            (
                # Printer
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Thermal
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Change Baudrate
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Back to Thermal
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                # Back to Printer
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Baudrate\n9600"),
                mocker.call("Baudrate\n19200"),
            ],
            lambda: Settings().printer.thermal.adafruit.baudrate == 19200,
            CategorySetting,
        ),
        (
            (
                # Language
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Change Locale
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call(text_en),
                mocker.call(text_next),
            ],
            lambda: Settings().i18n.locale == tlist[index_next],
            CategorySetting,
        ),
        (
            (
                # Logging
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Change log level
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Log Level\nNONE"),
                mocker.call("Log Level\nERROR"),
                mocker.call("Log Level\nWARN"),
                mocker.call("Log Level\nINFO"),
                mocker.call("Log Level\nDEBUG"),
            ],
            lambda: Settings().logging.level == "DEBUG",
            CategorySetting,
        ),
        (
            (
                # Printer
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Thermal
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Paper Width
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Change width
                # Remove digit
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                # Add 9
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                # Go
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Back to Thermal
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Back to Printer
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Paper Width", 10),
            ],
            lambda: Settings().printer.thermal.adafruit.paper_width == 389,
            NumberSetting,
        ),
    ]
    case_num = 0
    for case in cases:
        print("test_settings cases[" + str(case_num) + "]")
        case_num = case_num + 1

        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(side_effect=case[0])

        login = Login(ctx)

        Settings().i18n.locale = "en-US"
        login.settings()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if case[3] == NumberSetting:
            ctx.display.draw_hcentered_text.assert_has_calls(case[1])
        else:
            ctx.display.draw_centered_text.assert_has_calls(case[1])

        assert case[2]()


def test_settings_on_amigo_tft(mocker, amigo_tft):
    import krux
    from krux.pages.login import Login
    from krux.input import BUTTON_TOUCH
    from krux.settings import Settings, CategorySetting, NumberSetting

    from krux.translations import translation_table

    tlist = list(translation_table)
    index_en = tlist.index("en-US")
    index_next = (index_en + 1) % (len(tlist))
    text_en = translation_table[tlist[index_en]][1177338798] + "\n" + tlist[index_en]
    text_next = (
        translation_table[tlist[index_next]][1177338798] + "\n" + tlist[index_next]
    )

    PREV_INDEX = 0
    GO_INDEX = 1
    NEXT_INDEX = 2

    cases = [
        (
            (
                # Bitcoin
                0,
                # Change network
                NEXT_INDEX,
                GO_INDEX,
                # Leave Settings
                4,
            ),
            [
                mocker.call("Network\nmain"),
                mocker.call("Network\ntest"),
            ],
            lambda: Settings().bitcoin.network == "test",
            CategorySetting,
        ),
        (
            (
                # Printer
                3,
                # Thermal
                1,
                # Change Baudrate
                0,
                NEXT_INDEX,
                GO_INDEX,
                # Back to Thermal
                7,
                # Back to Printer
                3,
                # Leave Settings
                4,
            ),
            [
                mocker.call("Baudrate\n9600"),
                mocker.call("Baudrate\n19200"),
            ],
            lambda: Settings().printer.thermal.adafruit.baudrate == 19200,
            CategorySetting,
        ),
        (
            (
                # Language
                1,
                # Change Locale
                NEXT_INDEX,
                GO_INDEX,
            ),
            [
                mocker.call(text_en),
                mocker.call(text_next),
            ],
            lambda: Settings().i18n.locale == tlist[index_next],
            CategorySetting,
        ),
        (
            (
                # Logging
                2,
                # Change log level
                NEXT_INDEX,
                NEXT_INDEX,
                NEXT_INDEX,
                NEXT_INDEX,
                GO_INDEX,
                # Leave Settings
                4,
            ),
            [
                mocker.call("Log Level\nNONE"),
                mocker.call("Log Level\nERROR"),
                mocker.call("Log Level\nWARN"),
                mocker.call("Log Level\nINFO"),
                mocker.call("Log Level\nDEBUG"),
            ],
            lambda: Settings().logging.level == "DEBUG",
            CategorySetting,
        ),
    ]
    case_num = 0
    for case in cases:
        print("test_settings_on_amigo_tft cases[" + str(case_num) + "]")
        case_num = case_num + 1

        ctx = mock_context(mocker)
        ctx.input.wait_for_button = mocker.MagicMock(return_value=BUTTON_TOUCH)
        ctx.input.touch = mocker.MagicMock(
            current_index=mocker.MagicMock(side_effect=case[0])
        )

        mocker.patch.object(ctx.input.touch, "x_regions", (0, 100, 200, 300))
        mocker.patch.object(ctx.input.touch, "y_regions", (100, 200))

        login = Login(ctx)

        Settings().i18n.locale = "en-US"
        login.settings()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if case[3] == NumberSetting:
            ctx.display.draw_hcentered_text.assert_has_calls(case[1])
        else:
            ctx.display.draw_centered_text.assert_has_calls(case[1])

        assert case[2]()


def test_about(mocker, m5stickv):
    import krux

    from krux.pages.login import Login
    from krux.metadata import VERSION
    from krux.input import BUTTON_ENTER

    ctx = mock_context(mocker)
    ctx.input.wait_for_button = mocker.MagicMock(return_value=BUTTON_ENTER)
    ctx.input.wait_for_button = mocker.MagicMock(return_value=BUTTON_ENTER)

    login = Login(ctx)

    login.about()

    ctx.input.wait_for_button.assert_called_once()
    ctx.display.draw_centered_text.assert_called_with("Krux\n\n\nVersion\n" + VERSION)

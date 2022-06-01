from ..shared_mocks import *
from krux.settings import I18n
from krux.input import BUTTON_ENTER, BUTTON_PAGE
from krux.qr import FORMAT_UR, FORMAT_NONE
from ur.ur import UR
import binascii


def test_new_key_from_d6(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login, D6_MIN_ROLLS

    cases = [
        (
            # 1 press to proceed
            [BUTTON_ENTER] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(3 * D6_MIN_ROLLS)] +
            # 1 press to be done at min rolls
            [BUTTON_ENTER] +
            # 1 press to confirm SHA, 1 press to continue loading key, 1 press to select single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "hire injury false situate rare proof supply attend pause leave bitter enter",
        ),
        (
            # 1 press to proceed
            [BUTTON_ENTER] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(3 * D6_MIN_ROLLS)] +
            # 1 press to continue rolling to max rolls
            [BUTTON_PAGE] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(3 * D6_MIN_ROLLS)] +
            # 1 press to confirm SHA, 1 press to see last 12 words, 1 press to continue loading key, 1 press to select single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "owner muscle pioneer easily february chuckle strong fold lake lemon parade defy excuse where gap seek narrow cost convince trim great funny admit draft",
        ),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case[0])),
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)
        mocker.patch.object(ctx.input, "has_touch", False)

        login.new_key_from_d6()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        assert ctx.wallet.key.mnemonic == case[1]


def test_new_key_from_d20(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login, D20_MIN_ROLLS

    cases = [
        (
            # 1 press to proceed
            [BUTTON_ENTER] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(3 * D20_MIN_ROLLS)] +
            # 1 press to be done at min rolls
            [BUTTON_ENTER] +
            # 1 press to confirm SHA, 1 press to continue loading key, 1 press to select single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "erupt remain ride bleak year cabin orange sure ghost gospel husband oppose",
        ),
        (
            # 1 press to proceed
            [BUTTON_ENTER] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(3 * D20_MIN_ROLLS)] +
            # 1 press to continue rolling to max rolls
            [BUTTON_PAGE] +
            # 3 presses per roll
            [BUTTON_ENTER for _ in range(3 * D20_MIN_ROLLS)] +
            # 1 press to confirm SHA, 1 press to see last 12 words, 1 press to continue loading key, 1 press to select single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "fun island vivid slide cable pyramid device tuition only essence thought gain silk jealous eternal anger response virus couple faculty ozone test key vocal",
        ),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case[0])),
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)

        login.new_key_from_d20()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_qr_code(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login

    cases = [
        (
            FORMAT_NONE,
            "olympic term tissue route sense program under choose bean emerge velvet absurd",
            "olympic term tissue route sense program under choose bean emerge velvet absurd",
        ),
        (
            FORMAT_NONE,
            "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major",
            "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major",
        ),
        (
            FORMAT_NONE,
            "123417871814150815661375189403220156058119360008",
            "olympic term tissue route sense program under choose bean emerge velvet absurd",
        ),
        (
            FORMAT_NONE,
            "023301391610171019391278098413310856127602420628160203911717091708861236056502660800183118111075",
            "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major",
        ),
        (
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
        ctx = mock.MagicMock(
            input=mock.MagicMock(
                wait_for_button=mock.MagicMock(return_value=BUTTON_ENTER)
            ),
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)
        mocker.patch.object(
            login, "capture_qr_code", mock.MagicMock(return_value=(case[1], case[0]))
        )

        login.load_key_from_qr_code()

        assert ctx.wallet.key.mnemonic == case[2]


def test_load_key_from_text(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login

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
            # Done?, 12 word confirm, Continue?, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
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
            # Done?, 12 word confirm, Continue?, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case[0])),
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)

        login.load_key_from_text()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_digits(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login

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
            # Done?, 12 word confirm, Continue?, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
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
            # Done?, 12 word confirm, Continue?, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case[0])),
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)

        login.load_key_from_digits()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_bits(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mock.MagicMock())
    from krux.pages.login import Login

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
            # Done?, 12 word confirm, Continue?, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
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
            # Done?, 12 word confirm, Continue?, Single-key
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case[0])),
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)

        login.load_key_from_bits()

        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_network(mocker):
    import krux

    from krux.pages.login import Login

    ctx = mock.MagicMock(
        input=mock.MagicMock(
            wait_for_button=mock.MagicMock(
                side_effect=(BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER)
            )
        ),
        display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
    )
    login = Login(ctx)

    login.network()

    assert ctx.input.wait_for_button.call_count == 3
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

    ctx = mock.MagicMock(
        input=mock.MagicMock(
            wait_for_button=mock.MagicMock(
                side_effect=(BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER)
            )
        ),
        display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
    )
    login = Login(ctx)

    login.printer()

    assert ctx.input.wait_for_button.call_count == 3
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

        ctx = mock.MagicMock(
            input=mock.MagicMock(
                wait_for_button=mock.MagicMock(
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
            display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
        )
        login = Login(ctx)

        login.locale()

        assert ctx.input.wait_for_button.call_count == 7
        ctx.display.draw_centered_text.assert_has_calls(
            [mock.call("Locale\n%s" % locale) for locale in case[1]]
        )
        assert krux.pages.login.settings.i18n.locale == "en-US"


def test_debug(mocker):
    import krux

    from krux.pages.login import Login
    from krux.logging import NONE

    ctx = mock.MagicMock(
        input=mock.MagicMock(
            wait_for_button=mock.MagicMock(
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
        display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
    )
    login = Login(ctx)

    login.debug()

    assert ctx.input.wait_for_button.call_count == 6
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mock.call("Log Level\nNONE"),
            mock.call("Log Level\nDEBUG"),
            mock.call("Log Level\nINFO"),
            mock.call("Log Level\nWARN"),
            mock.call("Log Level\nERROR"),
            mock.call("Log Level\nNONE"),
        ]
    )
    assert krux.pages.login.settings.log.level == NONE


def test_about(mocker):
    import krux

    from krux.pages.login import Login
    from krux.metadata import VERSION

    ctx = mock.MagicMock(
        input=mock.MagicMock(wait_for_button=mock.MagicMock(return_value=BUTTON_ENTER)),
        display=mock.MagicMock(to_lines=mock.MagicMock(return_value=[""])),
    )
    login = Login(ctx)

    login.about()

    ctx.input.wait_for_button.assert_called_once()
    ctx.display.draw_centered_text.assert_called_with("Krux\n\n\nVersion\n" + VERSION)

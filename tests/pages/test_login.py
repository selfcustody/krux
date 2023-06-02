import pytest
from ..shared_mocks import mock_context


@pytest.fixture
def mocker_printer(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())


def create_ctx(mocker, btn_seq, touch_seq=None):
    """Helper to create mocked context obj"""
    ctx = mock_context(mocker)
    ctx.power_manager.battery_charge_remaining.return_value = 1
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=btn_seq)

    if touch_seq:
        ctx.input.touch = mocker.MagicMock(
            current_index=mocker.MagicMock(side_effect=touch_seq)
        )
    return ctx


################### new words from dice tests


def test_new_12w_from_d6(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login, D6_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D6_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # 1 press to confirm roll string,
            BUTTON_ENTER,  # 1 press to confirm SHA
            BUTTON_ENTER,  # 1 press to continue loading key
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # 1 press to select single-key
        ]
    )
    MNEMONIC = "diet glad hat rural panther lawsuit act drop gallery urge where fit"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_d6()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_new_24w_from_d6(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login, D6_24W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press change to 24 words and 1 press to proceed
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D6_24W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # 1 press to confirm roll string,
            BUTTON_ENTER,  # 1 press to confirm SHA
            BUTTON_ENTER,  # 1 press to see the next 12 words (24 total)
            BUTTON_ENTER,  # 1 press to continue loading key
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # 1 press to select single-key
        ]
    )
    MNEMONIC = "wheel erase puppy pistol chapter accuse carpet drop quote final attend near scrap satisfy limit style crunch person south inspire lunch meadow enact tattoo"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_d6()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_new_12w_from_d6_on_amigo_device(amigo_tft, mocker, mocker_printer):
    from krux.pages.login import Login, D6_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D6_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # 1 press to confirm roll string,
            BUTTON_ENTER,  # 1 press to confirm SHA
            BUTTON_ENTER,  # 1 press to continue loading key
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # 1 press to select single-key
        ]
    )
    MNEMONIC = "diet glad hat rural panther lawsuit act drop gallery urge where fit"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_d6()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_new_24w_from_d6_on_amigo_device(amigo_tft, mocker, mocker_printer):
    from krux.pages.login import Login, D6_24W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press change to 24 words and 1 press to proceed
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D6_24W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # 1 press to confirm roll string,
            BUTTON_ENTER,  # 1 press to confirm SHA
            BUTTON_ENTER,  # 1 press to continue loading key
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # 1 press to select single-key
        ]
    )
    MNEMONIC = "wheel erase puppy pistol chapter accuse carpet drop quote final attend near scrap satisfy limit style crunch person south inspire lunch meadow enact tattoo"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_d6()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_cancel_new_12w_from_d6_on_amigo_device(amigo_tft, mocker, mocker_printer):
    "Will test the Esc button on the roll screen"
    from krux.pages.login import Login, D6_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 2 press prev and 1 press on btn Esc
        [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # 1 press to proceed confirm exit msg
        [BUTTON_ENTER]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_d6()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_new_12w_from_d20(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login, D20_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D20_12W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # 1 press to confirm roll string,
            BUTTON_ENTER,  # 1 press to confirm SHA
            BUTTON_ENTER,  # 1 press to continue loading key
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # 1 press to select single-key
        ]
    )
    MNEMONIC = (
        "erupt remain ride bleak year cabin orange sure ghost gospel husband oppose"
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_d20()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_new_24w_from_d20(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login, D20_24W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press change to 24 words and 1 press to proceed
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D20_24W_MIN_ROLLS)]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # 1 press to confirm roll string,
            BUTTON_ENTER,  # 1 press to confirm SHA
            BUTTON_ENTER,  # 1 press to see the next 12 words (24 total)
            BUTTON_ENTER,  # 1 press to continue loading key
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # 1 press to select single-key
        ]
    )
    MNEMONIC = "fun island vivid slide cable pyramid device tuition only essence thought gain silk jealous eternal anger response virus couple faculty ozone test key vocal"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_d20()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_cancel_new_12w_from_d20(m5stickv, mocker, mocker_printer):
    "Will test the Deletion button and the minimum roll on the roll screen"
    from krux.pages.login import Login, D20_12W_MIN_ROLLS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # 1 presses per roll
        [BUTTON_ENTER for _ in range(D20_12W_MIN_ROLLS)]
        +
        # 3 press prev and 1 press on btn < (delete last roll)
        [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # 1 press prev and 1 press on btn Go
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # 1 press for msg not enough rolls!
        [BUTTON_ENTER]
        +
        # 2 press prev and 1 press on btn Esc
        [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # 1 press to proceed confirm exit msg
        [BUTTON_ENTER]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_d20()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


########## load words from qrcode tests


def test_load_12w_camera_qrcode_words(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    BTN_SEQUENCE = (
        # 1 press to proceed with the 12 words
        [BUTTON_ENTER]
        +
        # 1 press to move to Scan passphrase
        [BUTTON_PAGE]
        +
        # 1 press to move to No passphrase
        [BUTTON_PAGE]
        +
        # 1 press to skip passphrase
        [BUTTON_ENTER]
        +
        # 1 press to confirm fingerprint
        [BUTTON_ENTER]
        +
        # 1 press to select single-key
        [BUTTON_ENTER]
    )
    QR_FORMAT = FORMAT_NONE
    MNEMONIC = (
        "olympic term tissue route sense program under choose bean emerge velvet absurd"
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login, "capture_qr_code", mocker.MagicMock(return_value=(MNEMONIC, QR_FORMAT))
    )
    login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_12w_camera_qrcode_numbers(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    BTN_SEQUENCE = (
        # 1 press to proceed with the 12 words
        [BUTTON_ENTER]
        +
        # 1 press to move to Scan passphrase
        [BUTTON_PAGE]
        +
        # 1 press to move to No passphrase
        [BUTTON_PAGE]
        +
        # 1 press to skip passphrase
        [BUTTON_ENTER]
        +
        # 1 press to confirm fingerprint
        [BUTTON_ENTER]
        +
        # 1 press to select single-key
        [BUTTON_ENTER]
    )
    QR_FORMAT = FORMAT_NONE
    MNEMONIC = (
        "olympic term tissue route sense program under choose bean emerge velvet absurd"
    )
    ENCODED_MNEMONIC = "123417871814150815661375189403220156058119360008"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login,
        "capture_qr_code",
        mocker.MagicMock(return_value=(ENCODED_MNEMONIC, QR_FORMAT)),
    )
    login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_12w_camera_qrcode_binary(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    BTN_SEQUENCE = (
        # 1 press to proceed with the 12 words
        [BUTTON_ENTER]
        +
        # 1 press to move to Scan passphrase
        [BUTTON_PAGE]
        +
        # 1 press to move to No passphrase
        [BUTTON_PAGE]
        +
        # 1 press to skip passphrase
        [BUTTON_ENTER]
        +
        # 1 press to confirm fingerprint
        [BUTTON_ENTER]
        +
        # 1 press to select single-key
        [BUTTON_ENTER]
    )
    QR_FORMAT = FORMAT_NONE
    MNEMONIC = "forum undo fragile fade shy sign arrest garment culture tube off merit"
    BINARY_MNEMONIC = b"[\xbd\x9dq\xa8\xecy\x90\x83\x1a\xff5\x9dBeE"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login,
        "capture_qr_code",
        mocker.MagicMock(return_value=(BINARY_MNEMONIC, QR_FORMAT)),
    )
    login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_24w_camera_qrcode_words(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    BTN_SEQUENCE = (
        # 1 press to proceed with the 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed with the next 12 words
        [BUTTON_ENTER]
        +
        # 1 press to move to Scan passphrase
        [BUTTON_PAGE]
        +
        # 1 press to move to No passphrase
        [BUTTON_PAGE]
        +
        # 1 press to skip passphrase
        [BUTTON_ENTER]
        +
        # 1 press to confirm fingerprint
        [BUTTON_ENTER]
        +
        # 1 press to select single-key
        [BUTTON_ENTER]
    )
    QR_FORMAT = FORMAT_NONE
    MNEMONIC = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login, "capture_qr_code", mocker.MagicMock(return_value=(MNEMONIC, QR_FORMAT))
    )
    login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_24w_camera_qrcode_numbers(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    BTN_SEQUENCE = (
        # 1 press to proceed with the 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed with the next 12 words
        [BUTTON_ENTER]
        +
        # 1 press to move to Scan passphrase
        [BUTTON_PAGE]
        +
        # 1 press to move to No passphrase
        [BUTTON_PAGE]
        +
        # 1 press to skip passphrase
        [BUTTON_ENTER]
        +
        # 1 press to confirm fingerprint
        [BUTTON_ENTER]
        +
        # 1 press to select single-key
        [BUTTON_ENTER]
    )
    QR_FORMAT = FORMAT_NONE
    MNEMONIC = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
    ENCODED_MNEMONIC = "023301391610171019391278098413310856127602420628160203911717091708861236056502660800183118111075"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login,
        "capture_qr_code",
        mocker.MagicMock(return_value=(ENCODED_MNEMONIC, QR_FORMAT)),
    )
    login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_24w_camera_qrcode_binary(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    BTN_SEQUENCE = (
        # 1 press to proceed with the 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed with the next 12 words
        [BUTTON_ENTER]
        +
        # 1 press to move to Scan passphrase
        [BUTTON_PAGE]
        +
        # 1 press to move to No passphrase
        [BUTTON_PAGE]
        +
        # 1 press to skip passphrase
        [BUTTON_ENTER]
        +
        # 1 press to confirm fingerprint
        [BUTTON_ENTER]
        +
        # 1 press to select single-key
        [BUTTON_ENTER]
    )
    QR_FORMAT = FORMAT_NONE
    MNEMONIC = "attack pizza motion avocado network gather crop fresh patrol unusual wild holiday candy pony ranch winter theme error hybrid van cereal salon goddess expire"
    BINARY_MNEMONIC = b"\x0et\xb6A\x07\xf9L\xc0\xcc\xfa\xe6\xa1=\xcb\xec6b\x15O\xecg\xe0\xe0\t\x99\xc0x\x92Y}\x19\n"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login,
        "capture_qr_code",
        mocker.MagicMock(return_value=(BINARY_MNEMONIC, QR_FORMAT)),
    )
    login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_12w_camera_qrcode_format_ur(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_UR
    import binascii
    from ur.ur import UR

    BTN_SEQUENCE = (
        # 1 press to proceed with the 12 words
        [BUTTON_ENTER]
        +
        # 1 press to move to Scan passphrase
        [BUTTON_PAGE]
        +
        # 1 press to move to No passphrase
        [BUTTON_PAGE]
        +
        # 1 press to skip passphrase
        [BUTTON_ENTER]
        +
        # 1 press to confirm fingerprint
        [BUTTON_ENTER]
        +
        # 1 press to select single-key
        [BUTTON_ENTER]
    )
    QR_FORMAT = FORMAT_UR
    UR_DATA = UR(
        "crypto-bip39",
        bytearray(
            binascii.unhexlify(
                "A2018C66736869656C646567726F75706565726F6465656177616B65646C6F636B6773617573616765646361736865676C6172656477617665646372657765666C616D6565676C6F76650262656E"
            )
        ),
    )
    MNEMONIC = "shield group erode awake lock sausage cash glare wave crew flame glove"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login, "capture_qr_code", mocker.MagicMock(return_value=(UR_DATA, QR_FORMAT))
    )
    login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == MNEMONIC


############### load words from text tests


def test_load_key_from_text(m5stickv, mocker, mocker_printer):
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
            + [
                BUTTON_ENTER,  # Done?
                BUTTON_ENTER,  # 12 word confirm
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,  # Single-key
            ],
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
            [BUTTON_PAGE for _ in range(28)]
            + [BUTTON_ENTER]
            + [BUTTON_ENTER]
            + [
                BUTTON_ENTER,  # Done?
                BUTTON_ENTER,  # 12 word confirm
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,  # Single-key
            ],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    num = 0
    for case in cases:
        print(num)
        num += 1
        ctx = create_ctx(mocker, case[0])
        login = Login(ctx)

        login.load_key_from_text()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_load_key_from_text_on_amigo_tft_with_touch(amigo_tft, mocker, mocker_printer):
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
                + [BUTTON_TOUCH]  # index 14 -> "o"
                + [BUTTON_TOUCH]  # index 17 -> "r"
                +
                # Touch on del
                [BUTTON_TOUCH]  # index 27 -> "Del"
                +
                # Invalid Position
                [BUTTON_TOUCH]  # index 26 "empty"
                + [BUTTON_TOUCH]  # index 17 -> "r"
                + [BUTTON_TOUCH]  # index 19 -> "t"
                +
                # Confirm word <north> -> index 0 (Yes)
                [BUTTON_TOUCH]
            )
            +
            # Done? Confirm, Words correct? Confirm, No passphrase, Single-key
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,
            ],
            "ability ability ability ability ability ability ability ability ability ability ability north",
            [13, 14, 17, 27, 26, 17, 19, 0],
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
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,
            ],
            "ability ability ability ability ability ability ability ability ability ability ability",
            [0],
        ),
    ]

    num = 0
    for case in cases:
        print(num)
        num = num + 1

        ctx = create_ctx(mocker, case[0], case[2])

        login = Login(ctx)
        login.load_key_from_text()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


############## load words from digits tests


def test_load_key_from_digits(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    cases = [
        (
            [BUTTON_ENTER]  # 1 press confirm msg
            + (
                # 1 press change to number "2" and 1 press to select
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # 10 press to place on btn Go
                [BUTTON_PAGE for _ in range(10)]
                + [
                    BUTTON_ENTER,
                    BUTTON_ENTER,
                ]  # 1 press to select and 1 press to confirm
            )
            * 11  # repeat selection of word=2 (ability) eleven times
            + (
                # 1
                [BUTTON_ENTER]
                +
                # 2
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # 0
                [BUTTON_PAGE for _ in range(11)]
                + [BUTTON_ENTER]
                +
                # 3
                [
                    BUTTON_PAGE,
                    BUTTON_PAGE,
                    BUTTON_PAGE,
                    BUTTON_ENTER,
                ]  # twelve word=1203 (north)
                # Confirm
                + [BUTTON_ENTER]
            )
            + [
                BUTTON_ENTER,  # Done?
                BUTTON_ENTER,  # 12 word confirm
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,  # Single-key
            ],
            "ability ability ability ability ability ability ability ability ability ability ability north",
        ),
        (
            [BUTTON_ENTER]
            + (
                # 2
                [BUTTON_PAGE, BUTTON_ENTER]
                +
                # Go + Confirm
                [BUTTON_PAGE for _ in range(10)]
                + [BUTTON_ENTER, BUTTON_ENTER]
            )
            * 11
            +
            # Go + Confirm
            [BUTTON_PAGE for _ in range(11)]
            + [BUTTON_ENTER]
            + [BUTTON_ENTER]
            + [
                BUTTON_ENTER,  # Done?
                BUTTON_ENTER,  # 12 word confirm
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,  # Single-key
            ],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    num = 0
    for case in cases:
        print(num)
        num = num + 1
        ctx = create_ctx(mocker, case[0])
        login = Login(ctx)

        login.load_key_from_digits()

        assert ctx.input.wait_for_button.call_count == len(case[0])
        if len(case[1].split()) == 11:
            assert ctx.wallet.key.mnemonic.startswith(case[1])
        else:
            assert ctx.wallet.key.mnemonic == case[1]


def test_load_12w_from_hexadecimal(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # 1 press confirm msg
        + (
            # 4 press change to number "F"
            [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_PAGE_PREV]
            + [BUTTON_ENTER]  # 1 press to select F
            + [BUTTON_ENTER]  # 1 press to select F again
            + [BUTTON_ENTER]  # 1 press to confirm word=FF(255 decimal) cabin
        )
        * 11  # repeat selection of word=FF(255, cabin) eleven times
        + (
            [BUTTON_ENTER]  # 1 press to number 1
            + [BUTTON_ENTER]  # 1 press to number 1
            + [BUTTON_PAGE for _ in range(4)]  # 4 press change to number 5
            + [BUTTON_ENTER]  # 1 press to select 5
            + [BUTTON_ENTER]  # Confirm word=115(277 decimal) card
        )
        + [
            BUTTON_ENTER,  # Done?
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-key
        ]
    )
    MNEMONIC = "cabin cabin cabin cabin cabin cabin cabin cabin cabin cabin cabin card"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_hexadecimal()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_possible_letters_from_hexadecimal(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # 1 press confirm msg
        + (
            # 7 press change to number "8"
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
            ]
            + [BUTTON_ENTER]  # 1 press to select 8
            +
            # 8 press change to number "0"
            [
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
            ]
            + [BUTTON_ENTER]  # 1 press to select 0
            +
            # 3 press change to btn "Go" (all other numbers are disabled)
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
            ]
            + [BUTTON_ENTER]  # 1 press to select Go
            + [BUTTON_ENTER]  # 1 press to confirm word=80(128 decimal) avocado
        )
        * 11  # repeat selection of word=80(128, avocado) eleven times
        + (
            [BUTTON_PAGE_PREV]  # 1 press change to btn Go
            + [BUTTON_ENTER]  # 1 press to select Go
            + [BUTTON_ENTER]  # Confirm last random word
        )
        + [
            BUTTON_ENTER,  # Done?
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-key
        ]
    )
    MNEMONIC = "avocado avocado avocado avocado avocado avocado avocado avocado avocado avocado avocado "

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_hexadecimal()

    assert ctx.wallet.key.mnemonic.startswith(MNEMONIC)


def test_load_12w_from_octal(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # 1 press confirm msg
        + (
            # 4 press change to number "7"
            [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_PAGE_PREV]
            + [BUTTON_ENTER]  # 1 press to select 7
            + [BUTTON_ENTER]  # 1 press to select 7 again
            + [BUTTON_ENTER]  # 1 press to select 7 again
            + [BUTTON_ENTER]  # 1 press to confirm word=777(511 decimal) divert
        )
        * 11  # repeat selection of word=777(511, divert) eleven times
        + (
            [BUTTON_ENTER]  # 1 press to number 1
            + [BUTTON_PAGE for _ in range(4)]  # 4 press change to number 5
            + [BUTTON_ENTER]  # 1 press to number 5
            + [BUTTON_PAGE_PREV for _ in range(3)]  # 3 press change to number 2
            + [BUTTON_ENTER]  # 1 press to select 2
            + [BUTTON_PAGE for _ in range(2)]  # 2 press change to number 4
            + [BUTTON_ENTER]  # 1 press to select 4
            + [BUTTON_ENTER]  # Confirm word=1524(852 decimal) heavy
        )
        + [
            BUTTON_ENTER,  # Done?
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-key
        ]
    )
    MNEMONIC = "divert divert divert divert divert divert divert divert divert divert divert heavy"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_octal()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_possible_letters_from_octal(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # 1 press confirm msg
        + (
            # 3 press change to number "4"
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
            ]
            + [BUTTON_ENTER]  # 1 press to select 4
            +
            # 4 press change to number "0"
            [
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
            ]
            + [BUTTON_ENTER]  # 1 press to select 0
            + [BUTTON_ENTER]  # 1 press to select 0
            +
            # 3 press change to btn "Go" (all other numbers are disabled)
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
            ]
            + [BUTTON_ENTER]  # 1 press to select Go
            + [BUTTON_ENTER]  # 1 press to confirm word=400(256 decimal) cable
        )
        * 11  # repeat selection of word=400(256, cable) eleven times
        + (
            [BUTTON_PAGE_PREV]  # 1 press change to btn Go
            + [BUTTON_ENTER]  # 1 press to select Go
            + [BUTTON_ENTER]  # Confirm last random word
        )
        + [
            BUTTON_ENTER,  # Done?
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-key
        ]
    )
    MNEMONIC = "cable cable cable cable cable cable cable cable cable cable cable "

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_octal()

    assert ctx.wallet.key.mnemonic.startswith(MNEMONIC)


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


def test_no_passphrase_on_amigo(mocker, amigo_tft):
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
        # No BIP39 Passphrase menu
        [BUTTON_PAGE_PREV, BUTTON_ENTER]
        +
        # Accept fingerprint and derivation
        [
            BUTTON_ENTER,  # Continue?
            BUTTON_ENTER,  # Single-key
        ]
    )

    ctx = create_ctx(mocker, case)
    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(case)


def test_passphrase(amigo_tft, mocker, mocker_printer):
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
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single key
        ]
    )

    ctx = create_ctx(mocker, case)
    login = Login(ctx)
    login.load_key_from_text()
    assert ctx.input.wait_for_button.call_count == len(case)


############### load words from tiny seed (bits)


def test_load_12w_from_tiny_seed(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # 1 press 12w
        + [BUTTON_PAGE_PREV]  # 1 press to change to "Go"
        + [BUTTON_ENTER]  # 1 press to select Go
        + [
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-key
        ]
    )
    MNEMONIC = "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo daring"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_tiny_seed()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_24w_from_tiny_seed(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # 1 press to change to 24w
        + [BUTTON_ENTER]  # 1 press select 24w
        + [BUTTON_PAGE]  # 1 press to change to bit 1024
        + [BUTTON_ENTER]  # 1 press to select bit 1024
        + [BUTTON_PAGE_PREV for _ in range(2)]  # 2 press to change to "Go"
        + [BUTTON_ENTER]  # 1 press to select Go screen 12w
        + [BUTTON_ENTER]  # 1 press to select Go screen 24w
        + [
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_ENTER,  # 24 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-key
        ]
    )
    MNEMONIC = "lend zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo blossom"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_tiny_seed()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_12w_from_1248(m5stickv, mocker, mocker_printer):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        (
            [BUTTON_ENTER]  # 1 press select first column num 1
            + [BUTTON_PAGE_PREV]  # 1 press to change to "Go"
            + [BUTTON_ENTER]  # 1 press to select Go
            + [BUTTON_ENTER]  # 1 press to confirm word 1000 language
        )
        * 11  # do this eleven times
        + [BUTTON_PAGE for _ in range(2)]  # 2 press to change second column num 1
        + [BUTTON_ENTER]  # 1 press to select second column num 1
        + [BUTTON_PAGE for _ in range(5)]  # 5 press to change third column num 2
        + [BUTTON_ENTER]  # 1 press to select third column num 2
        + [BUTTON_PAGE for _ in range(8)]  # 8 press to change to "Go"
        + [BUTTON_ENTER]  # 1 press to select Go
        + [BUTTON_ENTER]  # 1 press to confirm word 120 auction
        + [
            BUTTON_ENTER,  # Done?
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-key
        ]
    )
    MNEMONIC = "language language language language language language language language language language language auction"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_1248()

    assert ctx.wallet.key.mnemonic == MNEMONIC


# import unittest
# tc = unittest.TestCase()
# tc.assertEqual(Settings().i18n.locale, 'b')


def test_settings_m5stickv(m5stickv, mocker, mocker_printer):
    import krux

    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.krux_settings import Settings, CategorySetting, NumberSetting
    from krux.translations import translation_table
    from krux.themes import WHITE, RED, GREEN, ORANGE, MAGENTA

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
                mocker.call("Network\nmain", ORANGE),
                mocker.call("Network\ntest", GREEN),
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
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Baudrate\n9600", WHITE),
                mocker.call("Baudrate\n19200", WHITE),
            ],
            lambda: Settings().printer.thermal.adafruit.baudrate == 19200,
            CategorySetting,
        ),
        (
            (
                # Language
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Change Locale
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call(text_en, WHITE),
                mocker.call(text_next, WHITE),
            ],
            lambda: Settings().i18n.locale == tlist[index_next],
            CategorySetting,
        ),
        (
            (
                # Logging
                BUTTON_PAGE,
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
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
            ),
            [
                mocker.call("Log Level\nNONE", WHITE),
                mocker.call("Log Level\nERROR", RED),
                mocker.call("Log Level\nWARN", ORANGE),
                mocker.call("Log Level\nINFO", GREEN),
                mocker.call("Log Level\nDEBUG", MAGENTA),
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
                BUTTON_ENTER,
                # Go
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,
                # Back to Thermal
                BUTTON_PAGE,
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

        ctx = create_ctx(mocker, case[0])
        login = Login(ctx)

        Settings().i18n.locale = "en-US"
        login.settings()

        assert ctx.input.wait_for_button.call_count == len(case[0])

        assert case[2]()


def test_settings_on_amigo_tft(amigo_tft, mocker, mocker_printer):

    import krux
    from krux.pages.login import Login
    from krux.input import BUTTON_TOUCH
    from krux.krux_settings import Settings, CategorySetting, NumberSetting
    from krux.translations import translation_table
    from krux.themes import WHITE, RED, GREEN, ORANGE, MAGENTA

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

    LOCALE_INDEX = 2
    LOGGING_INDEX = 3
    PRINTER_INDEX = 5
    LEAVE_INDEX = 8

    cases = [
        (
            (
                # Bitcoin
                0,
                # Change network
                NEXT_INDEX,
                GO_INDEX,
                # Leave Settings
                LEAVE_INDEX,
            ),
            [
                mocker.call("Network\nmain", ORANGE),
                mocker.call("Network\ntest", GREEN),
            ],
            lambda: Settings().bitcoin.network == "test",
            CategorySetting,
        ),
        (
            (
                # Printer
                PRINTER_INDEX,
                # Thermal
                1,
                # Change Baudrate
                0,
                NEXT_INDEX,
                GO_INDEX,
                # Back to Thermal
                8,
                # Back to Printer
                3,
                # Leave Settings
                LEAVE_INDEX,
            ),
            [
                mocker.call("Baudrate\n9600", WHITE),
                mocker.call("Baudrate\n19200", WHITE),
            ],
            lambda: Settings().printer.thermal.adafruit.baudrate == 19200,
            CategorySetting,
        ),
        (
            (
                # Language
                LOCALE_INDEX,
                # Change Locale
                NEXT_INDEX,
                GO_INDEX,
            ),
            [
                mocker.call(text_en, WHITE),
                mocker.call(text_next, WHITE),
            ],
            lambda: Settings().i18n.locale == tlist[index_next],
            CategorySetting,
        ),
        (
            (
                # Logging
                LOGGING_INDEX,
                # Change log level
                NEXT_INDEX,
                NEXT_INDEX,
                NEXT_INDEX,
                NEXT_INDEX,
                GO_INDEX,
                # Leave Settings
                LEAVE_INDEX,
            ),
            [
                mocker.call("Log Level\nNONE", WHITE),
                mocker.call("Log Level\nERROR", RED),
                mocker.call("Log Level\nWARN", ORANGE),
                mocker.call("Log Level\nINFO", GREEN),
                mocker.call("Log Level\nDEBUG", MAGENTA),
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
        ctx.power_manager.battery_charge_remaining.return_value = 1
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

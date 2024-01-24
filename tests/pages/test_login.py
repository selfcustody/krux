import sys
from unittest import mock
import pytest
from ..shared_mocks import mock_context


@pytest.fixture
def mocker_printer(mocker):
    mocker.patch("krux.printers.thermal.AdafruitPrinter", new=mocker.MagicMock())


def create_ctx(mocker, btn_seq, touch_seq=None):
    """Helper to create mocked context obj"""

    HASHED_IMAGE_BYTES = b"3\x0fr\x7fKY\x15\t\x83\xaab\x92\x0f&\x820\xb4\x14\x87\x19\xee\x95F\x9c\x8f\x0c\xbdo\xbc\x1d\xcbT"

    ctx = mock_context(mocker)
    ctx.power_manager.battery_charge_remaining.return_value = 1
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=btn_seq)
    ctx.camera.capture_entropy = mocker.MagicMock(return_value=HASHED_IMAGE_BYTES)

    if touch_seq:
        ctx.input.touch = mocker.MagicMock(
            current_index=mocker.MagicMock(side_effect=touch_seq)
        )
    return ctx


################### Test menus


def test_menu_load_from_camera(m5stickv, mocker):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # Load Key from Camera
        [BUTTON_ENTER]
        +
        # QR code
        [BUTTON_ENTER]
    )

    TEST_VALUE = "Test value"
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login, "load_key_from_qr_code", mocker.MagicMock(return_value=TEST_VALUE)
    )
    test_status = login.load_key()

    assert test_status == TEST_VALUE
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_menu_load_from_manual(m5stickv, mocker):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # Load Key from Manual
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # Load from Numbers
        [BUTTON_PAGE, BUTTON_ENTER]
        +
        # Decimal
        [BUTTON_ENTER]
    )

    TEST_VALUE = "Test value"
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login, "load_key_from_digits", mocker.MagicMock(return_value=TEST_VALUE)
    )
    test_status = login.load_key()

    assert test_status == TEST_VALUE
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_menu_new_key(m5stickv, mocker):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER

    BTN_SEQUENCE = (
        # New Key from Snapshot
        [BUTTON_ENTER]
    )

    TEST_VALUE = "Test value"
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login, "new_key_from_snapshot", mocker.MagicMock(return_value=TEST_VALUE)
    )
    test_status = login.new_key()

    assert test_status == TEST_VALUE
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_tools_menu(m5stickv, mocker):
    from krux.pages.login import Login, MENU_CONTINUE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    BTN_SEQUENCE = (
        # Back
        [BUTTON_PAGE] * 5
        + [BUTTON_ENTER]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    test_tools = login.tools()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert test_tools == MENU_CONTINUE


################### Test load from storage menu


def test_load_from_storage(m5stickv, mocker):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        # Load Key from Storage
        [BUTTON_PAGE] * 2
        + [BUTTON_ENTER]
        + [
            BUTTON_ENTER,  # 1 press to continue loading key
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # 1 press to select single-sig
        ]
    )

    MNEMONIC = "diet glad hat rural panther lawsuit act drop gallery urge where fit"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch(
        "krux.pages.encryption_ui.LoadEncryptedMnemonic.load_from_storage",
        mocker.MagicMock(return_value=MNEMONIC.split(" ")),
    )
    login.load_key()
    print(ctx.wallet.key.mnemonic)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.wallet.key.mnemonic == MNEMONIC


################### QR Passphrase


def test_qr_passphrase(m5stickv, mocker):
    from krux.pages.login import Login

    TEST_VALUE = "Test value"
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    login = Login(ctx)
    mocker.patch.object(
        login, "capture_qr_code", mocker.MagicMock(return_value=QR_DATA)
    )
    test_passphrase = login._load_qr_passphrase()

    assert test_passphrase == TEST_VALUE


def test_qr_passphrase_too_long(m5stickv, mocker):
    from krux.pages.login import Login, MENU_CONTINUE

    TEST_VALUE = "Test value" * 25
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    login = Login(ctx)
    mocker.patch.object(
        login, "capture_qr_code", mocker.MagicMock(return_value=QR_DATA)
    )
    test_passphrase = login._load_qr_passphrase()

    assert test_passphrase == MENU_CONTINUE


def test_qr_passphrase_fail(m5stickv, mocker):
    from krux.pages.login import Login, MENU_CONTINUE

    TEST_VALUE = None
    QR_DATA = (TEST_VALUE, None)
    ctx = create_ctx(mocker, None)
    login = Login(ctx)
    mocker.patch.object(
        login, "capture_qr_code", mocker.MagicMock(return_value=QR_DATA)
    )
    test_passphrase = login._load_qr_passphrase()

    assert test_passphrase == MENU_CONTINUE


def test_new_12w_from_snapshot(m5stickv, mocker):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    # mocks a result of a hashed image
    mock_capture_entropy = mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture", return_value=b"\x01" * 32
    )

    BTN_SEQUENCE = (
        # 1 press to proceed to 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed msg
        [BUTTON_ENTER]
        +
        # SHA256
        [BUTTON_ENTER]
        +
        # Words
        [BUTTON_ENTER]
        +
        # Move to No passphrase
        [BUTTON_PAGE_PREV]
        +
        # Confirm No passphrase
        [BUTTON_ENTER]
        +
        # Confirm Fingerpint
        [BUTTON_ENTER]
        +
        # Confirm Singlesig
        [BUTTON_ENTER]
    )
    MNEMONIC = "absurd amount doctor acoustic avoid letter advice cage absurd amount doctor adjust"
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.new_key_from_snapshot()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.wallet.key.mnemonic == MNEMONIC


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
        # 1 press to select single-sig
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
        # 1 press to select single-sig
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
        # 1 press to select single-sig
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
        # 1 press to select single-sig
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
        # 1 press to select single-sig
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
        # 1 press to select single-sig
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
        # 1 press to select single-sig
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
            + [BUTTON_ENTER]  # Pick valid checksum final word message
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
                BUTTON_ENTER,  # Single-sig
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
            + [BUTTON_ENTER]  # Pick valid checksum final word message
            +
            # Go + Confirm word
            [BUTTON_PAGE for _ in range(27)]
            + [BUTTON_ENTER]
            + [BUTTON_ENTER]
            + [
                BUTTON_ENTER,  # Done?
                BUTTON_ENTER,  # 12 word confirm
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,  # Single-sig
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
            + [BUTTON_ENTER]  # Pick valid checksum final word message
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
            # Done? Confirm, Words correct? Confirm, No passphrase, Single-sig
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
            + [BUTTON_ENTER]  # Pick valid checksum final word message
            +
            # Move to Go, press Go, confirm word
            [BUTTON_PAGE_PREV] + [BUTTON_ENTER] + [BUTTON_ENTER] +
            # Done? Confirm, Words correct? Confirm, No passphrase, Single-sig
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
            + [BUTTON_ENTER]  # Pick valid checksum final word message
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
                BUTTON_ENTER,  # 12 numbers confirm
                BUTTON_ENTER,  # 12 word confirm
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,  # Single-sig
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
            + [BUTTON_ENTER]  # Pick valid checksum final word message
            +
            # Go + Confirm
            [BUTTON_PAGE for _ in range(11)]
            + [BUTTON_ENTER]
            + [BUTTON_ENTER]
            + [
                BUTTON_ENTER,  # Done?
                BUTTON_ENTER,  # 12 numbers confirm
                BUTTON_ENTER,  # 12 word confirm
                BUTTON_PAGE,  # 1 press to move to Scan passphrase
                BUTTON_PAGE,  # 1 press to move to No passphrase
                BUTTON_ENTER,  # 1 press to skip passphrase
                BUTTON_ENTER,  # 1 press to confirm fingerprint
                BUTTON_ENTER,  # Single-sig
            ],
            "ability ability ability ability ability ability ability ability ability ability ability",
        ),
    ]
    num = 0
    for case in cases:
        print("case:", num)
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
        + [BUTTON_ENTER]  # Pick valid checksum final word message
        + (
            [BUTTON_ENTER]  # 1 press to number 1
            + [BUTTON_ENTER]  # 1 press to number 1
            + [BUTTON_PAGE for _ in range(4)]  # 4 press change to number 5
            + [BUTTON_ENTER]  # 1 press to select 5
            + [BUTTON_ENTER]  # Confirm word=115(277 decimal) card
        )
        + [
            BUTTON_ENTER,  # Done?
            BUTTON_ENTER,  # 12 numbers confirm
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-sig
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
        + [BUTTON_ENTER]  # Pick valid checksum final word message
        + (
            [BUTTON_PAGE_PREV]  # 1 press change to btn Go
            + [BUTTON_ENTER]  # 1 press to select Go
            + [BUTTON_ENTER]  # Confirm last random word
        )
        + [
            BUTTON_ENTER,  # Done?
            BUTTON_ENTER,  # 12 numbers confirm
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-sig
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
        + [BUTTON_ENTER]  # Pick valid checksum final word message
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
            BUTTON_ENTER,  # 12 numbers confirm
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-sig
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
        + [BUTTON_ENTER]  # Pick valid checksum final word message
        + (
            [BUTTON_PAGE_PREV]  # 1 press change to btn Go
            + [BUTTON_ENTER]  # 1 press to select Go
            + [BUTTON_ENTER]  # Confirm last random word
        )
        + [
            BUTTON_ENTER,  # Done?
            BUTTON_ENTER,  # 12 numbers confirm
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-sig
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
        + [BUTTON_ENTER]  # Pick valid checksum final word message
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
            BUTTON_ENTER,  # Single-sig
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
        + [BUTTON_ENTER]  # Pick valid checksum final word message
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


def test_load_12w_from_tiny_seed(amigo_tft, mocker, mocker_printer):
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
            BUTTON_ENTER,  # Single-sig
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
            BUTTON_ENTER,  # Single-sig
        ]
    )
    MNEMONIC = "lend zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo blossom"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_tiny_seed()

    assert ctx.wallet.key.mnemonic == MNEMONIC


def test_load_key_from_tiny_seed_scanner_12w(m5stickv, mocker):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # 12 words
        + [BUTTON_ENTER]  # Confirm
        + [
            BUTTON_ENTER,  # 12 word confirm
            BUTTON_PAGE,  # 1 press to move to Scan passphrase
            BUTTON_PAGE,  # 1 press to move to No passphrase
            BUTTON_ENTER,  # 1 press to skip passphrase
            BUTTON_ENTER,  # 1 press to confirm fingerprint
            BUTTON_ENTER,  # Single-sig
        ]
    )
    MNEMONIC = (
        "idle item three donate heavy auto worry mass casual wrestle shock orphan"
    )

    mocker.patch(
        "krux.pages.tiny_seed.TinyScanner.scanner",
        new=mocker.MagicMock(return_value=MNEMONIC.split()),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    login.load_key_from_tiny_seed_image()

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
            BUTTON_ENTER,  # Single-sig
        ]
    )
    MNEMONIC = "language language language language language language language language language language language auction"

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)

    login.load_key_from_1248()

    assert ctx.wallet.key.mnemonic == MNEMONIC


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

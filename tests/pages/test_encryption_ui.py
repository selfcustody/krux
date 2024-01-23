import sys
import pytest
from unittest import mock
from unittest.mock import patch
from Crypto.Cipher import AES
from ..shared_mocks import mock_context

if "ucryptolib" not in sys.modules:
    sys.modules["ucryptolib"] = mock.MagicMock(
        aes=AES.new, MODE_ECB=AES.MODE_ECB, MODE_CBC=AES.MODE_CBC
    )

TEST_KEY = "test key"
CBC_WORDS = "dog guitar hotel random owner gadget salute riot patrol work advice panic erode leader pass cross section laundry elder asset soul scale immune scatter"
ECB_WORDS = "brass creek fuel snack era success impulse dirt caution purity lottery lizard boil festival neither case swift smooth range mail gravity sample never ivory"
I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"
SEEDS_JSON = """{
    "ecbID": {
        "version": 0,
        "key_iterations": 100000,
        "data": "sMCvAUvVpGSCsXsBl7EBNGPZLymZoyB8eAUHb2TMbarhqD4GJga/SW/AstxIvZz6MR1opXLfF7Pyd+IJBe3E0lDQCkvqytSQfVGnVSeYz+sNfd5T1CXS0/C2zYKTKFL7RTpHd0IXHZ+GQuzX1hoJMHkh0sx0VgorVdDj87ykUQIeC95MS98y/ha2q/vWfLyIZU1hc5VcehzmTA1B6ExMGA=="
    },
    "cbcID": {
        "version": 1,
        "key_iterations": 100000,
        "data": "GpNxj9kzdiTuIf1UYC6R0FHoUokBhiNLkxWgSOHBhmBHb0Ew8wk1M+VlsR4v/koCfSGOTkgjFshC36+n7mx0W0PI6NizAoPClO8DUVamd5hS6irS+Lfff0//VJWK1BcdvOJjzYw8TBiVaL1swAEEySjn5GsqF1RaJXzAMMgu03Kq32iDIDy7h/jHJTiIPCoVQAle/C9vXq2HQeVx43c0LhGXTZmIhhkHPMgDzFTsMGM="
    }
}"""
ENCRYPTED_QR_TITLE_CBC = "353175d8"
ENCRYPTED_QR_DATA_CBC = b"\x08353175d8\x01\x00\x00\n!\xa1\xf3\x8b\x9e\xa1^\x8d\xab\x08\xf7\t\xf3\x94\x06\x89Q\x15]\xe0\xc6\xabf\x9c\x12E\xbcw\xcaa\x14\xfc\xa5\x16\x15\x0f;\x88\xbc\xb4H\xbe_\xf3\xf1b\x1e\x02\xff\xea\x9a\xe9z\xfd\xc9\xef\xcd\xa0A\x0c\xd1:a\x08"

ENCRYPTED_QR_TITLE_ECB = "06b79aa2"
ENCRYPTED_QR_DATA_ECB = b"\x0806b79aa2\x00\x00\x00\n\xa4\xaaa\xb9h\x0c\xdc-i\x85\x83.9,\x91\xf1\x19E,\xc9\xf0'\xb1b7\x91mo\xa2-\xb6\x16\xac\x04-2F\x10\xda\xd1\xdb,\x85\x9fr\x1c\x8aH"


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data="SEEDS_JSON"))


def create_ctx(mocker, btn_seq):
    """Helper to create mocked context obj"""
    ctx = mock_context(mocker)
    ctx.power_manager.battery_charge_remaining.return_value = 1
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=btn_seq)
    return ctx


def test_load_key_from_keypad(m5stickv, mocker):
    from krux.pages.encryption_ui import EncryptionKey
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # choose to type key
        + [BUTTON_PAGE]  # go to letter b
        + [BUTTON_ENTER]  # enter letter b
        + [BUTTON_PAGE_PREV] * 2  # move to "Go"
        + [BUTTON_ENTER]  # Go
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    key = key_generator.encryption_key()
    assert key == "b"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_esc_loading_key_from_keypad_is_none(m5stickv, mocker):
    from krux.pages.encryption_ui import EncryptionKey
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # choose to type key
        + [BUTTON_PAGE_PREV] * 2  # go to ESC
        + [BUTTON_ENTER]  # ESC
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    key = key_generator.encryption_key()
    assert key is None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_load_key_from_qr_code(m5stickv, mocker):
    from krux.pages.encryption_ui import EncryptionKey, ENCRYPTION_KEY_MAX_LEN
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    print("case 1: load_key_from_qr_code")
    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # move to QR code key
        + [BUTTON_ENTER]  # choose QR code key
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    mocker.patch.object(
        key_generator,
        "capture_qr_code",
        mocker.MagicMock(return_value=(("qr key", None))),
    )
    key = key_generator.encryption_key()
    assert key == "qr key"

    print("case 2: load_key_from_qr_code")
    # Repeat with too much characters >ENCRYPTION_KEY_MAX_LEN
    BTN_SEQUENCE = [BUTTON_PAGE] + [  # move to QR code key
        BUTTON_ENTER
    ]  # choose QR code key
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    too_long_text = "l" * (ENCRYPTION_KEY_MAX_LEN + 1)
    mocker.patch.object(
        key_generator,
        "capture_qr_code",
        mocker.MagicMock(return_value=((too_long_text, None))),
    )
    key = key_generator.encryption_key()
    assert key == None


def test_encrypt_cbc_sd_ui(m5stickv, mocker, mock_file_operations):
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key
    from embit.networks import NETWORKS

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # Move to store on SD card
        + [BUTTON_ENTER]  # Confirm SD card
        + [BUTTON_ENTER]  # Confirm add CBC cam entropy
        + [BUTTON_PAGE]  # add custom ID - move to no
        + [BUTTON_ENTER]  # Confirm encryption ID
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.wallet = Wallet(Key(CBC_WORDS, False, NETWORKS["main"]))
    storage_ui = EncryptMnemonic(ctx)
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture",
        mocker.MagicMock(return_value=I_VECTOR),
    )
    Settings().encryption.version = "AES-CBC"
    storage_ui.encrypt_menu()

    ctx.display.draw_centered_text.assert_has_calls(
        [mocker.call("Encrypted mnemonic was stored with ID: 353175d8")], any_order=True
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encrypt_to_qrcode_ecb_ui(m5stickv, mocker):
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key
    from embit.networks import NETWORKS

    BTN_SEQUENCE = (
        [BUTTON_PAGE] * 2  # Move to store on Encrypted QR
        + [BUTTON_ENTER]  # Confirm Encrypted QR
        # Key is mocked here, no press needed
        + [BUTTON_PAGE]  # add custom ID - No
        # QR view is mocked here, no press needed
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.wallet = Wallet(Key(ECB_WORDS, False, NETWORKS["main"]))
    ctx.printer = None
    storage_ui = EncryptMnemonic(ctx)
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    with patch("krux.pages.qr_view.SeedQRView", mocker.MagicMock()) as qr_view:
        Settings().encryption.version = "AES-ECB"
        storage_ui.encrypt_menu()
    qr_view.assert_has_calls(
        [
            mocker.call(
                mocker.ANY, data=ENCRYPTED_QR_DATA_ECB, title=ENCRYPTED_QR_TITLE_ECB
            )
        ]
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encrypt_to_qrcode_cbc_ui(m5stickv, mocker):
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key
    from embit.networks import NETWORKS

    BTN_SEQUENCE = (
        [BUTTON_PAGE] * 2  # Move to store on Encrypted QR
        + [BUTTON_ENTER]  # Confirm Encrypted QR
        + [BUTTON_ENTER]  # Confirm to add CBC cam entropy
        # Key is mocked here, no press needed
        + [BUTTON_PAGE]  # add custom ID - No
        # QR view is mocked here, no press needed
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.wallet = Wallet(Key(CBC_WORDS, False, NETWORKS["main"]))
    ctx.printer = None
    storage_ui = EncryptMnemonic(ctx)
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture",
        mocker.MagicMock(return_value=I_VECTOR),
    )

    with patch("krux.pages.qr_view.SeedQRView", mocker.MagicMock()) as qr_view:
        Settings().encryption.version = "AES-CBC"
        storage_ui.encrypt_menu()
    qr_view.assert_has_calls(
        [
            mocker.call(
                mocker.ANY, data=ENCRYPTED_QR_DATA_CBC, title=ENCRYPTED_QR_TITLE_CBC
            )
        ]
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_load_encrypted_from_flash(m5stickv, mocker):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import LoadEncryptedMnemonic

    BTN_SEQUENCE = [BUTTON_ENTER]  # First mnemonic
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    with patch("krux.encryption.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        encrypted_mnemonics = LoadEncryptedMnemonic(ctx)
        words = encrypted_mnemonics.load_from_storage()
    assert words == ECB_WORDS.split()


def test_load_encrypted_from_sd(m5stickv, mocker, mock_file_operations):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import LoadEncryptedMnemonic

    BTN_SEQUENCE = [BUTTON_ENTER]  # First mnemonic
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    with patch("krux.sd_card.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        encrypted_mnemonics = LoadEncryptedMnemonic(ctx)
        words = encrypted_mnemonics.load_from_storage()
    assert words == ECB_WORDS.split()


def test_load_encrypted_from_flash_wrong_key(m5stickv, mocker):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.pages.encryption_ui import LoadEncryptedMnemonic
    from krux.pages import MENU_CONTINUE

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # First mnemonic
        + [BUTTON_ENTER]  # Fail to decrypt
        + [BUTTON_PAGE_PREV]  # Go to back
        + [BUTTON_ENTER]  # Leave
    )
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value="wrong key"),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    with patch("krux.encryption.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        encrypted_mnemonics = LoadEncryptedMnemonic(ctx)
        words = encrypted_mnemonics.load_from_storage()
    assert words == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_load_encrypted_qr_code(m5stickv, mocker):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    BTN_SEQUENCE = (
        # Decrypt? Yes
        [BUTTON_ENTER]
        +
        # Key loading is mocked here
        # 1 press to proceed with the 12 words
        [BUTTON_ENTER]
        +
        # 1 press to proceed with the 24 words
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

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        login,
        "capture_qr_code",
        mocker.MagicMock(return_value=(ENCRYPTED_QR_DATA_CBC, QR_FORMAT)),
    )
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    _ = login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == CBC_WORDS
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

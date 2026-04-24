import pytest
from unittest.mock import patch
from . import create_ctx

TEST_KEY = "test key"
CBC_WORDS = "dog guitar hotel random owner gadget salute riot patrol work advice panic erode leader pass cross section laundry elder asset soul scale immune scatter"
ECB_WORDS = "brass creek fuel snack era success impulse dirt caution purity lottery lizard boil festival neither case swift smooth range mail gravity sample never ivory"
# TODO controls and unit_tests for CTR and GCM

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
OLD_ENCRYPTED_QR_DATA_CBC = b"\x08353175d8\x01\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\xa5\x95(IzR\x81\xabI:\x1e\x8a\x1d\xe7|O\xac\x9c\xe8.\x8cc\xc0\x93\x0e\xe67vpO#i\x99\xd1.\x85\xf7\x00\xfez\xadN\x9d7\xaex\xa6\xd3"
ENCRYPTED_QR_DATA_CBC = b"\x08353175d8\x0a\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\xa5\x95(IzR\x81\xabI:\x1e\x8a\x1d\xe7|O\xac\x9c\xe8.\x8cc\xc0\x93\x0e\xe67vpO#i\xc0\x1a)\x8d"
ENCRYPTED_QR_DATA_CBC_b43 = "VBRRAN4/CZD0I$4DYJWT8SU8R2+VAKKV*IKVFAXL0CIALR2AKM:.LUBEBS1CIT0DTX5VBE*HR7D3S8GY8D.H57$J3527$OP"

ENCRYPTED_QR_TITLE_ECB = "06b79aa2"
OLD_ENCRYPTED_QR_DATA_ECB = b"\x0806b79aa2\x00\x00\x00\n\xa4\xaaa\xb9h\x0c\xdc-i\x85\x83.9,\x91\xf1\x19E,\xc9\xf0'\xb1b7\x91mo\xa2-\xb6\x16\xac\x04-2F\x10\xda\xd1\xdb,\x85\x9fr\x1c\x8aH"
ENCRYPTED_QR_DATA_ECB = b"\x0806b79aa2\x05\x00\x00\n\xa4\xaaa\xb9h\x0c\xdc-i\x85\x83.9,\x91\xf1\x19E,\xc9\xf0'\xb1b7\x91mo\xa2-\xb6\x16\xb5\x16\xad"
ENCRYPTED_QR_DATA_ECB_b43 = (
    "OQD.HJOZXT8AMEC+19G.I3MARO1RUK5Q0NE1B826Q9.$7W4.$.A.HY*SADG*+97R+-ERI$"
)


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data="SEEDS_JSON"))


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


def test_load_key_from_keypad_when_creating(m5stickv, mocker):
    from krux.pages.encryption_ui import EncryptionKey
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.themes import RED

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
    key = key_generator.encryption_key(creating=True)
    assert key == "b"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    call_message = mocker.call(
        "Strength: Weak", 38, RED, highlight_prefix=":"
    )  # 38 = y_offset

    ctx.display.draw_hcentered_text.assert_has_calls([call_message])


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
    from krux.pages.qr_capture import QRCodeCapture

    print("case 1: load_key_from_qr_code")
    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # move to QR code key
        + [BUTTON_ENTER]  # choose QR code key
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    mocker.patch.object(
        QRCodeCapture, "qr_capture_loop", new=lambda self: ("qr key", None)
    )
    key = key_generator.encryption_key()
    assert key == "qr key"

    print("case 2: load_key_from_qr_code")
    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # move to QR code key
        + [BUTTON_ENTER]  # choose QR code key
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (b"decodable bytes qr key", None),
    )
    key = key_generator.encryption_key()
    assert key == "decodable bytes qr key"

    print("case 3: load_key_from_qr_code")
    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # move to QR code key
        + [BUTTON_ENTER]  # choose QR code key
        + [BUTTON_ENTER]  # Confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    mocker.patch.object(
        QRCodeCapture, "qr_capture_loop", new=lambda self: (b"\xde\xad\xbe\xef", None)
    )
    key = key_generator.encryption_key()
    assert key == b"\xde\xad\xbe\xef"
    call_message = mocker.call("Key (4): 0xdeadbeef", 10, highlight_prefix=":")
    ctx.display.draw_hcentered_text.assert_has_calls([call_message])

    print("case 4: load_key_from_qr_code")
    # Repeat with too much characters >ENCRYPTION_KEY_MAX_LEN
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # move to QR code key
        BUTTON_ENTER,  # read too long text
        BUTTON_ENTER,  # click to pass error
        BUTTON_ENTER,  # enter to read normal text
        BUTTON_ENTER,  # enter to accept "short text"
    ]  # choose QR code key
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    key_generator = EncryptionKey(ctx)
    too_long_text = "l" * (ENCRYPTION_KEY_MAX_LEN + 1)
    values_list = ["short text", too_long_text]

    def qr_return(self):
        return values_list.pop(), None

    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=qr_return)
    key = key_generator.encryption_key()
    assert key == "short text"

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encrypt_cbc_sd_ui(m5stickv, mocker, mock_file_operations):
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key, TYPE_SINGLESIG
    from embit.networks import NETWORKS

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # Move to store on SD card
        + [BUTTON_ENTER]  # Confirm SD card
        + [BUTTON_ENTER]  # Confirm add CBC cam entropy
        + [BUTTON_ENTER]  # YES, use fingerprint as ID
        + [BUTTON_ENTER]  # Confirm encryption ID
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.wallet = Wallet(Key(CBC_WORDS, TYPE_SINGLESIG, NETWORKS["main"]))

    Settings().encryption.version = "AES-CBC"
    storage_ui = EncryptMnemonic(ctx)
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture",
        mocker.MagicMock(return_value=I_VECTOR),
    )
    storage_ui.encrypt_menu()

    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call(
                "Encrypted mnemonic stored with ID: " + ENCRYPTED_QR_TITLE_CBC,
                highlight_prefix=":",
            )
        ],
        any_order=True,
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encrypt_save_error_exist(m5stickv, mocker, mock_file_operations):
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key
    from embit.networks import NETWORKS

    BTN_SEQUENCE = [BUTTON_ENTER] + [
        BUTTON_ENTER
    ]  # Confirm flash store  # Confirm fingerprint as ID
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.wallet = Wallet(Key(ECB_WORDS, False, NETWORKS["main"]))
    Settings().encryption.version = "AES-ECB"
    storage_ui = EncryptMnemonic(ctx)
    mocker.spy(storage_ui, "flash_error")
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    mocker.patch(
        "krux.encryption.MnemonicStorage.list_mnemonics",
        mocker.MagicMock(return_value=[ENCRYPTED_QR_TITLE_ECB]),
    )
    storage_ui.encrypt_menu()

    storage_ui.flash_error.assert_has_calls(
        [mocker.call("ID already exists" + "\n" + "Encrypted mnemonic was not stored")],
        any_order=True,
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encrypt_save_error(m5stickv, mocker, mock_file_operations):
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key
    from embit.networks import NETWORKS
    from krux.themes import theme

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # Confirm flash store
        + [BUTTON_ENTER]  # Yes, use fingerprint as ID
        + [BUTTON_ENTER]  # Confirm encryption ID
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.wallet = Wallet(Key(ECB_WORDS, False, NETWORKS["main"]))
    Settings().encryption.version = "AES-ECB"
    storage_ui = EncryptMnemonic(ctx)
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    mocker.patch(
        "krux.encryption.MnemonicStorage.store_encrypted_kef",
        mocker.MagicMock(return_value=False),
    )
    storage_ui.encrypt_menu()

    ctx.display.draw_centered_text.assert_has_calls(
        [mocker.call("Failed to store mnemonic", theme.error_color)], any_order=True
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encrypt_to_qrcode_ecb_ui(m5stickv, mocker):
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key, TYPE_SINGLESIG
    from embit.networks import NETWORKS

    BTN_SEQUENCE = (
        [BUTTON_PAGE] * 2  # Move to store on Encrypted QR
        + [BUTTON_ENTER]  # Confirm Encrypted QR
        # Key is mocked here, no press needed
        + [BUTTON_ENTER]  # Yes, use fingerprint as ID
        # QR view is mocked here, no press needed
    )
    mocker.patch("time.ticks_ms", return_value=0)  # tick_ms affects random delta
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.wallet = Wallet(Key(ECB_WORDS, TYPE_SINGLESIG, NETWORKS["main"]))
    ctx.printer = None
    Settings().encryption.version = "AES-ECB"
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
                mocker.ANY, data=ENCRYPTED_QR_DATA_ECB_b43, title=ENCRYPTED_QR_TITLE_ECB
            )
        ]
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encrypt_to_qrcode_cbc_ui(m5stickv, mocker):
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key, TYPE_SINGLESIG
    from embit.networks import NETWORKS

    BTN_SEQUENCE = (
        [BUTTON_PAGE] * 2  # Move to store on Encrypted QR
        + [BUTTON_ENTER]  # Confirm Encrypted QR
        + [BUTTON_ENTER]  # Confirm to add CBC cam entropy
        # Key is mocked here, no press needed
        + [BUTTON_ENTER]  # Yes, use fingerprint as ID
        # QR view is mocked here, no press needed
    )
    mocker.patch("time.ticks_ms", return_value=0)  # tick_ms affects random delta
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.wallet = Wallet(Key(CBC_WORDS, TYPE_SINGLESIG, NETWORKS["main"]))
    ctx.printer = None
    Settings().encryption.version = "AES-CBC"
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
        storage_ui.encrypt_menu()
    qr_view.assert_has_calls(
        [
            mocker.call(
                mocker.ANY, data=ENCRYPTED_QR_DATA_CBC_b43, title=ENCRYPTED_QR_TITLE_CBC
            )
        ]
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encrypted_qr_code_mode_and_density(amigo, mocker):
    import re, pyqrcode
    from krux.wallet import Wallet
    from krux.krux_settings import Settings
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import EncryptMnemonic
    from krux.key import Key, TYPE_SINGLESIG
    from embit.networks import NETWORKS

    TEST_MNEMONICS = [
        # 12w
        "crush inherit small egg include title slogan mom remain blouse boost bonus",
        # The following mnemonic bytes end with 0x00 requiring AESCipher.encrypt() be called
        # w/ non-default "fail_unsafe=False" for some versions (w/ auth, w/o pkcs_pad).
        # "olympic term tissue route sense program under choose bean emerge velvet absurd",
        # 24w
        "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major",
    ]

    # Dictionary mapping encryption modes to (mode, size) tuples
    QR_PROPS = {
        "AES-ECB": ("alphanumeric", 25, 29),
        # "AES-ECB v2": ("alphanumeric", 25, 29),
        # "AES-ECB +p": ("alphanumeric", 29, 33),
        # "AES-ECB +c": ("alphanumeric", 29, 33),
        "AES-CBC": ("alphanumeric", 29, 33),
        # "AES-CBC v2": ("alphanumeric", 29, 33),
        # "AES-CBC +p": ("alphanumeric", 33, 33),
        # "AES-CBC +c": ("alphanumeric", 33, 33),
        "AES-GCM": ("alphanumeric", 29, 33),
        # "AES-GCM +p": ("alphanumeric", 33, 33),
        # "AES-GCM +c": ("alphanumeric", 33, 33),
    }

    BTN_SEQUENCE = (
        [BUTTON_PAGE] * 2  # Move to store on Encrypted QR
        + [BUTTON_ENTER]  # Confirm Encrypted QR
        # Key is mocked here, no press needed
        + [BUTTON_ENTER]  # Confirm to add CBC or GCM cam entropy
        + [BUTTON_ENTER]  # Yes, use fingerprint as ID
        # QR view is mocked here, no press needed
    )
    BTN_SEQUENCE_ECB = (
        [BUTTON_PAGE] * 2  # Move to store on Encrypted QR
        + [BUTTON_ENTER]  # Confirm Encrypted QR
        + [BUTTON_ENTER]  # Yes, use fingerprint as ID
        # QR view is mocked here, no press needed
    )

    def is_qr_alphanumeric(string):
        return bool(re.match("^[A-Z0-9 $%*+\\-./:]+$", string))

    for mnemonic in TEST_MNEMONICS:
        for encryption_mode in sorted(QR_PROPS.keys()):
            btn_seq = (
                BTN_SEQUENCE if not encryption_mode == "AES-ECB" else BTN_SEQUENCE_ECB
            )
            ctx = create_ctx(mocker, btn_seq)
            ctx.wallet = Wallet(Key(mnemonic, TYPE_SINGLESIG, NETWORKS["main"]))
            ctx.printer = None
            Settings().encryption.version = encryption_mode
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
                storage_ui.encrypt_menu()

            assert qr_view.called, "SeedQRView was not called"
            _, called_kwargs = qr_view.call_args
            data = called_kwargs.get("data")
            mode = "binary"
            if isinstance(data, str):
                if data.isdigit():
                    mode = "numeric"
                elif is_qr_alphanumeric(data):
                    mode = "alphanumeric"
            try:
                code_str = pyqrcode.create(data, error="L", mode=mode).text(
                    quiet_zone=0
                )
            except:
                # pre-decode if binary (SeedQR)
                data = data.decode("latin-1")
                code_str = pyqrcode.create(data, error="L", mode="binary").text(
                    quiet_zone=0
                )
            size = 0
            while code_str[size] != "\n":
                size += 1

            expected_mode, expected_size_12w, expected_size_24w = QR_PROPS[
                encryption_mode
            ]
            len_mnemonic = len(mnemonic.split())
            expected_size = (
                expected_size_12w if len_mnemonic == 12 else expected_size_24w
            )
            assert mode == expected_mode, f"QR mode mismatch for {encryption_mode}"
            assert (
                size == expected_size
            ), f"QR size mismatch for {encryption_mode}, {len_mnemonic}w"
            assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_load_encrypted_from_flash(m5stickv, mocker):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import LoadEncryptedMnemonic

    BTN_SEQUENCE = [BUTTON_PAGE, BUTTON_ENTER]  # Second mnemonic
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    with patch("krux.encryption.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        encrypted_mnemonics = LoadEncryptedMnemonic(ctx)
        words = encrypted_mnemonics.load_from_storage()
    assert words == ECB_WORDS.split()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_load_encrypted_from_sd(m5stickv, mocker, mock_file_operations):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.pages.encryption_ui import LoadEncryptedMnemonic

    BTN_SEQUENCE = [BUTTON_PAGE, BUTTON_ENTER]  # Second mnemonic
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    with patch("krux.sd_card.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        encrypted_mnemonics = LoadEncryptedMnemonic(ctx)
        words = encrypted_mnemonics.load_from_storage()
    assert words == ECB_WORDS.split()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

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
        # 1 press to load wallet
        [BUTTON_ENTER]
    )
    QR_FORMAT = FORMAT_NONE

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    login = Login(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (ENCRYPTED_QR_DATA_CBC, QR_FORMAT),
    )
    mocker.patch(
        "krux.pages.encryption_ui.EncryptionKey.encryption_key",
        mocker.MagicMock(return_value=TEST_KEY),
    )
    _ = login.load_key_from_qr_code()

    assert ctx.wallet.key.mnemonic == CBC_WORDS
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_encryption_key_strength(m5stickv, mocker):
    from krux.pages.encryption_ui import EncryptionKey

    ctx = create_ctx(mocker, [])
    key_generator = EncryptionKey(ctx)
    assert key_generator.key_strength("abc") == "Weak"

    # Case 1: Very long but repeated chars
    assert key_generator.key_strength("a" * 41) == "Medium"

    # Case 2: Very long but some different chars
    assert key_generator.key_strength("a" * 20 + "b" * 10 + "c" * 11) == "Strong"

    # Case 3: All character types, good length, but low uniqueness
    # "Aa1!Aa1!" (8 chars, 4 types, 4 unique chars)
    assert key_generator.key_strength("Aa1!Aa1!") == "Medium"

    # Case 4: 8 chars, 4 types, high uniqueness)
    assert key_generator.key_strength("Aa1!Bb2@") == "Strong"

    # Case 5: Strong password (16 chars, 4 types, high uniqueness)
    assert key_generator.key_strength("Aa1!Bb2@Cc3#Dd4$") == "Strong"

    # Case 6: Medium password (11 chars, 3 types)
    assert key_generator.key_strength("Password123") == "Medium"

    # Case 7: 12 characters, 3 types
    assert key_generator.key_strength("Password1234") == "Strong"

    # Case 8: Low uniqueness penalty
    assert key_generator.key_strength("AAAaaa111!!") == "Medium"

    # Case 9: 12 chars, 3 types, uniqueness=3
    assert key_generator.key_strength("Aa1Aa1Aa1Aa1") == "Medium"

    # Case 10: Low base score=1 when not using enough keypads
    assert key_generator.key_strength("ABCDEFGHIJKLMNO") == "Weak"

    # Case 11: Low base score=2 when not using enough keypads and length
    assert key_generator.key_strength("ABCDEFghijk") == "Weak"

    # Case 12: Penalized if not enough unique characters
    assert key_generator.key_strength("ABcd1ABcd1A") == "Weak"

    # Cases 13-15: Binary keys are hexlified and hexstr is scored
    assert key_generator.key_strength(b"Stronger") == "Strong"
    assert key_generator.key_strength(b"barely") == "Medium"
    assert key_generator.key_strength(b"2Weak") == "Weak"


def test_decrypt_kef(m5stickv, mocker):
    """Verify that decrypt_kef attempts to unseal kef-envelope(s)"""
    from krux.pages.encryption_ui import decrypt_kef
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux import kef

    plaintext = b"this is plain text"
    key, salt, iterations, version = b"a", b"KEF ID", 10000, 0

    # create an internal kef envelope
    cryptor = kef.Cipher(key, salt, iterations)
    ciphertext = cryptor.encrypt(plaintext, version)
    envelope = kef.wrap(salt, version, iterations, ciphertext)

    # wrap it again in another kef envelope
    cryptor = kef.Cipher(key * 2, salt, iterations)
    ciphertext = cryptor.encrypt(envelope, version)
    envelope = kef.wrap(salt, version, iterations, ciphertext)
    print(envelope)

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # external envelope "Decrypt?"
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # "a" as key
        BUTTON_ENTER,  # "aa" as key
        BUTTON_PAGE_PREV,  # move to "Go"
        BUTTON_ENTER,  # Go
        BUTTON_ENTER,  # Confirm "aa" as key
        BUTTON_ENTER,  # internal envelope "Decrypt?"
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # "a" as key
        BUTTON_PAGE_PREV,  # move to "Go"
        BUTTON_ENTER,  # Go
        BUTTON_ENTER,  # Confirm "a" as key
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = decrypt_kef(ctx, envelope)
    assert result == plaintext
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # wrong decryption key will result in KeyError raised from decrypt_kef's call
    # to KEFEnvelope.unseal_ui() and does NOT catch it, allows KeyError to bubble up
    # callers decrypt_kef() can not catch KeyError and instead allow it to bubble up
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # external envelope "Decrypt?"
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # "a" as key
        BUTTON_PAGE_PREV,  # move to "Go"
        BUTTON_ENTER,  # Go
        BUTTON_ENTER,  # Confirm "a" as key
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    with pytest.raises(KeyError, match="Failed to decrypt"):
        decrypt_kef(ctx, envelope)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # declining to decrypt results in ValueError("Not decrypted")
    # which callers of decrypt_kef() will likely catch to deal with original data
    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # decline to "Decrypt?"
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    with pytest.raises(ValueError, match="Not decrypted"):
        decrypt_kef(ctx, envelope)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # as well, nothing to decrypt also results in ValueError("Not decrypted")
    # which callers of decrypt_kef() will likely catch to deal with original data
    ctx = create_ctx(mocker, [])
    with pytest.raises(ValueError, match="Not decrypted"):
        decrypt_kef(ctx, "I am not a valid KEF envelope")
    assert ctx.input.wait_for_button.call_count == 0


def test_decrypt_kef_offers_decrypt_ui_appropriately(m5stickv, mocker):
    """
    Intention here is to verify that KEFEnvelope class is instantiated
    and used when expected, not that decryption actually succeeds.
    """
    from binascii import hexlify
    from krux import kef
    from krux.baseconv import base_encode
    from krux.pages.encryption_ui import decrypt_kef, KEFEnvelope
    from krux.input import BUTTON_PAGE_PREV

    # setup data: a fake kef envelope, non-kef data, decrypt-evidence, and responding "No" to "Decrypt?"
    fake_kef = kef.wrap(b"", 0, 10000, bytes([i * 8 for i in range(32)]))
    non_kef = b"this is not a valid kef envelope"
    evidence = "KEF Encrypted (32 B)\nID: \nVersion: AES-ECB v1\nPBKDF2 iter.: 10000\n\nDecrypt?"
    BTN_SEQUENCE = [BUTTON_PAGE_PREV]

    print("test w/ kef bytes")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    try:
        decrypt_kef(ctx, fake_kef)
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.to_lines.assert_called_with(evidence)

    print("test w/ non-kef bytes")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, non_kef)
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test w/ kef hex")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    try:
        decrypt_kef(ctx, hexlify(fake_kef).decode())
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.to_lines.assert_called_with(evidence)

    print("test with non-kef hex")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, hexlify(non_kef).decode())
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with invalid hex-ish str")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, hexlify(non_kef).decode() + ":`")
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with kef HEX")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    try:
        decrypt_kef(ctx, hexlify(fake_kef).decode().upper())
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.to_lines.assert_called_with(evidence)

    print("test with non-kef HEX")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, hexlify(non_kef).decode().upper())
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with invalid HEX-ish str")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, hexlify(non_kef).decode().upper() + ":`")
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with kef base32")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    try:
        decrypt_kef(ctx, base_encode(fake_kef, 32))
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.to_lines.assert_called_with(evidence)

    print("test with non-kef base32")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, base_encode(non_kef, 32))
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with invalid base32-ish str")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, base_encode(non_kef, 32) + "8@")
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with kef base43")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    try:
        decrypt_kef(ctx, base_encode(fake_kef, 43))
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.to_lines.assert_called_with(evidence)

    print("test with non-kef base43")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, base_encode(non_kef, 43))
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with invalid base43-ish str")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, base_encode(non_kef, 43) + ":@")
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with kef base64")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    try:
        decrypt_kef(ctx, base_encode(fake_kef, 64))
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.to_lines.assert_called_with(evidence)

    print("test with non-kef base64")
    ctx = create_ctx(mocker, [])
    try:
        decrypt_kef(ctx, base_encode(non_kef, 64))
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()

    print("test with invalid base64-ish str")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    try:
        decrypt_kef(ctx, base_encode(non_kef, 64) + ">@")
    except ValueError:
        pass
    assert ctx.input.wait_for_button.call_count == 0
    ctx.display.to_lines.assert_not_called()


def test_prompt_for_text_update_dflt_via_yes(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER

    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx,
        dflt_value="Go Brrr",
        dflt_prompt="Number-go-up via printer-go-brrr?",
        dflt_affirm=True,
    )
    assert result == "Go Brrr"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_dflt_via_no(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_PAGE_PREV

    BTN_SEQUENCE = [BUTTON_PAGE_PREV]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx,
        dflt_value="Won't work",
        dflt_prompt="Save-fiat-world via printer-go-brrr?",
        dflt_affirm=False,
    )
    assert result == "Won't work"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_dflt_via_no_change_go1(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx,
        dflt_value="Go Brrr",
        dflt_prompt="Number-go-up via printer-go-brrr?",
        dflt_affirm=True,
        title="Back to Go",
    )
    assert result == "Go Brrr"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_dflt_via_no_change_go2(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx,
        dflt_value="Won't work",
        dflt_prompt="Save-fiat-world via printer-go-brrr?",
        dflt_affirm=False,
        title="Back to Go",
    )
    assert result == "Won't work"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_dflt_via_no_change_esc1(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx,
        dflt_value="Go Brrr",
        dflt_prompt="Number-go-up via printer-go-brrr?",
        dflt_affirm=True,
        title="Back to ESC",
    )
    assert result == "Go Brrr"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_dflt_via_no_change_esc2(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx,
        dflt_value="Won't work",
        dflt_prompt="Save-fiat-world via printer-go-brrr?",
        dflt_affirm=False,
        title="Back to ESC",
    )
    assert result == "Won't work"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_dflt_via_no_change_esc_confirm1(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,
        BUTTON_PAGE_PREV,
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
        BUTTON_ENTER,
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx,
        dflt_value="Go Brrr",
        dflt_prompt="Number-go-up via printer-go-brrr?",
        dflt_affirm=True,
        title="Back to ESC",
        esc_prompt=True,
    )
    assert result == "Go Brrr"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_dflt_via_no_change_esc_confirm2(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_ENTER,
        BUTTON_PAGE_PREV,
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
        BUTTON_ENTER,
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx,
        dflt_value="Won't work",
        dflt_prompt="Save-fiat-world via printer-go-brrr?",
        dflt_affirm=False,
        title="Back to ESC",
        esc_prompt=True,
    )
    assert result == "Won't work"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_new_value1(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [BUTTON_PAGE_PREV, BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(ctx, dflt_value="A", title="Edit value, then Go")
    assert result == "Aa"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_for_text_update_new_value2(m5stickv, mocker):
    from krux.pages.encryption_ui import prompt_for_text_update
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    result = prompt_for_text_update(
        ctx, dflt_value="A", dflt_affirm=False, title="Edit value, then Go"
    )
    assert result == "Aa"
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_kefenvelope_init(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope

    ctx = create_ctx(mocker, [])
    page = KEFEnvelope(ctx)

    print("some attributes are initialized to default values")
    assert None not in (
        page.iterations,
        page.mode_name,  # todo: is this needed
        page.mode,
        page.iv_len,  # todo: is this needed
    )

    print("other attributes are initialized to None")
    assert set([None]) == set(
        [
            page.label,
            page.version,
            page.version_name,  # todo: is this needed
            page.ciphertext,
        ]
    )


def test_kefenvelope_parse(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope

    print("parsing a valid kef envelope returns True")
    ctx = create_ctx(mocker, [])
    page = KEFEnvelope(ctx)
    valid_envelope = (
        b"\x02"
        + b"ID"
        + b"\x00"
        + int(10000).to_bytes(3, "big")
        + bytes([i for i in range(32)])
    )
    assert page.parse(valid_envelope) == True

    print("...and fills some unset attributes")
    assert None not in (
        page.label,
        page.version,
        page.version_name,
        page.ciphertext,
    )

    print("trying to parse an envelope again is not allowed")
    with pytest.raises(ValueError, match="KEF Envelope already parsed"):
        page.parse(valid_envelope)

    print("parsing an invalid kef envelope returns False")
    ctx = create_ctx(mocker, [])
    page = KEFEnvelope(ctx)
    assert page.parse(b"this is not a valid kef envelope") == False
    assert ctx.input.wait_for_button.call_count == 0


def test_kefenvelope_input_key_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.qr_capture import QRCodeCapture

    print('returns True if a key (ie: "a") was gathered')
    BTN_SEQUENCE = [
        BUTTON_ENTER,
        BUTTON_ENTER,
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
        BUTTON_ENTER,
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_key_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    print('returns True if a key (ie: "a") was scanned')
    BTN_SEQUENCE = [
        BUTTON_PAGE,
        BUTTON_ENTER,
        BUTTON_ENTER,
    ]
    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=lambda self: ("a", None))
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_key_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    print("returns True if a binary key (ie: 0x8f) was scanned")
    BTN_SEQUENCE = [
        BUTTON_PAGE,
        BUTTON_ENTER,
        BUTTON_ENTER,
    ]
    mocker.patch.object(
        QRCodeCapture, "qr_capture_loop", new=lambda self: (b"\x8f", None)
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_key_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    print("returns True if an encrypted binary key (ie: 0x8f) was scanned/decrypted")
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # select scan
        BUTTON_ENTER,  # scan key
        BUTTON_ENTER,  # confirm decrypt
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # key is "a"
        BUTTON_PAGE_PREV,  # move to Go
        BUTTON_ENTER,  # select Go
        BUTTON_ENTER,  # confirm key "a"
        BUTTON_ENTER,  # confirm weak key
    ]
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (
            b"\x06binkey\x05\x01\x88WB\xb9\xab\xb6\xe9\x83\x97y\x1ab\xb0F\xe2|\xd3E\x84\x2b\x2c",
            None,
        ),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_key_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    print("returns None if wrong key")
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # select scan
        BUTTON_ENTER,  # scan key
        BUTTON_ENTER,  # confirm decrypt
        BUTTON_ENTER,  # enter key
        BUTTON_PAGE,  # move to "b"
        BUTTON_ENTER,  # key is "b"
        BUTTON_PAGE_PREV,  # move to "a"
        BUTTON_PAGE_PREV,  # move to Go
        BUTTON_ENTER,  # select Go
        BUTTON_ENTER,  # confirm key "b"
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_key_ui() == bool(None)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.flash_text.assert_called_with(
        "Failed to decrypt", 248, 2000, highlight_prefix=""
    )

    print("returns False if no key was gathered")
    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_key_ui() == False
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_kefenvelope_input_mode_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    print("If user accepts: mode is default")
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    defaults = page.mode, page.mode_name
    assert page.input_mode_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.mode, page.mode_name == defaults

    print("If user selects a mode, it is updated")
    BTN_SEQUENCE = [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_mode_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.mode, page.mode_name != defaults


def test_kefenvelope_input_version_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    print("If user accepts: mode is default, version will be set later")
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    defaults = (page.mode, page.mode_name, page.version, page.version_name)
    assert page.input_version_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert (page.mode, page.mode_name, page.version, page.version_name) == defaults
    assert page.version is None and page.version_name is None

    print("If user selects a particular version: mode, version, iv_len are all updated")
    BTN_SEQUENCE = [BUTTON_PAGE_PREV, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_version_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert (page.mode, page.mode_name, page.version, page.version_name) != defaults
    assert page.version is not None and page.version_name is not None
    assert page.iv_len is not None


def test_kefenvelope_iterations_delta(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.krux_settings import Settings

    ELAPSED_TIMES = [0, 1234, 1567825, 1073741823]
    BASE_ITERATIONS_AND_EXPECTED_VALUES = [
        (10000, [10000, 10234, 10825, 10823]),
        (100000, [100000, 101234, 107825, 101823]),
        (500000, [500000, 501234, 517825, 541823]),
    ]

    ctx = create_ctx(mocker, [])

    for elapsed_time in ELAPSED_TIMES:
        for base_iterations, expected_values in BASE_ITERATIONS_AND_EXPECTED_VALUES:
            mocker.patch("time.ticks_ms", return_value=elapsed_time)
            Settings().encryption.pbkdf2_iterations = base_iterations

            page = KEFEnvelope(ctx)
            expected_iterations = expected_values[ELAPSED_TIMES.index(elapsed_time)]
            assert page.iterations == expected_iterations


def test_kefenvelope_input_iterations_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    print("If user accepts: iterations approximated near settings value")
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    default = page.iterations
    assert page.input_iterations_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert default == page.iterations

    print("If user denies default, iterations set by user")
    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # deny default
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_PAGE_PREV,  # back to ESC
        BUTTON_PAGE_PREV,  # back to "<" delete
        BUTTON_ENTER,  # remove last digit
        BUTTON_PAGE_PREV,  # back to "0"
        BUTTON_PAGE_PREV,  # back to "9"
        BUTTON_ENTER,  # select 9 (100009)
        BUTTON_PAGE,  # forward to "0"
        BUTTON_PAGE,  # forward to "<" delete
        BUTTON_PAGE,  # forward to ESC
        BUTTON_PAGE,  # forward to "Go"
        BUTTON_ENTER,  # select Go
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_iterations_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.iterations == 100009

    print("If user sets iterations too high, uses default and returns None")
    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # deny default
        BUTTON_ENTER,  # add another 0 to default
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # select Go
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_iterations_ui() == None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.iterations == default


def test_kefenvelope_input_label_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    print(
        "If proposed label but no prompt, user is asked to update? if they deny: it will be used"
    )
    BTN_SEQUENCE = [BUTTON_PAGE_PREV]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_label_ui("label") == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.label == "label"

    print(
        "if proposed label but no prompt, user is asked to update? if they accept, they update"
    )
    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_label_ui("label") == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.label == "labela"

    print("If user accepts proposed label, they use it")
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_label_ui("label", "use proposed label?") == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.label == "label"

    print("If user denies proposed label, they update")
    BTN_SEQUENCE = [BUTTON_PAGE_PREV, BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_label_ui("label", "use proposed label?") == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.label == "labela"

    print("If user accepts to update proposed label, they update")
    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_label_ui("label", "update proposed label?", False) == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.label == "labela"

    print("If user denies to update proposed label, they use it.")
    BTN_SEQUENCE = [BUTTON_PAGE_PREV]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_label_ui("label", "update proposed label?", False) == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.label == "label"

    print("if no proposed label, user updates empty label")
    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.input_label_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert page.label == "a"


def test_kefenvelope_input_iv_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.kef import MODE_IVS, MODE_NUMBERS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    print("if mode doesn't require iv, returns True w/o any interaction")
    ctx = create_ctx(mocker, [])
    page = KEFEnvelope(ctx)
    page.version = 0
    page.mode = MODE_NUMBERS["AES-ECB"]
    page.iv_len = MODE_IVS.get(MODE_NUMBERS["AES-ECB"], 0)
    assert page.input_iv_ui() == True
    assert ctx.input.wait_for_button.call_count == 0

    mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture",
        mocker.MagicMock(return_value=I_VECTOR),
    )

    print("if mode requires iv, entropy is captured from camera")
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.version = 1
    page.mode = MODE_NUMBERS["AES-CBC"]
    page.iv_len = MODE_IVS.get(MODE_NUMBERS["AES-CBC"], 0)
    assert page.input_iv_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    print("if mode requires iv, but user denies to capture entropy, returns False")
    BTN_SEQUENCE = [BUTTON_PAGE_PREV]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.version = 1
    page.mode = MODE_NUMBERS["AES-CBC"]
    page.iv_len = MODE_IVS[MODE_NUMBERS["AES-CBC"]]
    assert page.input_iv_ui() == None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture",
        mocker.MagicMock(return_value=None),
    )
    print("if mode requires iv, user accepts, but entropy is None, returns None")
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.version = 1
    page.mode = MODE_NUMBERS["AES-CBC"]
    page.iv_len = MODE_IVS[MODE_NUMBERS["AES-CBC"]]
    assert page.input_iv_ui() == None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_kefenvelope_public_info_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    text_id_envelope = (
        b"\x02"
        + b"ID"
        + b"\x00"
        + int(10000).to_bytes(3, "big")
        + bytes([i for i in range(32)])
    )
    binary_id_envelope = (
        b"\x02"
        + b"\xbe\xef"
        + b"\x00"
        + int(10000).to_bytes(3, "big")
        + bytes([i for i in range(32)])
    )
    text_id_evidence = (
        "KEF Encrypted (32 B)\nID: ID\nVersion: AES-ECB v1\nPBKDF2 iter.: 100000000"
    )
    binary_id_evidence = (
        "KEF Encrypted (32 B)\nID: 0xbeef\nVersion: AES-ECB v1\nPBKDF2 iter.: 100000000"
    )

    print("requires a kef_envelope argument or for parse() to have already been called")
    ctx = create_ctx(mocker, [])
    page = KEFEnvelope(ctx)
    with pytest.raises(ValueError, match="KEF Envelope not yet parsed"):
        page.public_info_ui()

    print("Default is an already-parsed kef_envelope no prompt to decrypt")
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.parse(text_id_envelope)
    assert page.public_info_ui() == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.draw_hcentered_text.assert_called_with(text_id_evidence)

    print("Can also pass a kef_envelope.  btw: KEF ID can be binary")
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.public_info_ui(binary_id_envelope) == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.draw_hcentered_text.assert_called_with(binary_id_evidence)

    print('Can request user to be prompted "Decrypt?" to alter boolean return: False')
    BTN_SEQUENCE = [BUTTON_PAGE_PREV]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.public_info_ui(text_id_envelope, prompt_decrypt=True) == False
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.draw_hcentered_text.assert_called_with(
        text_id_evidence + "\n\nDecrypt?", 120, 65535, 0, highlight_prefix=""
    )

    print('Can request user to be prompted "Decrypt?" to alter boolean return: True')
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.public_info_ui(text_id_envelope, prompt_decrypt=True) == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    ctx.display.draw_hcentered_text.assert_called_with(
        text_id_evidence + "\n\nDecrypt?", 120, 65535, 0, highlight_prefix=""
    )


def test_kefenvelope_seal_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import (
        KEFEnvelope,
        OVERRIDE_LABEL,
        OVERRIDE_MODE,
        OVERRIDE_ITERATIONS,
        OVERRIDE_VERSION,
    )
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    print("default is to seal plaintext using defaults w/ least interaction")
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # key is "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # select Go
        BUTTON_ENTER,  # confirm key "a"
        BUTTON_ENTER,  # confirm to add GCM cam entropy
    ]
    mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture",
        mocker.MagicMock(return_value=I_VECTOR),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.label = "my ID"  # id/label may be set elsewhere
    sealed = page.seal_ui(b"plain text")
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert isinstance(sealed, bytes) and len(sealed) > 8

    print("cannot call .seal_ui() if already sealed")
    with pytest.raises(ValueError, match="KEF Envelope already sealed"):
        page.seal_ui(b"more data")

    print("returns None if key not captured")
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # enter key
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # select go w/o key
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    assert page.seal_ui(b"plain text") == None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    print("overrides param is a list, ie: [OVERRIDE_LABEL]")
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # key is "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # select go
        BUTTON_ENTER,  # confirm key "a"
        BUTTON_ENTER,  # confirm to add GCM cam entropy
        BUTTON_PAGE_PREV,  # deny updating label
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.label = "my ID"
    sealed = page.seal_ui(b"plain text", overrides=[OVERRIDE_LABEL])
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert isinstance(sealed, bytes) and len(sealed) > 8
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call("Additional entropy from camera required for AES-GCM"),
            mocker.call("Update KEF ID? my ID", highlight_prefix="?"),
        ]
    )

    print(
        "overrides param is a list, ie: [OVERRIDE_MODE, OVERRIDE_ITERATIONS, OVERRIDE_LABEL]"
    )
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # key is "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # select go
        BUTTON_ENTER,  # confirm key "a"
        BUTTON_ENTER,  # accept proposed iterations
        BUTTON_ENTER,  # accept default mode
        BUTTON_ENTER,  # confirm to add GCM cam entropy
        BUTTON_PAGE_PREV,  # deny updating label
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.label = "my ID"
    sealed = page.seal_ui(
        b"plain text", overrides=[OVERRIDE_MODE, OVERRIDE_ITERATIONS, OVERRIDE_LABEL]
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert isinstance(sealed, bytes) and len(sealed) > 8
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call("Use default PBKDF2 iter.? 100001", highlight_prefix="?"),
            mocker.call("Use default Mode? AES-GCM", highlight_prefix="?"),
            mocker.call("Additional entropy from camera required for AES-GCM"),
            mocker.call("Update KEF ID? my ID", highlight_prefix="?"),
        ]
    )

    mocker.patch(
        "krux.pages.capture_entropy.CameraEntropy.capture",
        mocker.MagicMock(return_value=I_VECTOR),
    )

    print(
        "overrides param is a list, ie: [OVERRIDE_ITERATIONS, OVERRIDE_VERSION, OVERRIDE_LABEL]"
    )
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # key is "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # select go
        BUTTON_ENTER,  # confirm key "a"
        BUTTON_ENTER,  # accept proposed iterations
        BUTTON_PAGE_PREV,  # deny accepting default mode
        BUTTON_PAGE_PREV,  # move to AES-GCM +c
        BUTTON_ENTER,  # select AES-GCM +c
        BUTTON_ENTER,  # accept gathering camera entropy
        BUTTON_PAGE_PREV,  # deny updating label
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.label = "my ID"
    assert page.version == None
    sealed = page.seal_ui(
        b"plain text", overrides=[OVERRIDE_ITERATIONS, OVERRIDE_VERSION, OVERRIDE_LABEL]
    )
    assert page.version == 21
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert isinstance(sealed, bytes) and len(sealed) > 8
    ctx.display.draw_centered_text.assert_has_calls(
        [
            mocker.call("Use default PBKDF2 iter.? 100001", highlight_prefix="?"),
            mocker.call("Use default Mode? AES-GCM", highlight_prefix="?"),
            mocker.call("Additional entropy from camera required for AES-GCM"),
            mocker.call("Update KEF ID? my ID", highlight_prefix="?"),
        ]
    )


def test_kefenvelope_unseal_ui(m5stickv, mocker):
    from krux.pages.encryption_ui import KEFEnvelope
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    sealed_text = b"\x05my ID\x14\x01\x86\xa1OR\xa1\x93l>2q \x9e\x9ddY\xe9\x81\xf0\x07\xf2\x08M\xf65mx\xce\xbe"
    sealed_binary = (
        b"\x05my ID\x14\x01\x86\xa1OR\xa1\x93l>2q \x9e\x9dd\xf7(^v_\xdc\xe2\xdb"
    )

    print("fails w/o valid kef_envelope argument, or .parse() already done")
    ctx = create_ctx(mocker, [])
    page = KEFEnvelope(ctx)
    with pytest.raises(ValueError, match="KEF Envelope not yet parsed"):
        page.unseal_ui()

    print("fails if kef_envelope already parsed and passing it in again")
    ctx = create_ctx(mocker, [])
    page = KEFEnvelope(ctx)
    page.parse(sealed_text)
    with pytest.raises(ValueError, match="KEF Envelope already parsed"):
        page.unseal_ui(sealed_text)

    print(
        "default is to unseal a pre-parsed kef_envelope, prompting to decrypt, returning plaintext"
    )
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # accept decrypt
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # key is "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # select Go
        BUTTON_ENTER,  # confirm key "a"
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.parse(sealed_text)
    plain = page.unseal_ui()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert plain == b"plain text"

    print("can also pass a valid kef_envelope w/o parsing in advance")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    plain = page.unseal_ui(sealed_text)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert plain == b"plain text"

    print("can optionally display the decrypted plaintext")
    BTN_SEQUENCE = BTN_SEQUENCE + [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    plain = page.unseal_ui(sealed_text, display_plain=True)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert plain == b"plain text"
    ctx.display.draw_centered_text.assert_has_calls([mocker.call("plain text")])

    print("can optionally display the decrypted plain hexlified bytes")

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    plain = page.unseal_ui(sealed_binary, display_plain=True)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert plain == b"\xde\xad\xbe\xef"
    ctx.display.draw_centered_text.assert_has_calls([mocker.call("0xdeadbeef")])

    print("passing invalid kef_envelope returns None")
    ctx = create_ctx(mocker, [])
    page = KEFEnvelope(ctx)
    assert page.unseal_ui(b"not a valid kef envelope") == None

    print("if prompt_decrypt and user chooses no: returns None")
    BTN_SEQUENCE = [BUTTON_PAGE_PREV]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.parse(sealed_text)
    assert page.unseal_ui() == None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    print("if user decryption key is not captured: returns None")
    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.parse(sealed_text)
    assert page.unseal_ui() == None
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    print("if decryption key is wrong, raises KeyError(Failed to decrypt)")
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # accept decrypt
        BUTTON_ENTER,  # enter key
        BUTTON_ENTER,  # key is "a"
        BUTTON_ENTER,  # key is "aa"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # select Go
        BUTTON_ENTER,  # confirm key "aa"
    ]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = KEFEnvelope(ctx)
    page.parse(sealed_text)
    with pytest.raises(KeyError, match="Failed to decrypt"):
        page.unseal_ui()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

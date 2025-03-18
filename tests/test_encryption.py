import pytest
from unittest.mock import patch
from Crypto.Cipher import AES
import base64

TEST_KEY = "test key"
TEST_MNEMONIC_ID = "test ID"
ITERATIONS = 1000
TEST_WORDS = (
    "crush inherit small egg include title slogan mom remain blouse boost bonus"
)
ECB_WORDS = "brass creek fuel snack era success impulse dirt caution purity lottery lizard boil festival neither case swift smooth range mail gravity sample never ivory"
CBC_WORDS = "dog guitar hotel random owner gadget salute riot patrol work advice panic erode leader pass cross section laundry elder asset soul scale immune scatter"

ECB_ENCRYPTED_WORDS = b"\xd4\xd5y\xe6]'\xcb\xdb\xe4\x15^\xac\xe0\xc9\xc3\xbc9i\x89e\t\xa3~l\xbf\x98l\xe9\x92\xa9\xe1=3V\xb3\xb1]\xfb|\x13\xf4K_\xdb\xa7d\x92p\x8a-\xbfr\xb5`\xaf\xe5\xc4\xfeP Z\x12\xfbb\x82\x98\xb6)\x83\x99\xba]8R\xbdS\xce>\xdd\xb1"

B64_ECB_ENCRYPTED_WORDS = b"1NV55l0ny9vkFV6s4MnDvDlpiWUJo35sv5hs6ZKp4T0zVrOxXft8E/RLX9unZJJwii2/crVgr+XE/lAgWhL7YoKYtimDmbpdOFK9U84+3bE="

CBC_ENCRYPTED_WORDS = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x92\xdaXV%+\xdb\x12\x85\xa6\x0c\xc8\xee\xc1>h\xd4i\xc1!r\x8d\x97\xd4\xb1V\x0c/\x18D\xff\x99\xd8a\xb8\x85\x81(\x08\xca\x07\xc8\xe0(\x04\xf5\xe1\xf0\xfd\xd9\xd4>E\xdf\x8aV\xb4\x19`\x10\xeaF\x03\x01As\xe5^\raQ\x842\xd6.9z\xa5x\x9a"

B64_CBC_ENCRYPTED_WORDS = b"T1Khk2w+MnEgnp1kBZ7XjpLaWFYlK9sShaYMyO7BPmjUacEhco2X1LFWDC8YRP+Z2GG4hYEoCMoHyOAoBPXh8P3Z1D5F34pWtBlgEOpGAwFBc+VeDWFRhDLWLjl6pXia"

ECB_ENCRYPTED_QR = b"\x07test ID\x00\x00\x00\n*\xe1\x9d\xc5\x82\xc1\x19\x9b\xb7&\xf2?\x03\xc7o\xf6\xaf\x9e\x81#F,Qs\xe6\x1d\xeb\xd1Y\xa0/\xcf"
CBC_ENCRYPTED_QR = b'\x07test ID\x01\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x01\x03`u_\xd7\xab/N\xbc@\x19\xcc\n"\xc5\x8a^3xt\xa4\xb3\x0bK\xca\x8a@\x82\xdaz\xd3'

ECB_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-ECB\nKey iter.: 100000"
)
CBC_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-CBC\nKey iter.: 100000"
)

SEEDS_JSON = """{
    "ecbID": {
        "version": 0,
        "key_iterations": 100000,
        "data": "sMCvAUvVpGSCsXsBl7EBNGPZLymZoyB8eAUHb2TMbarhqD4GJga/SW/AstxIvZz6MR1opXLfF7Pyd+IJBe3E0lDQCkvqytSQfVGnVSeYz+sNfd5T1CXS0/C2zYKTKFL7RTpHd0IXHZ+GQuzX1hoJMHkh0sx0VgorVdDj87ykUQIeC95MS98y/ha2q/vWfLyIZU1hc5VcehzmTA1B6ExMGA=="
    },
    "cbcID": {
        "version": 1,
        "key_iterations": 100000,
        "data": "T1Khk2w+MnEgnp1kBZ7Xjp+66c9sy20J39ffK11XvVAaDSyQybsM6txAwKy/U1iU4KKYRu3ywDDN9q9sWAi1R+y7x4aHwQd0C0rRcW0iDxvWtFyWMKilA0AsDQwvBSgkhf5PQnQ1rfjnKVF75rTrG5vUNF01FRwa9PoM5cq30Yki/hFnWj/4niaeXqgQvIwjSzBNbXgaRLjfoaUyHiu8+zBX25rkpI0PW243fgDEfqI="
    }
}"""

ECB_ONLY_JSON = """{"ecbID": {"version": 0, "key_iterations": 100000, "data": "sMCvAUvVpGSCsXsBl7EBNGPZLymZoyB8eAUHb2TMbarhqD4GJga/SW/AstxIvZz6MR1opXLfF7Pyd+IJBe3E0lDQCkvqytSQfVGnVSeYz+sNfd5T1CXS0/C2zYKTKFL7RTpHd0IXHZ+GQuzX1hoJMHkh0sx0VgorVdDj87ykUQIeC95MS98y/ha2q/vWfLyIZU1hc5VcehzmTA1B6ExMGA=="}}"""
CBC_ONLY_JSON = """{"cbcID": {"version": 1, "key_iterations": 100000, "data": "T1Khk2w+MnEgnp1kBZ7Xjp+66c9sy20J39ffK11XvVAaDSyQybsM6txAwKy/U1iU4KKYRu3ywDDN9q9sWAi1R+y7x4aHwQd0C0rRcW0iDxvWtFyWMKilA0AsDQwvBSgkhf5PQnQ1rfjnKVF75rTrG5vUNF01FRwa9PoM5cq30Yki/hFnWj/4niaeXqgQvIwjSzBNbXgaRLjfoaUyHiu8+zBX25rkpI0PW243fgDEfqI="}}"""
I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=SEEDS_JSON))


# -------------------------


def test_ecb_encryption(m5stickv):
    from krux.encryption import AESCipher

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    encrypted = encryptor.encrypt(TEST_WORDS, AES.MODE_ECB)
    assert encrypted == ECB_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_ECB_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, AES.MODE_ECB)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS


def test_ecb_encryption_fails_duplicated_blocks(m5stickv):
    from krux.encryption import AESCipher

    # test controls
    key, id_, iterations = "a key", "a label", 100000
    plaintext = b"a 16-byte block." * 2
    ciphertext = b"I\x1fD!\x80\x88:\x9e\xc7\xbd\x8a<\x9d\x8f\xea(I\x1fD!\x80\x88:\x9e\xc7\xbd\x8a<\x9d\x8f\xea("

    cryptor = AESCipher(key, id_, iterations)
    err = "Duplicate blocks in ECB mode"
    with pytest.raises(ValueError, match=err):
        cryptor.encrypt(plaintext, AES.MODE_ECB)

    # but can still decrypt if previously encrypted
    assert cryptor.decrypt(ciphertext, AES.MODE_ECB) == plaintext


def test_cbc_encryption(m5stickv):
    from krux.encryption import AESCipher
    from Crypto.Random import get_random_bytes

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    iv = I_VECTOR
    encrypted = encryptor.encrypt(TEST_WORDS, AES.MODE_CBC, iv)
    assert encrypted == CBC_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, AES.MODE_CBC)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS


def test_cbc_iv_use(m5stickv):
    from krux.encryption import AESCipher
    from Crypto.Random import get_random_bytes

    SECOND_IV = b"\x8e\xc8b\x8f\xe2\xa8`\xaa\x06d\xe8\xe7\xaa.0\x03"
    CBC_ENCRYPTED_WORDS_SECOND_IV = b"\x8e\xc8b\x8f\xe2\xa8`\xaa\x06d\xe8\xe7\xaa.0\x03\xc0N7\xbd'u\xc5Z\x97\xde=\x10\xeaO\xf4x\xb5\xe6\x10l\xcfu\xef\x9e\x94\x03L-\xdc\xff\xa3m\xf0i\xd4\xe2\n{9G\x17\xbf.\x96\xba\x1a\x07\xackK9\x90-\xb6sf1\x01Y+\xa6\x80c/yO\x93'd\x8b\rnru\xe7\x17\xb0\x01\x9a\x9b"
    B64_CBC_ENCRYPTED_WORDS_SECOND_IV = b"jshij+KoYKoGZOjnqi4wA8BON70ndcVal949EOpP9Hi15hBsz3XvnpQDTC3c/6Nt8GnU4gp7OUcXvy6WuhoHrGtLOZAttnNmMQFZK6aAYy95T5MnZIsNbnJ15xewAZqb"

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    iv = I_VECTOR
    encrypted = encryptor.encrypt(TEST_WORDS, AES.MODE_CBC, iv)
    assert encrypted == CBC_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, AES.MODE_CBC)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS

    # Encrypt again with same data except for the IV
    iv = SECOND_IV
    encrypted = encryptor.encrypt(TEST_WORDS, AES.MODE_CBC, iv)
    assert encrypted == CBC_ENCRYPTED_WORDS_SECOND_IV

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS_SECOND_IV

    decrypted = encryptor.decrypt(encrypted, AES.MODE_CBC)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS


def test_list_mnemonic_storage(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    flash_list = storage.list_mnemonics(sd_card=False)
    sd_list = storage.list_mnemonics(sd_card=True)
    assert "ecbID" and "cbcID" in flash_list
    assert "ecbID" and "cbcID" in sd_list


def test_load_decrypt_ecb(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "ecbID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "ecbID", sd_card=True)
    assert words == ECB_WORDS
    assert words_sd == ECB_WORDS


def test_load_decrypt_cbc(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "cbcID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "cbcID", sd_card=True)
    assert words == CBC_WORDS
    assert words_sd == CBC_WORDS


def test_encrypt_ecb_flash(m5stickv, mocker):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.encryption.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-ECB"
        success = storage.store_encrypted(TEST_KEY, "ecbID", ECB_WORDS, sd_card=False)
    assert success is True
    m().write.assert_called_once_with(ECB_ONLY_JSON)


def test_encrypt_cbc_flash(m5stickv, mocker):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.encryption.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-CBC"
        success = storage.store_encrypted(
            TEST_KEY, "cbcID", CBC_WORDS, sd_card=False, i_vector=I_VECTOR
        )
    assert success is True
    m().write.assert_called_once_with(CBC_ONLY_JSON)


def test_encrypt_ecb_sd(m5stickv, mocker, mock_file_operations):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.sd_card.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-ECB"
        success = storage.store_encrypted(TEST_KEY, "ecbID", ECB_WORDS, sd_card=True)
    assert success is True
    m().write.assert_called_once_with(ECB_ONLY_JSON)


def test_encrypt_cbc_sd(m5stickv, mocker, mock_file_operations):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.sd_card.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-CBC"
        success = storage.store_encrypted(
            TEST_KEY, "cbcID", CBC_WORDS, sd_card=True, i_vector=I_VECTOR
        )
    assert success is True
    m().write.assert_called_once_with(CBC_ONLY_JSON)


def test_delete_from_flash(m5stickv, mocker):
    from krux.encryption import MnemonicStorage

    # Loads a file with 2 mnemonics, one with ID="ecbID", other with ID="cbcID"
    # Deletes "ecbID" and assures only "cbcID" is left
    with patch("krux.encryption.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        storage = MnemonicStorage()
        storage.del_mnemonic("ecbID")
    m().write.assert_called_once_with(CBC_ONLY_JSON)


def test_delete_from_sd(m5stickv, mocker, mock_file_operations):
    from krux.encryption import MnemonicStorage

    # Loads a file with 2 mnemonics, one with ID="ecbID", other with ID="cbcID"
    # Deletes "ecbID" and assures only "cbcID" is left
    with patch("krux.sd_card.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        storage = MnemonicStorage()
        storage.del_mnemonic("ecbID", sd_card=True)
    # Calculate padding size
    padding_size = len(SEEDS_JSON) - len(CBC_ONLY_JSON)
    m().write.assert_called_once_with(CBC_ONLY_JSON + " " * padding_size)


def test_create_ecb_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings

    Settings().encryption.version = "AES-ECB"
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS)
    assert qr_data == ECB_ENCRYPTED_QR


def test_create_cbc_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings

    Settings().encryption.version = "AES-CBC"
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS, I_VECTOR)
    print(qr_data)
    assert qr_data == CBC_ENCRYPTED_QR


def test_decode_ecb_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from embit import bip39

    encrypted_qr = EncryptedQRCode()
    public_data = encrypted_qr.public_data(ECB_ENCRYPTED_QR)
    assert public_data == ECB_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS


def test_decode_cbc_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from embit import bip39

    encrypted_qr = EncryptedQRCode()
    public_data = encrypted_qr.public_data(CBC_ENCRYPTED_QR)
    print(public_data)
    assert public_data == CBC_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS


def test_customize_pbkdf2_iterations_create_and_decode(m5stickv):
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings
    from embit import bip39

    print("case Encode: customize_pbkdf2_iterations")
    Settings().encryption.version = "AES-ECB"
    Settings().encryption.pbkdf2_iterations = 99999
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS)
    print(qr_data)
    print(ECB_ENCRYPTED_QR)

    print("case Decode: customize_pbkdf2_iterations")
    public_data = encrypted_qr.public_data(qr_data)
    assert public_data == (
        "Encrypted QR Code:\nID: test ID\nVersion: AES-ECB\nKey iter.: 90000"
    )
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS


def test_kef_encoding_is_faithful(m5stickv):
    from krux.encryption import kef_encode, kef_decode

    test_cases = (ECB_ENCRYPTED_QR, CBC_ENCRYPTED_QR)

    for encoded in test_cases:
        id_, version, iterations, ciphertext = kef_decode(encoded)
        assert kef_encode(id_, version, iterations, ciphertext) == encoded


def test_kef_encode_exceptions(m5stickv):
    from krux.encryption import kef_encode

    ten_k = 10000
    valid_ids = (
        "",
        "My Mnemonic",
        "ID can be empty or as long as 255 utf-8 characters, but not longer\nA purely peer-to-peer version of electronic cash would allow online\npayments to be sent directly from one party to another without going through a\nfinancial institution. Digital signatures",
    )
    valid_versions = (0, 1)
    valid_iterations = (ten_k, 50 * ten_k, ten_k + 1, 2**24 - 1, ten_k * ten_k)
    valid_ciphertexts = (ECB_ENCRYPTED_QR[-32:], CBC_ENCRYPTED_QR[-48:])

    # test individual exceptions against other valid params
    for id_ in valid_ids:
        for version in valid_versions:
            for iterations in valid_iterations:
                for ciphertext in valid_ciphertexts:

                    # ID is limited to length < 256 utf-8
                    err = "Invalid ID"
                    for invalid in (None, 21, ("Too Long! " * 26)[:256]):
                        with pytest.raises(ValueError, match=err):
                            kef_encode(invalid, version, iterations, ciphertext)

                    # Version must be 0-255, and supported
                    err = "Invalid version"
                    for invalid in (None, -1, 0.5, "0", 256, 2, 3):
                        with pytest.raises(ValueError, match=err):
                            kef_encode(id_, invalid, iterations, ciphertext)

                    # Iterations: used for key stretching
                    err = "Invalid iterations"
                    for invalid in (
                        None,
                        -ten_k,
                        "10000",
                        ten_k + 0.5,
                        0,
                        1,
                        ten_k - 1,
                        2**24,
                        ten_k * ten_k + 1,
                    ):
                        with pytest.raises(ValueError, match=err):
                            kef_encode(id_, version, invalid, ciphertext)

                    # Ciphertext must be bytes
                    err = "Ciphertext is not bytes"
                    invalid = (b"\x00" * 32).decode()
                    with pytest.raises(ValueError, match=err):
                        kef_encode(id_, version, iterations, invalid)

                    # ...and aligned
                    err = "Ciphertext is not aligned"
                    for extra in range(1, 16):
                        invalid = ciphertext + (b"\x00" * extra)
                        with pytest.raises(ValueError, match=err):
                            kef_encode(id_, version, iterations, invalid)

                    # ...and not too short
                    err = "Ciphertext is too short"
                    invalid = ciphertext[:16]
                    with pytest.raises(ValueError, match=err):
                        kef_encode(id_, version, iterations, invalid)


def test_kef_interpretation_of_iterations(m5stickv):
    from krux.encryption import kef_encode, kef_decode

    # int to 3-byte big-endian
    def i2b(an_int):
        return an_int.to_bytes(3, "big")

    ten_k = 10000

    # mock values so that iterations will be at bytes[6:9]
    id_ = "test"
    version = 0
    ciphertext = b"\x00" * 32

    # if (iterations % 10000 == 0) they are serialized divided by 10000
    for iterations in (ten_k, ten_k * 10, ten_k * 50, ten_k * ten_k):
        encoded = kef_encode(id_, version, iterations, ciphertext)
        assert encoded[6:9] == i2b(iterations // 10000)
        assert kef_decode(encoded)[2] == iterations

    # if (iterations % 10000 != 0) they are serialized as the same value
    for iterations in (ten_k + 1, ten_k * 10 + 1, ten_k * 50 + 1, 2**24 - 1):
        encoded = kef_encode(id_, version, iterations, ciphertext)
        assert encoded[6:9] == i2b(iterations)
        assert kef_decode(encoded)[2] == iterations


def test_kef_decode_exceptions(m5stickv):
    from krux.encryption import kef_decode

    test_cases = (ECB_ENCRYPTED_QR, CBC_ENCRYPTED_QR)

    # ID must be utf-8 encoded
    err = "Invalid ID encoding"
    for encoded in test_cases:
        encoded = encoded[:1] + b"\xff" + encoded[2:]
        with pytest.raises(ValueError, match=err):
            kef_decode(encoded)

    # Ciphertext is aligned on 16-byte blocks
    err = "Ciphertext is not aligned"
    for encoded in test_cases:
        for i in range(15):
            encoded = encoded[:-1]
            with pytest.raises(ValueError, match=err):
                kef_decode(encoded)

    # Ciphertext is at least 2 blocks (payload and checksum)
    err = "Ciphertext is too short"
    encoded = ECB_ENCRYPTED_QR[:-16]  # 24w ECB is 32 bytes w/ checksum
    with pytest.raises(ValueError, match=err):
        kef_decode(encoded)
    encoded = CBC_ENCRYPTED_QR[:-32]  # 24w CBC is 48 bytes w/ iv+checksum
    with pytest.raises(ValueError, match=err):
        kef_decode(encoded)

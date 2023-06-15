import sys
from unittest import mock
from Crypto.Cipher import AES
import base64

if "ucryptolib" not in sys.modules:
    sys.modules["ucryptolib"] = mock.MagicMock(
        aes=AES.new, MODE_ECB=AES.MODE_ECB, MODE_CBC=AES.MODE_CBC
    )

TEST_KEY = "test key"
TEST_MNEMONIC_ID = "test ID"
ITERATIONS = 1000
TEST_WORDS = (
    "crush inherit small egg include title slogan mom remain blouse boost bonus"
)
ECB_ENCRYPTED_WORDS = "1NV55l0ny9vkFV6s4MnDvDlpiWUJo35sv5hs6ZKp4T0zVrOxXft8E/RLX9unZJJwii2/crVgr+XE/lAgWhL7YoKYtimDmbpdOFK9U84+3bE="
CBC_ENCRYPTED_WORDS = "pJy/goOD11Nulfzd07PPKCOuPWsy2/tONwHrpY/AihVDcGxmIgzasyhs3fY90E0khrCqqgCvzjukMCdxif2OljKDxZQPGoVNeJKqE4nu5fq5023WhO1yKtAcPt3mML6Q"


def test_ecb_encryption(mocker, m5stickv):
    from krux.encryption import AESCipher

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    encrypted = encryptor.encrypt(TEST_WORDS, AES.MODE_ECB).decode("utf-8")
    assert encrypted == ECB_ENCRYPTED_WORDS
    decrypted = encryptor.decrypt(base64.b64decode(encrypted), AES.MODE_ECB)
    assert decrypted == TEST_WORDS


def test_cbc_encryption(mocker, m5stickv):
    from krux.encryption import AESCipher
    from Crypto.Random import get_random_bytes

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    iv = get_random_bytes(AES.block_size)
    encrypted = encryptor.encrypt(TEST_WORDS, AES.MODE_CBC, iv).decode("utf-8")
    assert encrypted == CBC_ENCRYPTED_WORDS
    data = base64.b64decode(encrypted)
    encrypted_mnemonic = data[AES.block_size :]
    i_vector = data[: AES.block_size]
    decrypted = encryptor.decrypt(encrypted_mnemonic, AES.MODE_CBC, i_vector)
    assert decrypted == TEST_WORDS

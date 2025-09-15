import pytest
from unittest.mock import patch
from Crypto.Cipher import AES
import base64

TEST_KEY = "test key"
TEST_MNEMONIC_ID = "test ID"
ITERATIONS = 1000  # this should be at least 10k, but remains 1K for legacy tests
TEST_WORDS = (
    "crush inherit small egg include title slogan mom remain blouse boost bonus"
)

ECB_WORDS = "brass creek fuel snack era success impulse dirt caution purity lottery lizard boil festival neither case swift smooth range mail gravity sample never ivory"
CBC_WORDS = "dog guitar hotel random owner gadget salute riot patrol work advice panic erode leader pass cross section laundry elder asset soul scale immune scatter"
CTR_WORDS = "unable point minimum sun peanut habit ready high nothing cherry silver eagle pen fabric list collect impact loan casual lyrics pig train middle screen"
GCM_WORDS = "alone lady rib jazz hold honey stem upgrade pass elite cinnamon joy fiction either dolphin knife nominee seed eternal make game unusual rigid pass"

ECB_ENTROPY = b"\x1b&ew\xe6\x84\xc5\xb0\x9c\x89\xf5$\xb5\xca\x10Aa\x90\xaae\t\x19\xdb\xd9\x9e\xc7C\x16a~%C"
CBC_ENTROPY = b"@\x8c\xf9\xb8\xd8\xd9\xe2\xbdo\xb5\xd1\xa1?\xb0\x10O\xd4\xc8\xfd()\xa0\xc2\xaf\xb5\x1d\x06\xdc\xfb\x80\x1cn"
CTR_ENTROPY = b'\xecT\xea4l\xaa\x1e\xd0l\xb3\\\x96\xc4\xef#"\x8a&\xa2\xe0\x99lq\xd0`\x8e\xc2\xbaI\xce#\x16'
GCM_ENTROPY = b"\x06\xef\x92\xe3\xbb\xb6\xc8\xdauWu\xa0\xa9\x00\xa4<E\\\x8e\x103\xdd\x95\xf8]6CE\xf3\xdc\xae}"

ECB_ENCRYPTED_WORDS = b"\xd4\xd5y\xe6]'\xcb\xdb\xe4\x15^\xac\xe0\xc9\xc3\xbc9i\x89e\t\xa3~l\xbf\x98l\xe9\x92\xa9\xe1=3V\xb3\xb1]\xfb|\x13\xf4K_\xdb\xa7d\x92p\x8a-\xbfr\xb5`\xaf\xe5\xc4\xfeP Z\x12\xfbbQ9G'\xael\x9d*F\xafn4\t\x7fE\xb2K\xc1\xbaB\xfa\xb7J6\xefu\x95\xa9\x9c\xe8\x14\x88"
# OLDECB_ENCRYPTED_WORDS = b"\xd4\xd5y\xe6]'\xcb\xdb\xe4\x15^\xac\xe0\xc9\xc3\xbc9i\x89e\t\xa3~l\xbf\x98l\xe9\x92\xa9\xe1=3V\xb3\xb1]\xfb|\x13\xf4K_\xdb\xa7d\x92p\x8a-\xbfr\xb5`\xaf\xe5\xc4\xfeP Z\x12\xfbb\x82\x98\xb6)\x83\x99\xba]8R\xbdS\xce>\xdd\xb1"
CBC_ENCRYPTED_WORDS = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x92\xdaXV%+\xdb\x12\x85\xa6\x0c\xc8\xee\xc1>h\xd4i\xc1!r\x8d\x97\xd4\xb1V\x0c/\x18D\xff\x99\xd8a\xb8\x85\x81(\x08\xca\x07\xc8\xe0(\x04\xf5\xe1\xf0\xfd\xd9\xd4>E\xdf\x8aV\xb4\x19`\x10\xeaF\x03\x01\x16\x9e\x07&+|\xcb\x15as\x92y\xa1>\xd0\xc8\xca\xb0YX\x08\xda>\xf0\xca6=\xc9cR\xb5j"
# OLDCBC_ENCRYPTED_WORDS = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x92\xdaXV%+\xdb\x12\x85\xa6\x0c\xc8\xee\xc1>h\xd4i\xc1!r\x8d\x97\xd4\xb1V\x0c/\x18D\xff\x99\xd8a\xb8\x85\x81(\x08\xca\x07\xc8\xe0(\x04\xf5\xe1\xf0\xfd\xd9\xd4>E\xdf\x8aV\xb4\x19`\x10\xeaF\x03\x01As\xe5^\raQ\x842\xd6.9z\xa5x\x9a"

B64_ECB_ENCRYPTED_WORDS = b"1NV55l0ny9vkFV6s4MnDvDlpiWUJo35sv5hs6ZKp4T0zVrOxXft8E/RLX9unZJJwii2/crVgr+XE/lAgWhL7YlE5RyeubJ0qRq9uNAl/RbJLwbpC+rdKNu91lamc6BSI"
# OLDB64_ECB_ENCRYPTED_WORDS = b"1NV55l0ny9vkFV6s4MnDvDlpiWUJo35sv5hs6ZKp4T0zVrOxXft8E/RLX9unZJJwii2/crVgr+XE/lAgWhL7YoKYtimDmbpdOFK9U84+3bE="
B64_CBC_ENCRYPTED_WORDS = b"T1Khk2w+MnEgnp1kBZ7XjpLaWFYlK9sShaYMyO7BPmjUacEhco2X1LFWDC8YRP+Z2GG4hYEoCMoHyOAoBPXh8P3Z1D5F34pWtBlgEOpGAwEWngcmK3zLFWFzknmhPtDIyrBZWAjaPvDKNj3JY1K1ag=="
# OLDB64_CBC_ENCRYPTED_WORDS = b"T1Khk2w+MnEgnp1kBZ7XjpLaWFYlK9sShaYMyO7BPmjUacEhco2X1LFWDC8YRP+Z2GG4hYEoCMoHyOAoBPXh8P3Z1D5F34pWtBlgEOpGAwFBc+VeDWFRhDLWLjl6pXia"

ECB_ENCRYPTED_ENTROPY_CKSUM = b"\x0cc\t\x7f\x90\xec\x9b$M\x88\xef4}\xc4\x8cW\xbc\xc4\xe0\x98\xdfN\x7f\xe4i@ \xf2\x15\xf8\x92rG\xe6\xf6\xc4\xbb\xb0h\xffL\xaaev\x8d\x1e7t"
CBC_ENCRYPTED_ENTROPY_CKSUM = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x13\x90d\xaa\xd6\xb8\xb4\xaas\x01{kj\xb6\xba\xa4\x93\x110\x1f\x0f\xbbW)\xaai\xaa\x13X\n@dM\xca{Y\x9d%B\xa2G\xde=\x8dk\xb8f\xc6"

B64_ECB_ENCRYPTED_ENTROPY_CKSUM = (
    b"DGMJf5DsmyRNiO80fcSMV7zE4JjfTn/kaUAg8hX4knJH5vbEu7Bo/0yqZXaNHjd0"
)
B64_CBC_ENCRYPTED_ENTROPY_CKSUM = b"T1Khk2w+MnEgnp1kBZ7XjhOQZKrWuLSqcwF7a2q2uqSTETAfD7tXKappqhNYCkBkTcp7WZ0lQqJH3j2Na7hmxg=="

ECB_ENCRYPTED_QR = (
    b"\x07test ID\x05\x00\x00\n*\xe1\x9d\xc5\x82\xc1\x19\x9b\xb7&\xf2?\x03\xc7o\xf6R>#"
)
OLDECB_ENCRYPTED_QR = b"\x07test ID\x00\x00\x00\n*\xe1\x9d\xc5\x82\xc1\x19\x9b\xb7&\xf2?\x03\xc7o\xf6\xaf\x9e\x81#F,Qs\xe6\x1d\xeb\xd1Y\xa0/\xcf"
CBC_ENCRYPTED_QR = b'\x07test ID\x0a\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x01\x03`u_\xd7\xab/N\xbc@\x19\xcc\n"\xc5C\xfa\x96\x90'
OLDCBC_ENCRYPTED_QR = b'\x07test ID\x01\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x01\x03`u_\xd7\xab/N\xbc@\x19\xcc\n"\xc5\x8a^3xt\xa4\xb3\x0bK\xca\x8a@\x82\xdaz\xd3'
CTR_ENCRYPTED_QR = b"\x07test ID\x0f\x00\x00\nd\xc2\xd8\xb7U\xe8\x02~\xda}\xcdO\x967\xbf\xc5%\xa7\x18\x11\xf4\xec\xfd=\xbaY\xbe|\x97\xe2;\xabb\xfa.L\xbc$]'\xc9\xcc#\xba\xcb\x84\xe4J"
GCM_ENCRYPTED_QR = b"\x07test ID\x14\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\xbf\xb7vo]]\x8aO\x90\x8e\x86\xe784L\x02]\x8f\xedT"

ECB_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-ECB\nPBKDF2 iter.: 100000"
)
OLDECB_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-ECB v1\nPBKDF2 iter.: 100000"
)
CBC_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-CBC\nPBKDF2 iter.: 100000"
)
OLDCBC_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-CBC v1\nPBKDF2 iter.: 100000"
)
CTR_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-CTR\nPBKDF2 iter.: 100000"
)
GCM_QR_PUBLIC_DATA = (
    "Encrypted QR Code:\nID: test ID\nVersion: AES-GCM\nPBKDF2 iter.: 100000"
)


KEF_ENVELOPE_ECB = b"\x08KEFecbID\x05\x00\x00\n\xb8\xd9>\xc1\xcf\xf6\xc04P\x02\xa2Z\xea-Ev\xe7\x16f\xbf\x1dY\xdfiP\x19W\xa2\xb0\xe5;\xbbP\xf4\xf7"
KEF_ENVELOPE_CBC = b"\x08KEFcbcID\n\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8el\x84S\xe8\x8d\x82\xc0\xe2\x1baX{\xf6gaR#$:~nJS\xcdM.$?\x99\x00\xcc\xe3\xa5\xea\xb5\xa2"
KEF_ENVELOPE_CTR = b"\x08KEFctrID\x0f\x00\x00\ni$\x05\xdcn\xa8\xbf\x1f,\xe2xyb\xd3\xf6\xcc7\x88\xfbF=\x9e\xfdi\xb7\xbb\x1aMXey\x1a\xa1\xc12Q\xab\nAn]\xe8\xa2\xa9\xe8X\x1c\x0c"
KEF_ENVELOPE_GCM = b"\x08KEFgcmID\x14\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\xbf\xa3\x0c?\xd7\xfa\xff,%\x8d\xf3\xee\x88\x81N\x08\xd3\xb7\xd0[&\x1df\x01\x0b\xac\xd6\xb6\xc5\x17\x80\xf8\x1c\x7f\x92W"


# Must maintain old in-the-wild versions of cipher-payloads in seeds.json to ensure recoverable
KEF_ECBENTROPY_ONLY_JSON = '{"KEFecbID": {"b64_kef": "CEtFRmVjYklEBQAACrjZPsHP9sA0UAKiWuotRXbnFma/HVnfaVAZV6Kw5Tu7UPT3"}}'
KEF_CBCENTROPY_ONLY_JSON = '{"KEFcbcID": {"b64_kef": "CEtFRmNiY0lECgAACk9SoZNsPjJxIJ6dZAWe145shFPojYLA4hthWHv2Z2FSIyQ6fm5KU81NLiQ/mQDM46XqtaI="}}'
KEF_CTRENTROPY_ONLY_JSON = '{"KEFctrID": {"b64_kef": "CEtFRmN0cklEDwAACmkkBdxuqL8fLOJ4eWLT9sw3iPtGPZ79abe7Gk1YZXkaocEyUasKQW5d6KKp6FgcDA=="}}'
KEF_GCMENTROPY_ONLY_JSON = '{"KEFgcmID": {"b64_kef": "CEtFRmdjbUlEFAAACk9SoZNsPjJxIJ6dZL+jDD/X+v8sJY3z7oiBTgjTt9BbJh1mAQus1rbFF4D4HH+SVw=="}}'
OLD_ECBWORDS_ONLY_JSON = '{"ecbID": {"version": 0, "key_iterations": 100000, "data": "sMCvAUvVpGSCsXsBl7EBNGPZLymZoyB8eAUHb2TMbarhqD4GJga/SW/AstxIvZz6MR1opXLfF7Pyd+IJBe3E0lDQCkvqytSQfVGnVSeYz+sNfd5T1CXS0/C2zYKTKFL7RTpHd0IXHZ+GQuzX1hoJMHkh0sx0VgorVdDj87ykUQIeC95MS98y/ha2q/vWfLyIZU1hc5VcehzmTA1B6ExMGA=="}}'
OLD_CBCWORDS_ONLY_JSON = '{"cbcID": {"version": 1, "key_iterations": 100000, "data": "T1Khk2w+MnEgnp1kBZ7Xjp+66c9sy20J39ffK11XvVAaDSyQybsM6txAwKy/U1iU4KKYRu3ywDDN9q9sWAi1R+y7x4aHwQd0C0rRcW0iDxvWtFyWMKilA0AsDQwvBSgkhf5PQnQ1rfjnKVF75rTrG5vUNF01FRwa9PoM5cq30Yki/hFnWj/4niaeXqgQvIwjSzBNbXgaRLjfoaUyHiu8+zBX25rkpI0PW243fgDEfqI="}}'
SEEDS_JSON = (
    "{"
    + ", ".join(
        [
            KEF_ECBENTROPY_ONLY_JSON[1:-1],
            KEF_CBCENTROPY_ONLY_JSON[1:-1],
            KEF_CTRENTROPY_ONLY_JSON[1:-1],
            KEF_GCMENTROPY_ONLY_JSON[1:-1],
            OLD_ECBWORDS_ONLY_JSON[1:-1],
            OLD_CBCWORDS_ONLY_JSON[1:-1],
        ]
    )
    + "}"
)

I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=SEEDS_JSON))


# -------------------------


def test_krux_encryption_settings_mode_names_constant(m5stickv):
    from krux.encryption import kef
    from krux.krux_settings import EncryptionSettings

    for name, mode_number in kef.MODE_NUMBERS.items():
        if mode_number is not None:
            assert EncryptionSettings().MODE_NAMES[mode_number] == name


def test_ecb_encryption(m5stickv):
    from krux.encryption import kef

    version = 0  # AES.MODE_ECB

    encryptor = kef.Cipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    encrypted = encryptor.encrypt(TEST_WORDS.encode(), version)
    assert encrypted == ECB_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_ECB_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, version)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS

    encrypted = encryptor.encrypt(ECB_ENTROPY, version)
    assert encryptor.decrypt(encrypted, version) == ECB_ENTROPY


def test_cbc_encryption(m5stickv):
    from krux.encryption import kef

    version = 1  # AES.MODE_CBC

    encryptor = kef.Cipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    iv = I_VECTOR
    encrypted = encryptor.encrypt(TEST_WORDS.encode(), version, iv)
    assert encrypted == CBC_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, version)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS

    encrypted = encryptor.encrypt(CBC_ENTROPY, version, iv)
    assert encryptor.decrypt(encrypted, version) == CBC_ENTROPY


def test_cbc_iv_use(m5stickv):
    from krux.encryption import kef

    SECOND_IV = b"\x8e\xc8b\x8f\xe2\xa8`\xaa\x06d\xe8\xe7\xaa.0\x03"
    CBC_ENCRYPTED_WORDS_SECOND_IV = b"\x8e\xc8b\x8f\xe2\xa8`\xaa\x06d\xe8\xe7\xaa.0\x03\xc0N7\xbd'u\xc5Z\x97\xde=\x10\xeaO\xf4x\xb5\xe6\x10l\xcfu\xef\x9e\x94\x03L-\xdc\xff\xa3m\xf0i\xd4\xe2\n{9G\x17\xbf.\x96\xba\x1a\x07\xackK9\x90-\xb6sf1\x01Y+\xa6\x80c/\x1f#[:\xb0,K\xa7M\x90\xa2\xe6d\x8aX\xe6~\x13\xc3\x8d\x82\x1f\xe0\xbf\x8d\r0\xfa\xc7\xde\x18'"
    # OLDCBC_ENCRYPTED_WORDS_SECOND_IV = b"\x8e\xc8b\x8f\xe2\xa8`\xaa\x06d\xe8\xe7\xaa.0\x03\xc0N7\xbd'u\xc5Z\x97\xde=\x10\xeaO\xf4x\xb5\xe6\x10l\xcfu\xef\x9e\x94\x03L-\xdc\xff\xa3m\xf0i\xd4\xe2\n{9G\x17\xbf.\x96\xba\x1a\x07\xackK9\x90-\xb6sf1\x01Y+\xa6\x80c/yO\x93'd\x8b\rnru\xe7\x17\xb0\x01\x9a\x9b"
    B64_CBC_ENCRYPTED_WORDS_SECOND_IV = b"jshij+KoYKoGZOjnqi4wA8BON70ndcVal949EOpP9Hi15hBsz3XvnpQDTC3c/6Nt8GnU4gp7OUcXvy6WuhoHrGtLOZAttnNmMQFZK6aAYy8fI1s6sCxLp02QouZkiljmfhPDjYIf4L+NDTD6x94YJw=="
    # OLDB64_CBC_ENCRYPTED_WORDS_SECOND_IV = b"jshij+KoYKoGZOjnqi4wA8BON70ndcVal949EOpP9Hi15hBsz3XvnpQDTC3c/6Nt8GnU4gp7OUcXvy6WuhoHrGtLOZAttnNmMQFZK6aAYy95T5MnZIsNbnJ15xewAZqb"

    version = 1

    encryptor = kef.Cipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    iv = I_VECTOR
    encrypted = encryptor.encrypt(TEST_WORDS.encode(), version, iv)
    assert encrypted == CBC_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, version)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS

    # Encrypt again with same data except for the IV
    iv = SECOND_IV
    encrypted = encryptor.encrypt(TEST_WORDS.encode(), version, iv)
    print("iv: {}, encrypted: {}".format(iv, encrypted))
    assert encrypted == CBC_ENCRYPTED_WORDS_SECOND_IV

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS_SECOND_IV

    decrypted = encryptor.decrypt(encrypted, version)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS


# TODO: correct above tests for all ecb and cbc versions
# TODO: fill in similar test_ctr_encryption and test_gcm_encryption


def test_list_mnemonic_storage(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    flash_list = storage.list_mnemonics(sd_card=False)
    sd_list = storage.list_mnemonics(sd_card=True)
    assert "ecbID" and "cbcID" in flash_list  # legacy seeds.json
    assert "ecbID" and "cbcID" in sd_list  # legacy seeds.json
    assert "KEFecbID" and "KEFcbcID" in flash_list
    assert "KEFecbID" and "KEFcbcID" in sd_list


def test_load_decrypt_ecb(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "ecbID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "ecbID", sd_card=True)
    assert words == ECB_WORDS
    assert words_sd == ECB_WORDS
    assert ECB_WORDS == storage.decrypt(TEST_KEY, "KEFecbID", sd_card=False)
    assert ECB_WORDS == storage.decrypt(TEST_KEY, "KEFecbID", sd_card=True)

    # returns silently with wrong key
    assert storage.decrypt("wrong", "ecbID", sd_card=False) == None
    assert storage.decrypt("wrong", "ecbID", sd_card=True) == None


def test_load_decrypt_cbc(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "cbcID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "cbcID", sd_card=True)
    assert words == CBC_WORDS
    assert words_sd == CBC_WORDS
    assert CBC_WORDS == storage.decrypt(TEST_KEY, "KEFcbcID", sd_card=False)
    assert CBC_WORDS == storage.decrypt(TEST_KEY, "KEFcbcID", sd_card=True)

    # returns silently with wrong key
    assert storage.decrypt("wrong", "cbcID", sd_card=False) == None
    assert storage.decrypt("wrong", "cbcID", sd_card=True) == None


def test_load_decrypt_gcm(m5stickv, mock_file_operations):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "KEFgcmID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "KEFgcmID", sd_card=True)
    assert words == GCM_WORDS
    assert words_sd == GCM_WORDS

    # returns silently with wrong key
    assert storage.decrypt("wrong", "KEFgcmID", sd_card=False) == None
    assert storage.decrypt("wrong", "KEFgcmID", sd_card=True) == None


def test_encrypt_ecb_flash(m5stickv, mocker):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.encryption.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-ECB"
        success = storage.store_encrypted_kef(
            "KEFecbID", KEF_ENVELOPE_ECB, sd_card=False
        )
    assert success is True
    m().write.assert_called_once_with(KEF_ECBENTROPY_ONLY_JSON)


def test_encrypt_cbc_flash(m5stickv, mocker):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.encryption.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-CBC"
        success = storage.store_encrypted_kef(
            "KEFcbcID", KEF_ENVELOPE_CBC, sd_card=False
        )
    assert success is True
    m().write.assert_called_once_with(KEF_CBCENTROPY_ONLY_JSON)


def test_encrypt_ctr_flash(m5stickv, mocker):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.encryption.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-CTR"
        success = storage.store_encrypted_kef(
            "KEFctrID", KEF_ENVELOPE_CTR, sd_card=False
        )
    assert success is True
    m().write.assert_called_once_with(KEF_CTRENTROPY_ONLY_JSON)


def test_encrypt_gcm_flash(m5stickv, mocker):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.encryption.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-GCM"
        success = storage.store_encrypted_kef(
            "KEFgcmID", KEF_ENVELOPE_GCM, sd_card=False
        )
    assert success is True
    m().write.assert_called_once_with(KEF_GCMENTROPY_ONLY_JSON)


def test_encrypt_ecb_sd(m5stickv, mocker, mock_file_operations):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.sd_card.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-ECB"
        success = storage.store_encrypted_kef(
            "KEFecbID", KEF_ENVELOPE_ECB, sd_card=True
        )
    assert success is True
    m().write.assert_called_once_with(KEF_ECBENTROPY_ONLY_JSON)


def test_encrypt_cbc_sd(m5stickv, mocker, mock_file_operations):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.sd_card.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-CBC"
        success = storage.store_encrypted_kef(
            "KEFcbcID", KEF_ENVELOPE_CBC, sd_card=True
        )
    assert success is True
    m().write.assert_called_once_with(KEF_CBCENTROPY_ONLY_JSON)


def test_encrypt_ctr_sd(m5stickv, mocker, mock_file_operations):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.sd_card.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-CTR"
        success = storage.store_encrypted_kef(
            "KEFctrID", KEF_ENVELOPE_CTR, sd_card=True
        )
    assert success is True
    m().write.assert_called_once_with(KEF_CTRENTROPY_ONLY_JSON)


def test_encrypt_gcm_sd(m5stickv, mocker, mock_file_operations):
    from krux.krux_settings import Settings
    from krux.encryption import MnemonicStorage

    with patch("krux.sd_card.open", new=mocker.mock_open(read_data="{}")) as m:
        storage = MnemonicStorage()
        Settings().encryption.version = "AES-GCM"
        success = storage.store_encrypted_kef(
            "KEFgcmID", KEF_ENVELOPE_GCM, sd_card=True
        )
    assert success is True
    m().write.assert_called_once_with(KEF_GCMENTROPY_ONLY_JSON)


def test_delete_from_flash(m5stickv, mocker):
    from krux.encryption import MnemonicStorage

    # Loads a seeds.json file with many entries
    # Deletes "KEFecbID" and assures the rest remain
    with patch("krux.encryption.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        storage = MnemonicStorage()
        storage.del_mnemonic("KEFecbID")
    expected = SEEDS_JSON.replace(KEF_ECBENTROPY_ONLY_JSON[1:-1] + ", ", "")
    m().write.assert_called_once_with(expected)


def test_delete_from_sd(m5stickv, mocker, mock_file_operations):
    from krux.encryption import MnemonicStorage

    # Loads a seeds.json file with many entries
    # Deletes "KEFgcmID" and assures the rest remain + padding to over-write abandoned bytes
    with patch("krux.sd_card.open", new=mocker.mock_open(read_data=SEEDS_JSON)) as m:
        storage = MnemonicStorage()
        storage.del_mnemonic("KEFgcmID", sd_card=True)
    padding_size = len(KEF_GCMENTROPY_ONLY_JSON)
    expected = SEEDS_JSON.replace(KEF_GCMENTROPY_ONLY_JSON[1:-1] + ", ", "")
    m().write.assert_called_once_with(expected + " " * padding_size)


def test_create_ecb_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings

    Settings().encryption.version = "AES-ECB"
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS)
    print("qr_data: {}".format(qr_data))
    assert qr_data == ECB_ENCRYPTED_QR


def test_create_cbc_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings

    Settings().encryption.version = "AES-CBC"
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS, I_VECTOR)
    print("qr_data: {}".format(qr_data))
    assert qr_data == CBC_ENCRYPTED_QR


def test_create_gcm_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings

    Settings().encryption.version = "AES-GCM"
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS, I_VECTOR[:12])
    print("qr_data: {}".format(qr_data))
    assert qr_data == GCM_ENCRYPTED_QR


def test_decode_ecb_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from embit import bip39

    encrypted_qr = EncryptedQRCode()
    public_data = encrypted_qr.public_data(ECB_ENCRYPTED_QR)
    print("public_data: {}".format(public_data))
    assert public_data == ECB_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS

    # legacy still decrypts
    public_data = encrypted_qr.public_data(OLDECB_ENCRYPTED_QR)
    assert public_data == OLDECB_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS


def test_decode_cbc_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from embit import bip39

    encrypted_qr = EncryptedQRCode()
    public_data = encrypted_qr.public_data(CBC_ENCRYPTED_QR)
    print("public_data: {}".format(public_data))
    assert public_data == CBC_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS

    # legacy still decrypts
    public_data = encrypted_qr.public_data(OLDCBC_ENCRYPTED_QR)
    assert public_data == OLDCBC_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS


def test_decode_gcm_encrypted_qr_code(m5stickv):
    from krux.encryption import EncryptedQRCode
    from embit import bip39

    encrypted_qr = EncryptedQRCode()
    public_data = encrypted_qr.public_data(GCM_ENCRYPTED_QR)
    print("public_data: {}".format(public_data))
    assert public_data == GCM_QR_PUBLIC_DATA
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS


def test_check_encrypted_qr_code_lengths(m5stickv):
    from krux.encryption import EncryptedQRCode, kef
    from krux.krux_settings import Settings, EncryptionSettings
    from krux.baseconv import base_encode

    # make encrypted_mnemonics using encryption settings mode preference
    qr_code_datum = {}
    for mode, mode_name in EncryptionSettings.MODE_NAMES.items():
        if (
            mode is None
            or len(
                [
                    x
                    for x in kef.VERSIONS.values()
                    if isinstance(x, dict) and x["mode"] == mode
                ]
            )
            == 0
        ):
            continue

        Settings().encryption.version = mode_name
        iv = I_VECTOR[: kef.MODE_IVS.get(kef.MODE_NUMBERS[mode_name], 0)]
        encrypted_qr = EncryptedQRCode()
        qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS, iv)
        if mode_name == "AES-ECB":
            assert len(qr_data) == 31
            assert len(base_encode(qr_data, 43)) == 45
        elif mode_name == "AES-CBC":
            assert len(qr_data) == 48
            assert len(base_encode(qr_data, 43)) == 70
        elif mode_name in ("AES-CTR", "AES-GCM"):
            assert len(qr_data) == 44
            assert len(base_encode(qr_data, 43)) == 64
        else:
            print(f"Unknown mode: {mode_name}")
            assert 0
        qr_code_datum[mode_name] = qr_data

    # re-create similar cipher-payloads for all versions, assert their kef-encoding is not any smaller
    from hashlib import sha256
    from embit.bip39 import mnemonic_to_bytes

    TEST_ENTROPY = mnemonic_to_bytes(TEST_WORDS)
    ITERATIONS = Settings().encryption.pbkdf2_iterations
    encryptor = kef.Cipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    for version, value in kef.VERSIONS.items():
        if value is None or value["mode"] is None:
            continue

        implied_mode = value["name"][:7]
        iv = I_VECTOR[: kef.MODE_IVS.get(value["mode"], 0)]
        payload = encryptor.encrypt(TEST_ENTROPY, version, iv)
        envelope = kef.wrap(TEST_MNEMONIC_ID, version, ITERATIONS, payload)
        qr_data = qr_code_datum[implied_mode]

        # looping through all versions, we didn't do any better than suggested version above
        assert len(qr_data) <= len(envelope)

        # where it's the same size, it's the same data
        if len(qr_data) == len(envelope):
            assert qr_data == envelope


def test_customize_pbkdf2_iterations_create_and_decode(m5stickv):
    from krux.encryption import EncryptedQRCode
    from krux.krux_settings import Settings
    from embit import bip39

    print("case Encode: customize_pbkdf2_iterations")
    Settings().encryption.version = "AES-ECB"
    Settings().encryption.pbkdf2_iterations = 99999
    encrypted_qr = EncryptedQRCode()
    qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS)
    print("qr_data: {}".format(qr_data))

    print("case Decode: customize_pbkdf2_iterations")
    public_data = encrypted_qr.public_data(qr_data)
    assert public_data == (
        "Encrypted QR Code:\nID: test ID\nVersion: AES-ECB\nPBKDF2 iter.: 99999"
    )
    word_bytes = encrypted_qr.decrypt(TEST_KEY)
    words = bip39.mnemonic_from_bytes(word_bytes)
    assert words == TEST_WORDS

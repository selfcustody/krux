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

ECB_ENTROPY = b"\x1b&ew\xe6\x84\xc5\xb0\x9c\x89\xf5$\xb5\xca\x10Aa\x90\xaae\t\x19\xdb\xd9\x9e\xc7C\x16a~%C"
CBC_ENTROPY = b"@\x8c\xf9\xb8\xd8\xd9\xe2\xbdo\xb5\xd1\xa1?\xb0\x10O\xd4\xc8\xfd()\xa0\xc2\xaf\xb5\x1d\x06\xdc\xfb\x80\x1cn"

ECB_ENCRYPTED_WORDS = b"\xd4\xd5y\xe6]'\xcb\xdb\xe4\x15^\xac\xe0\xc9\xc3\xbc9i\x89e\t\xa3~l\xbf\x98l\xe9\x92\xa9\xe1=3V\xb3\xb1]\xfb|\x13\xf4K_\xdb\xa7d\x92p\x8a-\xbfr\xb5`\xaf\xe5\xc4\xfeP Z\x12\xfbb\x82\x98\xb6)\x83\x99\xba]8R\xbdS\xce>\xdd\xb1"
CBC_ENCRYPTED_WORDS = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x92\xdaXV%+\xdb\x12\x85\xa6\x0c\xc8\xee\xc1>h\xd4i\xc1!r\x8d\x97\xd4\xb1V\x0c/\x18D\xff\x99\xd8a\xb8\x85\x81(\x08\xca\x07\xc8\xe0(\x04\xf5\xe1\xf0\xfd\xd9\xd4>E\xdf\x8aV\xb4\x19`\x10\xeaF\x03\x01As\xe5^\raQ\x842\xd6.9z\xa5x\x9a"

B64_ECB_ENCRYPTED_WORDS = b"1NV55l0ny9vkFV6s4MnDvDlpiWUJo35sv5hs6ZKp4T0zVrOxXft8E/RLX9unZJJwii2/crVgr+XE/lAgWhL7YoKYtimDmbpdOFK9U84+3bE="
B64_CBC_ENCRYPTED_WORDS = b"T1Khk2w+MnEgnp1kBZ7XjpLaWFYlK9sShaYMyO7BPmjUacEhco2X1LFWDC8YRP+Z2GG4hYEoCMoHyOAoBPXh8P3Z1D5F34pWtBlgEOpGAwFBc+VeDWFRhDLWLjl6pXia"

ECB_ENCRYPTED_ENTROPY_CKSUM = b"\x0cc\t\x7f\x90\xec\x9b$M\x88\xef4}\xc4\x8cW\xbc\xc4\xe0\x98\xdfN\x7f\xe4i@ \xf2\x15\xf8\x92rG\xe6\xf6\xc4\xbb\xb0h\xffL\xaaev\x8d\x1e7t"
CBC_ENCRYPTED_ENTROPY_CKSUM = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x13\x90d\xaa\xd6\xb8\xb4\xaas\x01{kj\xb6\xba\xa4\x93\x110\x1f\x0f\xbbW)\xaai\xaa\x13X\n@dM\xca{Y\x9d%B\xa2G\xde=\x8dk\xb8f\xc6"

B64_ECB_ENCRYPTED_ENTROPY_CKSUM = (
    b"DGMJf5DsmyRNiO80fcSMV7zE4JjfTn/kaUAg8hX4knJH5vbEu7Bo/0yqZXaNHjd0"
)
B64_CBC_ENCRYPTED_ENTROPY_CKSUM = b"T1Khk2w+MnEgnp1kBZ7XjhOQZKrWuLSqcwF7a2q2uqSTETAfD7tXKappqhNYCkBkTcp7WZ0lQqJH3j2Na7hmxg=="

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
        "data": "DGMJf5DsmyRNiO80fcSMV7zE4JjfTn/kaUAg8hX4knJH5vbEu7Bo/0yqZXaNHjd0"
    },
    "cbcID": {
        "version": 1,
        "key_iterations": 100000,
        "data": "T1Khk2w+MnEgnp1kBZ7XjhOQZKrWuLSqcwF7a2q2uqSTETAfD7tXKappqhNYCkBkTcp7WZ0lQqJH3j2Na7hmxg=="
    }
}"""

DEPRECATED_SEEDS_JSON = """{
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


ECB_ONLY_JSON = '{"ecbID": {"version": 0, "key_iterations": 100000, "data": "DGMJf5DsmyRNiO80fcSMV7zE4JjfTn/kaUAg8hX4knJH5vbEu7Bo/0yqZXaNHjd0"}}'
CBC_ONLY_JSON = '{"cbcID": {"version": 1, "key_iterations": 100000, "data": "T1Khk2w+MnEgnp1kBZ7XjhOQZKrWuLSqcwF7a2q2uqSTETAfD7tXKappqhNYCkBkTcp7WZ0lQqJH3j2Na7hmxg=="}}'

I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=SEEDS_JSON))


@pytest.fixture
def mock_deprecated_seeds_json(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=DEPRECATED_SEEDS_JSON))


# -------------------------


def test_encryption_VERSIONS_definition(m5stickv):
    """
    krux encryption VERSIONS are defined in src/krux/encryption.py

    VERSIONS is a dict with 1-byte-integer keys and dict values.
    The values are paramaters that define rules for each version.
    Once "released", these cannot be redefined w/o breaking compatibility
    to decrypt existing ciphertext in-the-wild, but more versions can be
    added in the future.
    """
    from krux.encryption import VERSIONS, VERSION_NUMBERS
    from krux.krux_settings import EncryptionSettings

    # the keys to VERSIONS are all integers between 0 and 255
    for k in VERSIONS:
        assert isinstance(k, int) and 0 <= k <= 255

    # each version has important key-value pairs which define it
    for v in VERSIONS.values():

        # each version has a human readable 'name'
        assert len(v["name"]) and isinstance(v["name"], str)

        # each version has a 'mode' integer that krux supports
        assert isinstance(v["mode"], int) and v["mode"] in (
            1,  # ECB
            2,  # CBC
            11,  # GCM
        )

        # each version has an 'iv' int to require this size i_vector
        assert isinstance(v.get("iv", 0), int)

        # each version has a 'pkcs_pad' boolean for pkcs style padding
        assert isinstance(v.get("pkcs_pad", False), bool)

        # each version has a 'auth' integer for bytes of authentication data
        # if negative, it's calculated and appended to plaintext "before"
        #   encryption/padding -- hidden but has a greater chance of needing
        #   an extra AES block!
        # if positive, it is appended "after" encryption/padding to ciphertext,
        #   it is unhidden.
        # if 0, it means that .decrypt() callers must figure out how to validate
        # successful decryption.
        assert isinstance(v.get("auth", 0), int) and -32 <= v.get("auth", 0) <= 32

    # VERSIONS['name'] must be unique else VERSION_NUMBERS will break
    assert len(VERSIONS) == len(VERSION_NUMBERS)

    # VERSION_NUMBERS is a reverse lookup (name->version) derived from VERSIONS
    for k, v in VERSION_NUMBERS.items():
        assert VERSIONS[v]["name"] == k

    # similarly, src/krux/krux_settings.py also requires a compatible structure
    assert len(VERSIONS) == len(EncryptionSettings().VERSION_NAMES)
    for k, v in EncryptionSettings().VERSION_NAMES.items():
        assert VERSIONS[k]["name"] == v


def test_AESCipher_initialization(m5stickv):
    from krux.encryption import AESCipher

    # .__init__() expects str (key, salt) and pos-int iterations
    valid_params = ("key", "salt", 1)
    AESCipher(*valid_params)  # this works

    invalid_keys = (None, 1, b"key")
    invalid_salts = (None, 1, b"salt")
    invalid_iterations = (None, -1, 0, 1.5)
    for invalid in invalid_keys:
        with pytest.raises(Exception):
            AESCipher(invalid, valid_params[1], valid_params[2])
    for invalid in invalid_salts:
        with pytest.raises(Exception):
            AESCipher(valid_params[0], invalid, valid_params[2])
    for invalid in invalid_iterations:
        with pytest.raises(Exception):
            AESCipher(valid_params[0], valid_params[1], invalid)


def test_AESCipher_calling_method_encrypt(m5stickv):
    from krux.encryption import AESCipher
    from ucryptolib import MODE_ECB, MODE_CBC, MODE_GCM

    encryptor = AESCipher("key", "salt", 1)

    # .encrypt() expects bytes raw, version, sometimes bytes i_vector
    valid_params = (
        ("\x00", 0),
        ("\x00", 0, b""),
        ("\x00", 1, b"\x00" * 16),
        ("\x00", 2),
        ("\x00", 2, b""),
        ("\x00", 3, b"\x00" * 16),
        ("\x00", 4),
        ("\x00", 4, b""),
        ("\x00", 5, b"\x00" * 16),
        ("\x00", 6, b"\x00" * 12),
        (b"\x00", 0),
        (b"\x00", 0, b""),
        (b"\x00", 1, b"\x00" * 16),
        (b"\x00", 2),
        (b"\x00", 2, b""),
        (b"\x00", 3, b"\x00" * 16),
        (b"\x00", 4),
        (b"\x00", 4, b""),
        (b"\x00", 5, b"\x00" * 16),
        (b"\x00", 6, b"\x00" * 12),
        (b"\x00", 7, b"\x00" * 12),
    )
    invalid_raws = (True, None, 1)
    invalid_versions = (None, -1, 8)
    invalid_ivs = ("\x00" * 16, b"\x00" * 15, 1)
    for valids in valid_params:
        # all calls for these unit tests use "fail_unsafe=False"
        # in order to pass simple "calling" testcases above
        kwargs = {"fail_unsafe": False}

        # valid params works
        encrypted = encryptor.encrypt(*valids, **kwargs)

        # test valid params against invalid ones
        for invalid in invalid_raws:
            with pytest.raises(TypeError):
                encryptor.encrypt(invalid, *valids[1:], **kwargs)
        for invalid in invalid_versions:
            with pytest.raises((ValueError, KeyError)):
                if len(valids) == 3:
                    encryptor.encrypt(valids[0], invalid, valids[2], **kwargs)
                else:
                    encryptor.encrypt(valids[0], invalid, **kwargs)
        if valids[1] == 0:
            err = "IV is not required"
            for invalid in invalid_ivs:
                with pytest.raises(ValueError, match=err):
                    encryptor.encrypt(valids[0], valids[1], invalid, **kwargs)
        elif valids[1] == 1:
            err = "Wrong IV length"
            for invalid in invalid_ivs:
                with pytest.raises(ValueError, match=err):
                    encryptor.encrypt(valids[0], valids[1], invalid, **kwargs)


def test_AESCipher_calling_method_decrypt(m5stickv):
    from krux.encryption import AESCipher, VERSIONS
    from ucryptolib import MODE_ECB, MODE_CBC, MODE_GCM

    decryptor = AESCipher("key", "salt", 1)

    valid_params = (
        (b"\x00" * 16, 0),
        (b"\x00" * 32, 1),
        (b"\x00" * 16, 2),
        (b"\x00" * 32, 3),
        (b"\x00" * 19, 4),
        (b"\x00" * 36, 5),
        (b"\x00" * 36, 6),
        (b"\x00" * 36, 7),
    )
    invalid_encrypteds = (True, None, 1, "\x00")
    invalid_versions = (None, -1, 8)
    for valids in valid_params:
        # valid params works
        encrypted = decryptor.decrypt(*valids)

        # test valid params against invalid ones
        for invalid in invalid_encrypteds:
            with pytest.raises((ValueError, TypeError)):
                decryptor.decrypt(invalid, valids[1])
        for invalid in invalid_versions:
            with pytest.raises((ValueError, KeyError)):
                decryptor.decrypt(valids[0], invalid)

    err = "Missing IV"
    for version, values in VERSIONS.items():
        if values.get("iv", 0) == 0:
            continue
        len_payload = 16 + values.get("iv")
        print(version, values, len_payload)
        with pytest.raises(ValueError, match=err):
            decryptor.decrypt(b"\x00" * (len_payload - 1), version)


def test_ecb_encryption(m5stickv):
    from krux.encryption import AESCipher, VERSIONS

    version = 0  # AES.MODE_ECB

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    encrypted = encryptor.encrypt(TEST_WORDS, version)
    assert encrypted == ECB_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_ECB_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, version)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS

    encrypted = encryptor.encrypt(ECB_ENTROPY, version)
    assert encryptor.decrypt(encrypted, version) == ECB_ENTROPY

    testplaintexts = (
        TEST_WORDS.encode(),
        ECB_WORDS.encode(),
        CBC_WORDS.encode(),
        ECB_ENTROPY,
        CBC_ENTROPY,
        b'"Running bitcoin" -Hal, January 10, 2009',
    )
    testversions = (
        0,  # AES.MODE_CBC
        2,  # AES.MODE_CBC +pkcs_pad -auth3
        4,  # AES.MODE_CBC +auth4
    )
    for version in testversions:
        for plain in testplaintexts:
            encrypted = encryptor.encrypt(plain, version)
            if VERSIONS[version].get("auth", 0):
                assert encryptor.decrypt(encrypted, version) == plain
            else:
                # versions that don't authenticate get close, must unpad/verify somehow
                assert plain in encryptor.decrypt(encrypted, version)

            # wrong key fails to decrypt silently
            wrong = AESCipher("wrong", "wrong", ITERATIONS)
            if VERSIONS[version].get("auth", 0):
                assert wrong.decrypt(encrypted, version) == None
            else:
                assert plain not in wrong.decrypt(encrypted, version)


def test_ecb_encryption_fails_duplicated_blocks(m5stickv):
    from krux.encryption import AESCipher

    # test controls
    version = 0  # AES.MODE_ECB
    key, id_, iterations = "a key", "a label", 100000
    plaintext = b"a 16-byte block." * 2

    encryptor = AESCipher(key, id_, iterations)

    # duplicate blocks in ECB mode can be encrypted only w/ fail_unsafe=False
    ciphertext = encryptor.encrypt(plaintext, version, fail_unsafe=False)

    # by default, unsafe plaintext encryption fails
    err = "Duplicate blocks in ECB mode"
    with pytest.raises(ValueError, match=err):
        encryptor.encrypt(plaintext, version)

    # but can still decrypt if previously encrypted
    assert encryptor.decrypt(ciphertext, version) == plaintext


def test_cbc_encryption(m5stickv):
    from krux.encryption import AESCipher, VERSIONS
    from Crypto.Random import get_random_bytes

    version = 1  # AES.MODE_CBC

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    iv = I_VECTOR
    encrypted = encryptor.encrypt(TEST_WORDS, version, iv)
    assert encrypted == CBC_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, version)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS

    encrypted = encryptor.encrypt(CBC_ENTROPY, version, iv)
    assert encryptor.decrypt(encrypted, version) == CBC_ENTROPY

    testplaintexts = (
        TEST_WORDS.encode(),
        ECB_WORDS.encode(),
        CBC_WORDS.encode(),
        ECB_ENTROPY,
        CBC_ENTROPY,
        b'"Running bitcoin" -Hal, January 10, 2009',
    )
    testversions = (
        1,  # AES.MODE_CBC
        3,  # AES.MODE_CBC +pkcs_pad -auth4
        5,  # AES.MODE_CBC +auth4
    )
    for version in testversions:
        for plain in testplaintexts:
            encrypted = encryptor.encrypt(plain, version, iv)
            if VERSIONS[version].get("auth", 0):
                assert encryptor.decrypt(encrypted, version) == plain
            else:
                # versions that don't authenticate get close, must unpad/verify somehow
                assert plain in encryptor.decrypt(encrypted, version)

            # wrong key fails to decrypt silently
            wrong = AESCipher("wrong", "wrong", ITERATIONS)
            if VERSIONS[version].get("auth", 0):
                assert wrong.decrypt(encrypted, version) == None
            else:
                assert plain not in wrong.decrypt(encrypted, version)


def test_cbc_iv_use(m5stickv):
    from krux.encryption import AESCipher
    from Crypto.Random import get_random_bytes

    SECOND_IV = b"\x8e\xc8b\x8f\xe2\xa8`\xaa\x06d\xe8\xe7\xaa.0\x03"
    CBC_ENCRYPTED_WORDS_SECOND_IV = b"\x8e\xc8b\x8f\xe2\xa8`\xaa\x06d\xe8\xe7\xaa.0\x03\xc0N7\xbd'u\xc5Z\x97\xde=\x10\xeaO\xf4x\xb5\xe6\x10l\xcfu\xef\x9e\x94\x03L-\xdc\xff\xa3m\xf0i\xd4\xe2\n{9G\x17\xbf.\x96\xba\x1a\x07\xackK9\x90-\xb6sf1\x01Y+\xa6\x80c/yO\x93'd\x8b\rnru\xe7\x17\xb0\x01\x9a\x9b"
    B64_CBC_ENCRYPTED_WORDS_SECOND_IV = b"jshij+KoYKoGZOjnqi4wA8BON70ndcVal949EOpP9Hi15hBsz3XvnpQDTC3c/6Nt8GnU4gp7OUcXvy6WuhoHrGtLOZAttnNmMQFZK6aAYy95T5MnZIsNbnJ15xewAZqb"

    version = 1  # AES.MODE_CBC

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)
    iv = I_VECTOR
    encrypted = encryptor.encrypt(TEST_WORDS, version, iv)
    assert encrypted == CBC_ENCRYPTED_WORDS

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS

    decrypted = encryptor.decrypt(encrypted, version)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS

    # Encrypt again with same data except for the IV
    iv = SECOND_IV
    encrypted = encryptor.encrypt(TEST_WORDS, version, iv)
    assert encrypted == CBC_ENCRYPTED_WORDS_SECOND_IV

    b64encrypted = base64.b64encode(encrypted)
    assert b64encrypted == B64_CBC_ENCRYPTED_WORDS_SECOND_IV

    decrypted = encryptor.decrypt(encrypted, version)
    assert decrypted.decode().replace("\x00", "") == TEST_WORDS


def test_gcm_encryption(m5stickv):
    from krux.encryption import AESCipher, VERSIONS

    testplaintexts = (
        TEST_WORDS.encode(),
        ECB_WORDS.encode(),
        CBC_WORDS.encode(),
        ECB_ENTROPY,
        CBC_ENTROPY,
        b'"Running bitcoin" -Hal, January 10, 2009',
    )
    testversions = (
        6,  # AES.MODE_GCM
        7,  # AES.MODE_GCM +pkcs_pad
    )
    iv = I_VECTOR[:12]

    encryptor = AESCipher(TEST_KEY, TEST_MNEMONIC_ID, ITERATIONS)

    for version in testversions:
        for plain in testplaintexts:
            encrypted = encryptor.encrypt(plain, version, iv)
            assert encryptor.decrypt(encrypted, version) == plain

            # wrong key fails to decrypt silently
            wrong = AESCipher("wrong", "wrong", ITERATIONS)
            assert wrong.decrypt(encrypted, version) == None


def test_broken_decryption_cases(m5stickv):
    """
    an edge case of broken AESCipher.decrypt() exists for versions which use
    authentication bytes but not pkcs_pad AND plaintext ends in 0x00 byte
    """

    from krux.encryption import AESCipher, VERSIONS

    plaintexts = (
        b"plaintext that isn't 16-byte aligned AND ends in \x00",
        b"plaintext that isn't 16-byte aligned",
        b"aligned plaintext that ends in \x00",
        b"aligned plaintext doesnt end nul",
        TEST_WORDS.encode(),
        ECB_WORDS.encode(),
        CBC_WORDS.encode(),
        ECB_ENTROPY,
        CBC_ENTROPY,
        b'"Running bitcoin" -Hal, January 10, 2009',
    )
    encryptor = AESCipher("key", "salt", 100000)
    for version in VERSIONS:
        iv = I_VECTOR[: VERSIONS[version].get("iv", 0)]
        v_auth = VERSIONS[version].get("auth", 0)
        v_pkcs_pad = VERSIONS[version].get("pkcs_pad", False)
        v_name = VERSIONS[version]["name"]

        for plain in plaintexts:
            encrypted = encryptor.encrypt(plain, version, iv, fail_unsafe=False)

            if v_auth != 0:
                # versions with authentication checking...
                if v_pkcs_pad == False:
                    # ...and without safe pkcs_pad
                    if plain[-1] == 0x00:
                        # ...and plaintext that ends in 0x00, ITS BROKEN
                        assert encryptor.decrypt(encrypted, version) != plain

                        # therefore, by default, krux fails to encrypt
                        err = "Cannot validate decryption for this plaintext"
                        with pytest.raises(ValueError, match=err):
                            encryptor.encrypt(plain, version, iv)
                    else:
                        # ...but if plaintext doesn't end in 0x00, it works
                        assert encryptor.decrypt(encrypted, version) == plain
                else:
                    # ... or if version uses safe pkcs_pad, it works
                    assert encryptor.decrypt(encrypted, version) == plain
            else:
                # if no auth checking, then it doesn't matter,
                # it's up to the caller to unpad and verify
                if len(plain) % 16 == 0:
                    assert encryptor.decrypt(encrypted, version) == plain
                else:
                    assert encryptor.decrypt(encrypted, version) != plain
                    assert plain in encryptor.decrypt(encrypted, version)


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

    # returns silently with wrong key
    assert storage.decrypt("wrong", "ecbID", sd_card=False) == None
    assert storage.decrypt("wrong", "ecbID", sd_card=True) == None


def test_load_decrypt_ecb_deprecated(m5stickv, mock_deprecated_seeds_json):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "ecbID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "ecbID", sd_card=True)
    assert words == ECB_WORDS
    assert words_sd == ECB_WORDS

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

    # returns silently with wrong key
    assert storage.decrypt("wrong", "cbcID", sd_card=False) == None
    assert storage.decrypt("wrong", "cbcID", sd_card=True) == None


def test_load_decrypt_cbc_deprecated(m5stickv, mock_deprecated_seeds_json):
    from krux.encryption import MnemonicStorage

    storage = MnemonicStorage()
    words = storage.decrypt(TEST_KEY, "cbcID", sd_card=False)
    words_sd = storage.decrypt(TEST_KEY, "cbcID", sd_card=True)
    assert words == CBC_WORDS
    assert words_sd == CBC_WORDS

    # returns silently with wrong key
    assert storage.decrypt("wrong", "cbcID", sd_card=False) == None
    assert storage.decrypt("wrong", "cbcID", sd_card=True) == None


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


def test_check_encrypted_qr_code_lengths(m5stickv):
    from krux.encryption import EncryptedQRCode, VERSIONS
    from krux.krux_settings import Settings
    from krux.baseconv import base_encode

    for version in VERSIONS:
        version_name = VERSIONS[version]["name"]
        Settings().encryption.version = version_name
        encrypted_qr = EncryptedQRCode()
        iv = None
        v_iv = VERSIONS[version].get("iv", 0)
        if v_iv:
            iv = I_VECTOR[:v_iv]
        encrypted_qr = EncryptedQRCode()
        qr_data = encrypted_qr.create(TEST_KEY, TEST_MNEMONIC_ID, TEST_WORDS, iv)
        if version_name == "AES-ECB":
            assert len(qr_data) == 44
            assert len(base_encode(qr_data, 43)) == 64
        elif version_name == "AES-CBC":
            assert len(qr_data) == 60
            assert len(base_encode(qr_data, 43)) == 88
        elif version_name == "AES-ECB v2p":
            assert len(qr_data) == 44
            assert len(base_encode(qr_data, 43)) == 64
        elif version_name == "AES-CBC v2p":
            assert len(qr_data) == 60
            assert len(base_encode(qr_data, 43)) == 88
        elif version_name == "AES-ECB v2":
            assert len(qr_data) == 31
            assert len(base_encode(qr_data, 43)) == 45
        elif version_name == "AES-CBC v2":
            assert len(qr_data) == 48
            assert len(base_encode(qr_data, 43)) == 70
        elif version_name == "AES-GCM v2":
            assert len(qr_data) == 44
            assert len(base_encode(qr_data, 43)) == 64
        elif version_name == "AES-GCM v2p":
            assert len(qr_data) == 60
            assert len(base_encode(qr_data, 43)) == 88
        else:
            print(f"Unknown version: {version_name}")
            assert 0


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
                    for invalid in (None, -1, 0.5, "0", 256, 8):
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
                    err = "Payload is not bytes"
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
                    invalid = ciphertext[:0]
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


NULPAD_TEST_CASES = [
    # (unpadded, padded)
    (b"0", b"0" + b"\x00" * 15),
    (b"0123456789abcde", b"0123456789abcde" + b"\x00"),
    (b"0123456789abcdef", b"0123456789abcdef"),
    (b"0123456789abcdef0", b"0123456789abcdef0" + b"\x00" * 15),
    (b"0123456789abcdef0123456789abcde", b"0123456789abcdef0123456789abcde" + b"\x00"),
    (b"0123456789abcdef0123456789abcdef", b"0123456789abcdef0123456789abcdef"),
    (b"\x00" * 16, b"\x00" * 16),
    (b"\x00" * 32, b"\x00" * 32),
    (b"\x01" * 15 + b"\x00" * 17, b"\x01" * 15 + b"\x00" * 17),
    (TEST_WORDS.encode(), TEST_WORDS.encode() + b"\x00" * 6),
    (ECB_WORDS.encode(), ECB_WORDS.encode() + b"\x00" * 5),
    (CBC_WORDS.encode(), CBC_WORDS.encode() + b"\x00" * 9),
]
BROKEN_NULPAD_TEST_CASES = [
    # (unpadded, padded)
    (b"\x01\x00", b"\x01\x00" + b"\x00" * 14),
    (b"\x01\x00" * 15, b"\x01\x00" * 15 + b"\x00" * 2),
]
PKCSPAD_TEST_CASES = [
    # (unpadded, padded)
    (b"0", b"0" + b"\x0f" * 15),
    (b"0123456789abcde", b"0123456789abcde" + b"\x01"),
    (b"0123456789abcdef", b"0123456789abcdef" + b"\x10" * 16),
    (b"0123456789abcdef0", b"0123456789abcdef0" + b"\x0f" * 15),
    (
        b"0123456789abcdef0123456789abcde",
        b"0123456789abcdef0123456789abcde" + b"\x01",
    ),
    (
        b"0123456789abcdef0123456789abcdef",
        b"0123456789abcdef0123456789abcdef" + b"\x10" * 16,
    ),
    (b"\x00" * 16, b"\x00" * 16 + b"\x10" * 16),
    (b"\x00" * 32, b"\x00" * 32 + b"\x10" * 16),
    (b"\x01" * 15 + b"\x00" * 17, b"\x01" * 15 + b"\x00" * 17 + b"\x10" * 16),
    (TEST_WORDS.encode(), TEST_WORDS.encode() + b"\x06" * 6),
    (ECB_WORDS.encode(), ECB_WORDS.encode() + b"\x05" * 5),
    (CBC_WORDS.encode(), CBC_WORDS.encode() + b"\x09" * 9),
]


def test_padding(m5stickv):
    from krux.encryption import pad, unpad

    # pad() and unpad() expect bytestrings, optionally pkcs_pad boolean
    unpadded = b"hello world"
    padded = pad(unpadded)
    assert padded == pad(unpadded, pkcs_pad=False)  # default: pkcs_pad=False
    assert unpadded == unpad(pad(unpadded, pkcs_pad=True), pkcs_pad=True)
    with pytest.raises(TypeError):
        pad(unpadded.decode())
    with pytest.raises(TypeError):
        unpad(padded.decode())

    # versions 0,1 pad to complete last 16byte block w/ b"\x00" bytes
    for unpadded, padded in NULPAD_TEST_CASES:
        assert pad(unpadded) == padded
        assert unpad(padded) == unpadded
        len_padding = len(padded) - len(unpadded)
        if len_padding:
            assert pad(unpadded)[-len_padding:] == b"\x00" * len_padding

    # versions 0,1 use non-faithful padding for bytestrings ending w/ b"\x00"
    for unpadded, padded in BROKEN_NULPAD_TEST_CASES:
        # pad() works just fine
        assert pad(unpadded) == padded

        # but unpad() will strip too many padding bytes
        with pytest.raises(AssertionError):
            assert unpad(padded) == unpadded

    # pkcs padding always adds at least 1 byte of padding
    for unpadded, padded in PKCSPAD_TEST_CASES:
        assert pad(unpadded, pkcs_pad=True) == padded
        assert unpad(padded, pkcs_pad=True) == unpadded
        len_padding = len(padded) - len(unpadded)
        assert (
            pad(unpadded, pkcs_pad=True)[-len_padding:]
            == len_padding.to_bytes(1, "big") * len_padding
        )

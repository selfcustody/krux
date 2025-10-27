import pytest
from unittest.mock import patch


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

ECB_ENCRYPTED_KEF = b"\x07test ID\x05\x00\x00\n*\xe1\x9d\xc5\x82\xc1\x19\x9b\xb7&\xf2?\x03\xc7o\xf6\xeb\x1a6"
CBC_ENCRYPTED_KEF = b'\x07test ID\x0a\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e\x01\x03`u_\xd7\xab/N\xbc@\x19\xcc\n"\xc5\xeb\x1a6m'
CTR_ENCRYPTED_KEF = b"\x07test ID\x0f\x00\x00\x01OR\xa1\x93l>2q \x9e\x9dd\xdeD'2$|7\xcbE]\x1bT\x10\xb2WD\xda\xd4\xaco\xe4\xf2\xf4\xcf\\M\xe7{\xfc\x82\x96\x82\x93\x82\x98\xf0"
GCM_ENCRYPTED_KEF = b"\x07test ID\x14\x00\x00\nOR\xa1\x93l>2q \x9e\x9dd\xbf\xb7vo]]\x8aO\x90\x8e\x86\xe784L\x02]\x8f\xedT"


I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"

BROKEN_AUTH16_ENTROPIES = (
    b"b#Cry<\xe5\x93\xf8\xf4\xafj\x89\xb4\xe3\x85",  # auth16 ends NUL suffix
    b"\x03a\x83\xa9C\xc4.\x86\x90;4G\xfd\xf1S\xf9",  # auth16 ends 2*NUL suffix
    b"f\xf3\x01j\x11\xad\xe7;\x97\x85\xa88c\xed\xf3g",  # auth16 ends 3*NUL suffix
    b'\xc7P^\x82\xcd\x17(\xcd^\x95\x9c\xc5z\xa4\x19"',  # auth16 ends 4*NUL suffix
)
BROKEN_AUTH4_ENTROPIES = (
    b"\x17\xef\xa2\x85\x86\xfd\x88\xa2\x81\x12\n\x03MDFz",  # auth4 ends NUL suffix
    b"z\xa3\xd3\xa3U\xa0\xb5W\xb3a\x0f`u\xc2&!",  # auth4 ends 2*NUL suffix
    b"\xcfum\xdfh\xdb\xb3p7\x1f}7\xcc\xcf\xa5\xda",  # auth4 ends 3*NUL suffix
    b"A\xe7\x9f'\x17q%\x9c\x13\x12\x9b\xb9C\x15\xc6\x91",  # auth4 ends 4*NUL suffix
)


def test_kef_VERSIONS_constants(m5stickv):
    """
    KEF VERSIONS constants are defined in `kef.py`

    VERSIONS is a dict with 1-byte-integer keys and dict values.
    The values are parameters that define rules for each version.
    Once "released", these cannot be redefined w/o breaking compatibility
    to decrypt existing ciphertext in-the-wild, but more versions can be
    added in the future.
    """
    from krux import kef

    # the keys to VERSIONS are all integers between 0 and 255
    for k in kef.VERSIONS:
        assert isinstance(k, int) and 0 <= k <= 255

    # each version has important key-value pairs which define it
    for version, v in kef.VERSIONS.items():

        # implementation may disable any version by setting VERSIONS value or VERSIONS["mode"] to None
        if v is None or v["mode"] is None:
            continue

        # each version has a human readable 'name'
        assert len(v["name"]) and isinstance(v["name"], str)

        # each version has a 'mode' integer that KEF supports (not 1:1 between MaixPy ucryptolib and Crypto.Cipher)
        assert isinstance(v["mode"], int) and v["mode"] in (
            kef.MODE_ECB,
            kef.MODE_CBC,
            kef.MODE_CTR,
            kef.MODE_GCM,
        )

        # each version has an implied "iv" value in MODE_IVS to require this size i_vector
        assert isinstance(kef.MODE_IVS.get(v["mode"], 0), int)

        # each version has an implied 'pkcs_pad': True=PKCS#7-padding, False=NUL-padding, None=no-padding
        assert v.get("pkcs_pad", False) in (True, False, None)

        # each version has an implied 'auth' integer for bytes of authentication data
        # if negative, it's calculated as sha256(plaintext) and appended to plaintext "before"
        #   encryption/padding -- hidden but has a greater chance of needing
        #   an extra AES block!
        # if positive, it's calculated as sha256(version + iv + plaintext + stretched_key) in order to obscure it,
        #   and appended "after" encryption/padding to ciphertext -- unhidden.
        # if 0, it means that .decrypt() callers must figure out how to validate
        #   successful decryption, but currently no versions define "auth" as 0.
        assert isinstance(v.get("auth", 0), int) and -32 <= v.get("auth", 0) <= 32

        # initially introduced in krux release 2023.08, KEF had only 2 versions (0 and 1) for encrypted mnemonics
        # additional KEF versions may be slotted by encryption-type and mode-of-operation
        if version > 1:
            if v["mode"] == kef.MODE_ECB:
                assert 5 <= version < 10
            elif v["mode"] == kef.MODE_CBC:
                assert 10 <= version < 15
            elif v["mode"] == kef.MODE_CTR:
                assert 15 <= version < 20
            elif v["mode"] == kef.MODE_GCM:
                assert 20 <= version < 25
            else:
                # overran a slot? new encryption type?, new mode of operation?
                assert 0

    # MODE_NUMBERS defines the AES modes of operation
    assert sorted(kef.MODE_NUMBERS.keys()) == [
        "AES-CBC",
        "AES-CTR",
        "AES-ECB",
        "AES-GCM",
    ]
    for k, v in kef.VERSIONS.items():
        if v is None or v["mode"] is None:
            continue
        implied_mode = v["name"][:7]
        assert implied_mode in kef.MODE_NUMBERS
        assert v["mode"] == kef.MODE_NUMBERS[implied_mode]

    # MODE_IVS defines initialization-vector/nonce length-in-bytes for modes that need it
    for mode, ivlen in kef.MODE_IVS.items():
        assert isinstance(ivlen, int)
        assert mode in kef.MODE_NUMBERS.values()


def test_Cipher_initialization(m5stickv):
    from krux import kef

    # .__init__() expects either utf8 str or bytes (key, salt) and pos-int iterations
    valid_params = (
        (b"key", b"salt", 1),
        ("key", "salt", 1),
        (
            int(255).to_bytes(1, "big"),
            int(255).to_bytes(1, "big"),
            1,
        ),
    )

    invalid_keys = (None, 1, True, False)
    invalid_salts = (None, 1, True, False)
    invalid_iterations = (None, -1, 0, 1.5)
    for valid_key, valid_salt, valid_iterations in valid_params:
        # this works
        kef.Cipher(valid_key, valid_salt, valid_iterations)

        # these fail
        for invalid in invalid_keys:
            with pytest.raises(Exception):
                kef.Cipher(invalid, valid_salt, valid_iterations)
        for invalid in invalid_salts:
            with pytest.raises(Exception):
                kef.Cipher(valid_key, invalid, valid_iterations)
        for invalid in invalid_iterations:
            with pytest.raises(Exception):
                kef.Cipher(valid_key, valid_salt, invalid)


def test_Cipher_calling_method_encrypt(m5stickv):
    from krux import kef

    encryptor = kef.Cipher(b"key", "salt", 1)

    # .encrypt() expects bytes raw, version, sometimes bytes i_vector
    valid_params = (
        (b"\x00", 0),  # ecb
        (b"\x00", 0, b""),  # ecb
        (b"\x00", 1, b"\x00" * 16),  # cbc
        (b"\x00", 5),  # ecb
        (b"\x00", 5, b""),  # ecb
        (b"\x00", 6),  # ecb
        (b"\x00", 6, b""),  # ecb
        (b"\x00", 7),  # ecb
        (b"\x00", 7, b""),  # ecb
        (b"\x00", 10, b"\x00" * 16),  # cbc
        (b"\x00", 11, b"\x00" * 16),  # cbc
        (b"\x00", 12, b"\x00" * 16),  # cbc
        (b"\x00", 15, b"\x00" * 12),  # ctr
        (b"\x00", 16, b"\x00" * 12),  # ctr
        (b"\x00", 20, b"\x00" * 12),  # gcm
        (b"\x00", 21, b"\x00" * 12),  # gcm
    )
    invalid_raws = ("\x00", True, None, 1)
    invalid_versions = (None, -1, 2, 3, 4, 8, 9, 13, 14, 17, 18, 19, 22)
    invalid_ivs = ("\x00" * 16, b"\x00" * 15, 1)
    for valids in valid_params:
        if kef.VERSIONS[valids[1]] is None or kef.VERSIONS[valids[1]]["mode"] is None:
            continue

        # all calls for these unit tests use "fail_unsafe=False"
        # in order to pass simple "calling" testcases above
        kwargs = {"fail_unsafe": False}

        # valid params works
        encrypted = encryptor.encrypt(*valids, **kwargs)

        # test valid params against invalid ones
        err = "Plaintext is not bytes"
        for invalid in invalid_raws:
            with pytest.raises(TypeError, match=err):
                encryptor.encrypt(invalid, *valids[1:], **kwargs)
        for invalid in invalid_versions:
            with pytest.raises((ValueError, KeyError)):
                if len(valids) == 3:
                    encryptor.encrypt(valids[0], invalid, valids[2], **kwargs)
                else:
                    encryptor.encrypt(valids[0], invalid, **kwargs)
        v_iv = kef.MODE_IVS.get(kef.VERSIONS[valids[1]]["mode"], 0)
        if v_iv == 0:
            err = "IV is not required"
            for invalid in invalid_ivs:
                with pytest.raises((ValueError, TypeError)):
                    encryptor.encrypt(valids[0], valids[1], invalid, **kwargs)
        else:
            err = "Wrong IV length"
            for invalid in invalid_ivs:
                with pytest.raises((ValueError, TypeError)):
                    encryptor.encrypt(valids[0], valids[1], invalid, **kwargs)

    # Exception when version is None or VERSIONS[version]["mode"] is None
    kef.VERSIONS[0] = None
    with pytest.raises(Exception):
        encryptor.encrypt(b"\x00", 0)
    kef.VERSIONS[1]["mode"] = None
    with pytest.raises(Exception):
        encryptor.encrypt(b"\x00", 1, b"\x01" * 16)


def test_Cipher_calling_method_decrypt(m5stickv):
    from krux import kef

    decryptor = kef.Cipher("key", b"salt", 1)

    valid_params = (
        (b"\x00" * 16, 0),  # ecb
        (b"\x00" * 32, 1),  # cbc
        (b"\x00" * 19, 5),  # ecb
        (b"\x00" * 32, 6),  # ecb
        (b"\x00" * 32, 7),  # ecb
        (b"\x00" * 36, 10),  # cbc
        (b"\x00" * 32, 11),  # cbc
        (b"\x00" * 48, 12),  # cbc
        (b"\x00" * 36, 15),  # ctr
        (b"\x00" * 36, 16),  # ctr
        (b"\x00" * 36, 20),  # gcm
        (b"\x00" * 48, 21),  # gcm
    )
    invalid_encrypteds = (True, None, 1, "\x00")
    invalid_versions = (None, -1, 2, 3, 4, 8, 9, 13, 14, 17, 18, 19, 22)
    for valids in valid_params:
        if kef.VERSIONS[valids[1]] is None or kef.VERSIONS[valids[1]]["mode"] is None:
            continue

        # valid params works
        encrypted = decryptor.decrypt(*valids)

        # test valid params against invalid ones
        for invalid in invalid_encrypteds:
            with pytest.raises((ValueError, TypeError)):
                decryptor.decrypt(invalid, valids[1])
        for invalid in invalid_versions:
            with pytest.raises((ValueError, KeyError)):
                decryptor.decrypt(valids[0], invalid)

    err = "Invalid Payload"
    for version, values in kef.VERSIONS.items():
        if kef.VERSIONS[valids[1]] is None or kef.VERSIONS[valids[1]]["mode"] is None:
            continue

        min_payload = 1 if values["mode"] in (kef.MODE_CTR, kef.MODE_GCM) else 16
        min_payload += kef.MODE_IVS.get(values["mode"], 0) + min(0, values["auth"])
        with pytest.raises(ValueError, match=err):
            decryptor.decrypt(b"\x00" * (min_payload - 1), version)

    # Exception when version is None or VERSIONS[version]["mode"] is None
    kef.VERSIONS[0] = None
    with pytest.raises(Exception):
        decryptor.decrypt(b"\x00" * 16, 0)
    kef.VERSIONS[1]["mode"] = None
    with pytest.raises(Exception):
        decryptor.decrypt(b"\x00" * 32, 1)


def test_Cipher_calling_method__authenticate(m5stickv):
    from krux import kef

    cipher = kef.Cipher(b"key", "salt", 10000)
    valid_decrypteds = (b"\x00",)
    valid_auths = (b"\x01\x02\x03", b"\x01\x02\x03\x04")

    invalid_versions = (1.0, -1, 256)
    invalid_ivs = ("Im a 16 char str",)
    invalid_decrypteds = (True, None, 1, "\x00")
    invalid_aes_objects = (list(), dict(), None)
    invalid_auths = (True, 1, "\x00")
    invalid_modes = (
        -1,
        0,
        3,
        5,
        7,
        10,
        12,
    )  # Crypto.Cipher:ECB,CBC,GCM=(1,2,11); MaixPy:ECB,CBC,GCM=(3,2,1)
    invalid_v_auths = (None, 1.0)
    invalid_v_pkcs_pad = ("True", "False", "NUL", "PKCS#7", "None", 0, 1)

    # try each invalid param with other valid params
    err = "Invalid call to ._authenticate()"
    for version, values in kef.VERSIONS.items():
        if values is None or values["mode"] is None:
            continue
        mode = values["mode"]
        v_auth = values["auth"]
        v_pkcs_pad = values.get("pkcs_pad", False)
        iv = I_VECTOR[: kef.MODE_IVS.get(mode, 0)]
        if iv == b"":
            aes_object = kef.AES(cipher._key, mode)
        elif mode == kef.MODE_CTR:
            aes_object = kef.AES(cipher._key, mode, nonce=iv)
        else:
            aes_object = kef.AES(cipher._key, mode, iv)
        for plain in valid_decrypteds:
            for auth in valid_auths:
                for invalid in invalid_versions:
                    with pytest.raises(ValueError, match=err):
                        cipher._authenticate(
                            invalid,
                            iv,
                            plain,
                            aes_object,
                            auth,
                            mode,
                            v_auth,
                            v_pkcs_pad,
                        )

                for invalid in invalid_ivs:
                    with pytest.raises(ValueError, match=err):
                        cipher._authenticate(
                            version,
                            invalid,
                            plain,
                            aes_object,
                            auth,
                            mode,
                            v_auth,
                            v_pkcs_pad,
                        )

                for invalid in invalid_decrypteds:
                    with pytest.raises(ValueError, match=err):
                        cipher._authenticate(
                            version,
                            iv,
                            invalid,
                            aes_object,
                            auth,
                            mode,
                            v_auth,
                            v_pkcs_pad,
                        )

                # GCM requires a valid aes_object where .verify() can be called
                if mode == kef.MODE_GCM:
                    for invalid in invalid_aes_objects:
                        with pytest.raises(ValueError, match=err):
                            cipher._authenticate(
                                version,
                                iv,
                                plain,
                                invalid,
                                auth,
                                mode,
                                v_auth,
                                v_pkcs_pad,
                            )

                for invalid in invalid_auths:
                    with pytest.raises(ValueError, match=err):
                        cipher._authenticate(
                            version,
                            iv,
                            plain,
                            aes_object,
                            invalid,
                            mode,
                            v_auth,
                            v_pkcs_pad,
                        )

                for invalid in invalid_modes:
                    with pytest.raises(ValueError, match=err):
                        cipher._authenticate(
                            version,
                            iv,
                            plain,
                            aes_object,
                            auth,
                            invalid,
                            v_auth,
                            v_pkcs_pad,
                        )

                for invalid in invalid_v_auths:
                    with pytest.raises(ValueError, match=err):
                        cipher._authenticate(
                            version,
                            iv,
                            plain,
                            aes_object,
                            auth,
                            mode,
                            invalid,
                            v_pkcs_pad,
                        )

                for invalid in invalid_v_pkcs_pad:
                    with pytest.raises(ValueError, match=err):
                        cipher._authenticate(
                            version, iv, plain, aes_object, auth, mode, v_auth, invalid
                        )


def test_Cipher_public_sha256_auth_commits_to_inputs(m5stickv):
    from krux import kef
    from hashlib import sha256

    testplaintexts = (
        (
            TEST_WORDS.encode(),
            ECB_WORDS.encode(),
            CBC_WORDS.encode(),
            CTR_WORDS.encode(),
            GCM_WORDS.encode(),
            ECB_ENTROPY,
            CBC_ENTROPY,
            CTR_ENTROPY,
            GCM_ENTROPY,
            b'"Running bitcoin" -Hal, January 10, 2009',
            b"\x00",
        )
        + BROKEN_AUTH16_ENTROPIES
        + BROKEN_AUTH4_ENTROPIES
    )

    cipher = kef.Cipher("key", b"salt", 10000)
    for v, values in kef.VERSIONS.items():
        if values is None or values["mode"] is None:
            continue

        v_mode = values["mode"]
        v_auth = values.get("auth", 0)
        v_iv = kef.MODE_IVS.get(values["mode"], 0)

        # Only AES-ECB, AES-CBC, and AES-CTR use sha256 for authentication
        if values["mode"] == kef.MODE_GCM:
            continue

        # When auth < 0: auth bytes are private, appended to plaintext; 0=no-auth
        if v_auth <= 0:
            continue

        # When auth > 0: auth bytes are public, appended to ciphertext
        iv = I_VECTOR[:v_iv]
        for plain in testplaintexts:
            print(v, values, plain)
            try:
                ciphertext = cipher.encrypt(plain, v, iv)
            except:
                continue
            auth_bytes = ciphertext[-v_auth:]

            # When auth bytes are public, KEF avoids simple sha256(plaintext) because
            # separate ciphertexts of same plaintext would share/reveal same auth bytes.
            # Thus, KEF also commits to version/iv/stretched-key when auth bytes are public.
            cksum = sha256(bytes([v]) + iv + plain + cipher._key).digest()[:v_auth]
            assert auth_bytes == cksum


def test_Cipher_public_auth_obscured_despite_similar_inputs(m5stickv):
    from krux import kef

    testplaintexts = (
        TEST_WORDS.encode(),
        ECB_WORDS.encode(),
        CBC_WORDS.encode(),
        CTR_WORDS.encode(),
        GCM_WORDS.encode(),
        ECB_ENTROPY,
        CBC_ENTROPY,
        CTR_ENTROPY,
        GCM_ENTROPY,
        b'"Running bitcoin" -Hal, January 10, 2009',
    )

    cipher = kef.Cipher("key", b"salt", 10000)
    for plain in testplaintexts:
        auth_bytes = []

        for v, values in kef.VERSIONS.items():
            if values is None or values["mode"] is None:
                continue

            v_mode = values["mode"]
            v_auth = values.get("auth", 0)
            v_iv = kef.MODE_IVS.get(values["mode"], 0)

            # When auth < 0: auth bytes are private, appended to plaintext; 0=no-auth
            if v_auth <= 0:
                continue

            # When auth > 0: auth bytes are public, appended to ciphertext
            iv = I_VECTOR[:v_iv]
            ciphertext = cipher.encrypt(plain, v, iv)
            auth_bytes.append((v, ciphertext[-v_auth:]))

            if iv:
                iv2 = iv[4:] + iv[:4]
                ciphertext2 = cipher.encrypt(plain, v, iv2)
                auth_bytes.append((v, ciphertext2[-v_auth:]))

        # while same plaintext was encrypted multiple times w/ similar inputs,
        # the unencrypted authentication bytes are obscured; not same and not found within others
        auth_bytes_set = set([auth for version, auth in auth_bytes])
        assert len(auth_bytes) == len(auth_bytes_set)
        len_long = max([len(x) for x in auth_bytes_set])
        for short_auth in (x for x in auth_bytes_set if len(x) != len_long):
            for auth in auth_bytes_set:
                if short_auth == auth:
                    continue
                assert short_auth not in auth


def test_Cipher_decrypt_exception_handling(m5stickv):
    """Test that decrypt returns None when _authenticate raises an exception"""
    from krux import kef

    # Payload structure: iv + ciphertext + auth
    iv = b"\x00" * 16
    ciphertext = b"\x00" * 16
    auth = b"\x00" * 4

    cases_decrypt = [
        (5, ciphertext + auth[:3]),  # ECB: no IV, 3-byte auth
        (10, iv + ciphertext + auth),  # CBC: 16-byte IV, 4-byte auth
        (15, iv[:12] + ciphertext + auth),  # CTR: 12-byte IV, 4-byte auth
        (20, iv[:12] + ciphertext + auth),  # GCM: 12-byte IV, 4-byte auth
    ]

    for version, payload in cases_decrypt:
        # Skip if version is disabled
        if kef.VERSIONS.get(version) is None:
            continue
        if kef.VERSIONS[version].get("mode") is None:
            continue

        cipher = kef.Cipher(b"testkey", b"testsalt", 10000)

        # Force _authenticate to fail by patching it
        with patch.object(
            cipher, "_authenticate", side_effect=Exception("Authentication failed")
        ):
            result = cipher.decrypt(payload, version)
            assert result is None


def test_faithful_encryption(m5stickv):
    from krux import kef

    testplaintexts = (
        (
            TEST_WORDS.encode(),
            ECB_WORDS.encode(),
            CBC_WORDS.encode(),
            CTR_WORDS.encode(),
            GCM_WORDS.encode(),
            ECB_ENTROPY,
            CBC_ENTROPY,
            CTR_ENTROPY,
            GCM_ENTROPY,
            b'"Running bitcoin" -Hal, January 10, 2009',
            b"\x00",
        )
        + BROKEN_AUTH16_ENTROPIES
        + BROKEN_AUTH4_ENTROPIES
    )
    cipher = kef.Cipher(b"key", "salt", 10000)
    wrong = kef.Cipher("wrong", b"wrong", 10000)
    for v, values in kef.VERSIONS.items():
        if values is None or values["mode"] is None:
            continue

        for plain in testplaintexts:
            iv = I_VECTOR[: kef.MODE_IVS.get(values["mode"], 0)]
            try:
                encrypted = cipher.encrypt(plain, v, iv)
            except ValueError as err:
                if str(err) == "Cannot validate decryption for this plaintext":
                    encrypted = cipher.encrypt(plain, v, iv, fail_unsafe=False)
            print(v, len(iv), plain)
            if values.get("auth", 0):
                assert cipher.decrypt(encrypted, v) == plain
            else:
                # versions that don't authenticate get close, must unpad/verify somehow
                assert plain in cipher.decrypt(encrypted, v)

            # wrong key fails to decrypt silently, usually
            if values.get("auth", 0):
                assert wrong.decrypt(encrypted, v) == None
            else:
                assert plain not in wrong.decrypt(encrypted, v)


def test_ecb_encryption_fails_duplicated_blocks(m5stickv):
    from krux import kef

    # test controls
    versions = (0, 5, 6)  # AES.MODE_ECB except w/compress
    key, id_, iterations = b"a key", "a label", 100000
    plaintext = b"a 16-byte block." * 2

    cipher = kef.Cipher(key, id_, iterations)

    for version in versions:
        # duplicate blocks in ECB mode can be encrypted only w/ fail_unsafe=False
        ciphertext = cipher.encrypt(plaintext, version, fail_unsafe=False)

        # by default, unsafe plaintext encryption fails
        err = "Duplicate blocks in ECB mode"
        with pytest.raises(ValueError, match=err):
            cipher.encrypt(plaintext, version)

        # but can still decrypt if previously encrypted
        assert cipher.decrypt(ciphertext, version) == plaintext


def test_broken_decryption_cases(m5stickv):
    """
    an edge case of broken AESCipher.decrypt() exists for versions which use
    authentication bytes but not pkcs_pad AND plaintext ends in 0x00 byte
    """

    from hashlib import sha256
    from krux import kef

    plaintexts = (
        (
            b"plaintext that isn't 16-byte aligned AND ends in \x00",
            b"plaintext that isn't 16-byte aligned",
            b"aligned plaintext that ends in \x00",
            b"aligned plaintext that ends 2*\x00\x00",
            b"aligned plaintext ending w/3 \x00\x00\x00",
            b"aligned plaintext ending 4x \x00\x00\x00\x00",
            b"aligned plaintext doesnt end nul",
            b'plaintext with a 3-byte "auth" that ends in \x00. (91)',
            b'plaintext with a 4-byte "auth" that ends in \x00. (818)',
            b'plaintext with a 16-byte "auth" that ends in \x00. (275)',
            b"-auth3[-1]=\x00 (15)",
            b"-auth4[-1]=\x00 (83)",
            b"-auth16[-1]=\x00 (221)",
            TEST_WORDS.encode(),
            ECB_WORDS.encode(),
            CBC_WORDS.encode(),
            CTR_WORDS.encode(),
            GCM_WORDS.encode(),
            ECB_ENTROPY,
            CBC_ENTROPY,
            CTR_ENTROPY,
            GCM_ENTROPY,
            b'"Running bitcoin" -Hal, January 10, 2009',
        )
        + BROKEN_AUTH16_ENTROPIES
        + BROKEN_AUTH4_ENTROPIES
    )

    cipher = kef.Cipher("key", b"salt", 100000)
    for version in kef.VERSIONS:
        if kef.VERSIONS[version] is None or kef.VERSIONS[version]["mode"] is None:
            continue

        iv = I_VECTOR[: kef.MODE_IVS.get(kef.VERSIONS[version]["mode"], 0)]
        v_auth = kef.VERSIONS[version].get("auth", 0)
        v_pkcs_pad = kef.VERSIONS[version].get("pkcs_pad", False)
        v_name = kef.VERSIONS[version]["name"]

        for plain in plaintexts:
            encrypted = cipher.encrypt(plain, version, iv, fail_unsafe=False)

            if v_auth > 0 and v_pkcs_pad is False and plain[-1] == 0x00:
                # for versions that append auth bytes after padded encryption...
                # ...and without safe pkcs_pad
                # ...and plaintext that ends in 0x00, ITS BROKEN
                # a hack that assumes NULpad broke auth-decryption is implemented
                assert cipher.decrypt(encrypted, version) == plain

                # hacks not ideal, therefore by default, KEF fails to encrypt
                err = "Cannot validate decryption for this plaintext"
                with pytest.raises(ValueError, match=err):
                    cipher.encrypt(plain, version, iv)

            elif (
                v_auth < 0
                and v_pkcs_pad is False
                and sha256(plain).digest()[-v_auth - 1] == 0x00
            ):
                # for version that append sha256 auth bytes to plain before encryption...
                # ...and without safe pkcs_pad
                # ...and auth byte ends in 0x00, ITS BROKEN
                # a hack that assumes NULpad broke auth-decryption is implemented
                assert cipher.decrypt(encrypted, version) == plain

                # hacks not ideal, therefore by default, KEF fails to encrypt
                err = "Cannot validate decryption for this plaintext"
                with pytest.raises(ValueError, match=err):
                    cipher.encrypt(plain, version, iv)

            elif v_auth == 0:
                # if no auth checking, then it doesn't matter,
                # it's up to the caller to unpad and verify
                # all KEF versions have "auth": this test remains just in case
                if len(plain) % 16 == 0:
                    assert cipher.decrypt(encrypted, version) == plain
                else:
                    assert cipher.decrypt(encrypted, version) != plain
                    assert plain in cipher.decrypt(encrypted, version)

            else:
                # other cases should encrypt and decrypt w/o problems
                assert cipher.decrypt(encrypted, version) == plain

    # test broken-auth-entropies constants
    for broken in BROKEN_AUTH4_ENTROPIES:
        assert sha256(broken).digest()[:4][-1] == 0x00
    for broken in BROKEN_AUTH16_ENTROPIES:
        assert sha256(broken).digest()[:16][-1] == 0x00


def test_suggest_versions(m5stickv):
    from krux import kef

    entropy16 = b"16 !random bytes"
    entropy32 = b"32 hardlyrandom bytes of entropy"
    nul_byte_str = "a nul byte string \x00"
    short_str = "Running bitcoin"
    bad_passwd = "N0 body will ever gue55 th!s 1"
    descriptor_single = "pkh([55f8fc5d/44h/0h/1h]xpub6C1dUaopHgps6X75i61KaJEDm4qkFeqjhm4by1ebvpgAsKDaEhGLgNX88bvuWPm4rSVe7GsYvQLDAXXLnxNsAbd3VwRihgM3q1kEkixBAbE)"
    descriptor_1of2 = "wsh(multi(1,[55f8fc5d/44h/0h/1h]xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB/1/0/*,xpub69H7F5d8KSRgmmdJg2KhpAK8SR3DjMwAdkxj3ZuxV27CprR9LgpeyGmXUbC6wb7ERfvrnKZjXoUmmDznezpbZb7ap6r1D3tgFxHmwMkQTPH/0/0/*))"
    descriptor_2of3 = "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/<0;1>/*,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/<0;1>/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/<0;1>/*))"
    descriptor_mini_liana_em = "tr(xpub661MyMwAqRbcFHMDceyRcHhEfeDBXneBmbTnqujM6EumzeNcd8wrs3SHGzkETt7dDwqSCmDJx2rz6uKEddXRcYUWuAu6rkaj4L2QuVxqNUS/<0;1>/*,{and_v(v:multi_a(2,[55f8fc5d/48'/0'/0'/2']xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/<2;3>/*,[3e15470d/48'/0'/0'/2']xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/<2;3>/*,[d3a80c8b/48'/0'/0'/2']xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/<0;1>/*),older(65535)),multi_a(2,[55f8fc5d/48'/0'/0'/2']xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/<0;1>/*,[3e15470d/48'/0'/0'/2']xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/<0;1>/*)})#uyj29ygt"
    descriptor_remint005 = "wsh(andor(multi(2,[fbf14e49/45h/1h/0h/3h]tpubDEPmZmWcL9G3XEbhBy6A5UG7tR4hAT7zvhu4cVmCSbVPhjkfuYRgqFnUfG4Gm1NSaoo412nzyRe3UAtC73BHQbVDLz4nAkrhJDSxcYSpUnz/<0;1>/*,[525cb3d5/45h/1h/0h/3h]tpubDF4yVr6ohjK1hQgyHvtLpanC4JxkshsMVUDHfmDvpXcBzdD2peXKdhfLFVNWQekAYAN1vU81dUNfgokZb1foUQfDMtf6X8mb3vMs7cYHbcr/<0;1>/*,[5fc83bce/45h/1h/0h/3h]tpubDFMqbP9gd34rd5Db2hHVYsJA3LnBD2fZo6zWFzeAA2kUC27cndyN2axBs55K9qJSghbvZx1Nyrrvb2ixgLXRzyK7dLLnXHGAmHe7apv4XwU/<0;1>/*),or_i(and_v(v:pkh([5acaced1/49h/1h/0h]tpubDDXMHf1PVPUPYHKyR9b5pbsfcd4SDC5FHtx7msTwazX4gkZPCRjoTYB2mFR4HsiybdptPtKH7yyoogx9d2gvc92SaoCYANEdZYqRR6FJKGx/<0;1>/*),after(230436)),thresh(2,pk([5ecc195f/48h/1h/0h/2h]tpubDFfTpjFSFT9FFvWwXand2JfnRBSpekQQpzdoz5qm8fy6cUhjLdTBuNrqxdsFgyTJ6xr5oeUAqa28VHPMprbosXLhGEgJW4SPa31tuSmp9Ub/<0;1>/*),s:pk([a1088994/48h/1h/0h/2h]tpubDFE64qjVGZ8L31gXFNtRUUpbaZ5viPgkFpth8j3XfGNWgaM6Vsm3F4z1nNE1soY3cQc6YZtNqMqfrywkeAQMiiYnR8N1oyFP5YuuFYTQ2nx/<0;1>/*),s:pk([8faeabe8/48h/1h/0h/2h]tpubDEMz5Gib3V3i1xzY4yaKH2k2J4MBRjNYNSace1YHMr6MgaM1oLZ4qiF7mWQvGPm9gH5bgroqPMr44viw16XWYoig6rbCQrkzakJw6hsapFw/<0;1>/*),snl:after(230220))),and_v(v:thresh(2,pkh([2bd4a49f/84h/1h/1h]tpubDCtwDKhf7tMtt2NDNrWsN7tFQSEvoKt9qvSBMUPuZVnoR52FwSaQS37UT5skDddUyzhVEGJozGxu8CBJPPc8MXhXidD7azaubMHgNCPvq28/<0;1>/*),a:pkh([d38f3599/84h/1h/2h]tpubDDYgycbJd7DgJjKFd4W8Dp8RRNhDDYfLs93cjhBP6boyXiZxdUyZc8fuLMJyetQXq6i9xfYSJwEf1GYxmND6jXExLS9q9ibP2YXZxtqe7mK/<0;1>/*),a:pkh([001ceab0/84h/1h/3h]tpubDCuJUyHrMq4PY4fXEHyADTkFwgy498AnuhrhFzgT7tWuuwp9JAeopqMTre99nzEVnqJNsJk21VRLeLsGz4cA5hboULrupdHqiZdxKRLJV9R/<0;1>/*)),after(230775))))#5flg0r73"
    testcases = (
        # plaintext, preferred mode, suggested-version-name
        # ECB
        (entropy16, "AES-ECB", "AES-ECB"),
        (entropy32, "AES-ECB", "AES-ECB"),
        (entropy16 * 2, "AES-ECB", "AES-ECB +c"),
        (entropy32 * 3, "AES-ECB", "AES-ECB +c"),
        (entropy32 * 8, "AES-ECB", "AES-ECB +c"),
        (nul_byte_str, "AES-ECB", "AES-ECB +p"),
        (entropy32 * 2 + nul_byte_str.encode(), "AES-ECB", "AES-ECB +c"),
        (short_str, "AES-ECB", "AES-ECB"),
        (bad_passwd, "AES-ECB", "AES-ECB"),
        (descriptor_single, "AES-ECB", "AES-ECB +c"),
        (descriptor_1of2, "AES-ECB", "AES-ECB +c"),
        (descriptor_2of3, "AES-ECB", "AES-ECB +c"),
        (descriptor_mini_liana_em, "AES-ECB", "AES-ECB +c"),
        (descriptor_remint005, "AES-ECB", "AES-ECB +c"),
        # CBC
        (entropy16, "AES-CBC", "AES-CBC"),
        (entropy32, "AES-CBC", "AES-CBC"),
        (entropy16 * 2, "AES-CBC", "AES-CBC"),
        (entropy32 * 3, "AES-CBC", "AES-CBC +p"),
        (entropy32 * 8, "AES-CBC", "AES-CBC +c"),
        (nul_byte_str, "AES-CBC", "AES-CBC +p"),
        (entropy32 * 2 + nul_byte_str.encode(), "AES-CBC", "AES-CBC +p"),
        (short_str, "AES-CBC", "AES-CBC"),
        (bad_passwd, "AES-CBC", "AES-CBC"),
        (descriptor_single, "AES-CBC", "AES-CBC +c"),
        (descriptor_1of2, "AES-CBC", "AES-CBC +c"),
        (descriptor_2of3, "AES-CBC", "AES-CBC +c"),
        (descriptor_mini_liana_em, "AES-CBC", "AES-CBC +c"),
        (descriptor_remint005, "AES-CBC", "AES-CBC +c"),
        # CTR
        (entropy16, "AES-CTR", "AES-CTR"),
        (entropy32, "AES-CTR", "AES-CTR"),
        (entropy16 * 2, "AES-CTR", "AES-CTR"),
        (entropy32 * 3, "AES-CTR", "AES-CTR"),
        (entropy32 * 8, "AES-CTR", "AES-CTR +c"),
        (nul_byte_str, "AES-CTR", "AES-CTR"),
        (entropy32 * 2 + nul_byte_str.encode(), "AES-CTR", "AES-CTR"),
        (short_str, "AES-CTR", "AES-CTR"),
        (bad_passwd, "AES-CTR", "AES-CTR"),
        (descriptor_single, "AES-CTR", "AES-CTR +c"),
        (descriptor_1of2, "AES-CTR", "AES-CTR +c"),
        (descriptor_2of3, "AES-CTR", "AES-CTR +c"),
        (descriptor_mini_liana_em, "AES-CTR", "AES-CTR +c"),
        (descriptor_remint005, "AES-CTR", "AES-CTR +c"),
        # GCM
        (entropy16, "AES-GCM", "AES-GCM"),
        (entropy32, "AES-GCM", "AES-GCM"),
        (entropy16 * 2, "AES-GCM", "AES-GCM"),
        (entropy32 * 3, "AES-GCM", "AES-GCM"),
        (entropy32 * 8, "AES-GCM", "AES-GCM +c"),
        (nul_byte_str, "AES-GCM", "AES-GCM"),
        (entropy32 * 2 + nul_byte_str.encode(), "AES-GCM", "AES-GCM"),
        (short_str, "AES-GCM", "AES-GCM"),
        (bad_passwd, "AES-GCM", "AES-GCM"),
        (descriptor_single, "AES-GCM", "AES-GCM +c"),
        (descriptor_1of2, "AES-GCM", "AES-GCM +c"),
        (descriptor_2of3, "AES-GCM", "AES-GCM +c"),
        (descriptor_mini_liana_em, "AES-GCM", "AES-GCM +c"),
        (descriptor_remint005, "AES-GCM", "AES-GCM +c"),
    )

    disabled_mode_names = []

    # call it with plaintext (bytes or str) and mode_name
    for mode_name, mode in kef.MODE_NUMBERS.items():
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
            disabled_mode_names.append(mode_name)
            continue

        assert len(kef.suggest_versions(b"arbitrary bytestring", mode_name)) > 0
        assert len(kef.suggest_versions("an arbitrary text str", mode_name)) > 0

        with pytest.raises(TypeError, match="Plaintext is not bytes or str"):
            kef.suggest_versions(None, mode_name)
        with pytest.raises(TypeError):
            kef.suggest_versions(b"some bytes")

    for plain, mode_name, version_name in testcases:
        if mode_name in disabled_mode_names:
            continue

        suggesteds = kef.suggest_versions(plain, mode_name)

        # begin debugging
        print(len(plain), mode_name, [kef.VERSIONS[x]["name"] for x in suggesteds])
        version = suggesteds[0]
        if isinstance(plain, str):
            plain = plain.encode()
        iv = b"\x00" * kef.MODE_IVS.get(kef.VERSIONS[version]["mode"], 0)
        encryptor = kef.Cipher("key", b"salt", 100000)
        encryptor.decrypt(encryptor.encrypt(plain, suggesteds[0], iv), suggesteds[0])

        # end debugging
        assert version_name in [kef.VERSIONS[x]["name"] for x in suggesteds]


def test_suggest_versions_with_disabled_versions(m5stickv):
    """Test that suggest_versions skips disabled versions"""
    from krux import kef

    # Test cases for disabling versions
    test_cases = [
        (5, "set_none", "AES-ECB"),  # Disable entire version by setting to None
        (10, "mode_none", "AES-CBC"),  # Disable by setting mode to None
    ]

    for version, disable_method, mode_name in test_cases:
        # Disable the version
        if disable_method == "set_none":
            kef.VERSIONS[version] = None
        else:
            kef.VERSIONS[version]["mode"] = None

        suggestions = kef.suggest_versions(b"test plaintext", mode_name)
        assert version not in suggestions


def test_wrapping_is_faithful(m5stickv):
    from krux import kef

    testplaintexts = (
        (
            TEST_WORDS.encode(),
            ECB_WORDS.encode(),
            CBC_WORDS.encode(),
            CTR_WORDS.encode(),
            GCM_WORDS.encode(),
            ECB_ENTROPY,
            CBC_ENTROPY,
            CTR_ENTROPY,
            GCM_ENTROPY,
            b'"Running bitcoin" -Hal, January 10, 2009',
            b"\x00",
        )
        + BROKEN_AUTH16_ENTROPIES
        + BROKEN_AUTH4_ENTROPIES
    )
    key, id_, iterations = b"key", "a label", 10000

    cipher = kef.Cipher(key, id_, iterations)
    for v, values in kef.VERSIONS.items():
        if values is None or values["mode"] is None:
            continue

        for plain in testplaintexts:
            iv = I_VECTOR[: kef.MODE_IVS.get(values["mode"], 0)]
            payload = cipher.encrypt(plain, v, iv, fail_unsafe=False)

            # for id_ wrap() is tolerant of str or bytes -- when wrapping
            envelope = kef.wrap(id_, v, iterations, payload)
            envelope2 = kef.wrap(id_.encode(), v, iterations, payload)
            assert envelope == envelope2

            # but unwrap() is strict about always return id_ as bytes -- when unwrapping
            parsed = kef.unwrap(envelope)
            parsed2 = kef.unwrap(envelope2)
            assert parsed == (id_.encode(), v, iterations, payload)
            assert parsed == parsed2


def test_wrapper_interpretation_of_iterations(m5stickv):
    from krux import kef

    # int to 3-byte big-endian
    def i2b(an_int):
        return an_int.to_bytes(3, "big")

    ten_k = 10000

    # mock values so that iterations will be at bytes[6:9]
    id_ = b"test"
    version = 0
    ciphertext = b"\x00" * 32

    # if (iterations % 10000 == 0) they are serialized divided by 10000
    for iterations in (ten_k, ten_k * 10, ten_k * 50, ten_k * ten_k):
        encoded = kef.wrap(id_, version, iterations, ciphertext)
        assert encoded[6:9] == i2b(iterations // 10000)
        assert kef.unwrap(encoded)[2] == iterations

    # if (iterations % 10000 != 0) they are serialized as the same value
    for iterations in (ten_k + 1, ten_k * 10 + 1, ten_k * 50 + 1, 2**24 - 1):
        encoded = kef.wrap(id_, version, iterations, ciphertext)
        assert encoded[6:9] == i2b(iterations)
        assert kef.unwrap(encoded)[2] == iterations


def test_wrap_exceptions(m5stickv):
    from krux import kef

    ten_k = 10000
    valid_ids = (
        b"",
        b"My Mnemonic",
        b"ID can be empty or as long as 252 utf-8 characters, but not longer. Limit is 252, leaving flexibility (253,254,255) to be redefined in the future.\nA purely peer-to-peer version of electronic cash would allow online\npayments to be sent directly from one",
        b"".join([i.to_bytes(1, "big") for i in range(252)]),
    )
    valid_versions = [0, 1, 5, 6, 7, 10, 11, 12, 15, 16, 20, 21]
    valid_iterations = (ten_k, 50 * ten_k, ten_k + 1, 2**24 - 1, ten_k * ten_k)
    plaintexts = (
        b"\xde\xad\xbe\xef" * 4,
        b"\xde\xad\xbe\xef" * 8,
        b"hello world",
    )

    # test individual exceptions against other valid params
    cipher = kef.Cipher("key", b"salt", 100000)
    for id_ in valid_ids:
        for version in valid_versions:
            if kef.VERSIONS[version] is None or kef.VERSIONS[version]["mode"] is None:
                continue

            for iterations in valid_iterations:
                for plaintext in plaintexts:
                    iv = b"\x00" * kef.MODE_IVS.get(kef.VERSIONS[version]["mode"], 0)
                    ciphertext = cipher.encrypt(
                        plaintext, version, iv, fail_unsafe=False
                    )

                    # ID is limited to length <= 252 utf-8
                    err = "Invalid ID"
                    for invalid in (None, 21, ("Too Long! " * 26)[:253]):
                        with pytest.raises(ValueError, match=err):
                            kef.wrap(invalid, version, iterations, ciphertext)

                    # Version must be 0-255, and supported
                    err = "Invalid version"
                    for invalid in (None, -1, 0.5, "0", 256, 13):
                        with pytest.raises(ValueError, match=err):
                            kef.wrap(id_, invalid, iterations, ciphertext)

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
                            kef.wrap(id_, version, invalid, ciphertext)

                    # Ciphertext must be bytes
                    err = "Payload is not bytes"
                    invalid = (b"\x00" * 32).decode()
                    with pytest.raises(ValueError, match=err):
                        kef.wrap(id_, version, iterations, invalid)

                    # except for modes that don't require padding...
                    if kef.VERSIONS[version].get("pkcs_pad", False) is None:
                        continue

                    # ...and aligned
                    err = "Ciphertext is not aligned"
                    for extra in range(1, 16):
                        invalid = ciphertext + (b"\xff" * extra)
                        with pytest.raises(ValueError, match=err):
                            kef.wrap(id_, version, iterations, invalid)

                    # ...and not too short
                    err = "Ciphertext is too short"
                    extra = kef.MODE_IVS.get(kef.VERSIONS[version]["mode"], 0)
                    if kef.VERSIONS[version].get("auth", 0) > 0:
                        extra += kef.VERSIONS[version]["auth"]
                    invalid = ciphertext[:extra]
                    with pytest.raises(ValueError, match=err):
                        kef.wrap(id_, version, iterations, invalid)

    # Exception when version is None or VERSIONS[version]["mode"] is None
    ciphertext = cipher.encrypt(b"plaintext", 0)
    kef.VERSIONS[0] = None
    with pytest.raises(ValueError, match="Invalid version"):
        kef.wrap("test", 0, 10000, ciphertext)
    ciphertext = cipher.encrypt(b"plaintext", 1, b"\x01" * 16)
    kef.VERSIONS[1]["mode"] = None
    with pytest.raises(ValueError, match="Invalid version"):
        kef.wrap("test", 0, 10000, ciphertext)


def test_unwrap_exceptions(m5stickv):
    from krux import kef

    block_test_cases = (ECB_ENCRYPTED_KEF, CBC_ENCRYPTED_KEF)
    stream_test_cases = (CTR_ENCRYPTED_KEF, GCM_ENCRYPTED_KEF)

    # an unknown version is not KEF Encryption Format
    err = "Invalid format"
    for encoded in block_test_cases + stream_test_cases:
        version_pos = encoded[0] + 1
        for i in range(256):
            if i in kef.VERSIONS:
                continue
            encoded = (
                encoded[:version_pos]
                + i.to_bytes(1, "big")
                + encoded[version_pos + 1 :]
            )
            with pytest.raises(ValueError, match=err):
                kef.unwrap(encoded)

    # Ciphertext is aligned on 16-byte blocks
    err = "Ciphertext is not aligned"
    for encoded in block_test_cases:
        for i in range(15):
            encoded = encoded[:-1]
            with pytest.raises(ValueError, match=err):
                kef.unwrap(encoded)

    # Ciphertext is at least 1 block (at least for ecb/cbc)
    err = "Ciphertext is too short"
    encoded = ECB_ENCRYPTED_KEF[:-16]  # 24w CBC is 48 bytes w/ iv+checksum
    with pytest.raises(ValueError, match=err):
        kef.unwrap(encoded)
    encoded = CBC_ENCRYPTED_KEF[:-32]  # 24w CBC is 48 bytes w/ iv+checksum
    with pytest.raises(ValueError, match=err):
        kef.unwrap(encoded)

    # Exception when version is None or VERSIONS[version]["mode"] is None
    err = "Invalid format"
    for v, encoded in (
        (5, ECB_ENCRYPTED_KEF),
        (10, CBC_ENCRYPTED_KEF),
        (15, CTR_ENCRYPTED_KEF),
        (20, GCM_ENCRYPTED_KEF),
    ):
        kef.VERSIONS[v] = None
        with pytest.raises(ValueError, match=err):
            kef.unwrap(encoded)


def test_faithful_encrypted_wrapper(m5stickv):
    from krux import kef

    iterations = (10000, 12345)
    keys = (b"", "key", b"key", "clé".encode(), int(255).to_bytes(1, "big"))
    salts = (b"", "salt", b"salt", "salé".encode(), int(255).to_bytes(1, "big"))
    plaintexts = (b"Hello World!", b"im sixteen bytes")

    for version in kef.VERSIONS:
        if kef.VERSIONS[version] is None or kef.VERSIONS[version]["mode"] is None:
            continue

        for key in keys:
            for salt in salts:
                for iteration in iterations:
                    for plain in plaintexts:
                        iv = b"\x00" * kef.MODE_IVS.get(
                            kef.VERSIONS[version]["mode"], 0
                        )
                        cipher = kef.Cipher(key, salt, iteration)
                        cipher_payload = cipher.encrypt(plain, version, iv)
                        envelope = kef.wrap(salt, version, iteration, cipher_payload)
                        print(version, plain, cipher_payload, envelope)
                        parsed = kef.unwrap(envelope)
                        assert (
                            parsed == (salt, version, iteration, cipher_payload)
                            or isinstance(salt, str)
                            and parsed
                            == (salt.encode(), version, iteration, cipher_payload)
                        )
                        assert cipher.decrypt(cipher_payload, version) == plain


NULPAD_TEST_CASES = [
    # (unpadded, padded)
    (b"0", b"0" + b"\x00" * 15),
    (b"0123456789abcde", b"0123456789abcde" + b"\x00"),
    (b"0123456789abcdef", b"0123456789abcdef"),
    (b"0123456789abcdef0", b"0123456789abcdef0" + b"\x00" * 15),
    (b"0123456789abcdef0123456789abcde", b"0123456789abcdef0123456789abcde" + b"\x00"),
    (b"0123456789abcdef0123456789abcdef", b"0123456789abcdef0123456789abcdef"),
    (TEST_WORDS.encode(), TEST_WORDS.encode() + b"\x00" * 6),
    (ECB_WORDS.encode(), ECB_WORDS.encode() + b"\x00" * 5),
    (CBC_WORDS.encode(), CBC_WORDS.encode() + b"\x00" * 9),
]
BROKEN_NULPAD_TEST_CASES = [
    # (unpadded, padded)
    (b"\x00", b"\x00" * 16),
    (b"\x00" * 17, b"\x00" * 32),
    (b"\x01" * 15 + b"\x00" * 17, b"\x01" * 15 + b"\x00" * 17),
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
    from krux.kef import _pad, _unpad

    # pad() and unpad() expect bytestrings, and pkcs_pad ternary False/True/None
    unpadded = b"7 bytes"
    assert unpadded == _unpad(_pad(unpadded, False), False)  # NUL-pad
    assert unpadded == _unpad(_pad(unpadded, True), True)  # PKCS#7-pad
    assert unpadded == _pad(unpadded, None) == _unpad(unpadded, None)  # no pad
    invalid_params = (
        ("a string",),
        (b"a byte string",),
        (b"a byte string", 1),
        (b"a byte string", 0),
    )
    for invalids in invalid_params:
        with pytest.raises(TypeError):
            _pad(*invalids)
        with pytest.raises(TypeError):
            _unpad(*invalids)

    # versions 0,1 pad to complete last 16byte block w/ b"\x00" bytes
    for unpadded, padded in NULPAD_TEST_CASES:
        assert _pad(unpadded, False) == padded
        assert _unpad(padded, False) == unpadded
        len_padding = len(padded) - len(unpadded)
        if len_padding:
            assert _pad(unpadded, False)[-len_padding:] == b"\x00" * len_padding

    # versions 0,1 use non-faithful padding for bytestrings ending w/ b"\x00"
    for unpadded, padded in BROKEN_NULPAD_TEST_CASES:
        # pad() works just fine
        assert _pad(unpadded, False) == padded

        # but unpad() will strip too many padding bytes
        with pytest.raises(AssertionError):
            assert _unpad(padded, False) == unpadded

    # pkcs padding always adds at least 1 byte of padding
    for unpadded, padded in PKCSPAD_TEST_CASES:
        assert _pad(unpadded, True) == padded
        assert _unpad(padded, True) == unpadded
        len_padding = len(padded) - len(unpadded)
        assert (
            _pad(unpadded, True)[-len_padding:]
            == len_padding.to_bytes(1, "big") * len_padding
        )


def test_deflate_compression(m5stickv):
    from krux import kef

    testtexts = (
        (
            TEST_WORDS.encode(),
            ECB_WORDS.encode(),
            CBC_WORDS.encode(),
            CTR_WORDS.encode(),
            GCM_WORDS.encode(),
            ECB_ENTROPY,
            CBC_ENTROPY,
            CTR_ENTROPY,
            GCM_ENTROPY,
            b'"Running bitcoin" -Hal, January 10, 2009',
            b"\x00",
        )
        + BROKEN_AUTH16_ENTROPIES
        + BROKEN_AUTH4_ENTROPIES
    )

    for uncompressed in testtexts:
        compressed = kef._deflate(uncompressed)
        assert kef._reinflate(compressed) == uncompressed

        # _deflate expects bytes
        try:
            non_compressible = uncompressed.decode()
        except:
            non_compressible = repr(uncompressed)
        with pytest.raises(ValueError, match="Error compressing"):
            kef._deflate(non_compressible)

        # _reinflate expects complete/non-corrupted compressed bytes
        with pytest.raises(ValueError, match="Error decompressing"):
            kef._reinflate(compressed[:-1])


def kef_self_document(version, label=None, iterations=None, limit=None):
    """This is NOT a unit-test, it's a way for KEF encoding to document itself"""

    from krux import kef
    from collections import OrderedDict

    def join_text(a_dict, limit):
        result = "\n".join(["{}: {}".format(k, v) for k, v in a_dict.items()])
        if not limit or len(result) <= limit:
            return result

        result = result.replace(" + ", " +")
        if len(result) <= limit:
            return result

        result = result.replace(" +", "+")
        if len(result) <= limit:
            return result

        result = result.replace(" ", "")
        if len(result) <= limit:
            return result

        return result[: limit - 3] + "..."

    # rules are declared as VERSIONS values
    v_name = kef.VERSIONS[version]["name"]
    v_mode = kef.VERSIONS[version]["mode"]
    mode_name = [k for k, v in kef.MODE_NUMBERS.items() if v == v_mode][0]
    v_iv = kef.MODE_IVS.get(v_mode, 0)
    v_auth = kef.VERSIONS[version].get("auth", 0)
    v_pkcs = kef.VERSIONS[version].get("pkcs_pad", False)
    v_compress = kef.VERSIONS[version].get("compress", False)

    label_key = "KEF bytes"
    if label:
        label_key = "[{}] KEF bytes".format(label)

    itertext = " big; =(i > 10K) ? i : i * 10K"
    if iterations:
        itertext = "; ={}".format(iterations)

    text = OrderedDict()
    text[label_key] = "len_id + id + v + i + cpl"
    text["len_id"] = "1b"
    text["id"] = "<len_id>b"
    text["v"] = "1b; ={}".format(version)
    text["i"] = "3b{}".format(itertext)
    text["cpl"] = None

    cpl = "{}"
    if v_iv:
        cpl = "iv + {}".format(cpl)
        iv_arg = ", iv"
        text["iv"] = "{}b".format(v_iv)
    else:
        iv_arg = ""

    if v_compress:
        plain = "zlib(<P>, wbits=-10)"
    else:
        plain = "<P>"

    if mode_name in ("AES-ECB", "AES-CBC", "AES-CTR"):
        if v_auth > 0:
            auth = "sha256({} + {} + k)[:{}]".format(
                "v + iv" if iv_arg else "v", plain, v_auth
            )
            cpl += " + auth"
            text["e"] = None
            text["pad"] = None
        elif v_auth < 0:
            auth = "sha256({})[:{}]".format(plain, -v_auth)
            plain += " + auth"
            text["e"] = None
            text["auth"] = None
    elif mode_name == "AES-GCM":
        auth = "e.authtag[:{}]".format(v_auth)
        cpl += " + auth"
        text["e"] = None
        text["auth"] = None

    pad = None
    if v_pkcs in (True, False):
        plain += " + pad"
        text["pad"] = None
        pad = "PKCS7" if v_pkcs else "NUL"

    text["cpl"] = cpl.format("e.encrypt({})".format(plain))
    text["e"] = "AES(k, {}{})".format(mode_name[-3:], iv_arg)
    text["auth"] = auth
    if pad:
        text["pad"] = pad
    text["k"] = "pbkdf2_hmac_sha256(<K>, id, i)"

    return join_text(text, limit)


def test_kef_self_document(m5stickv):
    """Does not test KEF code, tests the above kef_self_document function"""
    from krux import kef

    test_cases = {
        0: "[AES-ECB v1] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =0\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: e.encrypt(<P> + auth + pad)\ne: AES(k, ECB)\nauth: sha256(<P>)[:16]\npad: NUL\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        1: "[AES-CBC v1] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =1\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: iv + e.encrypt(<P> + auth + pad)\niv: 16b\ne: AES(k, CBC, iv)\nauth: sha256(<P>)[:16]\npad: NUL\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        5: "[AES-ECB] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =5\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: e.encrypt(<P> + pad) + auth\ne: AES(k, ECB)\npad: NUL\nauth: sha256(v + <P> + k)[:3]\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        6: "[AES-ECB +p] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =6\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: e.encrypt(<P> + auth + pad)\ne: AES(k, ECB)\nauth: sha256(<P>)[:4]\npad: PKCS7\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        7: "[AES-ECB +c] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =7\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: e.encrypt(zlib(<P>, wbits=-10) + auth + pad)\ne: AES(k, ECB)\nauth: sha256(zlib(<P>, wbits=-10))[:4]\npad: PKCS7\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        10: "[AES-CBC] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =10\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: iv + e.encrypt(<P> + pad) + auth\niv: 16b\ne: AES(k, CBC, iv)\npad: NUL\nauth: sha256(v + iv + <P> + k)[:4]\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        11: "[AES-CBC +p] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =11\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: iv + e.encrypt(<P> + auth + pad)\niv: 16b\ne: AES(k, CBC, iv)\nauth: sha256(<P>)[:4]\npad: PKCS7\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        12: "[AES-CBC +c] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =12\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: iv + e.encrypt(zlib(<P>, wbits=-10) + auth + pad)\niv: 16b\ne: AES(k, CBC, iv)\nauth: sha256(zlib(<P>, wbits=-10))[:4]\npad: PKCS7\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        15: "[AES-CTR] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =15\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: iv + e.encrypt(<P> + auth)\niv: 12b\ne: AES(k, CTR, iv)\nauth: sha256(<P>)[:4]\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        16: "[AES-CTR +c] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =16\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: iv + e.encrypt(zlib(<P>, wbits=-10) + auth)\niv: 12b\ne: AES(k, CTR, iv)\nauth: sha256(zlib(<P>, wbits=-10))[:4]\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        20: "[AES-GCM] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =20\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: iv + e.encrypt(<P>) + auth\niv: 12b\ne: AES(k, GCM, iv)\nauth: e.authtag[:4]\nk: pbkdf2_hmac_sha256(<K>, id, i)",
        21: "[AES-GCM +c] KEF bytes: len_id + id + v + i + cpl\nlen_id: 1b\nid: <len_id>b\nv: 1b; =21\ni: 3b big; =(i > 10K) ? i : i * 10K\ncpl: iv + e.encrypt(zlib(<P>, wbits=-10)) + auth\niv: 12b\ne: AES(k, GCM, iv)\nauth: e.authtag[:4]\nk: pbkdf2_hmac_sha256(<K>, id, i)",
    }

    for v in kef.VERSIONS:
        if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
            continue

        expected = test_cases[v]
        label = kef.VERSIONS[v]["name"]
        doc = kef_self_document(v, label=label)
        print("\n" + doc)
        assert doc == expected

        assert (
            kef_self_document(v, label=label, limit=53)
            == expected.replace(" ", "")[:50] + "..."
        )
    # assert 0


def test_multi_wrapped_envelopes(m5stickv):
    """Test that nothing breaks when KEF messages are used to hide other KEF messages"""
    from krux import kef
    from krux.wdt import wdt

    key = "abc"
    iterations, i_step = 10000, 1234
    orig_plaintext = "KEF my dear, you can call me Matryoshka. ;)".encode()

    # encrypt plaintext for versions of KEF
    plaintext = orig_plaintext
    plaintext2 = orig_plaintext
    for v, version in sorted(kef.VERSIONS.items()):
        wdt.feed()

        if version is None or version["mode"] is None:
            continue

        label = '"{}", K={}'.format(version["name"][4:], key)
        id_ = kef_self_document(v, label=label, iterations=iterations, limit=252)
        id2 = kef._deflate(id_.encode())  # id_ can be any bytes, here compressed
        cipher = kef.Cipher(key, id_, iterations)
        cipher2 = kef.Cipher(key, id2, iterations)
        iv = I_VECTOR[: kef.MODE_IVS.get(version["mode"], 0)]
        cipher_payload = cipher.encrypt(plaintext, v, iv)
        cipher_payload2 = cipher2.encrypt(plaintext2, v, iv)
        plaintext = kef.wrap(id_, v, iterations, cipher_payload)
        plaintext2 = kef.wrap(id2, v, iterations, cipher_payload2)
        assert plaintext[:-1] != b"\x00"
        assert plaintext2[:-1] != b"\x00"
        iterations += i_step

    print("\nI'm a KEF puzzle.", repr(plaintext))
    print(
        "\nI'm a KEF puzzle w/ compressed id `deflate(id, wbits=-10)`.",
        repr(plaintext2),
    )

    # decode and decrypt KEF packages until we find something that's not KEF
    while True:
        wdt.feed()

        try:
            parsed = kef.unwrap(plaintext)
            parsed2 = kef.unwrap(plaintext2)
            id_, v, iterations, cipher_payload = parsed
            id2, v2, iterations2, cipher_payload2 = parsed2
            assert v == v2
            assert iterations == iterations2
            assert id_ == kef._reinflate(id2)
            # print("\n" + id_)
        except:
            break
        cipher = kef.Cipher(key, id_, iterations)
        cipher2 = kef.Cipher(key, id2, iterations)
        plaintext = cipher.decrypt(cipher_payload, v)
        plaintext2 = cipher2.decrypt(cipher_payload2, v)

    assert plaintext == orig_plaintext
    assert plaintext2 == orig_plaintext


def test_report_rate_of_failure(m5stickv):
    from krux import kef
    from hashlib import sha512
    from embit.bip39 import mnemonic_from_bytes
    from krux.wdt import wdt

    encrs = {}
    errs = {}
    for v in sorted(kef.VERSIONS):
        if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
            continue

        name = kef.VERSIONS[v]["name"]
        iv = I_VECTOR[: kef.MODE_IVS.get(kef.VERSIONS[v]["mode"], 0)]
        e = kef.Cipher(b"key", b"salt", 10000)
        encrs[v] = {
            "name": name,
            "iv": iv,
            "e": e,
            "timid": 0,
            "avoided": 0,
            "failed": 0,
            "wrapper": 0,
            "sampled": 0,
        }
        errs[v] = {
            "encrypt": {},
            "wrapper": {},
            "decrypt": {},
        }

    # plaintext: will be deterministically altered for each loop
    plain = b""  # play here

    # samples per message type: *1 per message function below, *2 for re-encoding utf8
    # (256 is enough, 1K takes 9 seconds, 100K takes 12 minutes)
    samples = 256  # play here

    # message functions: takes message bytes, returns new same-size message bytes
    def f_16bytes(msg):
        return msg[:16]

    def f_32bytes(msg):
        return msg[:32]

    def f_12w_mnemonic(msg):
        return mnemonic_from_bytes(f_16bytes(msg[:16])).encode()

    def f_24w_mnemonic(msg):
        return mnemonic_from_bytes(f_32bytes(msg[:32])).encode()

    def f_repeated(msg):
        return msg[:16] * 2

    def f_medium(msg):
        return msg

    def f_long(msg):
        return b"".join(
            [
                f_16bytes(msg),
                f_32bytes(msg),
                f_12w_mnemonic(msg),
                f_24w_mnemonic(msg),
                f_repeated(msg),
                f_medium(msg),
            ]
        )

    msg_funcs = (
        f_16bytes,
        f_32bytes,
        f_12w_mnemonic,
        f_24w_mnemonic,
        f_repeated,
        f_medium,
        f_long,
    )

    def utf8_encoded(msg):
        # decoding latin-1 maintains byte-length; re-encoding to utf8 likely adds bytes
        return msg.decode("latin-1").encode("utf8")

    failures = 0
    for i in range(samples):
        # rehash plain, make another for each message function, again for utf8 re-encoding
        plain = sha512(plain).digest()
        plaintexts = [msgfunc(plain) for msgfunc in msg_funcs]
        plaintexts.extend([utf8_encoded(msgfunc(plain)) for msgfunc in msg_funcs])
        for plain in plaintexts:
            for v in sorted(kef.VERSIONS):
                wdt.feed()

                if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
                    continue

                avoided = False
                failed = False
                kef_failed = False
                try:
                    cipher = encrs[v]["e"].encrypt(plain, v, encrs[v]["iv"])
                except Exception as err:
                    avoided = True
                    cipher = encrs[v]["e"].encrypt(
                        plain, v, encrs[v]["iv"], fail_unsafe=False
                    )
                    if repr(err) in errs[v]["encrypt"]:
                        errs[v]["encrypt"][repr(err)] += 1
                    else:
                        errs[v]["encrypt"][repr(err)] = 1

                try:
                    envelope = kef.wrap(b"salt", v, 10000, cipher)
                    assert kef.unwrap(envelope)[3] == cipher
                except Exception as err:
                    kef_failed = True
                    if repr(err) in errs[v]["wrapper"]:
                        errs[v]["wrapper"][repr(err)] += 1
                    else:
                        errs[v]["wrapper"][repr(err)] = 1

                try:
                    assert plain == encrs[v]["e"].decrypt(cipher, v)
                except Exception as err:
                    failed = True
                    if avoided:
                        err = "Decryption has failed but encryption was avoided"
                    if repr(err) in errs[v]["decrypt"]:
                        errs[v]["decrypt"][repr(err)] += 1
                    else:
                        errs[v]["decrypt"][repr(err)] = 1

                if not failed and avoided:
                    encrs[v]["timid"] += 1
                if failed and avoided:
                    encrs[v]["avoided"] += 1
                if failed and not avoided:
                    encrs[v]["failed"] += 1
                    failures += 1
                    print(
                        "Failure to decrypt: v: {}, plain: {}, cipher: {}".format(
                            v, plain, cipher
                        )
                    )
                if kef_failed:
                    failures += 1
                    print(
                        "KEF wrapping failure: v: {}, plain: {}, cipher: {}".format(
                            v, plain, cipher
                        )
                    )

                encrs[v]["sampled"] += 1

    print("Failure Summary:\nVer  Ver Name     Timid   Avoid    Fail  KEFerr   Samples")
    for v in sorted(kef.VERSIONS):
        if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
            continue

        print(
            " {:2d}  {:10s}  {:6d}  {:6d}  {:6d}  {:6d}  {:8d}".format(
                v,
                encrs[v]["name"],
                encrs[v]["timid"],  # able to decrypt, but refused to encrypt
                encrs[v]["avoided"],  # couldn't decrypt and refused to encrypt
                encrs[v]["failed"],  # failed to decrypt w/o refusing to encrypt
                encrs[v]["wrapper"],  # failure during KEF wrapping
                encrs[v]["sampled"],  # total samples
            )
        )

    print("\nPer-Version Failure Details:\nVer  Function    Count  Description")
    for v in sorted(kef.VERSIONS):
        if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
            continue

        for func in ("encrypt", "decrypt", "wrapper"):
            for error, count in errs[v][func].items():
                print(" {:2d}  {:10s} {:6d}  {}".format(v, func, count, error))

    assert failures == 0
    # assert 0


def NOtest_find_optimal_compress_threshold(m5stickv):
    from krux.kef import deflate_compress
    from krux.baseconv import base_encode
    from hashlib import sha512
    from embit.bip39 import WORDLIST

    def compression_value(content):
        orig = len(content)
        comp = len(deflate_compress(content))
        return orig - comp

    samples = (
        b"rand:" + b"".join([sha512(x).digest() for x in (b"a", b"b", b"c")]),
        b"pass:" + b"N01$houldE45uess7#!sP@5$w0rdNIW0n7R3m8eri73!ther",
        b"descr:"
        + b"wsh(sortedmulti(2,[d63dc4a7/48h/1h/0h/2h]tpubDEXCvh2aPYzMz2xfgsh9ZM6dQZxioYfCafUgw16keqschYbED4VeS46Qhr7EoonDHNr9dSsKPEGeRP5WRzDGdY3aazneR7wKmtDVNTf6qic,[c98cbe58/48h/1h/0h/2h]tpubDFXZ3rcRyvU6AvNrb4kRQFomJbtCTCyMX9jDJmfN5XfHLEAZq7a8h3CrYDZYtdexk6XWfT5DB8PYgySWA5GSdyWdzWwveQcbrzvVQw3u7bV,[9590b69a/48h/1h/0h/2h]tpubDEgtrNHQ68KvQPABjV4Ah39MpUH6aniH8gbHKygJSwNwbsQpnzPJMcssdqjwPtNshjAj8nP35iZisEFchFdZtPG4rXi7FW35dsCtQSj93Qv))",
        b"lower:" + b" ".join([x.encode() for x in WORDLIST]),
    )
    contents = []
    for sample in samples:
        contents.append(sample)
        for base in (43, 58, 64):
            label = "b{}:".format(base).encode()
            contents.append(label + base_encode(sample, base))

    results = {}
    for content in contents:
        best = len(content)
        end, step = best, best
        while True:
            step = step // 2
            if step < 2:
                break
            if compression_value(content[:end]) > 0:
                best = end
                end = end - step
            else:
                end = end + step
        results[content] = best

    for k, v in results.items():
        print("thresh: {} for {}b content: {}".format(v, len(k), k[:50]))
    # assert 0


def test_brute_force_compression_checks(m5stickv):
    """
    It is expected that different implementations of deflate/zlib.compress will
    result in different compressed bytes.  KEF defines that compression MUST be done
    with a 10-bits window -- so that others on restricted hardware may decompress.
    However, implementations may safely decompress using a larger window.

    This test verifies that `reinflate(deflate(original)) == original`.
    By default it will run external to krux devices but can be used to create a file
    for sdcard externally, then read on device, or created on device and read externally

    To play, hack tests.shared_mocks.DeflateIO to:
    * FAILURES: compress/write() using wrong wbits=-15, -14, -13, or -12,
      while leaving decompress/read() using wbits=-10, as KEF Specificiations demand.
    * OKAY: decompress/read() using non-standard wbits=-11 through -15,
      while restricting compress/write() using wbits=-10
    """
    from hashlib import sha256
    from binascii import hexlify
    from krux.baseconv import base_encode, base_decode
    from krux import kef
    from krux.wdt import wdt

    # default to make samples slightly larger than wbits
    bstr_size_threshold = 2**10 + 1

    def new_uncompressed_bytes(some_bytes):
        some_bytes = sha256(some_bytes).digest()
        while len(some_bytes) < bstr_size_threshold:
            some_bytes += sha256(some_bytes).digest()
        return some_bytes

    file_name = "/sd/brute-force-compression.txt"
    file_mode = "r"  # "w": to create file; "r": to read file; None to avoid file I/O
    attempts = 1000  # 1000 good enough for unit-tests, increase for on-device testing
    bstr_size_threshold = 2**14 + 1  # much larger than zlib.compression's 2**abs(wbits)

    # samples of problematic uncompressed bytestrings (wrong wbits for compression)
    try:
        from kef_brute_force_compression_samples import (
            all_samples as bstr_test_cases,
        )
    except:
        bstr_test_cases = []

    if file_mode:
        if file_mode == "r":
            print("Reading file '{}'...".format(file_name))
            try:
                file_handle = open(file_name, file_mode)
            except:
                file_mode = "w"
                print("  failed to read file {}".format(file_name))

        if file_mode == "w":
            print("Creating file '{}'...".format(file_name))
            try:
                file_handle = open(file_name, file_mode)
            except:
                file_mode = None
                print("  failed to create file {}, skipping file I/O".format(file_name))

    bstr = b""
    errors = 0
    for i in range(attempts):
        wdt.feed()

        if i < len(bstr_test_cases):
            bstr = bstr_test_cases[i]
        else:
            bstr = new_uncompressed_bytes(bstr)

        # test that we can compress and decompress on this platform
        comp = kef._deflate(bstr)
        sb64 = base_encode(comp, 64)
        try:
            assert bstr == kef._reinflate(base_decode(sb64, 64))
        except:
            errors += 1
            print("failed to reinflate after compressing bytes: ", repr(bstr))

        # when in "write" mode, export compressed to test another platform
        if file_mode == "w":
            file_handle.write(sb64 + "\n")
            continue

        if file_mode != "r":
            continue

        # when in "read" mode, test uncompressing from another platform
        sb64_from_file = file_handle.readline()
        try:
            bstr = kef._reinflate(base_decode(sb64_from_file, 64))
        except:
            errors += 1
            print(
                "failed to reinflate compressed bytes: ",
                repr(base_decode(sb64_from_file, 64)),
            )

    if file_mode:
        file_handle.close()

    print(
        "file_mode: {}  Completed {} deflate/reinflate assertions".format(
            file_mode, i + 1
        )
    )
    assert errors == 0


def NOtest_assuming_kef_is_working_create_one_control(m5stickv):
    """
    NOT TO BE USED UNTIL ALL TESTS ARE PASSING!!!
    Creates control strings for hard-coded tests
    """
    from krux import kef

    # adjust these to match your test
    plaintext = b"some secret bytes"
    id_ = b"label"
    version = 5
    iterations = 10000
    key = b"key"
    iv = I_VECTOR

    # encrypt the plaintext, wrap it in an envelope
    iv = iv[: kef.MODE_IVS.get(kef.VERSIONS[version]["mode"], 0)]
    cryptor = kef.Cipher(key, id_, iterations)
    encrypted = cryptor.encrypt(plaintext, version, iv)
    envelope = kef.wrap(id_, version, iterations, encrypted)

    # UNCERTAIN sanity checks that KEF code is at least faithful
    assert kef.unwrap(envelope) == (id_, version, iterations, encrypted)
    assert cryptor.decrypt(encrypted, version)

    # output copy-paste strings for use as hard-coded test controls
    print(
        "plaintext: {}\nid: {}\nversion: {}\niterations: {}\nkey: {}\niv: {}\n\nencrypted: {}\nkef: {}".format(
            plaintext,
            id_,
            "{} ({})".format(version, kef.VERSIONS[version]["name"]),
            iterations,
            key,
            iv,
            encrypted,
            envelope,
        )
    )
    assert 0


def test_grind_alternate_decryption_key(m5stickv):
    """
    KEF version 5 uses 3 bytes of auth, which is trivially weak.
    Same for versions which have 4 bytes of auth (others except 0 and 1).

    Therefore: an alternate decryption key, unlikely to be the
    correct key (if strong), can be found soon-ish, resulting in "garbage"
    bytes which are not the original secret.
    """
    from datetime import datetime, timedelta
    from embit import bip39, bip32
    from krux import kef
    from krux.baseconv import base_encode

    def another_key(byte_len):
        """yields all 'hex' values of byte_len from counter, as bytes"""
        counter = 0

        while True:
            try:
                yield counter.to_bytes(byte_len, "big").hex().encode()
                counter += 1
            except:
                break

    grinding = False  # False so that test-suite completes; True to grind

    test_cases = (
        # true key, true secret, KEF envelope, alternate key (from past grinding), garbage (from alt key)
        [
            # AES-ECB version 5 w/ 3 bytes auth
            b"abc",
            b"I'm 16 raw bytes",
            b"\x08a1e6c7e4\x05\x00\x00\x01\xe3\xc3\xb2\xa7)g\xa5q\x1eT\xd8sK\xf1\xfd\xd0-\xdc\x80",
            b"421a8f",
            b"'`+\xca\x9alt\xee\x9ad&k\x87\xdb\rp",
        ],
        [
            # AES-ECB version 5 w/ 3 bytes auth
            b"key",
            b"I'm 16 raw bytes",
            b"\x08a1e6c7e4\x05\x00\x00\x01\xf1\xe37\x1b\x01B*HC\x0cZW\x9b\xf9\xf0/\xca\x8a\x8f",
            b"f2a8e9",
            b"\xc8k\xa0\xc2i!\xe7`\xcen\x11!o\xff\xc42",
        ],
        # TODO: more examples from other versions once a performance-optimized KEF exists
    )

    for test_case in test_cases:
        key, control_secret, kef_envelope, alt_key, control_garbage = test_case
        id_, version, iterations, cpl = kef.unwrap(kef_envelope)
        decryptor = kef.Cipher(key, id_, iterations)
        secret = decryptor.decrypt(cpl, version)
        assert secret == control_secret

        decryptor = kef.Cipher(alt_key, id_, iterations)
        garbage = decryptor.decrypt(cpl, version)
        assert garbage == control_garbage
        assert garbage != secret

    if grinding:
        # original secret, bip39 mnemonic entropy
        secret = b"I'm 16 raw bytes"  # bad example of bip39 12w mnemonic entropy
        key = b"key"  # bad example of a user-supplied encryption key

        # kef setup
        id_ = b"a1e6c7e4"  # bip32 mfp derived w/ secret as bip39 entropy
        version = 20  # play here for other versions w/ "weak" auth
        iterations = 10000  # minimal amount of iterations
        ivec = I_VECTOR[:12]  # Initialization_Vector or b""

        # try 256x more than probably necessary
        key_len = abs(kef.VERSIONS[version]["auth"]) + 1

        # create a KEF envelope
        encryptor = kef.Cipher(key, id_, iterations)
        cpl = encryptor.encrypt(secret, version, ivec)
        envelope = kef.wrap(id_, version, iterations, cpl)
        fmt = "Original:\n secret: {}\n key: {}\n id_: {}\n version: {}\n iterations: {}\n IV: {}\n KEF: {}\n b43 KEF: {}\n"
        print(
            fmt.format(
                secret,
                key,
                id_,
                version,
                iterations,
                ivec,
                envelope,
                base_encode(envelope, 43),
            )
        )

        progress_step = 10
        begin = datetime.now()
        print("Grinding for an alternate decryption key: {}...".format(begin))
        for i, alternate in enumerate(another_key(key_len)):
            alternate = alternate.lstrip(
                b"0"
            )  # strip leading b'0's from hex encoded key
            decryptor = kef.Cipher(alternate, id_, iterations)
            decrypted = decryptor.decrypt(cpl, version)

            if (i + 1) % progress_step == 0:
                print(
                    " grinding attempts: {}, elapsed: {}".format(
                        i + 1, datetime.now() - begin
                    )
                )
                progress_step *= 10

            if decrypted is not None and alternate != key:
                fmt = "Alternate key found: {}, attempts: {}, elapsed: {}\n returns {} bytes: {}"
                print(
                    fmt.format(
                        alternate,
                        i + 1,
                        datetime.now() - begin,
                        len(decrypted),
                        decrypted,
                    )
                )
                assert decrypted != secret
                assert len(decrypted) <= len(secret)

                try:
                    alt_mnemonic = bip39.mnemonic_from_bytes(decrypted)
                    alt_seed = bip39.mnemonic_to_seed(alt_mnemonic)
                    alt_bip32 = bip32.HDKey.from_seed(alt_seed)
                    fmt = " would load bip39 mnemonic: {}\n w/ bip32 fingerprint: {}"
                    print(fmt.format(alt_mnemonic, alt_bip32.my_fingerprint.hex()))
                    break
                except:
                    pass

        assert 0

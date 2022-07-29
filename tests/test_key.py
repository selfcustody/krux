import pytest


@pytest.fixture
def tdata(mocker):
    import binascii
    from collections import namedtuple

    TEST_12_WORD_MNEMONIC = (
        "olympic term tissue route sense program under choose bean emerge velvet absurd"
    )
    TEST_24_WORD_MNEMONIC = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"

    D6_STATES = "123456"
    D20_STATES = [str(i + 1) for i in range(20)]

    TEST_D6_MIN_ENTROPY = "-".join([D6_STATES[i % 6] for i in range(50)])
    TEST_D6_MAX_ENTROPY = "-".join([D6_STATES[i % 6] for i in range(100)])
    TEST_D20_MIN_ENTROPY = "-".join([D20_STATES[i % 20] for i in range(30)])
    TEST_D20_MAX_ENTROPY = "-".join([D20_STATES[i % 20] for i in range(60)])

    TEST_MNEMONIC = TEST_12_WORD_MNEMONIC
    TEST_FINGERPRINT = b"U\xf8\xfc]"
    TEST_DERIVATION = "[55f8fc5d/84h/1h/0h]"
    TEST_XPUB = "tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s"
    TEST_P2WSH_ZPUB = "Vpub5j5qqZeDSW2z2PiEnggvphpeiz1ipDtXHAAwMnV7quhsEWZnv5xrSwDm2hyxsyHLzeUM4EVX3P9V82inZkpeLpszEkwwsk1jNYq63ygjZ6V"
    TEST_P2WPKH_ZPUB = "vpub5YBkiKumsYUcbpYrr2DwzdUr1ByTbsCvxtXGSXDaU8sTcKzt9gaaMpMqE12VKY4SmBQNBeVQAAkyzs72GXfhCLmKQHqYULYjUpZDU4Y7tv6"

    TEST_HASH = binascii.unhexlify(
        "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7"
    )
    TEST_INVALID_HASH = binascii.unhexlify("deadbeef")
    TEST_SIG = binascii.unhexlify(
        "3044022050655d5880d719680a445bc4dbf31971869a37cc30d874480d740ee82407f43102202352f1e779e2de5a63dd90dc210db6ff80544ec0cf7410e8ffda1d2d4f002740"
    )

    return namedtuple(
        "TestData",
        [
            "TEST_12_WORD_MNEMONIC",
            "TEST_24_WORD_MNEMONIC",
            "D6_STATES",
            "D20_STATES",
            "TEST_D6_MIN_ENTROPY",
            "TEST_D6_MAX_ENTROPY",
            "TEST_D20_MIN_ENTROPY",
            "TEST_D20_MAX_ENTROPY",
            "TEST_MNEMONIC",
            "TEST_FINGERPRINT",
            "TEST_DERIVATION",
            "TEST_XPUB",
            "TEST_P2WSH_ZPUB",
            "TEST_P2WPKH_ZPUB",
            "TEST_HASH",
            "TEST_INVALID_HASH",
            "TEST_SIG",
        ],
    )(
        TEST_12_WORD_MNEMONIC,
        TEST_24_WORD_MNEMONIC,
        D6_STATES,
        D20_STATES,
        TEST_D6_MIN_ENTROPY,
        TEST_D6_MAX_ENTROPY,
        TEST_D20_MIN_ENTROPY,
        TEST_D20_MAX_ENTROPY,
        TEST_MNEMONIC,
        TEST_FINGERPRINT,
        TEST_DERIVATION,
        TEST_XPUB,
        TEST_P2WSH_ZPUB,
        TEST_P2WPKH_ZPUB,
        TEST_HASH,
        TEST_INVALID_HASH,
        TEST_SIG,
    )


def mock_modules(mocker):
    from embit import bip39, bip32
    import binascii

    mocker.patch("krux.key.bip32", new=mocker.MagicMock(wraps=bip32))
    mocker.patch("krux.key.bip39", new=mocker.MagicMock(wraps=bip39))
    mocker.patch("krux.key.hexlify", new=mocker.MagicMock(wraps=binascii.hexlify))


def test_init(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from embit.networks import NETWORKS
    from krux.key import Key

    cases = [
        (
            [tdata.TEST_12_WORD_MNEMONIC, False],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "multisig": False,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPfJtsjGcMm6f7ibxmy2LbqbePeCJnhE3tFNKfuWmNHUyMnAfgwQXDSAhfTLGvN4f8zjEFochGbnHiZcrGXnyHDKQaTRK5trx",
                "derivation": "m/84h/1h/0h",
                "xpub": "tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s",
            },
        ),
        (
            [tdata.TEST_12_WORD_MNEMONIC, True],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "multisig": True,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPfJtsjGcMm6f7ibxmy2LbqbePeCJnhE3tFNKfuWmNHUyMnAfgwQXDSAhfTLGvN4f8zjEFochGbnHiZcrGXnyHDKQaTRK5trx",
                "derivation": "m/48h/1h/0h/2h",
                "xpub": "tpubDDyrxYEe6bifecFTgj8vzsoUhoJmtVWeARR5xRun6haVnVrC2oTAYhj7Ja2KTkcnkW1mZPPuWGDxEsHMtRf8aAf4WfrqhLDN7xi9zAZMphv",
            },
        ),
        (
            [tdata.TEST_12_WORD_MNEMONIC, False, NETWORKS["main"]],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "multisig": False,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K4VfM4hkrbT38QUYZjWJbW3jGmmtLDFZQTmaav9RcmjburzW2w38u4jAtTEfACi5LXsgWgQMKnj282ydxsSFEJDfA1o1TySf",
                "derivation": "m/84h/0h/0h",
                "xpub": "xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA",
            },
        ),
        (
            [tdata.TEST_12_WORD_MNEMONIC, True, NETWORKS["main"]],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "multisig": True,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K4VfM4hkrbT38QUYZjWJbW3jGmmtLDFZQTmaav9RcmjburzW2w38u4jAtTEfACi5LXsgWgQMKnj282ydxsSFEJDfA1o1TySf",
                "derivation": "m/48h/0h/0h/2h",
                "xpub": "xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy",
            },
        ),
        (
            [tdata.TEST_24_WORD_MNEMONIC, False],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "multisig": False,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPe5ghS4VTSeC3XwXJqVcJo4pzkFpuqZzFxhjuMsF13r8avzU8nwnwng6PCZ5EcJuPuqWwvJVCMRj3G9ZZyJ884RcrjAQ52BG",
                "derivation": "m/84h/1h/0h",
                "xpub": "tpubDDSTQYhtVBGJQjoQFyjUnctER4oTnCrr9vo9Cy6ACaMJvgrABE5WVwXjUGRep2K7aSRjqG8Cjtd2oH47oMA9fDbT1aLLeB3MN76tYo9MM8P",
            },
        ),
        (
            [tdata.TEST_24_WORD_MNEMONIC, True],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "multisig": True,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPe5ghS4VTSeC3XwXJqVcJo4pzkFpuqZzFxhjuMsF13r8avzU8nwnwng6PCZ5EcJuPuqWwvJVCMRj3G9ZZyJ884RcrjAQ52BG",
                "derivation": "m/48h/1h/0h/2h",
                "xpub": "tpubDENqBFtjHoP1Srrs62NY4hLtv9zTMVXPD4Vcca3orST5NgXEcjNhf67vcoaZxTDEThbCELNCt6i9WQrH5F7BuUZ4iZkBsZPoT5H3KyWMkWZ",
            },
        ),
        (
            [tdata.TEST_24_WORD_MNEMONIC, False, NETWORKS["main"]],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "multisig": False,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K3GTAmVdxGza4Dp76byaJTWussqQTMbVnB6zpNVuFY6m91pJUnaQdREZcCTTUSxKbSyyCo69FYNTSjWMGJwQ59KsSHUeNNQd",
                "derivation": "m/84h/0h/0h",
                "xpub": "xpub6Cyi7p8mUzogfZUvZ8DAMgvTBHKzFEnnX8SW4NPm8wNHDEYPf3utHZnuzPp3FW5MqvCrQ65UmUTPhMYMSgbmjP9ZtBnRwzAfqvT1e3YoEoC",
            },
        ),
        (
            [tdata.TEST_24_WORD_MNEMONIC, True, NETWORKS["main"]],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "multisig": True,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K3GTAmVdxGza4Dp76byaJTWussqQTMbVnB6zpNVuFY6m91pJUnaQdREZcCTTUSxKbSyyCo69FYNTSjWMGJwQ59KsSHUeNNQd",
                "derivation": "m/48h/0h/0h/2h",
                "xpub": "xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu",
            },
        ),
    ]

    for case in cases:
        key = Key(*case[0])

        assert isinstance(key, Key)
        assert key.mnemonic == case[1]["mnemonic"]
        assert key.multisig == case[1]["multisig"]
        assert key.network == case[1]["network"]
        assert key.root.to_base58() == case[1]["root key"]
        assert key.derivation == case[1]["derivation"]
        assert key.account.to_base58() == case[1]["xpub"]


def test_xpub(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import Key

    key = Key(tdata.TEST_MNEMONIC, False)
    mocker.spy(key.account, "to_base58")

    assert key.xpub() == tdata.TEST_XPUB
    key.account.to_base58.assert_called()


def test_key_expression(mocker, m5stickv, tdata):
    mock_modules(mocker)
    import krux
    from krux.key import Key

    key = Key(tdata.TEST_MNEMONIC, False)
    mocker.spy(key.account, "to_base58")

    cases = [
        (None, tdata.TEST_DERIVATION + tdata.TEST_XPUB),
        (key.network["xpub"], tdata.TEST_DERIVATION + tdata.TEST_XPUB),
        (key.network["zpub"], tdata.TEST_DERIVATION + tdata.TEST_P2WPKH_ZPUB),
        (key.network["Zpub"], tdata.TEST_DERIVATION + tdata.TEST_P2WSH_ZPUB),
    ]
    for case in cases:
        assert key.key_expression(case[0]) == case[1]
        krux.key.hexlify.assert_called_with(tdata.TEST_FINGERPRINT)
        key.account.to_base58.assert_called()


def test_sign(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from embit import ec
    from krux.key import Key

    key = Key(tdata.TEST_MNEMONIC, False)

    signature = key.sign(tdata.TEST_HASH)
    assert isinstance(signature, ec.Signature)
    assert signature.serialize() == tdata.TEST_SIG


def test_sign_fails_with_invalid_hash(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import Key

    key = Key(tdata.TEST_MNEMONIC, False)

    with pytest.raises(ValueError):
        key.sign(tdata.TEST_INVALID_HASH)


def test_to_mnemonic_words(mocker, m5stickv, tdata):
    mock_modules(mocker)
    import hashlib
    from krux.key import to_mnemonic_words

    cases = [
        (
            tdata.TEST_D6_MIN_ENTROPY,
            16,
            "range fatigue into stadium endless kitchen royal present rally welcome scatter twice",
        ),
        (
            tdata.TEST_D6_MAX_ENTROPY,
            32,
            "universe multiply siege pizza chapter copper huge regular flock soft tragic what method lesson ancient acquire amused dinner dial skate toilet affair warrior crazy",
        ),
        (
            tdata.TEST_D20_MIN_ENTROPY,
            16,
            "wasp payment shoot govern mobile strike dizzy ahead plastic cross dog joy",
        ),
        (
            tdata.TEST_D20_MAX_ENTROPY,
            32,
            "episode sentence sauce near bridge frequent forum junior develop slender sun title master twenty pair sudden nasty admit vault fitness reason setup hamster adult",
        ),
    ]
    for case in cases:
        words = to_mnemonic_words(hashlib.sha256(case[0].encode()).digest()[: case[1]])
        assert " ".join(words) == case[2]


def test_pick_final_word(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import pick_final_word

    mocker.patch("time.ticks_ms", new=lambda: 0)
    cases = [
        (
            tdata.TEST_D6_MIN_ENTROPY,
            16,
            "range fatigue into stadium endless kitchen royal present rally welcome scatter twice",
        ),
        (
            tdata.TEST_D6_MAX_ENTROPY,
            32,
            "universe multiply siege pizza chapter copper huge regular flock soft tragic what method lesson ancient acquire amused dinner dial skate toilet affair warrior crazy",
        ),
        (
            tdata.TEST_D20_MIN_ENTROPY,
            16,
            "wasp payment shoot govern mobile strike dizzy ahead plastic cross dog joy",
        ),
        (
            tdata.TEST_D20_MAX_ENTROPY,
            32,
            "episode sentence sauce near bridge frequent forum junior develop slender sun title master twenty pair sudden nasty admit vault fitness reason setup hamster adult",
        ),
    ]
    assert (
        pick_final_word(
            mocker.MagicMock(input=mocker.MagicMock(entropy=123456789)),
            tdata.TEST_12_WORD_MNEMONIC.split()[:-1],
        )
        == "army"
    )
    assert (
        pick_final_word(
            mocker.MagicMock(input=mocker.MagicMock(entropy=123456789)),
            tdata.TEST_24_WORD_MNEMONIC.split()[:-1],
        )
        == "habit"
    )
    assert (
        pick_final_word(
            mocker.MagicMock(input=mocker.MagicMock(entropy=987654321)),
            tdata.TEST_12_WORD_MNEMONIC.split()[:-1],
        )
        == "situate"
    )
    assert (
        pick_final_word(
            mocker.MagicMock(input=mocker.MagicMock(entropy=987654321)),
            tdata.TEST_24_WORD_MNEMONIC.split()[:-1],
        )
        == "speak"
    )


def test_pick_final_word_fails_when_wrong_word_count(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import pick_final_word

    with pytest.raises(ValueError):
        pick_final_word(mocker.MagicMock(), tdata.TEST_12_WORD_MNEMONIC.split()[:-2])

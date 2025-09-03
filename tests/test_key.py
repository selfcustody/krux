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

    TEST_D6_MIN_ENTROPY = "".join([D6_STATES[i % 6] for i in range(50)])
    TEST_D6_MAX_ENTROPY = "".join([D6_STATES[i % 6] for i in range(100)])
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


def test_init_fail_unknown_policy_type(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import Key

    # Assuming that the policy type is an integer
    # and that the valid types are 0, 1, and 2
    # (TYPE_SINGLESIG, TYPE_MULTISIG, TYPE_MINISCRIPT)
    # let's say that 3 is an unknown policy type,
    # not supported by the Key class.
    UNKNOWN_POLICY_TYPE = 3

    # It should raise a ValueError
    # when a non-supported policy type is passed
    # to the Key constructor
    with pytest.raises(ValueError) as exc_info:
        Key(tdata.TEST_12_WORD_MNEMONIC, UNKNOWN_POLICY_TYPE)

    # Check that the exception message is as expected
    # (e.g., "Invalid policy type: <some invalid type>")
    assert str(exc_info.value) == f"Invalid policy type: {UNKNOWN_POLICY_TYPE}"


def test_init(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from embit.networks import NETWORKS
    from krux.key import (
        Key,
        TYPE_SINGLESIG,
        TYPE_MULTISIG,
        P2SH,
        P2SH_P2WPKH,
        P2SH_P2WSH,
        P2WSH,
    )

    cases = [
        (
            # 0 - 12 words, testnet, singlesig, P2WPKH
            [tdata.TEST_12_WORD_MNEMONIC, TYPE_SINGLESIG],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_SINGLESIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPfJtsjGcMm6f7ibxmy2LbqbePeCJnhE3tFNKfuWmNHUyMnAfgwQXDSAhfTLGvN4f8zjEFochGbnHiZcrGXnyHDKQaTRK5trx",
                "derivation": "m/84h/1h/0h",
                "xpub": "tpubDCDuqu5HtBX2aD7wxvnHcj1DgFN1UVgzLkA1Ms4Va4P7TpJ3jDknkPLwWT2SqrKXNNAtJBCPcbJ8Tcpm6nLxgFapCZyhKgqwcEGv1BVpD7s",
            },
        ),
        (
            # 1- 12 words, testnet, singlesig, nested P2WPKH in a P2SH
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_SINGLESIG,
                NETWORKS["test"],
                "",
                0,
                P2SH_P2WPKH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_SINGLESIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPfJtsjGcMm6f7ibxmy2LbqbePeCJnhE3tFNKfuWmNHUyMnAfgwQXDSAhfTLGvN4f8zjEFochGbnHiZcrGXnyHDKQaTRK5trx",
                "derivation": "m/49h/1h/0h",
                "xpub": "tpubDDYHYR15Go9aqQVnXxBL2Dhpd3wCNzpicPdu2jdCxBMEKbEqVsNQSWF4uSkdETqeWNfhLcW6zNr5JMh9TmdCCheSSJMhTtQLDd3kFWM4xA6",
            },
        ),
        (
            # 2 - 12 words, testnet, multisig P2SH without cosigner index
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["test"],
                "",
                None,
                P2SH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPfJtsjGcMm6f7ibxmy2LbqbePeCJnhE3tFNKfuWmNHUyMnAfgwQXDSAhfTLGvN4f8zjEFochGbnHiZcrGXnyHDKQaTRK5trx",
                "derivation": "m/45h",
                "xpub": "tpubD8tn7Rd9J6j2TAz18j2qXbu9TVAkxX4sekKcgQhanzYJpNFztibFFGv9F6GZg9oBkZvKr79kDmYxiKkGogCQx2Fz2cwc7MNyY2AWZxxuX4y",
            },
        ),
        (
            # 3 - 12 words, testnet, multisig P2SH with cosigner index
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["test"],
                "",
                0,
                P2SH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPfJtsjGcMm6f7ibxmy2LbqbePeCJnhE3tFNKfuWmNHUyMnAfgwQXDSAhfTLGvN4f8zjEFochGbnHiZcrGXnyHDKQaTRK5trx",
                "derivation": "m/45h/0",
                "xpub": "tpubDAygfkgVAKk9rs6a4nDASPYUqqNgXCJy9DWECV8oeTDEM4AxN17pfsCmzRs38xdYr1rubtyAuiZxGCtLGUVoZP66G5GrT3jYUzWUBWPKuwX",
            },
        ),
        (
            # 4 - 12 words, testnet, nested multisig P2WSH in a P2SH
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["test"],
                "",
                0,
                P2SH_P2WSH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPfJtsjGcMm6f7ibxmy2LbqbePeCJnhE3tFNKfuWmNHUyMnAfgwQXDSAhfTLGvN4f8zjEFochGbnHiZcrGXnyHDKQaTRK5trx",
                "derivation": "m/48h/1h/0h/1h",
                "xpub": "tpubDDyrxYEe6bifdhnUibJwbHiAtEY8tmkfbvDPR13mWz9Dms8npePbG5hXwhrG5x9RxyvyRiWwoFWRoR4o4Axj2rq7Y656DGqkGFVhfNbZZNh",
            },
        ),
        (
            # 5 - 12 words, testnet, multisig P2WSH
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["test"],
                "",
                0,
                P2WSH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPfJtsjGcMm6f7ibxmy2LbqbePeCJnhE3tFNKfuWmNHUyMnAfgwQXDSAhfTLGvN4f8zjEFochGbnHiZcrGXnyHDKQaTRK5trx",
                "derivation": "m/48h/1h/0h/2h",
                "xpub": "tpubDDyrxYEe6bifecFTgj8vzsoUhoJmtVWeARR5xRun6haVnVrC2oTAYhj7Ja2KTkcnkW1mZPPuWGDxEsHMtRf8aAf4WfrqhLDN7xi9zAZMphv",
            },
        ),
        (
            # 6 - 12 words, mainnet, singlesig, P2WPKH
            [tdata.TEST_12_WORD_MNEMONIC, TYPE_SINGLESIG, NETWORKS["main"]],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_SINGLESIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K4VfM4hkrbT38QUYZjWJbW3jGmmtLDFZQTmaav9RcmjburzW2w38u4jAtTEfACi5LXsgWgQMKnj282ydxsSFEJDfA1o1TySf",
                "derivation": "m/84h/0h/0h",
                "xpub": "xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA",
            },
        ),
        (
            # 7 - 12 words, mainnet, singlesig, nested P2WPKH in a P2SH
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_SINGLESIG,
                NETWORKS["main"],
                "",
                0,
                P2SH_P2WPKH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_SINGLESIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K4VfM4hkrbT38QUYZjWJbW3jGmmtLDFZQTmaav9RcmjburzW2w38u4jAtTEfACi5LXsgWgQMKnj282ydxsSFEJDfA1o1TySf",
                "derivation": "m/49h/0h/0h",
                "xpub": "xpub6Ca1JGnSFNZ7g8zXNjwY1Li1GKEJPQnbq8Lcev7qoXj33PzMkwWnRKjwqSPo1ArJ2KY3GYAcYhJvcZTwvb99yWuQ5eH4rPEd5mvazBhKiTn",
            },
        ),
        (
            # 8 - 12 words, mainnet, multisig P2SH without cosigner index
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["main"],
                "",
                None,
                P2SH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K4VfM4hkrbT38QUYZjWJbW3jGmmtLDFZQTmaav9RcmjburzW2w38u4jAtTEfACi5LXsgWgQMKnj282ydxsSFEJDfA1o1TySf",
                "derivation": "m/45h",
                "xpub": "xpub68X9bBoTapmaBNo9gY3kKgZn8N56y8Zp77jKKreST5nR55bHpVkA6qFK14Bn9eqwxfPREXdsgfiv29FfQpMB4aogy2CJRpijx4a6owUbB8F",
            },
        ),
        (
            # 9 - 12 words, mainnet, multisig P2SH with cosigner index
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["main"],
                "",
                0,
                P2SH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K4VfM4hkrbT38QUYZjWJbW3jGmmtLDFZQTmaav9RcmjburzW2w38u4jAtTEfACi5LXsgWgQMKnj282ydxsSFEJDfA1o1TySf",
                "derivation": "m/45h/0",
                "xpub": "xpub6Ac49WroT3nhb4uicbE5EUD7WiH2Xooubauvqw5fJYTLbmWFHnGjXRXwkPnFcTgK47KzzKTJNcjua2PisceZfwdoCUXYmX5Ju2v4RU2C7ps",
            },
        ),
        (
            # 10 - 12 words, mainnet, nested multisig P2WSH in a P2SH
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["main"],
                "",
                0,
                P2SH_P2WSH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K4VfM4hkrbT38QUYZjWJbW3jGmmtLDFZQTmaav9RcmjburzW2w38u4jAtTEfACi5LXsgWgQMKnj282ydxsSFEJDfA1o1TySf",
                "derivation": "m/48h/0h/0h/1h",
                "xpub": "xpub6EKmKYGYc1WY3XTWp59sdZrAHGs7mB9dszpwtKBcS1icCfWiYqtGgmgQmm6emkQdSFCiTmX5bpQiMbt8rPsb7D6Skqsr1SeJcffkEHE4358",
            },
        ),
        (
            # 11 - 12 words, mainnet, multisig P2WSH
            [
                tdata.TEST_12_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["main"],
                "",
                0,
                P2WSH,
            ],
            {
                "mnemonic": tdata.TEST_12_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K4VfM4hkrbT38QUYZjWJbW3jGmmtLDFZQTmaav9RcmjburzW2w38u4jAtTEfACi5LXsgWgQMKnj282ydxsSFEJDfA1o1TySf",
                "derivation": "m/48h/0h/0h/2h",
                "xpub": "xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy",
            },
        ),
        (
            # 12 - 24 words, testnet, singlesig, P2WPKH
            [tdata.TEST_24_WORD_MNEMONIC, TYPE_SINGLESIG],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_SINGLESIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPe5ghS4VTSeC3XwXJqVcJo4pzkFpuqZzFxhjuMsF13r8avzU8nwnwng6PCZ5EcJuPuqWwvJVCMRj3G9ZZyJ884RcrjAQ52BG",
                "derivation": "m/84h/1h/0h",
                "xpub": "tpubDDSTQYhtVBGJQjoQFyjUnctER4oTnCrr9vo9Cy6ACaMJvgrABE5WVwXjUGRep2K7aSRjqG8Cjtd2oH47oMA9fDbT1aLLeB3MN76tYo9MM8P",
            },
        ),
        (
            # 13 - 24 words, testnet, singlesig, nested P2WPKH in a P2SH
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_SINGLESIG,
                NETWORKS["test"],
                "",
                0,
                P2SH_P2WPKH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_SINGLESIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPe5ghS4VTSeC3XwXJqVcJo4pzkFpuqZzFxhjuMsF13r8avzU8nwnwng6PCZ5EcJuPuqWwvJVCMRj3G9ZZyJ884RcrjAQ52BG",
                "derivation": "m/49h/1h/0h",
                "xpub": "tpubDCEmab93DuP5pAB9bSngzLwoSZmAp3kUV9pYKaTMiwzj68Enti2iMkteAJsSbmRJiPoKngqP7DtqA4ksNQmRdufzQttkxG1MEKz2haqJzKr",
            },
        ),
        (
            # 14 - 24 words, testnet, multisig P2SH without cosigner index
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["test"],
                "",
                None,
                P2SH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPe5ghS4VTSeC3XwXJqVcJo4pzkFpuqZzFxhjuMsF13r8avzU8nwnwng6PCZ5EcJuPuqWwvJVCMRj3G9ZZyJ884RcrjAQ52BG",
                "derivation": "m/45h",
                "xpub": "tpubD8ibRJxqmo4jButbUXjLkHP7btKVNJEGEsBSH3NsjHkMJKrzMzv2AxHLkMptDkjDjnLTeWu4nhPMgyJeg3HMwJ921TM6x31kG8zUroVy46N",
            },
        ),
        (
            # 15 - 24 words, testnet, multisig P2SH with cosigner index
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["test"],
                "",
                0,
                P2SH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPe5ghS4VTSeC3XwXJqVcJo4pzkFpuqZzFxhjuMsF13r8avzU8nwnwng6PCZ5EcJuPuqWwvJVCMRj3G9ZZyJ884RcrjAQ52BG",
                "derivation": "m/45h/0",
                "xpub": "tpubDAcr6jwpLb4kAY47ho3F9KBH9Lwc6G8NpgZYw1tQLUvyqmH7qFPTGRrGSgqr934yoeCZmNcCYPR64zF2nBebfujdgvwBUhbSfrpBq6X1urD",
            },
        ),
        (
            # 16 - 24 words, testnet, nested multisig P2WSH in a P2SH
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["test"],
                "",
                0,
                P2SH_P2WSH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPe5ghS4VTSeC3XwXJqVcJo4pzkFpuqZzFxhjuMsF13r8avzU8nwnwng6PCZ5EcJuPuqWwvJVCMRj3G9ZZyJ884RcrjAQ52BG",
                "derivation": "m/48h/1h/0h/1h",
                "xpub": "tpubDENqBFtjHoP1R8oj9tmyF5GuyHzSt6hGxBrMhTKvWw6qpB1NBmPvwoHH5TFuhjNQthuk7FZEHS9L33rsfg1LJmv89NuF9nvsWkTdYEH5tNj",
            },
        ),
        (
            # 17 - 24 words, testnet, netive multisig P2WSH
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["test"],
                "",
                0,
                P2WSH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["test"],
                "root key": "tprv8ZgxMBicQKsPe5ghS4VTSeC3XwXJqVcJo4pzkFpuqZzFxhjuMsF13r8avzU8nwnwng6PCZ5EcJuPuqWwvJVCMRj3G9ZZyJ884RcrjAQ52BG",
                "derivation": "m/48h/1h/0h/2h",
                "xpub": "tpubDENqBFtjHoP1Srrs62NY4hLtv9zTMVXPD4Vcca3orST5NgXEcjNhf67vcoaZxTDEThbCELNCt6i9WQrH5F7BuUZ4iZkBsZPoT5H3KyWMkWZ",
            },
        ),
        (
            # 18 - 24 words, mainnet, singlesig, P2WPKH
            [tdata.TEST_24_WORD_MNEMONIC, TYPE_SINGLESIG, NETWORKS["main"]],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_SINGLESIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K3GTAmVdxGza4Dp76byaJTWussqQTMbVnB6zpNVuFY6m91pJUnaQdREZcCTTUSxKbSyyCo69FYNTSjWMGJwQ59KsSHUeNNQd",
                "derivation": "m/84h/0h/0h",
                "xpub": "xpub6Cyi7p8mUzogfZUvZ8DAMgvTBHKzFEnnX8SW4NPm8wNHDEYPf3utHZnuzPp3FW5MqvCrQ65UmUTPhMYMSgbmjP9ZtBnRwzAfqvT1e3YoEoC",
            },
        ),
        (
            # 19 - 24 words, mainnet, singlesig, nested P2WPKH in a P2SH
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_SINGLESIG,
                NETWORKS["main"],
                "",
                0,
                P2SH_P2WPKH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_SINGLESIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K3GTAmVdxGza4Dp76byaJTWussqQTMbVnB6zpNVuFY6m91pJUnaQdREZcCTTUSxKbSyyCo69FYNTSjWMGJwQ59KsSHUeNNQd",
                "derivation": "m/49h/0h/0h",
                "xpub": "xpub6Bp2xfHLJNf8oLVdMJmPS2io82rS8TMv5wkuvE14CXEyGVnYubdE5NGDc46Yr68qTRLAq6YToEP9LxzX8PEPhKxed7XfTKGFdgkDHy83LkX",
            },
        ),
        (
            # 20 - 24 words, mainnet, multisig P2SH without cosigner index
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["main"],
                "",
                None,
                P2SH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K3GTAmVdxGza4Dp76byaJTWussqQTMbVnB6zpNVuFY6m91pJUnaQdREZcCTTUSxKbSyyCo69FYNTSjWMGJwQ59KsSHUeNNQd",
                "derivation": "m/45h",
                "xpub": "xpub68Lxu59A4X7Gv7hk2LkFYN3kGmDqNujChEb8vVKjPNzTZ3CHHn4w2WcWWKk6hFmywsoZ2wPCFbZJznp3HBS83rgiwrboGWMWgBQ56mfu8dQ",
            },
        ),
        (
            # 21 - 24 words, mainnet, multisig P2SH with cosigner index
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["main"],
                "",
                0,
                P2SH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K3GTAmVdxGza4Dp76byaJTWussqQTMbVnB6zpNVuFY6m91pJUnaQdREZcCTTUSxKbSyyCo69FYNTSjWMGJwQ59KsSHUeNNQd",
                "derivation": "m/45h/0",
                "xpub": "xpub6AFDaW88dK7HtjsGFc49wPqupDqx6sdKH3yFaTqFzaB66UcQm2YN7zBSCem4cY7k1jff9o6L1Hb3NokRPKoMnUHLdLBsoAwD5uDn531racV",
            },
        ),
        (
            # 22 - 24 words, mainnet, multisig P2SH-P2WSH
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["main"],
                "",
                0,
                P2SH_P2WSH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K3GTAmVdxGza4Dp76byaJTWussqQTMbVnB6zpNVuFY6m91pJUnaQdREZcCTTUSxKbSyyCo69FYNTSjWMGJwQ59KsSHUeNNQd",
                "derivation": "m/48h/0h/0h/1h",
                "xpub": "xpub6F2P6Pz5KLPgBu5k6kU8H9KGtYSqciCd9HQ7Jb7NNwNbThBw3NufvSoVJdMeJFR5ABQy1EHtSFJsDbuwSt3HXmUHRWqY3qc8jdoLYuvYKBg",
            },
        ),
        (
            # 23 - 24 words, mainnet, native multisig P2WSH
            [
                tdata.TEST_24_WORD_MNEMONIC,
                TYPE_MULTISIG,
                NETWORKS["main"],
                "",
                0,
                P2WSH,
            ],
            {
                "mnemonic": tdata.TEST_24_WORD_MNEMONIC,
                "policy_type": TYPE_MULTISIG,
                "network": NETWORKS["main"],
                "root key": "xprv9s21ZrQH143K3GTAmVdxGza4Dp76byaJTWussqQTMbVnB6zpNVuFY6m91pJUnaQdREZcCTTUSxKbSyyCo69FYNTSjWMGJwQ59KsSHUeNNQd",
                "derivation": "m/48h/0h/0h/2h",
                "xpub": "xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu",
            },
        ),
    ]

    n = 0
    for case in cases:
        print(f"Key init test case {n}")
        key = Key(*case[0])

        assert isinstance(key, Key)
        assert key.mnemonic == case[1]["mnemonic"]
        assert key.policy_type == case[1]["policy_type"]
        assert key.network == case[1]["network"]
        assert key.root.to_base58() == case[1]["root key"]
        assert key.derivation == case[1]["derivation"]
        assert key.account.to_base58() == case[1]["xpub"]
        n += 1


def test_xpub(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import Key, TYPE_SINGLESIG

    key = Key(tdata.TEST_MNEMONIC, TYPE_SINGLESIG)
    mocker.spy(key.account, "to_base58")

    assert key.xpub() == tdata.TEST_XPUB
    key.account.to_base58.assert_called()


def test_key_expression(mocker, m5stickv, tdata):
    mock_modules(mocker)
    import krux
    from krux.key import Key, TYPE_SINGLESIG

    key = Key(tdata.TEST_MNEMONIC, TYPE_SINGLESIG)
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
    from krux.key import Key, TYPE_SINGLESIG

    key = Key(tdata.TEST_MNEMONIC, TYPE_SINGLESIG)

    signature = key.sign(tdata.TEST_HASH)
    assert isinstance(signature, ec.Signature)
    assert signature.serialize() == tdata.TEST_SIG


def test_sign_fails_with_invalid_hash(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import Key, TYPE_SINGLESIG

    key = Key(tdata.TEST_MNEMONIC, TYPE_SINGLESIG)

    with pytest.raises(ValueError):
        key.sign(tdata.TEST_INVALID_HASH)


def test_to_mnemonic_words(mocker, m5stickv, tdata):
    mock_modules(mocker)
    import hashlib
    from embit.bip39 import mnemonic_from_bytes

    cases = [
        (
            tdata.TEST_D6_MIN_ENTROPY,
            16,
            "unveil nice picture region tragic fault cream strike tourist control recipe tourist",
        ),
        (
            tdata.TEST_D6_MAX_ENTROPY,
            32,
            "tornado cactus wheel picture target finish home neither trend picture shoulder endless deputy glide open oxygen another ability forum swear side alcohol devote random",
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
        words = mnemonic_from_bytes(
            hashlib.sha256(case[0].encode()).digest()[: case[1]]
        )
        assert words == case[2]


def test_pick_final_word(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import Key

    mocker.patch("time.ticks_ms", new=lambda: 0)
    assert (
        Key.pick_final_word(
            123456789,
            tdata.TEST_12_WORD_MNEMONIC.split()[:-1],
        )
        == "tobacco"
    )
    assert (
        Key.pick_final_word(
            123456789,
            tdata.TEST_24_WORD_MNEMONIC.split()[:-1],
        )
        == "uphold"
    )
    assert (
        Key.pick_final_word(
            987654321,
            tdata.TEST_12_WORD_MNEMONIC.split()[:-1],
        )
        == "flavor"
    )
    assert (
        Key.pick_final_word(
            987654321,
            tdata.TEST_24_WORD_MNEMONIC.split()[:-1],
        )
        == "drink"
    )


def test_pick_final_word_fails_when_wrong_word_count(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import Key

    with pytest.raises(ValueError):
        Key.pick_final_word(
            mocker.MagicMock(), tdata.TEST_12_WORD_MNEMONIC.split()[:-2]
        )


def test_get_final_word_candidates(mocker, m5stickv, tdata):
    from embit.bip39 import mnemonic_is_valid
    from krux.key import Key

    for mnemonic in (tdata.TEST_12_WORD_MNEMONIC, tdata.TEST_24_WORD_MNEMONIC):
        partial = mnemonic.split()[:-1]
        candidates = Key.get_final_word_candidates(partial)
        for final_word in candidates:
            assert mnemonic_is_valid(" ".join(partial + [final_word]))


def test_get_final_word_candidates_fails_when_wrong_word_count(mocker, m5stickv, tdata):
    mock_modules(mocker)
    from krux.key import Key

    with pytest.raises(ValueError):
        Key.get_final_word_candidates(tdata.TEST_12_WORD_MNEMONIC.split()[:-2])


def test_classmethod_extract_fingerprint(mocker, m5stickv, tdata):
    from krux.key import Key

    # extract_fingerprint also calls Key.extract_root - we don't need to create its tests
    fingerprint = Key.extract_fingerprint(tdata.TEST_12_WORD_MNEMONIC, pretty=False)

    assert fingerprint == "55f8fc5d"

    fingerprint = Key.extract_fingerprint("this is not a mnemonic", pretty=False)

    assert fingerprint == ""

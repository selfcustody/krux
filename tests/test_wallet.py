import pytest


@pytest.fixture
def tdata(mocker):
    import binascii
    from collections import namedtuple
    from ur.ur import UR
    from embit.networks import NETWORKS
    from krux.key import Key

    TEST_MNEMONIC1 = (
        "olympic term tissue route sense program under choose bean emerge velvet absurd"
    )
    TEST_MNEMONIC2 = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
    TEST_MNEMONIC3 = "range fatigue into stadium endless kitchen royal present rally welcome scatter twice"

    SINGLESIG_KEY = Key(TEST_MNEMONIC1, False, NETWORKS["main"])
    MULTISIG_KEY1 = Key(TEST_MNEMONIC1, True, NETWORKS["main"])
    MULTISIG_KEY2 = Key(TEST_MNEMONIC2, True, NETWORKS["main"])
    MULTISIG_KEY3 = Key(TEST_MNEMONIC3, True, NETWORKS["main"])

    # SINGLESIG_KEY [55f8fc5d/84h/0h/0h]xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA
    # MULTISIG_KEY1 [55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy
    # MULTISIG_KEY2 [3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu
    # MULTISIG_KEY3 [d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv

    SPECTER_SINGLESIG_DESCRIPTOR = "wpkh([55f8fc5d/84h/0h/0h]xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA/0/*)"
    SPECTER_SINGLESIG_WALLET_DATA = '{"label": "Specter Singlesig Wallet", "blockheight": 0, "descriptor": "wpkh([55f8fc5d/84h/0h/0h]xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA/0/*)#9qx3vqss", "devices": [{"type": "other", "label": "Key1"}]}'

    SPECTER_MULTISIG_DESCRIPTOR = "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/0/*,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/0/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/0/*))"
    SPECTER_MULTISIG_WALLET_DATA = '{"label": "Specter Multisig Wallet", "blockheight": 0, "descriptor": "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/0/*,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/0/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/0/*))#3nfc6jdy", "devices": [{"type": "other", "label": "Key1"}, {"type": "other", "label": "Key2"}, {"type": "other", "label": "Key3"}]}'

    BLUEWALLET_SINGLESIG_DESCRIPTOR = "wpkh(xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA)"
    BLUEWALLET_SINGLESIG_WALLET_DATA = "zpub6s3t4jJ6fCirgxL4WAasdamVyus8i4Dks4at95tw8tezYJvCtKBeZ1CHH33P7BUdY1iFBPQbB1XnnNxCmi9BoZ4BhBmYYCf9Sfxs6jY8Ycw"

    BLUEWALLET_MULTISIG_DESCRIPTOR = "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv))"
    BLUEWALLET_MULTISIG_WALLET_DATA = """
    # BlueWallet Multisig setup file
    # this file contains only public keys and is safe to
    # distribute among cosigners
    #
    Name: BlueWallet Multisig Wallet
    Policy: 2 of 3
    Derivation: m/48'/0'/0'/2'
    Format: P2WSH

    55f8fc5d:
    xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy

    3e15470d:
    xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu

    d3a80c8b:
    xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv
    """

    BLUEWALLET_MULTISIG_WALLET_DATA_INVALID_SCRIPT = """
    # BlueWallet Multisig setup file
    # this file contains only public keys and is safe to
    # distribute among cosigners
    #
    Name: BlueWallet Multisig Wallet
    Policy: 2 of 3
    Derivation: m/48'/0'/0'/2'
    Format: P2WPH

    55f8fc5d:
    xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy

    3e15470d:
    xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu

    d3a80c8b:
    xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv
    """

    BLUEWALLET_MULTISIG_WALLET_DATA_INVALID_KEYS = """
    # BlueWallet Multisig setup file
    # this file contains only public keys and is safe to
    # distribute among cosigners
    #
    Name: BlueWallet Multisig Wallet
    Policy: 2 of 3
    Derivation: m/48'/0'/0'/2'
    Format: P2WSH

    55f8fc5d:
    xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy
    """

    BLUEWALLET_MULTISIG_WALLET_DATA_MISSING_KEYS = """
    # BlueWallet Multisig setup file
    # this file contains only public keys and is safe to
    # distribute among cosigners
    #
    Name: BlueWallet Multisig Wallet
    Policy: 2 of 3
    """

    # TODO: Switch to 2-of-3 from keys defined above
    UR_OUTPUT_MULTISIG_DESCRIPTOR = "wsh(multi(1,xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB/1/0/*,xpub69H7F5d8KSRgmmdJg2KhpAK8SR3DjMwAdkxj3ZuxV27CprR9LgpeyGmXUbC6wb7ERfvrnKZjXoUmmDznezpbZb7ap6r1D3tgFxHmwMkQTPH/0/0/*))"
    UR_OUTPUT_MULTISIG_WALLET_DATA = UR(
        "crypto-output",
        bytearray(
            binascii.unhexlify(
                "d90191d90196a201010282d9012fa403582103cbcaa9c98c877a26977d00825c956a238e8dddfbd322cce4f74b0b5bd6ace4a704582060499f801b896d83179a4374aeb7822aaeaceaa0db1f85ee3e904c4defbd968906d90130a20180030007d90130a1018601f400f480f4d9012fa403582102fc9e5af0ac8d9b3cecfe2a888e2117ba3d089d8585886c9c826b6b22a98d12ea045820f0909affaa7ee7abe5dd4e100598d4dc53cd709d5a5c2cac40e7412f232f7c9c06d90130a2018200f4021abd16bee507d90130a1018600f400f480f4"
            )
        ),
    )

    UR_BYTES_MULTISIG_DESCRIPTOR = "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/0/*,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/0/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/0/*))"
    UR_BYTES_MULTISIG_WALLET_DATA = UR(
        "bytes",
        bytearray(
            b"y\x01\xf3"
            + '{"label": "Unknown Multisig Wallet", "descriptor": "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/0/*,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/0/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/0/*))#3nfc6jdy"}'.encode()
        ),
    )

    UNAMBIGUOUS_SINGLESIG_DESCRIPTOR = "wpkh([55f8fc5d/84h/0h/0h]xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA/<0;1>/*)"
    AMBIGUOUS_SINGLESIG_DESCRIPTOR = "wpkh([55f8fc5d/84h/0h/0h]xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA)"

    UNAMBIGUOUS_MULTISIG_DESCRIPTOR = "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/<0;1>/*,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/<0;1>/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/<0;1>/*))"
    AMBIGUOUS_MULTISIG_DESCRIPTOR = "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv))"

    UNRELATED_SINGLESIG_DESCRIPTOR = "wpkh([55f8fc5d/84h/0h/0h]xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB)"
    UNRELATED_MULTISIG_DESCRIPTOR = "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub661MyMwAqRbcFW31YEwpkMuc5THy2PSt5bDMsktWQcFF8syAmRUapSCGu8ED9W6oDMSgv6Zz8idoc4a6mr8BDzTJY47LJhkJ8UB7WEGuduB,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv))"

    UNSORTED_MULTISIG_DESCRIPTOR = "wsh(multi(2,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/<0;1>/*,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/<0;1>/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/<0;1>/*))"

    return namedtuple(
        "TestData",
        [
            "TEST_MNEMONIC1",
            "TEST_MNEMONIC2",
            "TEST_MNEMONIC3",
            "SINGLESIG_KEY",
            "MULTISIG_KEY1",
            "MULTISIG_KEY2",
            "MULTISIG_KEY3",
            "SPECTER_SINGLESIG_DESCRIPTOR",
            "SPECTER_SINGLESIG_WALLET_DATA",
            "SPECTER_MULTISIG_DESCRIPTOR",
            "SPECTER_MULTISIG_WALLET_DATA",
            "BLUEWALLET_SINGLESIG_DESCRIPTOR",
            "BLUEWALLET_SINGLESIG_WALLET_DATA",
            "BLUEWALLET_MULTISIG_DESCRIPTOR",
            "BLUEWALLET_MULTISIG_WALLET_DATA",
            "BLUEWALLET_MULTISIG_WALLET_DATA_INVALID_SCRIPT",
            "BLUEWALLET_MULTISIG_WALLET_DATA_INVALID_KEYS",
            "BLUEWALLET_MULTISIG_WALLET_DATA_MISSING_KEYS",
            "UR_OUTPUT_MULTISIG_DESCRIPTOR",
            "UR_OUTPUT_MULTISIG_WALLET_DATA",
            "UR_BYTES_MULTISIG_DESCRIPTOR",
            "UR_BYTES_MULTISIG_WALLET_DATA",
            "UNAMBIGUOUS_SINGLESIG_DESCRIPTOR",
            "AMBIGUOUS_SINGLESIG_DESCRIPTOR",
            "UNAMBIGUOUS_MULTISIG_DESCRIPTOR",
            "AMBIGUOUS_MULTISIG_DESCRIPTOR",
            "UNRELATED_SINGLESIG_DESCRIPTOR",
            "UNRELATED_MULTISIG_DESCRIPTOR",
            "UNSORTED_MULTISIG_DESCRIPTOR",
        ],
    )(
        TEST_MNEMONIC1,
        TEST_MNEMONIC2,
        TEST_MNEMONIC3,
        SINGLESIG_KEY,
        MULTISIG_KEY1,
        MULTISIG_KEY2,
        MULTISIG_KEY3,
        SPECTER_SINGLESIG_DESCRIPTOR,
        SPECTER_SINGLESIG_WALLET_DATA,
        SPECTER_MULTISIG_DESCRIPTOR,
        SPECTER_MULTISIG_WALLET_DATA,
        BLUEWALLET_SINGLESIG_DESCRIPTOR,
        BLUEWALLET_SINGLESIG_WALLET_DATA,
        BLUEWALLET_MULTISIG_DESCRIPTOR,
        BLUEWALLET_MULTISIG_WALLET_DATA,
        BLUEWALLET_MULTISIG_WALLET_DATA_INVALID_SCRIPT,
        BLUEWALLET_MULTISIG_WALLET_DATA_INVALID_KEYS,
        BLUEWALLET_MULTISIG_WALLET_DATA_MISSING_KEYS,
        UR_OUTPUT_MULTISIG_DESCRIPTOR,
        UR_OUTPUT_MULTISIG_WALLET_DATA,
        UR_BYTES_MULTISIG_DESCRIPTOR,
        UR_BYTES_MULTISIG_WALLET_DATA,
        UNAMBIGUOUS_SINGLESIG_DESCRIPTOR,
        AMBIGUOUS_SINGLESIG_DESCRIPTOR,
        UNAMBIGUOUS_MULTISIG_DESCRIPTOR,
        AMBIGUOUS_MULTISIG_DESCRIPTOR,
        UNRELATED_SINGLESIG_DESCRIPTOR,
        UNRELATED_MULTISIG_DESCRIPTOR,
        UNSORTED_MULTISIG_DESCRIPTOR,
    )


def test_init_singlesig(mocker, m5stickv, tdata):
    from krux.wallet import Wallet

    wallet = Wallet(tdata.SINGLESIG_KEY)

    assert isinstance(wallet, Wallet)
    assert wallet.descriptor.to_string() == tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR
    assert wallet.label == "Single-sig"
    assert wallet.policy == {"type": "p2wpkh"}


def test_init_multisig(mocker, m5stickv, tdata):
    from krux.wallet import Wallet

    wallet = Wallet(tdata.MULTISIG_KEY1)

    assert isinstance(wallet, Wallet)
    assert wallet.descriptor is None
    assert wallet.label is None
    assert wallet.policy is None


def test_is_multisig(mocker, m5stickv, tdata):
    from krux.wallet import Wallet

    wallet = Wallet(tdata.SINGLESIG_KEY)

    assert not wallet.is_multisig()

    wallet = Wallet(tdata.MULTISIG_KEY1)

    assert wallet.is_multisig()


def test_is_loaded(mocker, m5stickv, tdata):
    from krux.wallet import Wallet

    wallet = Wallet(tdata.SINGLESIG_KEY)

    assert not wallet.is_loaded()

    wallet = Wallet(tdata.MULTISIG_KEY1)

    assert not wallet.is_loaded()

    wallet.wallet_data = tdata.UR_OUTPUT_MULTISIG_WALLET_DATA

    assert wallet.is_loaded()


def test_wallet_qr(mocker, m5stickv, tdata):
    from krux.wallet import Wallet
    from krux.qr import FORMAT_UR

    wallet = Wallet(tdata.MULTISIG_KEY1)
    wallet.wallet_data = tdata.UR_OUTPUT_MULTISIG_WALLET_DATA
    wallet.wallet_qr_format = FORMAT_UR

    wallet_data, wallet_qr_format = wallet.wallet_qr()

    assert wallet_data == tdata.UR_OUTPUT_MULTISIG_WALLET_DATA
    assert wallet_qr_format == FORMAT_UR


def test_receive_addresses(mocker, m5stickv, tdata):
    from krux.wallet import Wallet
    from krux.qr import FORMAT_PMOFN

    cases = [
        (
            tdata.SINGLESIG_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            FORMAT_PMOFN,
            [
                "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
                "bc1q6hpnrwgy7a26newf5ewgl6a3f6cqz2xtmmhghx",
                "bc1qjfygdgjvw6euxtzs3fxx5d7fxvs8ypykzu8cjs",
                "bc1qjl4kpu95s2z9lws3pmwlww5260n66ccnc5uc8t",
                "bc1qzdwh9ctwj7wg5ul2pskc6rvzmmpn2l5j4lkprc",
                "bc1qdx4z958lcu0xfe9jkjm3v5354k0tq9pqwtv6th",
                "bc1q7s8u2g260f6qs97vmhc34kvpuque87uk3aw47h",
                "bc1qdm8yaere7fnu02tstwrxkhfgrfpteumjsl7l4r",
                "bc1qfz3rfm0da9m7lca8rfkzgs2uhk5cxnms5dxmxu",
                "bc1q6mlxs236fmyeteummv9x5pmxteh86lkln4emag",
            ],
        ),
        (
            tdata.MULTISIG_KEY1,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            FORMAT_PMOFN,
            [
                "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
                "bc1qv72e35u2qjtzm60qznzzc63aq6mjlxg6y8xnctw9vq5q9mp43lasj69v67",
                "bc1qymmm8s0g38hhjfxn0kdm2r9xsvch3gzxc07th2athuq7r9rje3xskwvk0q",
                "bc1qaerrqmm0ce4qsrlsvswvm6mmcw462cydwzawh4wy7eed8fcjkvtsdkccnl",
                "bc1qacxshm6p84zj4x6vevat65uqu6k8379x55vzp0gz5y6m0eyrgayqpuamez",
                "bc1q0xvq09ep68jp57v3f2et2pmm6vtdu9f5le9c5qr75rmlge4et25qlt2lkz",
                "bc1qnqq4qfa7c5vg9nh0ddvnwf9fxucms2c992h4qht9hzs96qc8fggsegfurq",
                "bc1qnds506sq72glz8x7pq3dkywhktg7scaua3d4mdzjpluwvtzxdwcsxlmj89",
                "bc1qss8w8dygehsqusat6hzxlrtzykqxjsmjsccdf9qlsx7yhjcze9xqekznh5",
                "bc1qgzqffn9f4fal2ld04wdafakvgrl5gexp744gm8eg58j7a633lf9slzcjup",
            ],
        ),
    ]

    for case in cases:
        wallet = Wallet(case[0])
        wallet.load(case[1], case[2])

        assert [addr for addr in wallet.obtain_addresses(0, limit=10)] == case[3]


def test_load_multisig(mocker, m5stickv, tdata):
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE, FORMAT_PMOFN, FORMAT_UR

    wallet = Wallet(tdata.MULTISIG_KEY1)

    cases = [
        (
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            FORMAT_PMOFN,
            tdata.SPECTER_MULTISIG_DESCRIPTOR,
            "Specter Multisig Wallet",
            {
                "type": "p2wsh",
                "m": 2,
                "n": 3,
                "cosigners": [
                    tdata.MULTISIG_KEY1.xpub(),
                    tdata.MULTISIG_KEY2.xpub(),
                    tdata.MULTISIG_KEY3.xpub(),
                ],
            },
        ),
        (
            tdata.BLUEWALLET_MULTISIG_WALLET_DATA,
            FORMAT_NONE,
            tdata.UNAMBIGUOUS_MULTISIG_DESCRIPTOR,
            "BlueWallet Multisig Wallet",
            {
                "type": "p2wsh",
                "m": 2,
                "n": 3,
                "cosigners": [
                    tdata.MULTISIG_KEY1.xpub(),
                    tdata.MULTISIG_KEY2.xpub(),
                    tdata.MULTISIG_KEY3.xpub(),
                ],
            },
        ),
        # TODO: Fix - ValueError: xpub not a cosigner
        # (tdata.UR_OUTPUT_MULTISIG_WALLET_DATA, FORMAT_UR, tdata.UR_OUTPUT_MULTISIG_DESCRIPTOR, '2 of 3', {
        #     'type': 'p2wsh', 'm': 2, 'n': 3, 'cosigners': [
        #         tdata.MULTISIG_KEY1.xpub(),
        #         tdata.MULTISIG_KEY2.xpub(),
        #         tdata.MULTISIG_KEY3.xpub()
        #     ]
        # }),
        (
            tdata.UR_BYTES_MULTISIG_WALLET_DATA,
            FORMAT_UR,
            tdata.UR_BYTES_MULTISIG_DESCRIPTOR,
            "Unknown Multisig Wallet",
            {
                "type": "p2wsh",
                "m": 2,
                "n": 3,
                "cosigners": [
                    tdata.MULTISIG_KEY1.xpub(),
                    tdata.MULTISIG_KEY2.xpub(),
                    tdata.MULTISIG_KEY3.xpub(),
                ],
            },
        ),
        (
            tdata.UNSORTED_MULTISIG_DESCRIPTOR,
            FORMAT_NONE,
            tdata.UNSORTED_MULTISIG_DESCRIPTOR,
            "2 of 3 multisig",
            {
                "type": "p2wsh",
                "m": 2,
                "n": 3,
                "cosigners": [
                    tdata.MULTISIG_KEY2.xpub(),
                    tdata.MULTISIG_KEY1.xpub(),
                    tdata.MULTISIG_KEY3.xpub(),
                ],
            },
        ),
    ]
    for case in cases:
        wallet.load(case[0], case[1])
        assert wallet.wallet_data == case[0]
        assert wallet.wallet_qr_format == case[1]
        assert wallet.descriptor.to_string() == case[2]
        assert wallet.label == case[3]
        assert wallet.policy == case[4]


def test_load_singlesig(mocker, m5stickv, tdata):
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE, FORMAT_PMOFN

    wallet = Wallet(tdata.SINGLESIG_KEY)

    cases = [
        (
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            FORMAT_PMOFN,
            tdata.SPECTER_SINGLESIG_DESCRIPTOR,
            "Specter Singlesig Wallet",
            {"type": "p2wpkh"},
        ),
        (
            tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR,
            FORMAT_NONE,
            tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR,
            "Single-sig",
            {"type": "p2wpkh"},
        ),
    ]
    for case in cases:
        wallet.load(case[0], case[1])
        assert wallet.wallet_data == case[0]
        assert wallet.wallet_qr_format == case[1]
        assert wallet.descriptor.to_string() == case[2]
        assert wallet.label == case[3]
        assert wallet.policy == case[4]


def test_load_singlesig_fails_with_multisig_descriptor(mocker, m5stickv, tdata):
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE, FORMAT_PMOFN, FORMAT_UR

    wallet = Wallet(tdata.SINGLESIG_KEY)

    cases = [
        (tdata.SPECTER_MULTISIG_WALLET_DATA, FORMAT_PMOFN),
        (tdata.BLUEWALLET_MULTISIG_WALLET_DATA, FORMAT_NONE),
        (tdata.UR_OUTPUT_MULTISIG_WALLET_DATA, FORMAT_UR),
        (tdata.UR_BYTES_MULTISIG_WALLET_DATA, FORMAT_UR),
    ]
    for case in cases:
        with pytest.raises(ValueError):
            wallet.load(case[0], case[1])


def test_load_multisig_fails_with_singlesig_descriptor(mocker, m5stickv, tdata):
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE, FORMAT_PMOFN

    wallet = Wallet(tdata.MULTISIG_KEY1)

    cases = [
        (tdata.SPECTER_SINGLESIG_WALLET_DATA, FORMAT_PMOFN),
        (tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR, FORMAT_NONE),
    ]
    for case in cases:
        with pytest.raises(ValueError):
            wallet.load(case[0], case[1])


def test_load_singlesig_fails_when_key_not_in_descriptor(mocker, m5stickv, tdata):
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(tdata.SINGLESIG_KEY)

    with pytest.raises(ValueError):
        wallet.load(tdata.UNRELATED_SINGLESIG_DESCRIPTOR, FORMAT_NONE)


def test_load_multisig_fails_when_key_not_in_descriptor(mocker, m5stickv, tdata):
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(tdata.MULTISIG_KEY1)

    with pytest.raises(ValueError):
        wallet.load(tdata.UNRELATED_MULTISIG_DESCRIPTOR, FORMAT_NONE)


def test_parse_wallet(mocker, m5stickv, tdata):
    from krux.wallet import parse_wallet
    from embit.networks import NETWORKS

    cases = [
        (
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            tdata.SPECTER_SINGLESIG_DESCRIPTOR,
            "Specter Singlesig Wallet",
        ),
        (
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            tdata.SPECTER_MULTISIG_DESCRIPTOR,
            "Specter Multisig Wallet",
        ),
        (
            tdata.BLUEWALLET_SINGLESIG_WALLET_DATA,
            tdata.BLUEWALLET_SINGLESIG_DESCRIPTOR,
            None,
        ),
        (
            tdata.BLUEWALLET_MULTISIG_WALLET_DATA,
            tdata.BLUEWALLET_MULTISIG_DESCRIPTOR,
            "BlueWallet Multisig Wallet",
        ),
        (
            tdata.UR_OUTPUT_MULTISIG_WALLET_DATA,
            tdata.UR_OUTPUT_MULTISIG_DESCRIPTOR,
            None,
        ),
        (
            tdata.UR_BYTES_MULTISIG_WALLET_DATA,
            tdata.UR_BYTES_MULTISIG_DESCRIPTOR,
            "Unknown Multisig Wallet",
        ),
        (
            tdata.AMBIGUOUS_MULTISIG_DESCRIPTOR,
            tdata.AMBIGUOUS_MULTISIG_DESCRIPTOR,
            None,
        ),
        (
            tdata.UNAMBIGUOUS_MULTISIG_DESCRIPTOR,
            tdata.UNAMBIGUOUS_MULTISIG_DESCRIPTOR,
            None,
        ),
        (
            tdata.AMBIGUOUS_SINGLESIG_DESCRIPTOR,
            tdata.AMBIGUOUS_SINGLESIG_DESCRIPTOR,
            None,
        ),
        (
            tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR,
            tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR,
            None,
        ),
    ]

    case_n = 1
    for case in cases:
        print(case_n)
        case_n += 1
        descriptor, label = parse_wallet(case[0], NETWORKS["main"])
        assert descriptor.to_string() == case[1]
        assert label == case[2]


def test_parse_wallet_raises_errors(mocker, m5stickv, tdata):
    from krux.wallet import parse_wallet
    from embit.networks import NETWORKS
    from ur.ur import UR

    cases = [
        tdata.BLUEWALLET_MULTISIG_WALLET_DATA_MISSING_KEYS,
        tdata.BLUEWALLET_MULTISIG_WALLET_DATA_INVALID_KEYS,
        tdata.BLUEWALLET_MULTISIG_WALLET_DATA_INVALID_SCRIPT,
        UR("unknown-type", bytearray("invalid wallet format".encode())),
        "invalid wallet format",
        '{"invalid": "json", "wallet": "format"}',
    ]
    for case in cases:
        with pytest.raises(ValueError):
            parse_wallet(case, NETWORKS["main"])


def test_parse_address(mocker, m5stickv, tdata):
    from krux.wallet import parse_address

    cases = [
        # m/44
        ("14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ", "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ"),
        # m/48/0/0/2
        ("1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k", "1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k"),
        # m/84
        (
            "bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn",
            "bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn",
        ),
        # m/49
        ("32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg", "32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg"),
        # m/0
        ("3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw", "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw"),
        (
            "bitcoin:14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
        ),
        (
            "bitcoin:1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k",
            "1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k",
        ),
        (
            "bitcoin:bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn",
            "bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn",
        ),
        (
            "bitcoin:32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg",
            "32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg",
        ),
        (
            "bitcoin:3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
        ),
        (
            "bitcoin:14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ?message=test",
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
        ),
        (
            "bitcoin:1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k?message=test",
            "1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k",
        ),
        (
            "bitcoin:bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn?message=test",
            "bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn",
        ),
        (
            "bitcoin:32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg?message=test",
            "32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg",
        ),
        (
            "bitcoin:3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw?message=test",
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
        ),
    ]

    for case in cases:
        assert parse_address(case[0]) == case[1]


def test_parse_address_raises_errors(mocker, m5stickv, tdata):
    from krux.wallet import parse_address

    cases = [
        "invalidaddress",
        "32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg$",
        "bitcorn:32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg",
    ]
    for case in cases:
        with pytest.raises(ValueError):
            parse_address(case)


def test_to_unambiguous_descriptor(mocker, m5stickv, tdata):
    from embit.descriptor import Descriptor
    from krux.wallet import to_unambiguous_descriptor

    cases = [
        (
            tdata.AMBIGUOUS_SINGLESIG_DESCRIPTOR,
            tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR,
        ),
        (
            tdata.AMBIGUOUS_MULTISIG_DESCRIPTOR,
            tdata.UNAMBIGUOUS_MULTISIG_DESCRIPTOR,
        ),
        (
            tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR,
            tdata.UNAMBIGUOUS_SINGLESIG_DESCRIPTOR,
        ),
        (
            tdata.UNAMBIGUOUS_MULTISIG_DESCRIPTOR,
            tdata.UNAMBIGUOUS_MULTISIG_DESCRIPTOR,
        ),
        (
            tdata.UR_OUTPUT_MULTISIG_DESCRIPTOR,
            tdata.UR_OUTPUT_MULTISIG_DESCRIPTOR,
        ),
        (tdata.SPECTER_MULTISIG_DESCRIPTOR, tdata.SPECTER_MULTISIG_DESCRIPTOR),
    ]

    for case in cases:
        unambiguous_descriptor = to_unambiguous_descriptor(
            Descriptor.from_string(case[0])
        )
        assert unambiguous_descriptor.to_string() == case[1]

import pytest
from ..shared_mocks import MockPrinter


@pytest.fixture
def tdata(mocker):
    from collections import namedtuple
    from krux.key import Key
    from embit.networks import NETWORKS

    TEST_12_WORD_MNEMONIC = (
        "olympic term tissue route sense program under choose bean emerge velvet absurd"
    )
    TEST_24_WORD_MNEMONIC = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
    SIGNING_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

    SINGLEKEY_12_WORD_KEY = Key(TEST_12_WORD_MNEMONIC, False, NETWORKS["main"])
    SINGLEKEY_24_WORD_KEY = Key(TEST_24_WORD_MNEMONIC, False, NETWORKS["main"])
    MULTISIG_12_WORD_KEY = Key(TEST_12_WORD_MNEMONIC, True, NETWORKS["main"])
    SINGLEKEY_SIGNING_KEY = Key(SIGNING_MNEMONIC, False, NETWORKS["main"])
    MULTISIG_SIGNING_KEY = Key(SIGNING_MNEMONIC, True, NETWORKS["main"])

    SPECTER_SINGLEKEY_WALLET_DATA = '{"label": "Specter Singlekey Wallet", "blockheight": 0, "descriptor": "wpkh([55f8fc5d/84h/0h/0h]xpub6DPMTPxGMqdtzMwpqT1dDQaVdyaEppEm2qYSaJ7ANsuES7HkNzrXJst1Ed8D7NAnijUdgSDUFgph1oj5LKKAD5gyxWNhNP2AuDqaKYqzphA/0/*)#9qx3vqss", "devices": [{"type": "other", "label": "Key1"}]}'
    SPECTER_MULTISIG_WALLET_DATA = '{"label": "Specter Multisig Wallet", "blockheight": 0, "descriptor": "wsh(sortedmulti(2,[55f8fc5d/48h/0h/0h/2h]xpub6EKmKYGYc1WY6t9d3d9SksR8keSaPZbFa6tqsGiH4xVxx8d2YyxSX7WG6yXEX3CmG54dPCxaapDw1XsjwCmfoqP7tbsAeqMVfKvqSAu4ndy/0/*,[3e15470d/48h/0h/0h/2h]xpub6F2P6Pz5KLPgCc6pTBd2xxCunaSYWc8CdkL28W5z15pJrN3aCYY7mCUAkCMtqrgT2wdhAGgRnJxAkCCUpGKoXKxQ57yffEGmPwtYA3DEXwu/0/*,[d3a80c8b/48h/0h/0h/2h]xpub6FKYY6y3oVi7ihSCszFKRSeZj5SzrfSsUFXhKqjMV4iigrLhxwMX3mrjioNyLTZ5iD3u4wU9S3tyzpJGxhd5geaXoQ68jGz2M6dfh2zJrUv/0/*))#3nfc6jdy", "devices": [{"type": "other", "label": "Key1"}, {"type": "other", "label": "Key2"}, {"type": "other", "label": "Key3"}]}'

    P2WPKH_PSBT_B64 = "cHNidP8BAHECAAAAAc88WMMpgq4gUIjZvUnrmwKs3009rnalFsazBrFd46FOAAAAAAD9////Anw/XQUAAAAAFgAULzSqHPAKU7BVopGgOn1F8KaYi1KAlpgAAAAAABYAFOZq/v/Dg45x8KJ7B+OwDt5q6OFgAAAAAAABAR8A4fUFAAAAABYAFNDEo+8J6Ze26Z45flGP4+QaEYyhIgYC56slN7XUnpcDCargbp5J82zhyf671E7I4NHMoLT5wxkYc8XaClQAAIABAACAAAAAgAAAAAAAAAAAACICA11J7M1U0AmeQ2did8em1GJdYR2oil30m/lReneRp3elGHPF2gpUAACAAQAAgAAAAIABAAAAAAAAAAAA"
    SIGNED_P2WPKH_PSBT_B64 = "cHNidP8BAHECAAAAAc88WMMpgq4gUIjZvUnrmwKs3009rnalFsazBrFd46FOAAAAAAD9////Anw/XQUAAAAAFgAULzSqHPAKU7BVopGgOn1F8KaYi1KAlpgAAAAAABYAFOZq/v/Dg45x8KJ7B+OwDt5q6OFgAAAAAAAiAgLnqyU3tdSelwMJquBunknzbOHJ/rvUTsjg0cygtPnDGUcwRAIgPmX/O0zUfxIfp8mCKEYY24AxR7BW05OU1OxCDv38a6ECIGy92IrFGGw/Lv0kJTHteRd1dlGsJiN089MdhdYWzWqBAQAAAA=="
    P2WSH_PSBT_B64 = "cHNidP8BALICAAAAAq1DhxRK+mUH4T6uUNob8bUaZ7MP+44MW4+Y9bOxpjhZAAAAAAD9////aWclWQ+45HKrI07r878E2UrAupT2paT4QurbmtNjYNQBAAAAAP3///8CQEIPAAAAAAAiACCpkDPDhmIzPlkJrjw9A71xjbIUWf3VUB7ooFJhTVm04tjSIQEAAAAAIgAgjQKFDauIXsV5u23LBdYgOwX1FwGGrLiQfWzBtFKZ7dIAAAAATwEENYfPBD5i336AAAACQStJhNVJul7vHKbo83VdmuAW2m0WaXLKDlFANn7dUNoCNbhLMdw4Knz7Q7o6exdL6UFhQegW9nJb0SUStbLEpawUAgjLdzAAAIABAACAAAAAgAIAAIBPAQQ1h88EnbHQAIAAAAI/2Nc7x7iMpJNapTe/OJTV4oifqzQcYY9KV2+PGRjCdQJoww1WnSNqfcxXGyux0q1PqfmzUqgJNqKJCpmqI9t47BQmu4PEMAAAgAEAAIAAAACAAgAAgE8BBDWHzwS6wUg5gAAAAh1Pvr3ZZ+GvcUwJl9OPz2cLXOnTAcBEC7zDtqIOt3IcA1aOofNgUZFu0baQw54SqOcGA7KAvTDOXygfKRilU2OqFHPF2gowAACAAQAAgAAAAIACAACAAAEBK4CWmAAAAAAAIgAgiYAxcG7dnrEiZ4VHFVHOo18XCalvhZYuMqBr9n7HESQBBWlSIQJOjQgMfX26XEf+trHIEk3rYkEX5Y2NfrFKQARPcd2X8iEDBWHUgq25PfHvE+hlcBryJG7wo2y8jKUSPY7sd85OOMchA2iVcuKLD+2p1pgcAjfZ5d7b/sFt5xQ/aAoC7V0Vn3WHU64iBgJOjQgMfX26XEf+trHIEk3rYkEX5Y2NfrFKQARPcd2X8hwmu4PEMAAAgAEAAIAAAACAAgAAgAAAAAABAAAAIgYDBWHUgq25PfHvE+hlcBryJG7wo2y8jKUSPY7sd85OOMccAgjLdzAAAIABAACAAAAAgAIAAIAAAAAAAQAAACIGA2iVcuKLD+2p1pgcAjfZ5d7b/sFt5xQ/aAoC7V0Vn3WHHHPF2gowAACAAQAAgAAAAIACAACAAAAAAAEAAAAAAQErgJaYAAAAAAAiACAzd60wM9EFnPHSNbsSJfyipL8myVLVP2/vwzotVUSNxQEFaVIhAiKCMRLlzIhLkRbLIUIMx5KYJM0v6LcjW/mS6K7eFGwiIQKDzUflU23LeecRgzDo5IBCEvaWGfHW7JkNxzXvuc7FdCEDC5DtLoa61/Kk/pdpu0F9e6nKoRJIB9v7Ni377rZefgFTriIGAiKCMRLlzIhLkRbLIUIMx5KYJM0v6LcjW/mS6K7eFGwiHAIIy3cwAACAAQAAgAAAAIACAACAAAAAAAAAAAAiBgKDzUflU23LeecRgzDo5IBCEvaWGfHW7JkNxzXvuc7FdBwmu4PEMAAAgAEAAIAAAACAAgAAgAAAAAAAAAAAIgYDC5DtLoa61/Kk/pdpu0F9e6nKoRJIB9v7Ni377rZefgEcc8XaCjAAAIABAACAAAAAgAIAAIAAAAAAAAAAAAABAWlSIQKtIdmtKKuZrH7f2R4iIU8RWVOrCdHVWBCS+0e9pZJy/iEDoH074LrWPIA10hyXtBCJDT06GdLkA6+z/PxoJqomPHYhA6GoQ/otQdk71nUpYZFfbkSKdBkkSj4CuPTPYrzGp6JrU64iAgKtIdmtKKuZrH7f2R4iIU8RWVOrCdHVWBCS+0e9pZJy/hwCCMt3MAAAgAEAAIAAAACAAgAAgAEAAAAAAAAAIgIDoH074LrWPIA10hyXtBCJDT06GdLkA6+z/PxoJqomPHYcc8XaCjAAAIABAACAAAAAgAIAAIABAAAAAAAAACICA6GoQ/otQdk71nUpYZFfbkSKdBkkSj4CuPTPYrzGp6JrHCa7g8QwAACAAQAAgAAAAIACAACAAQAAAAAAAAAAAA=="
    SIGNED_P2WSH_PSBT_B64 = "cHNidP8BALICAAAAAq1DhxRK+mUH4T6uUNob8bUaZ7MP+44MW4+Y9bOxpjhZAAAAAAD9////aWclWQ+45HKrI07r878E2UrAupT2paT4QurbmtNjYNQBAAAAAP3///8CQEIPAAAAAAAiACCpkDPDhmIzPlkJrjw9A71xjbIUWf3VUB7ooFJhTVm04tjSIQEAAAAAIgAgjQKFDauIXsV5u23LBdYgOwX1FwGGrLiQfWzBtFKZ7dIAAAAAACICA2iVcuKLD+2p1pgcAjfZ5d7b/sFt5xQ/aAoC7V0Vn3WHRzBEAiBoP20ZBEOJlYu67bu6OCkJrl7jYBZHyItxnA68xbFqogIgBQ1QKOCcY10pceXiU5+vK+Rfqcb5DSIl9KIAO6KvMlcBACICAwuQ7S6GutfypP6XabtBfXupyqESSAfb+zYt++62Xn4BRzBEAiB+TxuMu4d4o7v/BNgQQ3HIWQ87TjaX2FP+dGmAsxLgPgIgbJM9Am20PJD0JflaJHu37E8ZFaOjU/JRgdxY+9UmnsUBAAAA"

    return namedtuple(
        "TestData",
        [
            "TEST_12_WORD_MNEMONIC",
            "TEST_24_WORD_MNEMONIC",
            "SIGNING_MNEMONIC",
            "SINGLEKEY_12_WORD_KEY",
            "SINGLEKEY_24_WORD_KEY",
            "MULTISIG_12_WORD_KEY",
            "SINGLEKEY_SIGNING_KEY",
            "MULTISIG_SIGNING_KEY",
            "SPECTER_SINGLEKEY_WALLET_DATA",
            "SPECTER_MULTISIG_WALLET_DATA",
            "P2WPKH_PSBT_B64",
            "SIGNED_P2WPKH_PSBT_B64",
            "P2WSH_PSBT_B64",
            "SIGNED_P2WSH_PSBT_B64",
        ],
    )(
        TEST_12_WORD_MNEMONIC,
        TEST_24_WORD_MNEMONIC,
        SIGNING_MNEMONIC,
        SINGLEKEY_12_WORD_KEY,
        SINGLEKEY_24_WORD_KEY,
        MULTISIG_12_WORD_KEY,
        SINGLEKEY_SIGNING_KEY,
        MULTISIG_SIGNING_KEY,
        SPECTER_SINGLEKEY_WALLET_DATA,
        SPECTER_MULTISIG_WALLET_DATA,
        P2WPKH_PSBT_B64,
        SIGNED_P2WPKH_PSBT_B64,
        P2WSH_PSBT_B64,
        SIGNED_P2WSH_PSBT_B64,
    )


def test_mnemonic(mocker, m5stickv, tdata):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    cases = [
        # No print prompt
        (Wallet(tdata.SINGLEKEY_12_WORD_KEY), None, [BUTTON_ENTER]),
        (Wallet(tdata.SINGLEKEY_24_WORD_KEY), None, [BUTTON_ENTER, BUTTON_ENTER]),
        # Print
        (
            Wallet(tdata.SINGLEKEY_12_WORD_KEY),
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER],
        ),
        (
            Wallet(tdata.SINGLEKEY_24_WORD_KEY),
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Decline to print
        (
            Wallet(tdata.SINGLEKEY_12_WORD_KEY),
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_PAGE],
        ),
        (
            Wallet(tdata.SINGLEKEY_24_WORD_KEY),
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE],
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[2])
            ),
            wallet=case[0],
            printer=case[1],
        )
        home = Home(ctx)

        mocker.spy(home, "display_mnemonic")
        mocker.spy(home, "print_qr_prompt")

        home.mnemonic()

        home.display_mnemonic.assert_called_with(ctx.wallet.key.mnemonic)
        home.print_qr_prompt.assert_called_with(ctx.wallet.key.mnemonic, FORMAT_NONE)

        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_mnemonic_touch(mocker, amigo_ips, tdata):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    from krux.input import BUTTON_TOUCH, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    cases = [
        # No print prompt
        (Wallet(tdata.SINGLEKEY_12_WORD_KEY), None, [BUTTON_TOUCH]),
        (Wallet(tdata.SINGLEKEY_24_WORD_KEY), None, [BUTTON_TOUCH]),
        # Print
        (
            Wallet(tdata.SINGLEKEY_12_WORD_KEY),
            MockPrinter(),
            [BUTTON_TOUCH, BUTTON_TOUCH],
        ),
        (
            Wallet(tdata.SINGLEKEY_24_WORD_KEY),
            MockPrinter(),
            [BUTTON_TOUCH, BUTTON_TOUCH],
        ),
        # Decline to print
        (
            Wallet(tdata.SINGLEKEY_12_WORD_KEY),
            MockPrinter(),
            [BUTTON_TOUCH, BUTTON_PAGE],
        ),
        (
            Wallet(tdata.SINGLEKEY_24_WORD_KEY),
            MockPrinter(),
            [BUTTON_TOUCH, BUTTON_TOUCH],
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[2])
            ),
            wallet=case[0],
            printer=case[1],
        )
        home = Home(ctx)

        mocker.spy(home, "display_mnemonic")
        mocker.spy(home, "print_qr_prompt")

        home.mnemonic()

        home.display_mnemonic.assert_called_with(ctx.wallet.key.mnemonic)
        home.print_qr_prompt.assert_called_with(ctx.wallet.key.mnemonic, FORMAT_NONE)

        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_public_key(mocker, m5stickv, tdata):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    cases = [
        # No print prompt
        (
            Wallet(tdata.SINGLEKEY_12_WORD_KEY),
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Print
        (
            Wallet(tdata.SINGLEKEY_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
        ),
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
        ),
        # Decline to print
        (
            Wallet(tdata.SINGLEKEY_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
            ],
        ),
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
            ],
        ),
    ]
    for case in cases:
        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[2])
            ),
            wallet=case[0],
            printer=case[1],
        )
        home = Home(ctx)

        mocker.spy(home, "display_qr_codes")
        mocker.spy(home, "print_qr_prompt")

        home.public_key()

        version = "Zpub" if ctx.wallet.key.multisig else "zpub"
        display_qr_calls = [
            mocker.call(
                ctx.wallet.key.key_expression(None),
                FORMAT_NONE,
                None,
            ),
            mocker.call(
                ctx.wallet.key.key_expression(ctx.wallet.key.network[version]),
                FORMAT_NONE,
                None,
            ),
        ]
        print_qr_calls = [
            mocker.call(ctx.wallet.key.key_expression(None), FORMAT_NONE),
            mocker.call(
                ctx.wallet.key.key_expression(ctx.wallet.key.network[version]),
                FORMAT_NONE,
            ),
        ]
        home.display_qr_codes.assert_has_calls(display_qr_calls)
        home.print_qr_prompt.assert_has_calls(print_qr_calls)

        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_wallet(mocker, m5stickv, tdata):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN

    cases = [
        # Don't load
        (
            False,
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            None,
            [BUTTON_PAGE],
        ),
        # Load, good data, accept
        (
            False,
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Load, good data, decline
        (
            False,
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_PAGE],
        ),
        # Load, bad capture
        (False, tdata.SINGLEKEY_12_WORD_KEY, None, None, [BUTTON_ENTER]),
        # Load, bad wallet data
        (False, tdata.SINGLEKEY_12_WORD_KEY, "{}", None, [BUTTON_ENTER, BUTTON_ENTER]),
        # No print prompt
        (
            True,
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            None,
            [BUTTON_ENTER],
        ),
        # Print
        (
            True,
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Decline to print
        (
            True,
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_PAGE],
        ),
        # Multisig wallet, no print prompt
        (
            True,
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            None,
            [BUTTON_ENTER],
        ),
    ]
    for case in cases:
        wallet = Wallet(case[1])
        if case[0]:
            wallet.load(case[2], FORMAT_PMOFN)

        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[4])
            ),
            wallet=wallet,
            printer=case[3],
        )

        home = Home(ctx)
        mocker.patch.object(
            home, "capture_qr_code", new=lambda: (case[2], FORMAT_PMOFN)
        )
        mocker.patch.object(
            home,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(home, "print_qr_prompt")
        mocker.spy(home, "capture_qr_code")
        mocker.spy(home, "display_wallet")

        home.wallet()

        if case[0]:
            home.display_wallet.assert_called_once()
            home.print_qr_prompt.assert_called_once()
        else:
            if case[4][0] == BUTTON_ENTER:
                home.capture_qr_code.assert_called_once()
                if case[2] is not None and case[2] != "{}":
                    home.display_wallet.assert_called_once()
        assert ctx.input.wait_for_button.call_count == len(case[4])


def test_scan_address(mocker, m5stickv, tdata):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN, FORMAT_NONE

    cases = [
        # Single-key, loaded, owned address, No print prompt, search successful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-key, not loaded, owned address, No print prompt, search successful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            False,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-key, loaded, owned address, Print, search successful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-key, loaded, owned address, Decline to print, search successful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Multisig, loaded, owned address, No print prompt, search successful
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Multisig, not loaded, owned address, No print prompt, can't search
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            False,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            None,
            True,
            [BUTTON_ENTER],
        ),
        # Multisig, loaded, owned address, Print, search successful
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Multisig, loaded, owned address, Decline to print, search successful
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Multisig, loaded, unowned address, No print prompt, search unsuccessful
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned m/44 address, No print prompt, skip search
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            None,
            True,
            [BUTTON_ENTER, BUTTON_PAGE],
        ),
        # Single-key, loaded, unowned m/44 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned m/44 address, No print prompt, 2x search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned m/48/0/0/2 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned m/84 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned m/49 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned m/0 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned m/0 address, Print, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, unowned m/0 address, Decline to print, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-key, loaded, fail to capture QR of address, No print prompt, can't search
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            None,
            None,
            False,
            [],
        ),
        # Single-key, loaded, invalid address, No print prompt, can't search
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "invalidaddress",
            None,
            False,
            [],
        ),
    ]
    for case in cases:
        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)

        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[6])
            ),
            wallet=wallet,
            printer=case[4],
        )

        home = Home(ctx)
        mocker.patch.object(home, "capture_qr_code", new=lambda: (case[3], FORMAT_NONE))
        mocker.patch.object(
            home,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(home, "print_qr_prompt")
        mocker.spy(home, "capture_qr_code")
        mocker.spy(home, "display_qr_codes")

        home.scan_address()

        home.capture_qr_code.assert_called_once()
        if case[5]:
            home.display_qr_codes.assert_called_once()
            home.print_qr_prompt.assert_called_once()
        else:
            home.display_qr_codes.assert_not_called()
            home.print_qr_prompt.assert_not_called()

        assert ctx.input.wait_for_button.call_count == len(case[6])


def test_sign_psbt(mocker, m5stickv, tdata):
    from krux.pages.home import Home
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN, FORMAT_NONE

    cases = [
        # Single-key, not loaded, no format => pmofn, sign, No print prompt
        (
            tdata.SINGLEKEY_SIGNING_KEY,
            None,
            False,
            tdata.P2WPKH_PSBT_B64,
            FORMAT_NONE,
            True,
            tdata.SIGNED_P2WPKH_PSBT_B64,
            FORMAT_PMOFN,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-key, not loaded, pmofn, sign, No print prompt
        (
            tdata.SINGLEKEY_SIGNING_KEY,
            None,
            False,
            tdata.P2WPKH_PSBT_B64,
            FORMAT_PMOFN,
            True,
            tdata.SIGNED_P2WPKH_PSBT_B64,
            FORMAT_PMOFN,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-key, not loaded, pmofn, sign, Print
        (
            tdata.SINGLEKEY_SIGNING_KEY,
            None,
            False,
            tdata.P2WPKH_PSBT_B64,
            FORMAT_PMOFN,
            True,
            tdata.SIGNED_P2WPKH_PSBT_B64,
            FORMAT_PMOFN,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-key, not loaded, pmofn, sign, Decline to print
        (
            tdata.SINGLEKEY_SIGNING_KEY,
            None,
            False,
            tdata.P2WPKH_PSBT_B64,
            FORMAT_PMOFN,
            True,
            tdata.SIGNED_P2WPKH_PSBT_B64,
            FORMAT_PMOFN,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE],
        ),
        # Single-key, not loaded, pmofn, decline to sign
        (
            tdata.SINGLEKEY_SIGNING_KEY,
            None,
            False,
            tdata.P2WPKH_PSBT_B64,
            FORMAT_PMOFN,
            False,
            None,
            None,
            None,
            [BUTTON_ENTER, BUTTON_PAGE],
        ),
        # Single-key, not loaded, failed to capture PSBT QR
        (
            tdata.SINGLEKEY_SIGNING_KEY,
            None,
            False,
            None,
            None,
            False,
            None,
            None,
            None,
            [BUTTON_ENTER],
        ),
        # Multisig, not loaded, decline to proceed after warning
        (
            tdata.MULTISIG_SIGNING_KEY,
            None,
            False,
            None,
            None,
            False,
            None,
            None,
            None,
            [BUTTON_PAGE],
        ),
        # Multisig, not loaded, pmofn, sign, No print prompt
        (
            tdata.MULTISIG_SIGNING_KEY,
            None,
            False,
            tdata.P2WSH_PSBT_B64,
            FORMAT_PMOFN,
            True,
            tdata.SIGNED_P2WSH_PSBT_B64,
            FORMAT_PMOFN,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Multisig, not loaded, pmofn, sign, Print
        (
            tdata.MULTISIG_SIGNING_KEY,
            None,
            False,
            tdata.P2WSH_PSBT_B64,
            FORMAT_PMOFN,
            True,
            tdata.SIGNED_P2WSH_PSBT_B64,
            FORMAT_PMOFN,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Multisig, not loaded, pmofn, sign, Decline to print
        (
            tdata.MULTISIG_SIGNING_KEY,
            None,
            False,
            tdata.P2WSH_PSBT_B64,
            FORMAT_PMOFN,
            True,
            tdata.SIGNED_P2WSH_PSBT_B64,
            FORMAT_PMOFN,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE],
        ),
    ]
    for case in cases:
        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)

        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[9])
            ),
            wallet=wallet,
            printer=case[8],
        )

        home = Home(ctx)
        mocker.patch.object(home, "capture_qr_code", new=lambda: (case[3], case[4]))
        mocker.patch.object(
            home,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(home, "print_qr_prompt")
        mocker.spy(home, "capture_qr_code")
        mocker.spy(home, "display_qr_codes")

        home.sign_psbt()

        if case[2] or (not case[2] and case[9][0] == BUTTON_ENTER):
            home.capture_qr_code.assert_called_once()
            if case[5]:
                home.display_qr_codes.assert_called_once()
                home.print_qr_prompt.assert_called_once()
            else:
                home.display_qr_codes.assert_not_called()
        else:
            home.capture_qr_code.assert_not_called()

        assert ctx.input.wait_for_button.call_count == len(case[9])


def test_sign_message(mocker, m5stickv, tdata):
    import binascii
    from krux.pages.home import Home
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE

    cases = [
        # Hex-encoded hash, Sign, No print prompt
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",
            FORMAT_NONE,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "MEQCID/PulsmI+E1HhJ55HdJJnKoMbUHw3c1WZnSrHqW5jlKAiB+vPbnRtmw6R9ZP8jUB8o02n+6QsX9uKy3hDiv9R2SuA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
        # Hash, Sign, No print prompt
        (
            binascii.unhexlify(
                "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7"
            ),
            FORMAT_NONE,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "MEQCID/PulsmI+E1HhJ55HdJJnKoMbUHw3c1WZnSrHqW5jlKAiB+vPbnRtmw6R9ZP8jUB8o02n+6QsX9uKy3hDiv9R2SuA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
        # Message, Sign, No print prompt
        (
            "hello world",
            FORMAT_NONE,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "MEQCIHKmpv1+vgPpFTN0JXjyrMK2TtLHVeJJ2TydPYmEt0RnAiBJVt/Y61ef5VlWjG08zf92AeF++BWdYm1Yd9IEy2cSqA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
        # 64-byte message, Sign, No print prompt
        (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
            FORMAT_NONE,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            "MEQCIEHpCMfQ+5mBAOH//OCxF6iojpVtIS6G7X+3r3qB/0CaAiAkbjW2SGrPLvju+O05yH2x/4EKL2qlkdWnquiVkUY3jQ==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
        # Hex-encoded hash, Sign, Print
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",
            FORMAT_NONE,
            MockPrinter(),
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "MEQCID/PulsmI+E1HhJ55HdJJnKoMbUHw3c1WZnSrHqW5jlKAiB+vPbnRtmw6R9ZP8jUB8o02n+6QsX9uKy3hDiv9R2SuA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
        # Hex-encoded hash, Sign, Decline to print
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",
            FORMAT_NONE,
            MockPrinter(),
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_ENTER,
                BUTTON_PAGE,
            ],
            "MEQCID/PulsmI+E1HhJ55HdJJnKoMbUHw3c1WZnSrHqW5jlKAiB+vPbnRtmw6R9ZP8jUB8o02n+6QsX9uKy3hDiv9R2SuA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
        # Hex-encoded hash, Decline to sign
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",
            FORMAT_NONE,
            None,
            [BUTTON_PAGE],
            None,
            None,
        ),
        # Failed to capture message QR
        (None, FORMAT_NONE, None, [], None, None),
    ]
    for case in cases:
        wallet = Wallet(tdata.SINGLEKEY_SIGNING_KEY)

        ctx = mocker.MagicMock(
            input=mocker.MagicMock(
                wait_for_button=mocker.MagicMock(side_effect=case[3])
            ),
            wallet=wallet,
            printer=case[2],
        )

        home = Home(ctx)
        mocker.patch.object(home, "capture_qr_code", new=lambda: (case[0], case[1]))
        mocker.patch.object(
            home,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(home, "print_qr_prompt")
        mocker.spy(home, "capture_qr_code")
        mocker.spy(home, "display_qr_codes")

        home.sign_message()

        home.capture_qr_code.assert_called_once()
        if case[0] and case[3][0] == BUTTON_ENTER:
            home.display_qr_codes.assert_has_calls(
                [mocker.call(case[4], case[1]), mocker.call(case[5], case[1])]
            )
            home.print_qr_prompt.assert_has_calls(
                [mocker.call(case[4], case[1]), mocker.call(case[5], case[1])]
            )
        else:
            home.display_qr_codes.assert_not_called()
            home.print_qr_prompt.assert_not_called()

        assert ctx.input.wait_for_button.call_count == len(case[3])

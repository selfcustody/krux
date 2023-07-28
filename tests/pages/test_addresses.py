from ..shared_mocks import MockPrinter, mock_context
from .test_home import tdata, create_ctx


def test_scan_address(mocker, m5stickv, tdata):
    from krux.pages.addresses import Addresses
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN, FORMAT_NONE

    cases = [
        # Single-sig, loaded, owned address, No print prompt, search successful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-sig, not loaded, owned address, No print prompt, search successful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            False,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-sig, loaded, owned address, Print, search successful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
        # Single-sig, loaded, owned address, Decline to print, search successful
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
        # Single-sig, loaded, unowned address, No print prompt, search unsuccessful
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
        # Single-sig, loaded, unowned m/44 address, No print prompt, skip search
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            None,
            True,
            [BUTTON_ENTER, BUTTON_PAGE],
        ),
        # Single-sig, loaded, unowned m/44 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-sig, loaded, unowned m/44 address, No print prompt, 2x search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-sig, loaded, unowned m/48/0/0/2 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-sig, loaded, unowned m/84 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-sig, loaded, unowned m/49 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-sig, loaded, unowned m/0 address, No print prompt, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            None,
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-sig, loaded, unowned m/0 address, Print, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-sig, loaded, unowned m/0 address, Decline to print, search unsuccessful
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            MockPrinter(),
            True,
            [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
        ),
        # Single-sig, loaded, fail to capture QR of address, No print prompt, can't search
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            True,
            None,
            None,
            False,
            [],
        ),
        # Single-sig, loaded, invalid address, No print prompt, can't search
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

        ctx = create_ctx(mocker, case[6], wallet, case[4])
        addresses_ui = Addresses(ctx)
        mocker.patch.object(
            addresses_ui, "capture_qr_code", new=lambda: (case[3], FORMAT_NONE)
        )
        mocker.patch.object(
            addresses_ui,
            "display_qr_codes",
            new=lambda data, qr_format, title=None, allow_any_btn=True: ctx.input.wait_for_button(),
        )
        mocker.spy(addresses_ui, "capture_qr_code")
        mocker.spy(addresses_ui, "display_qr_codes")

        addresses_ui.scan_address()

        addresses_ui.capture_qr_code.assert_called_once()
        if case[5]:
            addresses_ui.display_qr_codes.assert_called_once()
        else:
            addresses_ui.display_qr_codes.assert_not_called()

        assert ctx.input.wait_for_button.call_count == len(case[6])


def test_list_receive_addresses(mocker, m5stickv, tdata):
    from krux.pages.addresses import Addresses
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_PMOFN, FORMAT_NONE

    cases = [
        # Single-sig, loaded, No print prompt, show address nº1
        (
            tdata.SINGLEKEY_12_WORD_KEY,
            tdata.SPECTER_SINGLEKEY_WALLET_DATA,
            False,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            None,
            [
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
    ]
    for case in cases:
        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)

        ctx = create_ctx(mocker, case[5], wallet, case[4])
        addresses_ui = Addresses(ctx)
        mocker.patch.object(
            addresses_ui,
            "display_qr_codes",
            new=lambda data, qr_format=FORMAT_NONE, title=None, allow_any_btn=True: ctx.input.wait_for_button(),
        )
        mocker.spy(addresses_ui, "display_qr_codes")

        addresses_ui.list_address_type()

        addresses_ui.display_qr_codes.assert_called_once()
        assert ctx.input.wait_for_button.call_count == len(case[5])

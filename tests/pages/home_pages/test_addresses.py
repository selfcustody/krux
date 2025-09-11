import pytest
from .test_home import tdata, create_ctx

# fortdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH
DESCRIPTOR_SINGLESIG_ACTION_WITHOUT_CHANGE = b"wpkh([e0c595c5/84h/1h/0h]tpubDCberYHnzBMaKUa34hXGTNXECt9bKprGKtqYt2Bm4qGFK3bqMkMA6KxRR1kPPSh73QoX6LtmsArgNYXRw8HnkWwc8ywf7Ru6XcxRnJo9HfW/2/*)#tykcfujt"


def test_multisig_addresses_without_descriptor(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.wallet import Wallet

    wallet = Wallet(tdata.MULTISIG_12_WORD_KEY)
    ctx = create_ctx(mocker, None, wallet, None)
    addresses_ui = Addresses(ctx)
    mocker.spy(addresses_ui, "flash_error")
    addresses_ui.addresses_menu()
    addresses_ui.flash_error.assert_called_with(
        "Please load a wallet output descriptor"
    )


def test_scan_address(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN, FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture
    from krux.format import format_address

    cases = [
        # (
        # Wallet key,
        # Descriptor data,
        # Wallet loaded,
        # Address to scan,
        # Address is valid,
        # Buttons pressed
        # Search should be successful
        # )
        # 0 - Single-sig, loaded, owned address, search successful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # 1 - Single-sig, not loaded, owned address, search successful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            None,
            False,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # 2 - Single-sig, loaded, owned address, search successful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # 3 - Single-sig, loaded, owned address, search successful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # 4 - Multisig, loaded, owned address, No print prompt, search successful
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # 5 - Multisig, not loaded, owned address, can't search
        (
            tdata.MULTISIG_12_WORD_KEY,
            None,
            False,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            True,
            [BUTTON_ENTER],
            False,
        ),
        # 6 - Multisig, loaded, owned address, search successful
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # 7 - Multisig, loaded, owned address, search successful
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # 8 - Single-sig, loaded, unowned address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 9 - Multisig, loaded, unowned address, search unsuccessful
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 10 - Single-sig, loaded, unowned m/44 address, skip search
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            True,
            [BUTTON_ENTER, BUTTON_PAGE],
            False,
        ),
        # 11 - Single-sig, loaded, unowned m/44 address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 12 - Single-sig, loaded, unowned m/44 address, 2x search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "14ihRbmxbgZ6JN9HdDDo6u6nGradHDy4GJ",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 13 - Single-sig, loaded, unowned m/48/0/0/2 address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "1BRwWQ3GHabCV5DP6MfnCpr6dF6GBAwQ7k",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 14 - Single-sig, loaded, unowned m/84 address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "bc1qx2zuday8d6j4ufh4df6e9ttd06lnfmn2cuz0vn",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 15 - Single-sig, loaded, unowned m/49 address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "32iCX1pY1iztdgM5qzurGLPMu5xhNfAUtg",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 16 - Single-sig, loaded, unowned m/0 address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 17 - Single-sig, loaded, unowned m/0 address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 18 - Single-sig, loaded, unowned m/0 address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "3KLoUhwLihgC5aPQPFHakWUtJ4QoBkT7Aw",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
        # 19 - Single-sig, loaded, fail to capture QR of address, can't search
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            None,
            False,
            [],
            False,
        ),
        # 20 - Single-sig, loaded, invalid address, can't search
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "invalidaddress",
            False,
            [],
            False,
        ),
    ]
    case_num = 0
    for case in cases:
        print("Case: %d" % case_num)
        case_num += 1

        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)
            assert wallet.has_change_addr()

        ctx = create_ctx(mocker, case[5], wallet, None)
        addresses_ui = Addresses(ctx)

        mocker.patch.object(
            QRCodeCapture, "qr_capture_loop", new=lambda self: (case[3], FORMAT_NONE)
        )
        qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")
        mocker.spy(addresses_ui, "show_address")

        addresses_ui.scan_address()

        qr_capturer.assert_called_once()
        if case[4]:  # If address is valid
            addresses_ui.show_address.assert_called_once()
            can_search = (
                case[2] or not ctx.wallet.is_multisig()
            )  # If wallet is loaded or single-sig
            can_search &= len(case[5]) > 2  # If didn't skip search
            if can_search:
                if case[6]:  # If search should be successful
                    ctx.display.draw_centered_text.assert_called_with(
                        "0.\n\n%s\n\nis a valid address!" % format_address(case[3])
                    )
                else:
                    attempts = 50 * (len(case[5]) - 3)
                    ctx.display.draw_centered_text.assert_called_with(
                        "%s\n\nwas NOT FOUND in the first %s addresses"
                        % (format_address(case[3]), attempts)
                    )
        else:
            addresses_ui.show_address.assert_not_called()

        assert ctx.input.wait_for_button.call_count == len(case[5])


def test_scan_address_highlight(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN, FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture
    from krux.format import format_address

    cases = [
        # 1 - Single-sig, not loaded, owned address, search successful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            None,
            False,
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # 8 - Single-sig, loaded, unowned address, search unsuccessful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER],
            False,
        ),
    ]

    # To use as display.to_lines
    def _to_lines(text):
        if isinstance(text, list):
            return text
        return text.split("\n")

    case_num = 0
    for case in cases:
        print("Case: %d" % case_num)
        case_num += 1

        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)
            assert wallet.has_change_addr()

        ctx = create_ctx(mocker, case[5], wallet, None)

        # custom display.to_lines to increase coverage
        ctx.display.to_lines = _to_lines

        addresses_ui = Addresses(ctx)

        mocker.patch.object(
            QRCodeCapture, "qr_capture_loop", new=lambda self: (case[3], FORMAT_NONE)
        )
        qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")
        mocker.spy(addresses_ui, "show_address")

        addresses_ui.scan_address()

        qr_capturer.assert_called_once()

        assert ctx.input.wait_for_button.call_count == len(case[5])


def test_list_disable_change_address(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    btn_seq = [
        BUTTON_PAGE,  # move to list addr
        BUTTON_ENTER,  # click list addr
        BUTTON_PAGE,  # move to change addr
        BUTTON_ENTER,  # click change addr to enter list_address_type (nothing happen - disabled)
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit menu
        BUTTON_PAGE,  # move to export
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit screen
    ]
    wallet = Wallet(tdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH)
    wallet.load(DESCRIPTOR_SINGLESIG_ACTION_WITHOUT_CHANGE, FORMAT_NONE)
    ctx = create_ctx(mocker, btn_seq, wallet)
    addresses_ui = Addresses(ctx)

    mocker.spy(addresses_ui, "list_address_type")

    addresses_ui.addresses_menu()

    addresses_ui.list_address_type.assert_not_called()
    assert not wallet.has_change_addr()

    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_scan_disable_change_address(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    btn_seq = [
        BUTTON_ENTER,  # click scan addr
        BUTTON_PAGE,  # move to change addr
        BUTTON_ENTER,  # click change addr to enter scan_address (nothing happen - disabled)
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit menu
        BUTTON_PAGE,  # move to list addr
        BUTTON_PAGE,  # move to export addr
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit screen
    ]
    wallet = Wallet(tdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH)
    wallet.load(DESCRIPTOR_SINGLESIG_ACTION_WITHOUT_CHANGE, FORMAT_NONE)
    ctx = create_ctx(mocker, btn_seq, wallet, None)
    addresses_ui = Addresses(ctx)

    mocker.spy(addresses_ui, "scan_address")

    addresses_ui.addresses_menu()

    addresses_ui.scan_address.assert_not_called()
    assert not wallet.has_change_addr()

    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_export_disabled(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    btn_seq = [
        BUTTON_PAGE,  # move to list addr
        BUTTON_PAGE,  # move to export addr
        BUTTON_ENTER,  # click export (nothing happen - disabled)
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit screen
    ]
    wallet = Wallet(tdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH)
    wallet.load(DESCRIPTOR_SINGLESIG_ACTION_WITHOUT_CHANGE, FORMAT_NONE)
    ctx = create_ctx(mocker, btn_seq, wallet, None)
    addresses_ui = Addresses(ctx)

    mocker.spy(addresses_ui, "_receive_change_menu")

    addresses_ui.addresses_menu()

    addresses_ui._receive_change_menu.assert_not_called()
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_export_disable_change_address(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    btn_seq = [
        BUTTON_PAGE,  # move to list addr
        BUTTON_PAGE,  # move to export addr
        BUTTON_ENTER,  # click export
        BUTTON_PAGE,  # move to change addr
        BUTTON_ENTER,  # click change addr to enter (nothing happen - disabled)
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit menu
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit screen
    ]
    wallet = Wallet(tdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH)
    wallet.load(DESCRIPTOR_SINGLESIG_ACTION_WITHOUT_CHANGE, FORMAT_NONE)
    ctx = create_ctx(mocker, btn_seq, wallet, None)
    addresses_ui = Addresses(ctx)

    # SD available
    mocker.patch.object(addresses_ui, "has_sd_card", new=lambda: True)

    mocker.spy(addresses_ui, "export_address")

    addresses_ui.addresses_menu()

    addresses_ui.export_address.assert_not_called()
    assert not wallet.has_change_addr()

    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_export_address(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE
    from unittest.mock import mock_open, patch

    btn_seq = [
        BUTTON_PAGE,  # move to list addr
        BUTTON_PAGE,  # move to export addr
        BUTTON_ENTER,  # click export
        BUTTON_ENTER,  # click receive addr to enter
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_PAGE_PREV,  # move to ESC
        BUTTON_ENTER,
        BUTTON_ENTER,  # enter and confirm ESC (at index input)
        BUTTON_ENTER,  # click export (start over)
        BUTTON_ENTER,  # click receive addr to enter
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm index 0
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_PAGE_PREV,  # move to ESC
        BUTTON_ENTER,
        BUTTON_ENTER,  # enter and confirm ESC (at quantity input)
        BUTTON_ENTER,  # click export (start over)
        BUTTON_ENTER,  # click receive addr to enter
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm index 0
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm quantity 50
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_PAGE_PREV,  # move to ESC
        BUTTON_ENTER,
        BUTTON_ENTER,  # enter and confirm ESC (at filename input)
        BUTTON_ENTER,  # click export (start over)
        BUTTON_ENTER,  # click receive addr to enter
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm index 0
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm quantity 50
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm filename Receive-fingerprint
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit screen
    ]
    wallet = Wallet(tdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH)
    ctx = create_ctx(mocker, btn_seq, wallet, None)
    addresses_ui = Addresses(ctx)

    # SDHandler
    mocker.patch(
        "os.listdir",
        return_value=["somefile", "otherfile"],
    )

    mocker.spy(addresses_ui, "export_address")

    m = mock_open()
    with patch("builtins.open", m):
        addresses_ui.addresses_menu()
        m().write.assert_any_call("0,tb1q4fhuxhrmz26kkuxxwataqw323cs2l3mgerz6kp\n")
        m().write.assert_any_call("49,tb1q8e9cxkrvg2d3q72wp9t33739pcnygrdyp2dm38\n")

    addresses_ui.export_address.assert_called()

    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_export_address_fail(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE
    from unittest.mock import mock_open, patch

    btn_seq = [
        BUTTON_PAGE,  # move to list addr
        BUTTON_PAGE,  # move to export addr
        BUTTON_ENTER,  # click export
        BUTTON_ENTER,  # click receive addr to enter
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm index 0
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm quantity 50
        BUTTON_PAGE_PREV,  # move to go
        BUTTON_ENTER,  # enter confirm filename Receive-fingerprint (will fail - SD card not detected)
        BUTTON_PAGE,  # move to back
        BUTTON_ENTER,  # exit screen
    ]
    wallet = Wallet(tdata.SINGLESIG_ACTION_KEY_TEST_P2WPKH)
    ctx = create_ctx(mocker, btn_seq, wallet, None)
    addresses_ui = Addresses(ctx)

    # SD available for entering export than fail when exporting
    mocker.patch.object(addresses_ui, "has_sd_card", side_effect=[True])

    mocker.spy(addresses_ui, "export_address")

    m = mock_open()
    with patch("builtins.open", m):
        addresses_ui.addresses_menu()
        m().write.assert_not_called()

    addresses_ui.export_address.assert_called()

    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_scan_change_address(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN, FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture
    from krux.format import format_address

    cases = [
        # Single-sig, not loaded, owned address, search successful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            None,
            False,
            "bc1qjv3nexd4rphldspsx8hwrasxw8x8dmsgu28wt5",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
        # Single-sig, loaded, owned address, search successful
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            "bc1qjv3nexd4rphldspsx8hwrasxw8x8dmsgu28wt5",
            True,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
            True,
        ),
    ]
    case_num = 0
    for case in cases:
        print("Case: %d" % case_num)
        case_num += 1
        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)
            assert wallet.has_change_addr()

        ctx = create_ctx(mocker, case[5], wallet, None)
        addresses_ui = Addresses(ctx)
        mocker.patch.object(
            QRCodeCapture, "qr_capture_loop", new=lambda self: (case[3], FORMAT_NONE)
        )
        qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")
        mocker.spy(addresses_ui, "show_address")

        addresses_ui.scan_address(1)  # Change addresses

        qr_capturer.assert_called_once()
        if case[4]:  # If address is valid
            addresses_ui.show_address.assert_called_once()
            can_search = (
                case[2] or not ctx.wallet.is_multisig()
            )  # If wallet is loaded or single-sig
            can_search &= len(case[5]) > 2  # If didn't skip search
            if can_search:
                if case[6]:  # If search should be successful
                    ctx.display.draw_centered_text.assert_called_with(
                        "0.\n\n%s\n\nis a valid address!" % format_address(case[3])
                    )
                else:
                    attempts = 50 * (len(case[5]) - 3)
                    ctx.display.draw_centered_text.assert_called_with(
                        "%s\n\nwas NOT FOUND in the first %s receive addresses"
                        % (format_address(case[3]), attempts)
                    )
        else:
            addresses_ui.show_address.assert_not_called()

        assert ctx.input.wait_for_button.call_count == len(case[5])


def test_scan_address_menu(mocker, m5stickv, tdata):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.pages.home_pages.addresses import Addresses
    from krux.wallet import Wallet

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    btn_seq = [BUTTON_PAGE_PREV, BUTTON_ENTER]
    ctx = create_ctx(mocker, btn_seq, wallet, None)
    addresses_ui = Addresses(ctx)
    addresses_ui._receive_change_menu(addresses_ui.scan_address)
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_scan_address_fails_on_decrypt_kef_key_error(mocker, m5stickv):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.home_pages.addresses import Addresses
    from krux.pages.qr_capture import QRCodeCapture
    from krux.pages import MENU_CONTINUE

    # nonsensical 0x8f byte encrypted w/ key="a" to test decryption failure
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (
            b"\x06binkey\x05\x01\x88WB\xb9\xab\xb6\xe9\x83\x97y\x1ab\xb0F\xe2|\xd3E\x84\x2b\x2c",
            0,
        ),
    )

    btn_seq = [
        BUTTON_ENTER,  # confirm decrypt
        BUTTON_ENTER,  # type key
        BUTTON_PAGE,  # to "b"
        BUTTON_ENTER,  # enter "b"
        BUTTON_PAGE_PREV,  # back to "a"
        BUTTON_PAGE_PREV,  # back to Go
        BUTTON_ENTER,  # go Go
        BUTTON_ENTER,  # confirm key "b" (while "a" is correct key)
    ]
    ctx = create_ctx(mocker, btn_seq)
    addresses_ui = Addresses(ctx)
    assert addresses_ui.scan_address() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)
    ctx.display.flash_text.assert_called_with(
        "Failed to decrypt", 248, 2000, highlight_prefix=""
    )


def test_list_receive_addresses(mocker, m5stickv, tdata):
    from krux.format import format_address
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.pages import MENU_CONTINUE
    from krux.pages.home_pages.addresses import Addresses
    from krux.qr import FORMAT_PMOFN
    from krux.settings import THIN_SPACE
    from krux.wallet import Wallet

    cases = [
        # 1 - Single-sig, no descriptor, unloaded, receive addr,
        # No print prompt, show address nº1
        (
            tdata.SINGLESIG_12_WORD_KEY,
            None,
            False,
            0,
            "show_address",
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 2 - Single-sig, descriptor, loaded, receive addr,
        # No print prompt, show address nº1
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            0,
            "show_address",
            "bc1qrhjqrz2d9tdym3p2r9m2vwzn2sn2yl6k5m357y",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 3 - Multisig, no descriptor, unloaded, receive addr,
        # No print prompt, flash error
        (
            tdata.MULTISIG_12_WORD_KEY,
            None,
            False,
            0,
            "flash_error",
            "Please load a wallet output descriptor",
            None,
            [],  # since it will flash an error, no buttons will be pressed
        ),
        # 4 - Multisig, descriptor, loaded, receive addr,
        # No print prompt, show address nº1
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            0,
            "show_address",
            "bc1q6y95p2qkcmsr7kp5zpnt04qx5l2slq73d9um62ka3s5nr83mlcfsywsn65",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 5 - Miniscript segwit v0, no descriptor, unloaded,
        # receive addr, No print prompt, flash error
        (
            tdata.MINISCRIPT_NATIVESW1_KEY,
            None,
            False,
            0,
            "flash_error",
            "Please load a wallet output descriptor",
            None,
            [],  # since it will flash an error, no buttons will be pressed
        ),
        # 6 - Miniscript segwit v0, single inheritance, descriptor, loaded,
        # receive address, No print prompt, show address nº1
        (
            tdata.MINISCRIPT_NATIVESW1_KEY,
            tdata.SPECTER_MINISCRIPT_SINGLE_INHERITANCE_WALLET_DATA,
            True,
            0,
            "show_address",
            "bc1qt3kx887zthezx02nzqv74evxztcdf8k8se00k5sgkr62ymc2sffssjx9dm",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 7 - Miniscript segwit v0 expanded multisig, descriptor, loaded,
        # receive address, No print prompt, show address nº1
        (
            tdata.MINISCRIPT_NATIVESW1_KEY,
            tdata.SPECTER_MINISCRIPT_EXPANDING_MULTISIG_WALLET_DATA,
            True,
            0,
            "show_address",
            "bc1qddnjn6vpm9fe7cgl5jvfk2fpa5huzsmddsm3vgz00nygx45mgxcs3t5a6j",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 8 - Miniscript segwit v0 3 joint keys, descriptor, loaded,
        # receive address, No print prompt, show address nº1
        (
            tdata.MINISCRIPT_NATIVESW1_KEY,
            tdata.SPECTER_MINISCRIPT_3_KEY_JOINT_CUSTODY_WALLET_DATA,
            True,
            0,
            "show_address",
            "bc1qtwhtzyd6yq6mkzpzk0sz7udcv59nhvm5zevkgp9f3hh6vu3kkg3sfkku2a",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
    ]

    for case in cases:
        # lets name the variables
        # for better readability
        mnemonic = case[0]
        descriptor = case[1]
        load = case[2]
        addr_type = case[3]
        method = case[4]
        result = case[5]
        print_prompt = case[6]
        sequence_buttons = case[7]

        print(f"Case: {cases.index(case)}: {descriptor}")

        # Create a wallet object and load the descriptor if needed
        wallet = Wallet(mnemonic)
        if load:
            wallet.load(descriptor, FORMAT_PMOFN)
            assert wallet.has_change_addr()

        # Create a context object with the mocker and the wallet
        # and adadpt the method to the test case
        ctx = create_ctx(mocker, sequence_buttons, wallet, print_prompt)
        addresses_ui = Addresses(ctx)

        # spy method dynamically, this is a method that
        # we want to assert when is called
        mocker.spy(addresses_ui, method)

        # load the address list in accordance to the test case
        addresses_ui.list_address_type(addr_type)

        # assert the method was called with the expected parameters
        # if the method is "show_address", assert that the address was shown
        # otherwise, assert that the error was flashed
        kwargs = (
            {}
            if (wallet.is_multisig() or wallet.is_miniscript())
            and not wallet.is_loaded()
            else {"title": "0." + THIN_SPACE + format_address(result)}
        )

        # assert that the method was called with the expected parameters
        getattr(addresses_ui, method).assert_called_once_with(result, **kwargs)

        # assert the number of calls to wait_for_button
        assert ctx.input.wait_for_button.call_count == len(sequence_buttons)


def test_list_change_addresses(mocker, m5stickv, tdata):
    from krux.format import format_address
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.pages.home_pages.addresses import Addresses
    from krux.qr import FORMAT_PMOFN
    from krux.settings import THIN_SPACE
    from krux.wallet import Wallet

    cases = [
        # 1 - Single-sig, no descriptor, unloaded, change addr,
        # No print prompt, show address nº1
        (
            tdata.SINGLESIG_12_WORD_KEY,
            None,
            False,
            1,
            "show_address",
            "bc1qjv3nexd4rphldspsx8hwrasxw8x8dmsgu28wt5",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 2 - Single-sig, descriptor, loaded, change addr,
        # No print prompt, show address nº1
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            True,
            1,
            "show_address",
            "bc1qjv3nexd4rphldspsx8hwrasxw8x8dmsgu28wt5",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 3 - Multisig, no descriptor, unloaded, change addr,
        # No print prompt, flash error
        (
            tdata.MULTISIG_12_WORD_KEY,
            None,
            False,
            1,
            "flash_error",
            "Please load a wallet output descriptor",
            None,
            [],  # since it will flash an error, no buttons will be pressed
        ),
        # 4 - Multisig, descriptor, loaded, change addr,
        # No print prompt, show address nº1
        (
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            True,
            1,
            "show_address",
            "bc1qew2hqa8wetygjdjnr784jdaeqlpa8qyx7eyfket3p8qlwuedwudskuel4p",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 5 - Miniscript (single inheritance), no descriptor, unloaded,
        # change addr, No print prompt, flash error
        (
            tdata.MINISCRIPT_NATIVESW1_KEY,
            None,
            False,
            1,
            "flash_error",
            "Please load a wallet output descriptor",
            None,
            [],  # since it will flash an error, no buttons will be pressed
        ),
        # 6 - Miniscript segwit v0 single inheritance, descriptor, loaded,
        # change address, No print prompt, show address nº1
        (
            tdata.MINISCRIPT_NATIVESW1_KEY,
            tdata.SPECTER_MINISCRIPT_SINGLE_INHERITANCE_WALLET_DATA,
            True,
            1,
            "show_address",
            "bc1q8vkx3lxu5dscgy053vcfvf8k6t8chws3h9lhqgwrluj5y8vctflsartf6u",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 7 - Miniscript segwit v0 expanded multisig, descriptor, loaded,
        # change address, No print prompt, show address nº1
        (
            tdata.MINISCRIPT_NATIVESW1_KEY,
            tdata.SPECTER_MINISCRIPT_EXPANDING_MULTISIG_WALLET_DATA,
            True,
            1,
            "show_address",
            "bc1q7cjmxupy4ef9rkwutzap3v3lznpyelkz9fjga2f8lyge0m2ghtgqrxhekg",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
        # 8 - Miniscript segwit v0 3 joint keys, descriptor, loaded,
        # change address, No print prompt, show address nº1
        (
            tdata.MINISCRIPT_NATIVESW1_KEY,
            tdata.SPECTER_MINISCRIPT_3_KEY_JOINT_CUSTODY_WALLET_DATA,
            True,
            1,
            "show_address",
            "bc1qtufz48hmjvf0ahwx8npg33z49enx0gcku20s88u608y7yqp0plustd4q8d",
            None,
            [
                *([BUTTON_PAGE_PREV] * 2),  # Go to "Next addresses"
                BUTTON_ENTER,  # Show next address
                BUTTON_ENTER,  # Go to previous addresses
                BUTTON_ENTER,  # Show address nº1
                BUTTON_ENTER,  # QR Menu
                BUTTON_PAGE_PREV,  # Go to "Back to Menu"
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Go to "Back"
                BUTTON_ENTER,  # Leave
            ],
        ),
    ]

    for case in cases:
        # lets name the variables
        # for better readability
        mnemonic = case[0]
        descriptor = case[1]
        load = case[2]
        addr_type = case[3]
        method = case[4]
        result = case[5]
        print_prompt = case[6]
        sequence_buttons = case[7]

        print(f"Case: {cases.index(case)}: {descriptor}")

        # Create a wallet object and load the descriptor if needed
        wallet = Wallet(mnemonic)
        if load:
            wallet.load(descriptor, FORMAT_PMOFN)
            assert wallet.has_change_addr()

        # Create a context object with the mocker and the wallet
        # and adadpt the method to the test case
        ctx = create_ctx(mocker, sequence_buttons, wallet, print_prompt)
        addresses_ui = Addresses(ctx)

        # spy method dynamically, this is a method that
        # we want to assert when is called
        mocker.spy(addresses_ui, method)

        # load the address list in accordance to the test case
        addresses_ui.list_address_type(addr_type)

        # assert the method was called with the expected parameters
        # if the method is "show_address", assert that the address was shown
        # otherwise, assert that the error was flashed
        kwargs = (
            {}
            if (wallet.is_multisig() or wallet.is_miniscript())
            and not wallet.is_loaded()
            else {"title": "0." + THIN_SPACE + format_address(result)}
        )

        # assert that the method was called with the expected parameters
        getattr(addresses_ui, method).assert_called_once_with(result, **kwargs)

        # assert the number of calls to wait_for_button
        assert ctx.input.wait_for_button.call_count == len(sequence_buttons)

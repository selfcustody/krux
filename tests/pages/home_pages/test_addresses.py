from .test_home import tdata, create_ctx


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
                        "0. \n\n%s\n\nis a valid address!" % format_address(case[3])
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
                        "0. \n\n%s\n\nis a valid address!" % format_address(case[3])
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
    from krux.pages.home_pages.addresses import Addresses
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(mocker, [BUTTON_PAGE_PREV, BUTTON_ENTER], wallet, None)
    addresses_ui = Addresses(ctx)
    addresses_ui.pre_scan_address()
    assert ctx.input.wait_for_button.call_count == 2


def test_list_receive_addresses(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_PMOFN
    from krux.settings import THIN_SPACE
    from krux.format import format_address

    cases = [
        # Single-sig, loaded, No print prompt, show address nº1
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            False,
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
        # TODO: Add cases for multisig and thermal printing
    ]
    for case in cases:
        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)

        ctx = create_ctx(mocker, case[5], wallet, case[4])
        addresses_ui = Addresses(ctx)
        mocker.spy(addresses_ui, "show_address")

        addresses_ui.list_address_type()

        addresses_ui.show_address.assert_called_with(
            case[3], title="0." + THIN_SPACE + format_address(case[3])
        )
        assert ctx.input.wait_for_button.call_count == len(case[5])


def test_list_change_addresses(mocker, m5stickv, tdata):
    from krux.pages.home_pages.addresses import Addresses
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_PMOFN
    from krux.settings import THIN_SPACE
    from krux.format import format_address

    cases = [
        # Single-sig, loaded, No print prompt, show address nº1
        (
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            False,
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
    ]
    for case in cases:
        wallet = Wallet(case[0])
        if case[2]:
            wallet.load(case[1], FORMAT_PMOFN)

        ctx = create_ctx(mocker, case[5], wallet, case[4])
        addresses_ui = Addresses(ctx)
        mocker.spy(addresses_ui, "show_address")

        addresses_ui.list_address_type(1)  # Change addresses

        addresses_ui.show_address.assert_called_with(
            case[3], title="0." + THIN_SPACE + format_address(case[3])
        )
        assert ctx.input.wait_for_button.call_count == len(case[5])

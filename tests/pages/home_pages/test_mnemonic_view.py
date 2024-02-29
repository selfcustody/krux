from .test_home import tdata
from ...shared_mocks import MockPrinter
from .. import create_ctx


def test_mnemonic_words(mocker, m5stickv, tdata):
    from krux.pages.home_pages.mnemonic_view import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE

    cases = [
        # See 12 Words
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # See 24 Words
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            None,
            [
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # See and print 24 Words
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # Words
                BUTTON_ENTER,  # Page 1
                BUTTON_ENTER,  # Page 2
                BUTTON_ENTER,  # Print
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
    ]
    num = 0
    for case in cases:
        print(num)
        num = num + 1
        ctx = create_ctx(mocker, case[2], case[0], case[1])
        mnemonics = MnemonicsView(ctx)

        mocker.spy(mnemonics, "display_mnemonic")
        mnemonics.mnemonic()

        mnemonics.display_mnemonic.assert_called_with(
            ctx.wallet.key.mnemonic, "Mnemonic"
        )
        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_mnemonic_standard_qr(mocker, m5stickv, tdata):
    from krux.pages.home_pages.mnemonic_view import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE

    cases = [
        # No print prompt
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,  # printer
            [
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Plaintext QR
                BUTTON_ENTER,  # click
                BUTTON_ENTER,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            None,  # printer
            [
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Plaintext QR
                BUTTON_ENTER,  # click
                BUTTON_ENTER,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # Print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Plaintext QR
                BUTTON_ENTER,  # click
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Plaintext QR
                BUTTON_ENTER,  # click
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # Decline to print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Plaintext QR
                BUTTON_ENTER,  # click
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Plaintext QR
                BUTTON_ENTER,  # click
                BUTTON_ENTER,
                BUTTON_PAGE,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
    ]
    num = 0
    for case in cases:
        print(num)
        num = num + 1
        ctx = create_ctx(mocker, case[2], case[0], case[1])
        mnemonics = MnemonicsView(ctx)

        mocker.spy(mnemonics, "display_qr_codes")
        mocker.spy(mnemonics.utils, "print_standard_qr")
        mnemonics.mnemonic()

        title = "Plaintext QR"
        mnemonics.display_qr_codes.assert_called_with(
            ctx.wallet.key.mnemonic, FORMAT_NONE, title
        )
        if case[1] is not None:
            mnemonics.utils.print_standard_qr.assert_called_with(
                ctx.wallet.key.mnemonic, FORMAT_NONE, title
            )
        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_mnemonic_compact_qr(mocker, m5stickv, tdata):
    from krux.pages.home_pages.mnemonic_view import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE

    cases = [
        # 0 - 12W
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # Select Compact SeedQR
                BUTTON_ENTER,  # Open Compact SeedQR
                BUTTON_ENTER,  # Open QR Menu
                BUTTON_PAGE_PREV,  # Move to leave QR Viewer
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 1 - 24W
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            None,
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # Select Compact SeedQR
                BUTTON_ENTER,  # Open Compact SeedQR
                BUTTON_ENTER,  # Open QR Menu
                BUTTON_PAGE_PREV,  # Move to leave QR Viewer
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 2 - 12W Print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Compact SeedQR
                BUTTON_ENTER,  # Open Compact SeedQR
                BUTTON_ENTER,  # Open QR Menu
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # Move to Print
                BUTTON_ENTER,  # Print
                BUTTON_ENTER,  # Print confirm
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Move to leave QR Viewer
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 3 - 24W Print
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Compact SeedQR
                BUTTON_ENTER,  # Open Compact SeedQR
                BUTTON_ENTER,  # Open QR Menu
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # Move to Print
                BUTTON_ENTER,  # Print
                BUTTON_ENTER,  # Print confirm
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Move to leave QR Viewer
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 4 - 12W Print, Decline to print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Compact SeedQR
                BUTTON_ENTER,  # Open Compact SeedQR
                BUTTON_ENTER,  # Open QR Menu
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # Move to Print
                BUTTON_ENTER,  # Print
                BUTTON_PAGE,  # Print decline
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Move to leave QR Viewer
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 5 - 24W Print, Decline to print
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # select Compact SeedQR
                BUTTON_ENTER,  # Open Compact SeedQR
                BUTTON_ENTER,  # Open QR Menu
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,  # Move to Print
                BUTTON_ENTER,  # Print
                BUTTON_PAGE,  # Print decline
                BUTTON_ENTER,  # Leave
                BUTTON_PAGE_PREV,  # Move to leave QR Viewer
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
    ]
    num = 0
    for case in cases:
        print(num)
        num = num + 1
        ctx = create_ctx(mocker, case[2], case[0], case[1])
        mnemonics = MnemonicsView(ctx)

        mocker.spy(mnemonics, "display_seed_qr")
        mnemonics.mnemonic()

        mnemonics.display_seed_qr.assert_called_once()

        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_mnemonic_st_qr_touch(mocker, amigo, tdata):
    from krux.pages.home_pages.mnemonic_view import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_TOUCH, BUTTON_PAGE_PREV, BUTTON_ENTER
    from krux.qr import FORMAT_NONE

    position = [2, 0]

    cases = [
        # No print prompt
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,
            [
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
            position,
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            None,
            [
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
            position,
        ),
        # Print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
            position + [0],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
            position + [0],
        ),
        # Decline to print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
            position + [1],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_TOUCH,
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
            position + [1],
        ),
    ]
    num = 0
    for case in cases:
        print(num)
        num = num + 1
        ctx = create_ctx(mocker, case[2], case[0], case[1], touch_seq=case[3])
        mnemonics = MnemonicsView(ctx)

        mocker.spy(mnemonics, "display_qr_codes")
        mocker.spy(mnemonics.utils, "print_standard_qr")

        mnemonics.mnemonic()

        title = "Plaintext QR"
        mnemonics.display_qr_codes.assert_called_with(
            ctx.wallet.key.mnemonic, FORMAT_NONE, title
        )
        if case[1] is not None:
            mnemonics.utils.print_standard_qr.assert_called_with(
                ctx.wallet.key.mnemonic, FORMAT_NONE, title
            )

        assert ctx.input.wait_for_button.call_count == len(case[2])

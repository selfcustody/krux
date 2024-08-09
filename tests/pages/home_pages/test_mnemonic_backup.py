from .test_home import tdata
from ...shared_mocks import MockPrinter
from .. import create_ctx


def test_load_mnemonic_encryption(mocker, amigo):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # Go to Back
        BUTTON_ENTER,  # Exit
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    m_view = MnemonicsView(ctx)
    m_view.encrypt_mnemonic_menu()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_mnemonic_words(mocker, m5stickv, tdata):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE

    cases = [
        # See 12 Words
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,  # Other
                BUTTON_ENTER,  # Words
                BUTTON_ENTER,  # Leave Page 1
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # See 24 Words
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            None,
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,  # Other
                BUTTON_ENTER,  # Words
                BUTTON_ENTER,  # Leave Page 1
                BUTTON_ENTER,  # Leave Page 2
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # See and print 24 Words
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_ENTER,  # Other
                BUTTON_ENTER,  # Words
                BUTTON_ENTER,  # Leave Page 1
                BUTTON_ENTER,  # Leave Page 2
                BUTTON_ENTER,  # Print
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE,  # change to btn Back
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
            ctx.wallet.key.mnemonic, "Mnemonic", None
        )
        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_mnemonic_standard_qr(mocker, m5stickv, tdata):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE

    cases = [
        # No print prompt
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,  # printer
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_ENTER,  # Plaintext QR
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            None,  # printer
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_ENTER,  # Plaintext QR
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # Print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_ENTER,  # Plaintext QR
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_ENTER,  # Print
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_ENTER,  # Plaintext QR
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_ENTER,  # Print
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # Decline to print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_ENTER,  # Plaintext QR
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE,  # Decline to print
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_ENTER,  # Plaintext QR
                BUTTON_ENTER,  # Leave QR Viewer
                BUTTON_PAGE,  # Decline to print
                BUTTON_PAGE_PREV,  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
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
        mnemonics.mnemonic()

        title = "Plaintext QR"
        mnemonics.display_qr_codes.assert_called_with(
            ctx.wallet.key.mnemonic, FORMAT_NONE, title
        )
        assert ctx.input.wait_for_button.call_count == len(case[2])


def test_mnemonic_compact_qr(mocker, m5stickv, tdata):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE

    cases = [
        # 0 - 12W
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_PAGE,  # Move to Compact SeedQR
                BUTTON_ENTER,  # Compact SeedQR
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # change to btn Back to Menu on QR Menu
                BUTTON_ENTER,  # click on back to return to QR codes Backup Menu
                *([BUTTON_PAGE_PREV] * 2),  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 1 - 24W
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            None,
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_PAGE,  # Move to Compact SeedQR
                BUTTON_ENTER,  # Compact SeedQR
                BUTTON_ENTER,  # Enter QR Menu
                BUTTON_PAGE_PREV,  # change to btn Back to Menu on QR Menu
                BUTTON_ENTER,  # click on back to return to QR codes Backup Menu
                *([BUTTON_PAGE_PREV] * 2),  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 2 - 12W Print
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_PAGE,  # Move to Compact SeedQR
                BUTTON_ENTER,  # Compact SeedQR
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 3),  # Move to Print
                BUTTON_ENTER,  # Print
                BUTTON_ENTER,  # Confirm Print
                BUTTON_ENTER,  # Enter QR Menu again
                BUTTON_PAGE_PREV,  # move to btn Back to Menu on QR Menu
                BUTTON_ENTER,  # click on back to return to QR codes Backup Menu
                *([BUTTON_PAGE_PREV] * 2),  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 3 - 24W Print
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_PAGE,  # Move to Compact SeedQR
                BUTTON_ENTER,  # Compact SeedQR
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 3),  # Move to Print
                BUTTON_ENTER,  # Print
                BUTTON_ENTER,  # Confirm Print
                BUTTON_ENTER,  # Enter QR Menu again
                BUTTON_PAGE_PREV,  # move to btn Back to Menu on QR Menu
                BUTTON_ENTER,  # click on back to return to QR codes Backup Menu
                *([BUTTON_PAGE_PREV] * 2),  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 4 - 12W Print, Decline to print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_PAGE,  # Move to Compact SeedQR
                BUTTON_ENTER,  # Compact SeedQR
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 3),  # Move to Print
                BUTTON_ENTER,  # Print
                BUTTON_PAGE,  # Decline Print
                BUTTON_ENTER,  # Enter QR Menu again
                BUTTON_PAGE_PREV,  # move to btn Back to Menu on QR Menu
                BUTTON_ENTER,  # click on back to return to QR codes Backup Menu
                *([BUTTON_PAGE_PREV] * 2),  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,  # click on back to return to home init screen
            ],
        ),
        # 5 - 24W Print, Decline to print
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                BUTTON_ENTER,  # QR Code
                BUTTON_PAGE,  # Move to Compact SeedQR
                BUTTON_ENTER,  # Compact SeedQR
                BUTTON_ENTER,  # Enter QR Menu
                *([BUTTON_PAGE] * 3),  # Move to Print
                BUTTON_ENTER,  # Print
                BUTTON_PAGE,  # Decline Print
                BUTTON_ENTER,  # Enter QR Menu again
                BUTTON_PAGE_PREV,  # move to btn Back to Menu on QR Menu
                BUTTON_ENTER,  # click on back to return to QR codes Backup Menu
                *([BUTTON_PAGE_PREV] * 2),  # change to btn Back
                BUTTON_ENTER,  # click on back to return to Mnemonic Backup
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


def test_mnemonic_standard_qr_touch(mocker, amigo, tdata):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.wallet import Wallet
    from krux.input import BUTTON_TOUCH
    from krux.qr import FORMAT_NONE

    touch_index = [0, 0]  # Enter QR Code, Enter Plaintext QR

    cases = [
        # No print prompt
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            None,
            [
                *([BUTTON_TOUCH] * 5),
            ],
            touch_index
            + [
                # 0,  # QR code leave press won't read index
                4,  # Back to Mnemonic Backup
                3,  # Back to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            None,
            [
                *([BUTTON_TOUCH] * 5),
            ],
            touch_index
            + [
                # 0,  # QR code leave press won't read index
                4,  # Back to Mnemonic Backup
                3,  # Back to home init screen
            ],
        ),
        # Print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                *([BUTTON_TOUCH] * 6),
            ],
            touch_index
            + [
                # 0,  # QR code leave press won't read index
                0,  # Print
                4,  # Back to Mnemonic Backup
                3,  # Back to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                *([BUTTON_TOUCH] * 6),
            ],
            touch_index
            + [
                # 0,  # QR code leave press won't read index
                0,  # Print
                4,  # Back to Mnemonic Backup
                3,  # Back to home init screen
            ],
        ),
        # Decline to print
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            MockPrinter(),
            [
                *([BUTTON_TOUCH] * 6),
            ],
            touch_index
            + [
                # 0,  # QR code leave press won't read index
                1,  # Decline to print
                4,  # Back to Mnemonic Backup
                3,  # Back to home init screen
            ],
        ),
        (
            Wallet(tdata.SINGLESIG_24_WORD_KEY),
            MockPrinter(),
            [
                *([BUTTON_TOUCH] * 6),
            ],
            touch_index
            + [
                # 0,  # QR code leave press won't read index
                1,  # Decline to print
                4,  # Back to Mnemonic Backup
                3,  # Back to home init screen
            ],
        ),
    ]
    num = 0
    for case in cases:
        print(num)
        num = num + 1
        ctx = create_ctx(mocker, case[2], case[0], case[1], touch_seq=case[3])
        mnemonics = MnemonicsView(ctx)

        mocker.spy(mnemonics, "display_qr_codes")

        mnemonics.mnemonic()

        title = "Plaintext QR"
        mnemonics.display_qr_codes.assert_called_with(
            ctx.wallet.key.mnemonic, FORMAT_NONE, title
        )

        assert ctx.input.wait_for_button.call_count == len(case[2])

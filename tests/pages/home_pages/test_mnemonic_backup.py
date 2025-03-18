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


def test_print_mnemonic_other_words(mocker, amigo, tdata):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.input import BUTTON_PAGE_PREV, BUTTON_ENTER
    from krux.wallet import Wallet

    BTN_SEQ = [
        BUTTON_ENTER,  # WORDS
        BUTTON_ENTER,  # Exit view
        BUTTON_ENTER,  # Print
        BUTTON_PAGE_PREV,  # Move back
        BUTTON_ENTER,  # Exit
    ]

    printer = MockPrinter()

    def custom_create_printer():
        return printer

    ctx = create_ctx(mocker, BTN_SEQ, printer=printer)
    ctx.wallet = Wallet(tdata.SINGLESIG_24_WORD_KEY)

    mocker.patch("krux.printers.create_printer", new=custom_create_printer)
    mnemonics = MnemonicsView(ctx)

    mocker.spy(printer, "print_string")
    mocker.spy(mnemonics, "show_mnemonic")

    mnemonics.other_backup_formats()

    mnemonics.show_mnemonic.assert_called()

    # brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
    printer.print_string.assert_has_calls(
        [
            mocker.call("1:brush   9:help     17:human\n"),
            mocker.call("2:badge   10:panel   18:once\n"),
            mocker.call("3:sing    11:bundle  19:effort\n"),
            mocker.call("4:still   12:excess  20:candy\n"),
            mocker.call("5:venue   13:sign    21:goat\n"),
            mocker.call("6:panther 14:couch   22:top\n"),
            mocker.call("7:kitchen 15:stove   23:tiny\n"),
            mocker.call("8:please  16:increase 24:major\n"),
        ]
    )


def test_print_mnemonic_numbers_decimal(mocker, amigo, tdata):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.input import BUTTON_PAGE_PREV, BUTTON_ENTER
    from krux.wallet import Wallet

    BTN_SEQ = [
        BUTTON_ENTER,  # DECIMAL
        BUTTON_ENTER,  # Exit view
        BUTTON_ENTER,  # Print
        BUTTON_PAGE_PREV,  # Move back
        BUTTON_ENTER,  # Exit
    ]

    printer = MockPrinter()

    def custom_create_printer():
        return printer

    ctx = create_ctx(mocker, BTN_SEQ, printer=printer)
    ctx.wallet = Wallet(tdata.SINGLESIG_24_WORD_KEY)

    mocker.patch("krux.printers.create_printer", new=custom_create_printer)
    mnemonics = MnemonicsView(ctx)

    mocker.spy(printer, "print_string")
    mocker.spy(mnemonics, "show_mnemonic")

    mnemonics.display_mnemonic_numbers()

    mnemonics.show_mnemonic.assert_called()

    # brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
    printer.print_string.assert_has_calls(
        [
            mocker.call("1:234     9:857      17:887\n"),
            mocker.call("2:140     10:1277    18:1237\n"),
            mocker.call("3:1611    11:243     19:566\n"),
            mocker.call("4:1711    12:629     20:267\n"),
            mocker.call("5:1940    13:1603    21:801\n"),
            mocker.call("6:1279    14:392     22:1832\n"),
            mocker.call("7:985     15:1718    23:1812\n"),
            mocker.call("8:1332    16:918     24:1076\n"),
        ]
    )


def test_print_mnemonic_numbers_hex(mocker, amigo, tdata):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.input import BUTTON_PAGE_PREV, BUTTON_PAGE, BUTTON_ENTER
    from krux.wallet import Wallet

    BTN_SEQ = [
        BUTTON_PAGE,  # HEX
        BUTTON_ENTER,  # Confirm
        BUTTON_ENTER,  # Exit view
        BUTTON_ENTER,  # Print prompt
        BUTTON_PAGE,  # Move to OCT
        BUTTON_PAGE,  # Move to < back
        BUTTON_ENTER,  # press < back
    ]

    printer = MockPrinter()

    def custom_create_printer():
        return printer

    ctx = create_ctx(mocker, BTN_SEQ, printer=printer)
    ctx.wallet = Wallet(tdata.SINGLESIG_24_WORD_KEY)

    mocker.patch("krux.printers.create_printer", new=custom_create_printer)
    mnemonics = MnemonicsView(ctx)

    mocker.spy(printer, "print_string")
    mocker.spy(mnemonics, "show_mnemonic")

    mnemonics.display_mnemonic_numbers()

    mnemonics.show_mnemonic.assert_called()

    # brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
    printer.print_string.assert_has_calls(
        [
            mocker.call("1:EA      9:359      17:377\n"),
            mocker.call("2:8C      10:4FD     18:4D5\n"),
            mocker.call("3:64B     11:F3      19:236\n"),
            mocker.call("4:6AF     12:275     20:10B\n"),
            mocker.call("5:794     13:643     21:321\n"),
            mocker.call("6:4FF     14:188     22:728\n"),
            mocker.call("7:3D9     15:6B6     23:714\n"),
            mocker.call("8:534     16:396     24:434\n"),
        ]
    )


def test_print_mnemonic_numbers_oct(mocker, amigo, tdata):
    from krux.pages.home_pages.mnemonic_backup import MnemonicsView
    from krux.input import BUTTON_PAGE_PREV, BUTTON_PAGE, BUTTON_ENTER
    from krux.wallet import Wallet

    BTN_SEQ = [
        BUTTON_PAGE,  # HEX
        BUTTON_PAGE,  # OCT
        BUTTON_ENTER,  # Confirm
        BUTTON_ENTER,  # Exit view
        BUTTON_ENTER,  # Print prompt
        BUTTON_PAGE,  # Move to < back
        BUTTON_ENTER,  # press < back
    ]

    printer = MockPrinter()

    def custom_create_printer():
        return printer

    ctx = create_ctx(mocker, BTN_SEQ, printer=printer)
    ctx.wallet = Wallet(tdata.SINGLESIG_24_WORD_KEY)

    mocker.patch("krux.printers.create_printer", new=custom_create_printer)
    mnemonics = MnemonicsView(ctx)

    mocker.spy(printer, "print_string")
    mocker.spy(mnemonics, "show_mnemonic")

    mnemonics.display_mnemonic_numbers()

    mnemonics.show_mnemonic.assert_called()

    # brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
    printer.print_string.assert_has_calls(
        [
            mocker.call("1:352     9:1531     17:1567\n"),
            mocker.call("2:214     10:2375    18:2325\n"),
            mocker.call("3:3113    11:363     19:1066\n"),
            mocker.call("4:3257    12:1165    20:413\n"),
            mocker.call("5:3624    13:3103    21:1441\n"),
            mocker.call("6:2377    14:610     22:3450\n"),
            mocker.call("7:1731    15:3266    23:3424\n"),
            mocker.call("8:2464    16:1626    24:2064\n"),
        ]
    )

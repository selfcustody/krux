from .test_home import tdata, create_ctx


def test_bip85_bip39_mnemonic_derivation(mocker, amigo, tdata):
    from krux.krux_settings import Settings
    from krux.settings import THIN_SPACE
    from krux.pages.home_pages.bip85 import Bip85
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.themes import theme
    from krux.key import FINGERPRINT_SYMBOL

    cases = [
        # case
        # (
        # wallet
        # Button presses
        # BIP85 child mnemonic
        # BIP85 child fingerprint
        # Loaded?
        # )
        # 0 - give up at beginning
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_PAGE_PREV,  # Move to "Back"
                BUTTON_ENTER,  # Confirm
            ],
            None,
            None,
            False,
        ),
        # 1 - 12w, load
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                BUTTON_ENTER,  # Child index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "neutral cattle hill strong someone enjoy deputy plastic cat birth athlete inherit",
            "a620a1bc",
            True,
        ),
        # 2 - 24w in, 12w out, load
        (
            tdata.SINGLESIG_24_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words out
                BUTTON_ENTER,  # Child index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "mule patient cloth romance tongue taxi animal sweet develop settle elegant exercise",
            "f1556c60",
            True,
        ),
        # 3 - 12w in, 24w out, load
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_PAGE,  # Move to 24 words
                BUTTON_ENTER,  # Choose 24 words
                BUTTON_ENTER,  # Child index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "nice hundred tree change section dismiss wet birth sleep under cattle beef cross chunk rain elbow work tag tiger weird toy stand offer smart",
            "cac16c1b",
            True,
        ),
        # 4 - 12w, don't load
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                BUTTON_ENTER,  # Child index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_PAGE,  # Move to Cancel
                BUTTON_ENTER,  # Cancel
            ],
            "neutral cattle hill strong someone enjoy deputy plastic cat birth athlete inherit",
            "a620a1bc",
            False,
        ),
        # 12w, ESC
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                *([BUTTON_PAGE_PREV] * 2),  # Move to "Esc"
                BUTTON_ENTER,  # Press "Esc"
                BUTTON_ENTER,  # Confirm
            ],
            None,
            None,
            False,
        ),
        # Assert if no index is assigned it stays in the loop
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                BUTTON_PAGE_PREV,  # Move to "Go" with no index assigned
                BUTTON_ENTER,  # Go
                # Loop back to initial state
                BUTTON_ENTER,  # this time assign 1 for index
                BUTTON_PAGE_PREV,  # Move to "Go" with no index assigned
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "neutral cattle hill strong someone enjoy deputy plastic cat birth athlete inherit",
            "a620a1bc",
            True,
        ),
        # Too big index
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                BUTTON_PAGE,  # Move to 2
                *([BUTTON_ENTER] * 12),  # Type 222222222222
                *([BUTTON_PAGE_PREV] * 2),  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Invalid value message
                BUTTON_ENTER,  # Assign index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "neutral cattle hill strong someone enjoy deputy plastic cat birth athlete inherit",
            "a620a1bc",
            True,
        ),
    ]

    case_num = 0
    for case in cases:
        print(case_num)
        wallet = Wallet(case[0])
        ctx = create_ctx(mocker, case[1], wallet)
        bip85_ui = Bip85(ctx)
        mocker.spy(bip85_ui, "display_mnemonic")
        bip85_ui.export()

        assert ctx.input.wait_for_button.call_count == len(case[1])

        if case[2]:
            bip85_ui.display_mnemonic.assert_called_with(
                case[2],
                suffix="Words",
                fingerprint=FINGERPRINT_SYMBOL + THIN_SPACE + "%s" % case[3],
            )
        else:
            bip85_ui.display_mnemonic.assert_not_called()

        if case[4]:
            assert ctx.wallet.key.mnemonic == case[2]
        else:
            assert ctx.wallet.key.mnemonic == case[0].mnemonic
        case_num += 1

    # Test with hidden mnemonic setting enabled
    Settings().security.hide_mnemonic = True
    ctx = create_ctx(mocker, cases[1][1], wallet)
    bip85_ui = Bip85(ctx)
    mocker.spy(bip85_ui, "display_mnemonic")
    bip85_ui.export()
    ctx.display.draw_centered_text.assert_called_with(
        FINGERPRINT_SYMBOL + THIN_SPACE + "%s" % case[3], color=theme.highlight_color
    )


def test_bip85_bip39_mnemonic_derivation_m5(mocker, m5stickv, tdata):
    from krux.krux_settings import Settings
    from krux.settings import THIN_SPACE
    from krux.pages.home_pages.bip85 import Bip85
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.themes import theme
    from krux.key import FINGERPRINT_SYMBOL

    cases = [
        # case
        # (
        # wallet
        # Button presses
        # BIP85 child mnemonic
        # BIP85 child fingerprint
        # Loaded?
        # )
        # 0 - give up at beginning
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_PAGE_PREV,  # Move to "Back"
                BUTTON_ENTER,  # Confirm
            ],
            None,
            None,
            False,
        ),
        # 1 - 12w, load
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                BUTTON_ENTER,  # Child index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "neutral cattle hill strong someone enjoy deputy plastic cat birth athlete inherit",
            "a620a1bc",
            True,
        ),
        # 2 - 24w in, 12w out, load
        (
            tdata.SINGLESIG_24_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words out
                BUTTON_ENTER,  # Child index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "mule patient cloth romance tongue taxi animal sweet develop settle elegant exercise",
            "f1556c60",
            True,
        ),
        # 3 - 12w in, 24w out, load
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_PAGE,  # Move to 24 words
                BUTTON_ENTER,  # Choose 24 words
                BUTTON_ENTER,  # Child index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # confirm 12
                BUTTON_ENTER,  # Load? Yes
            ],
            "nice hundred tree change section dismiss wet birth sleep under cattle beef cross chunk rain elbow work tag tiger weird toy stand offer smart",
            "cac16c1b",
            True,
        ),
        # 4 - 12w, don't load
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                BUTTON_ENTER,  # Child index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_PAGE,  # Cancel
            ],
            "neutral cattle hill strong someone enjoy deputy plastic cat birth athlete inherit",
            "a620a1bc",
            False,
        ),
        # 12w, ESC
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                *([BUTTON_PAGE_PREV] * 2),  # Move to "Esc"
                BUTTON_ENTER,  # Press "Esc"
                BUTTON_ENTER,  # Confirm
            ],
            None,
            None,
            False,
        ),
        # Assert if no index is assigned it stays in the loop
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                BUTTON_PAGE_PREV,  # Move to "Go" with no index assigned
                BUTTON_ENTER,  # Go
                # Loop back to initial state
                BUTTON_ENTER,  # this time assign 1 for index
                BUTTON_PAGE_PREV,  # Move to "Go" with no index assigned
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "neutral cattle hill strong someone enjoy deputy plastic cat birth athlete inherit",
            "a620a1bc",
            True,
        ),
        # Too big index
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_ENTER,  # BIP39 Mnemonics
                BUTTON_ENTER,  # 12 words
                BUTTON_PAGE,  # Move to 2
                *([BUTTON_ENTER] * 12),  # Type 222222222222
                *([BUTTON_PAGE_PREV] * 2),  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Invalid value message
                BUTTON_ENTER,  # Assign index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Load? Yes
            ],
            "neutral cattle hill strong someone enjoy deputy plastic cat birth athlete inherit",
            "a620a1bc",
            True,
        ),
    ]

    case_num = 0
    for case in cases:
        print(case_num)
        wallet = Wallet(case[0])
        ctx = create_ctx(mocker, case[1], wallet)
        bip85_ui = Bip85(ctx)
        mocker.spy(bip85_ui, "display_mnemonic")
        bip85_ui.export()

        assert ctx.input.wait_for_button.call_count == len(case[1])

        if case[2]:
            bip85_ui.display_mnemonic.assert_called_with(
                case[2],
                suffix="Words",
                fingerprint=FINGERPRINT_SYMBOL + THIN_SPACE + "%s" % case[3],
            )
        else:
            bip85_ui.display_mnemonic.assert_not_called()

        if case[4]:
            assert ctx.wallet.key.mnemonic == case[2]
        else:
            assert ctx.wallet.key.mnemonic == case[0].mnemonic
        case_num += 1

    print("last case hide_mnemonic")
    # Test with hidden mnemonic setting enabled
    Settings().security.hide_mnemonic = True
    ctx = create_ctx(mocker, cases[1][1], wallet)
    bip85_ui = Bip85(ctx)
    mocker.spy(bip85_ui, "display_mnemonic")
    bip85_ui.export()
    ctx.display.draw_centered_text.assert_called_with(
        FINGERPRINT_SYMBOL + THIN_SPACE + "%s" % case[3], color=theme.highlight_color
    )


def test_bip85_base64_password_derivation(mocker, amigo, tdata):
    from krux.pages.home_pages.bip85 import Bip85
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.settings import TEST_TXT
    from embit import bip32
    from embit.networks import NETWORKS

    cases = [
        # case
        # (
        # wallet
        # Button presses
        # Password info
        # QR data
        # Save to SD card (True/False)
        # )
        # 0 - 12w input, check the password and leave
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_PAGE,  # Move to "Base64 Password"
                BUTTON_ENTER,  # Confirm
                BUTTON_ENTER,  # Index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Keep length = 21
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_PAGE_PREV,  # Move to "< Back"
                BUTTON_ENTER,  # Leave
            ],
            "n6JwU7iRyf2vhYeaToS3K\n\nIndex: 1\nLength: 21",
        ),
        # 1 - 24w input, check the password and leave
        (
            tdata.SINGLESIG_24_WORD_KEY,
            [
                BUTTON_PAGE,  # Move to "Base64 Password"
                BUTTON_ENTER,  # Confirm
                BUTTON_ENTER,  # Index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Keep length = 21
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_PAGE_PREV,  # Move to "< Back"
                BUTTON_ENTER,  # Leave
            ],
            "SC7Ib2KFm8/Fo6T8Okw+m\n\nIndex: 1\nLength: 21",
        ),
        # 2 - invalid password length, retry
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_PAGE,  # Move to "Base64 Password"
                BUTTON_ENTER,  # Confirm
                BUTTON_ENTER,  # Index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_ENTER,  # Append 1 to (211)
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Wait for the error message
                BUTTON_PAGE_PREV,  # Move to "Go" again
                BUTTON_ENTER,  # Go with 21
                BUTTON_PAGE_PREV,  # Move to "< Back"
                BUTTON_ENTER,  # Leave
            ],
            "n6JwU7iRyf2vhYeaToS3K\n\nIndex: 1\nLength: 21",
        ),
        # 3 - ESC at password length input
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_PAGE,  # Move to "Base64 Password"
                BUTTON_ENTER,  # Confirm
                BUTTON_ENTER,  # Index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                *([BUTTON_PAGE_PREV] * 2),  # Move to "Esc"
                BUTTON_ENTER,  # Press "Esc"
                BUTTON_ENTER,  # Confirm
            ],
            None,
        ),
        # 4 - Print QR code
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_PAGE,  # Move to "Base64 Password"
                BUTTON_ENTER,  # Confirm
                BUTTON_ENTER,  # Index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Keep length = 21
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Print QR code
                BUTTON_ENTER,  # Print QR code
                BUTTON_ENTER,  # Back main menu
                BUTTON_PAGE_PREV,  # Move to "< Back"
                BUTTON_ENTER,  # Leave
            ],
            "n6JwU7iRyf2vhYeaToS3K\n\nIndex: 1\nLength: 21",
            "n6JwU7iRyf2vhYeaToS3K",
        ),
        # 5 - Test save to SD card
        (
            tdata.SINGLESIG_12_WORD_KEY,
            [
                BUTTON_PAGE,  # Move to "Base64 Password"
                BUTTON_ENTER,  # Confirm
                BUTTON_ENTER,  # Index 1
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Keep length = 21
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Save to SD card
                BUTTON_PAGE,  # Move to "Save to SD card"
                BUTTON_ENTER,  # Press to save
                BUTTON_ENTER,  # Confirm
                # Confirm file name
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Save
                BUTTON_PAGE_PREV,  # Move to "< Back"
                BUTTON_ENTER,  # Leave
            ],
            "n6JwU7iRyf2vhYeaToS3K\n\nIndex: 1\nLength: 21",
            None,
            True,
        ),
        # 6 - Test xprv example from BIP85 spec
        (
            "xprv9s21ZrQH143K2LBWUUQRFXhucrQqBpKdRRxNVq2zBqsx8HVqFk2uYo8kmbaLLHRdqtQpUm98uKfu3vca1LqdGhUtyoFnCNkfmXRyPXLjbKb",
            [
                BUTTON_PAGE,  # Move to "Base64 Password"
                BUTTON_ENTER,  # Confirm
                *([BUTTON_PAGE_PREV] * 4),  # Type 21 characters
                BUTTON_ENTER,  # Index 0
                *([BUTTON_PAGE] * 3),  # Move to "Go"
                BUTTON_ENTER,  # Go
                # Keep length = 21
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Go
                BUTTON_PAGE_PREV,  # Move to "< Back"
                BUTTON_ENTER,  # Leave
            ],
            "dKLoepugzdVJvdL56ogNV\n\nIndex: 0\nLength: 21",
        ),
    ]
    mock_save_file = mocker.patch(
        "krux.pages.file_operations.SaveFile.save_file",
    )
    case_num = 0
    for case in cases:
        print(case_num)
        if isinstance(case[0], str):
            # Create a dummy wallet
            wallet = Wallet(cases[0][0])
            # Replace root with the xprv
            wallet.key.root = bip32.HDKey.from_string(case[0])
        else:
            wallet = Wallet(case[0])
        ctx = create_ctx(mocker, case[1], wallet)
        mocker.spy(ctx.display, "draw_hcentered_text")
        bip85_ui = Bip85(ctx)
        mocker.patch.object(bip85_ui, "has_sd_card", new=lambda: True)
        mocker.spy(bip85_ui, "_base64_password_qr")
        bip85_ui.export()

        assert ctx.input.wait_for_button.call_count == len(case[1])
        if case[2]:
            ctx.display.draw_hcentered_text.assert_has_calls(
                [mocker.call(case[2], info_box=True, highlight_prefix=":")]
            )
        if len(case) > 3 and case[3]:
            bip85_ui._base64_password_qr.assert_has_calls(
                [mocker.call(case[3], "Base64 Password")]
            )

        if len(case) > 4 and case[4]:
            mock_save_file.assert_called_once_with(
                case[2],
                "BIP85_password",
                "BIP85_password",
                "BIP85 Password:",
                ".txt",
                save_as_binary=False,
            )
        case_num += 1

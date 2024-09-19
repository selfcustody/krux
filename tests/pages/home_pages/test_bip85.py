from .test_home import tdata, create_ctx


def test_bip85_wallet_creation(mocker, amigo, tdata):
    from krux.krux_settings import Settings
    from krux.settings import THIN_SPACE
    from krux.pages.home_pages.bip85 import Bip85
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

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
                case[2], suffix="Words", fingerprint="⊚" + THIN_SPACE + "%s" % case[3]
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
    ctx.display.draw_centered_text.assert_called_with("⊚" + THIN_SPACE + "%s" % case[3])

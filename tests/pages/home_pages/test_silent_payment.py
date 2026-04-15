from .test_home import create_ctx, tdata

# Expected SP addresses for tdata.SINGLESIG_12_WORD_KEY
# (mnemonic: "olympic term tissue route sense program under choose bean emerge velvet absurd", mainnet)
EXPECTED_SP_ADDRESS = "sp1qqf702ka9tkw9au8txt9q2z4yv3glhfs2g26msmr2fe96vcmdpegryq6w0c0tw5sctj7fg09t09dl6xjka2zhx06u0wrg4ykedazt3vadyujmlsu7"
EXPECTED_SP_ADDRESS_LABEL_42 = "sp1qqf702ka9tkw9au8txt9q2z4yv3glhfs2g26msmr2fe96vcmdpegryqectr7zkr53sjuur6dwz794aye3gnsmyreergr2a2hmasx07m0k0gsymg4h"


def test_silent_payment_export_back(mocker, amigo, tdata):
    """Test navigating into the SP menu and going back"""
    from krux.pages.home_pages.silent_payment import SilentPayment
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(
        mocker,
        [
            BUTTON_PAGE_PREV,  # Move to "< Back"
            BUTTON_ENTER,  # Press "< Back"
        ],
        wallet,
    )
    sp = SilentPayment(ctx)
    sp.export()

    assert ctx.input.wait_for_button.call_count == 2


def test_silent_payment_generate_address(mocker, amigo, tdata):
    """Test generating a silent payment address (no label)"""
    from krux.pages.home_pages.silent_payment import SilentPayment
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(
        mocker,
        [
            BUTTON_ENTER,  # SP Address
            BUTTON_PAGE_PREV,  # Move to "< Back" in address display
            BUTTON_ENTER,  # Press "< Back"
            BUTTON_PAGE_PREV,  # Move to "< Back" in main menu
            BUTTON_ENTER,  # Press "< Back"
        ],
        wallet,
    )
    sp = SilentPayment(ctx)
    sp.export()

    # Verify the exact expected address was drawn
    found_sp_address = any(
        isinstance(arg, str) and EXPECTED_SP_ADDRESS in arg
        for call in ctx.display.draw_hcentered_text.call_args_list
        for arg in (call[0] if call[0] else [])
    )
    assert found_sp_address


def test_silent_payment_generate_labeled_address(mocker, amigo, tdata):
    """Test generating a labeled silent payment address"""
    from krux.pages.home_pages.silent_payment import SilentPayment
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    mocker.patch(
        "krux.pages.utils.Utils.capture_index_from_keypad",
        return_value=42,
    )
    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(
        mocker,
        [
            BUTTON_PAGE,      # Move to "SP Address with Label"
            BUTTON_ENTER,     # Select "SP Address with Label"
            BUTTON_PAGE_PREV, # Move to "< Back" in address display
            BUTTON_ENTER,     # Press "< Back"
            BUTTON_PAGE,      # Move to "< Back" in main menu (from index 1 → 2)
            BUTTON_ENTER,     # Press "< Back"
        ],
        wallet,
    )
    sp = SilentPayment(ctx)
    sp.export()

    found_sp_address = any(
        isinstance(arg, str) and EXPECTED_SP_ADDRESS_LABEL_42 in arg
        for call in ctx.display.draw_hcentered_text.call_args_list
        for arg in (call[0] if call[0] else [])
    )
    assert found_sp_address


def test_silent_payment_generate_address_m5(mocker, m5stickv, tdata):
    """Test generating a silent payment address on m5stickv"""
    from krux.pages.home_pages.silent_payment import SilentPayment
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    wallet = Wallet(tdata.SINGLESIG_12_WORD_KEY)
    ctx = create_ctx(
        mocker,
        [
            BUTTON_ENTER,  # SP Address
            BUTTON_PAGE,  # Move to "< Back" in address display (1 item + back)
            BUTTON_ENTER,  # Press "< Back"
            BUTTON_PAGE,  # Move past "SP Address"
            BUTTON_PAGE,  # Move past "SP Address with Label" to "< Back"
            BUTTON_ENTER,  # Press "< Back"
        ],
        wallet,
    )
    sp = SilentPayment(ctx)
    sp.export()

    found_sp_address = any(
        isinstance(arg, str) and EXPECTED_SP_ADDRESS in arg
        for call in ctx.display.draw_hcentered_text.call_args_list
        for arg in (call[0] if call[0] else [])
    )
    assert found_sp_address

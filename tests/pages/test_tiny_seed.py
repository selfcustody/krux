from ..shared_mocks import MockPrinter, mock_context


def create_ctx(mocker, btn_seq, wallet, printer, touch_seq=None):
    """Helper to create mocked context obj"""
    ctx = mock_context(mocker)
    ctx.power_manager.battery_charge_remaining.return_value = 1
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=btn_seq)

    ctx.wallet = wallet
    ctx.printer = printer

    if touch_seq:
        ctx.input.touch = mocker.MagicMock(
            current_index=mocker.MagicMock(side_effect=touch_seq)
        )
    return ctx


def test_load_tiny_seed(amigo_tft, mocker):
    from krux.pages.tiny_seed import TinySeed
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH
    from krux.wallet import Wallet
    from krux.key import Key
    from embit.networks import NETWORKS

    BTN_SEQUENCE = [
        BUTTON_ENTER,
        BUTTON_ENTER,
        BUTTON_ENTER,
    ]
    TEST_24_WORD_MNEMONIC = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"
    # Amount of rectangles filled for this mnemonic + menus
    FILLED_RECTANGLES = 189
    SINGLEKEY_24_WORD_KEY = Key(TEST_24_WORD_MNEMONIC, False, NETWORKS["main"])
    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(SINGLEKEY_24_WORD_KEY), MockPrinter())
    tiny_seed = TinySeed(ctx)
    tiny_seed.export()

    assert ctx.display.fill_rectangle.call_count == FILLED_RECTANGLES

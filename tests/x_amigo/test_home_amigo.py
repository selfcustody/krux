import sys
from ..shared_mocks import *
from krux.display import DEFAULT_PADDING
from krux.key import Key
from krux.input import BUTTON_TOUCH, BUTTON_PAGE, BUTTON_TOUCH
from krux.qr import FORMAT_PMOFN, FORMAT_NONE
from embit.networks import NETWORKS


TEST_12_WORD_MNEMONIC = (
    "olympic term tissue route sense program under choose bean emerge velvet absurd"
)
TEST_24_WORD_MNEMONIC = "brush badge sing still venue panther kitchen please help panel bundle excess sign couch stove increase human once effort candy goat top tiny major"

SINGLEKEY_12_WORD_KEY = Key(TEST_12_WORD_MNEMONIC, False, NETWORKS["main"])
SINGLEKEY_24_WORD_KEY = Key(TEST_24_WORD_MNEMONIC, False, NETWORKS["main"])
MULTISIG_12_WORD_KEY = Key(TEST_12_WORD_MNEMONIC, True, NETWORKS["main"])


def test_mnemonic_touch(mocker):
    import board
    from krux.pages.home import Home
    from krux.wallet import Wallet

    cases = [
        # No print prompt
        (Wallet(SINGLEKEY_12_WORD_KEY), None, [BUTTON_TOUCH]),
        (Wallet(SINGLEKEY_24_WORD_KEY), None, [BUTTON_TOUCH]),
        # Print
        (Wallet(SINGLEKEY_12_WORD_KEY), MockPrinter(), [BUTTON_TOUCH, BUTTON_TOUCH]),
        (
            Wallet(SINGLEKEY_24_WORD_KEY),
            MockPrinter(),
            [BUTTON_TOUCH, BUTTON_TOUCH],
        ),
        # Decline to print
        (Wallet(SINGLEKEY_12_WORD_KEY), MockPrinter(), [BUTTON_TOUCH, BUTTON_PAGE]),
        (
            Wallet(SINGLEKEY_24_WORD_KEY),
            MockPrinter(),
            [BUTTON_TOUCH, BUTTON_TOUCH],
        ),
    ]
    for case in cases:
        ctx = mock.MagicMock(
            input=mock.MagicMock(wait_for_button=mock.MagicMock(side_effect=case[2])),
            wallet=case[0],
            printer=case[1],
        )
        home = Home(ctx)

        mocker.spy(home, "display_mnemonic")
        mocker.spy(home, "print_qr_prompt")

        home.mnemonic()

        home.display_mnemonic.assert_called_with(ctx.wallet.key.mnemonic)
        home.print_qr_prompt.assert_called_with(ctx.wallet.key.mnemonic, FORMAT_NONE)

        assert ctx.input.wait_for_button.call_count == len(case[2])
    assert board.config["lcd"]["invert"] == 1

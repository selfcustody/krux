from ...shared_mocks import MockPrinter
from ..test_home import tdata, create_ctx


def test_wallet(mocker, m5stickv, tdata):
    from krux.pages.home_pages.wallet_descriptor import WalletDescriptor
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_PMOFN

    cases = [
        # 0 Don't load
        (
            False,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            None,
            [BUTTON_PAGE],
        ),
        # 1 Load, good data, accept
        (
            False,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_ENTER],
        ),
        # 2 Load, good data, decline
        (
            False,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_PAGE],
        ),
        # 3 Load, bad capture
        (False, tdata.SINGLESIG_12_WORD_KEY, None, None, [BUTTON_ENTER]),
        # 4 Load, bad wallet data
        (False, tdata.SINGLESIG_12_WORD_KEY, "{}", None, [BUTTON_ENTER, BUTTON_ENTER]),
        # 5 No print prompt
        (
            True,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            None,
            [BUTTON_ENTER],
        ),
        # 6 Print
        (
            True,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_ENTER],
        ),
        # 7 Decline to print
        (
            True,
            tdata.SINGLESIG_12_WORD_KEY,
            tdata.SPECTER_SINGLESIG_WALLET_DATA,
            MockPrinter(),
            [BUTTON_ENTER, BUTTON_PAGE],
        ),
        # 8 Multisig wallet, no print prompt
        (
            True,
            tdata.MULTISIG_12_WORD_KEY,
            tdata.SPECTER_MULTISIG_WALLET_DATA,
            None,
            [BUTTON_ENTER, BUTTON_ENTER, BUTTON_ENTER],
        ),
    ]

    num = 0
    for case in cases:
        print("case: %d" % num)
        num = num + 1
        wallet = Wallet(case[1])
        if case[0]:
            wallet.load(case[2], FORMAT_PMOFN)

        ctx = create_ctx(mocker, case[4], wallet, case[3])
        wallet_desciptor = WalletDescriptor(ctx)
        mocker.patch.object(
            wallet_desciptor, "capture_qr_code", new=lambda: (case[2], FORMAT_PMOFN)
        )
        mocker.patch.object(
            wallet_desciptor,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(wallet_desciptor, "capture_qr_code")
        mocker.spy(wallet_desciptor, "display_wallet")

        wallet_desciptor.wallet()

        if case[0]:
            wallet_desciptor.display_wallet.assert_called_once()
        else:
            if case[4][0] == BUTTON_ENTER:
                wallet_desciptor.capture_qr_code.assert_called_once()
                if case[2] is not None and case[2] != "{}":
                    wallet_desciptor.display_wallet.assert_called_once()
        assert ctx.input.wait_for_button.call_count == len(case[4])

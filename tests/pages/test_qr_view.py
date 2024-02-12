from ..shared_mocks import mock_context
from .test_home import create_ctx, tdata


def test_load_qr_view(amigo_tft, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT

    BTN_SEQUENCE = [
        SWIPE_LEFT,  # lines mode
        BUTTON_ENTER,  # move to line 1
        SWIPE_LEFT,  # zoomed regions mode
        SWIPE_LEFT,  # regions mode
        SWIPE_LEFT,  # grided mode
        SWIPE_LEFT,  # back to standard mode
        SWIPE_LEFT,  # lines mode again
        SWIPE_RIGHT,  # back to standard mode
        BUTTON_ENTER,  # leave
        BUTTON_PAGE_PREV,  # move to Back to Main Menu
        BUTTON_ENTER,  # confirm
    ]

    ctx = mock_context(mocker)
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=BTN_SEQUENCE)
    data = "test code"
    seed_qr_view = SeedQRView(ctx, data=data, title="Test QR Code")
    seed_qr_view.display_qr()
    assert ctx.display.draw_qr_code.call_count == 8


def test_load_seed_qr(amigo_tft, mocker, tdata):
    from krux.pages.qr_view import SeedQRView
    from krux.themes import WHITE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT
    from krux.wallet import Wallet

    BTN_SEQUENCE = [
        SWIPE_LEFT,  # lines mode
        BUTTON_ENTER,  # move to line 1
        SWIPE_LEFT,  # zoomed regions mode
        SWIPE_LEFT,  # regions mode
        SWIPE_LEFT,  # grided mode
        SWIPE_LEFT,  # back to standard mode
        SWIPE_LEFT,  # lines mode again
        SWIPE_RIGHT,  # back to standard mode
        BUTTON_ENTER,  # leave
        BUTTON_PAGE_PREV,  # move to Back to Main Menu
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY), None)
    seed_qr_view = SeedQRView(ctx, binary=False)
    seed_qr_view.display_qr()
    assert ctx.display.draw_qr_code.call_count == 8
    ctx.display.draw_qr_code.assert_called_with(
        0,
        # Standard SeedQR
        bytearray(
            b"\x7fT\xc8?\xa8P\nvA$\xdd\xae\xdb\xab\xdb%\x84t\x83\xb6\xa3\xe0_U\xf5\x07p\x0e\x00\xdf\xbb\xb7*\xb4\x0ei.Q\x96\xa4\x07H\xcc\xa8\xe4z\xeb.\xb2\x94\xa2s%\xe1\xca\x85\xe6\xc8V\xa6\xb7\xaeGKi\x16A\xd2\xbcX(\x18Pwz\xff\x00\xfa0\xea\xdf%V\n\xb2\xa2H]\xa1\xf7\xaf+\x0bUv\xc5\x16\xbd\xa0'\xfe\xf4\x17zr\x00"
        ),
    )


def test_loop_through_regions(amigo_tft, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT
    from ..test_encryption import CBC_ENCRYPTED_QR

    BTN_SEQUENCE = (
        [
            SWIPE_LEFT,  # lines mode
            BUTTON_ENTER,  # move to line 1
            SWIPE_LEFT,  # zoomed regions mode
            SWIPE_LEFT,  # regions mode
        ]
        + [BUTTON_ENTER] * 49  # Loop through regions and return to A1
        + [
            SWIPE_LEFT,  # grided mode
            SWIPE_LEFT,  # back to standard mode
            SWIPE_LEFT,  # lines mode again
            SWIPE_RIGHT,  # back to standard mode
            BUTTON_ENTER,  # leave
            BUTTON_PAGE_PREV,  # move to Back to Main Menu
            BUTTON_ENTER,  # confirm
        ]
    )

    ctx = mock_context(mocker)
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=BTN_SEQUENCE)
    data = CBC_ENCRYPTED_QR  # Will produce an QR code with 48 regions, max=G7
    seed_qr_view = SeedQRView(ctx, data=data, title="Test QR Code")
    seed_qr_view.display_qr()
    assert ctx.display.draw_qr_code.call_count == 57

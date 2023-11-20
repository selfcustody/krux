from ..shared_mocks import mock_context


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

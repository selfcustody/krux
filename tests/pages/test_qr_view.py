from ..shared_mocks import mock_context


def create_ctx(mocker, btn_seq, touch_seq=None):
    """Helper to create mocked context obj"""
    ctx = mock_context(mocker)
    ctx.power_manager.battery_charge_remaining.return_value = 1
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=btn_seq)

    if touch_seq:
        ctx.input.touch = mocker.MagicMock(
            current_index=mocker.MagicMock(side_effect=touch_seq)
        )
    return ctx


def test_load_qr_view(amigo_tft, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, SWIPE_LEFT, SWIPE_RIGHT
    import qrcode

    BTN_SEQUENCE = (
        [SWIPE_LEFT]  # lines mode
        + [BUTTON_ENTER]  # move to line 1
        + [SWIPE_LEFT]  # zoomed regions mode
        + [SWIPE_LEFT]  # regions mode
        + [SWIPE_LEFT]  # grided mode
        + [SWIPE_LEFT]  # back to standard mode
        + [SWIPE_LEFT]  # lines mode again
        + [SWIPE_RIGHT]  # back to standard mode
        + [BUTTON_ENTER]  # leave
        + [BUTTON_ENTER]  # confirm
        + [BUTTON_ENTER]  # confirm
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    code = qrcode.encode_to_string("test code")
    seed_qr_view = SeedQRView(ctx, code=code, title="Test QR Code")
    seed_qr_view.display_seed_qr()
    assert ctx.display.draw_qr_code.call_count == 8

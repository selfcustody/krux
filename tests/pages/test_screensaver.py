from ..shared_mocks import mock_context
from .test_login import create_ctx


def test_screensaver_m5stickv(m5stickv, mocker):
    """Test whether the screensaver is animating and changing color over time"""
    from krux.themes import theme
    from krux.input import BUTTON_ENTER, QR_ANIM_PERIOD
    from krux.display import SPLASH
    from krux.pages.screensaver import ScreenSaver
    import time

    SCREENSAVER_ANIMATION_TIME = QR_ANIM_PERIOD

    # a sequence of events to simulate users waiting and after some time press BUTTON_ENTER
    btn_seq = []
    time_seq = []
    tmp = SCREENSAVER_ANIMATION_TIME + 1
    for _ in range(28):
        time_seq.append(tmp)
        time_seq.append(tmp)
        tmp += SCREENSAVER_ANIMATION_TIME + 1
        btn_seq.append(None)

    time_seq.append(tmp)
    time_seq.append(tmp)
    btn_seq.append(BUTTON_ENTER)

    ctx = create_ctx(mocker, btn_seq)
    time.ticks_ms = mocker.MagicMock(side_effect=time_seq)

    screen_saver = ScreenSaver(ctx)
    screen_saver.start()

    ctx.display.draw_hcentered_text.assert_any_call(
        SPLASH[10], 182, theme.fg_color, theme.bg_color
    )
    ctx.display.draw_hcentered_text.assert_any_call(
        SPLASH[5], 112, theme.bg_color, theme.fg_color
    )
    ctx.input.wait_for_button.assert_called()

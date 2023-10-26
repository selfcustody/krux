from .shared_mocks import get_mock_open


def mock_modules(mocker):
    mocker.patch("krux.context.logger", new=mocker.MagicMock())
    mocker.patch("krux.context.Display", new=mocker.MagicMock())
    mocker.patch("krux.context.Camera", new=mocker.MagicMock())
    mocker.patch("krux.context.Light", new=mocker.MagicMock())
    mocker.patch("krux.context.Input", new=mocker.MagicMock())


def test_init(mocker, m5stickv):
    mock_modules(mocker)
    from krux.context import Context

    c = Context()

    assert isinstance(c, Context)


def test_clear(mocker, m5stickv):
    mock_modules(mocker)
    from krux.context import Context

    c = Context()

    c.clear()

    assert c.wallet is None


def test_log(mocker, m5stickv):
    mock_modules(mocker)
    import krux
    from krux.context import Context

    c = Context()

    assert c.log == krux.context.logger


def test_clear_clears_printer(mocker, m5stickv):
    mock_modules(mocker)
    from krux.context import Context
    from krux.printers import Printer

    c = Context()
    c.printer = mocker.MagicMock(clear=mocker.MagicMock())

    c.clear()

    assert c.wallet is None
    c.printer.clear.assert_called()


def test_screensaver(mocker, m5stickv):
    """Test whether the screensaver is animating and changing color over time"""
    mock_modules(mocker)
    from krux.context import Context, SCREENSAVER_ANIMATION_TIME
    from krux.themes import theme
    from krux.input import BUTTON_ENTER
    import time

    logo = """
        ██
        ██
        ██
        ██████
        ██
        ██  ██
        ██ ██
        ████ 
        ██ ██
        ██  ██
        ██   ██
"""[
        1:-1
    ].split(
        "\n"
    )
    c = Context(logo)

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

    c.input.wait_for_button = mocker.MagicMock(side_effect=btn_seq)
    time.ticks_ms = mocker.MagicMock(side_effect=time_seq)

    c.screensaver()

    c.display.draw_line_hcentered_with_fullw_bg.assert_any_call(
        logo[10], 10, theme.fg_color, theme.bg_color
    )
    c.display.draw_line_hcentered_with_fullw_bg.assert_any_call(
        logo[5], 5, theme.bg_color, theme.fg_color
    )
    c.input.wait_for_button.assert_called()

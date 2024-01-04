# TODO: cleanup .shared_mocks.get_mock_open?
# tests go well without calling it
# pylint calls warning `unused-import`
# W0611: Unused get_mock_open imported from shared_mocks (unused-import)
# from .shared_mocks import get_mock_open


def mock_modules(mocker):
    """
    Utility method to patch :module:`krux.context` classes:

    - :class:`krux.context.logger`
    - :class:`krux.context.Display`
    - :class:`krux.context.Input`
    - :class:`krux.context.Camera`
    - :class:`krux.context.Light`

    :param mocker
    """
    mocker.patch("krux.context.logger", new=mocker.MagicMock())
    mocker.patch("krux.context.Display", new=mocker.MagicMock())
    mocker.patch("krux.context.Camera", new=mocker.MagicMock())
    mocker.patch("krux.context.Light", new=mocker.MagicMock())
    mocker.patch("krux.context.Input", new=mocker.MagicMock())


# pylint: disable=unused-argument
def test_init(mocker, m5stickv):
    """
    Test the initialization of :class:`krux.context.Context`
    
    :param mocker: the mocker
    :param m5stickv: the device
    """
    mock_modules(mocker)
    from krux.context import Context

    # Avoid pylint `invalid-name` warning
    # 0103: Variable name "c" doesn't conform to snake_case naming style
    context = Context()

    assert isinstance(context, Context)


# pylint: disable=unused-argument
def test_clear(mocker, m5stickv):
    """
    Test the cleanup of :class:`krux.context.Context`
    
    :param mocker: the mocker
    :param m5stickv: the device
    """
    mock_modules(mocker)
    from krux.context import Context

    # Avoid pylint `invalid-name` warning
    # 0103: Variable name "c" doesn't conform to snake_case naming style
    context = Context()

    context.clear()

    assert context.wallet is None


# pylint: disable=unused-argument
def test_log(mocker, m5stickv):
    """
    Test the initialization of :class:`krux.context.logger`
    inside the :class:`krux.context.Context`
    
    :param mocker: the mocker
    :param m5stickv: the device
    """
    mock_modules(mocker)
    import krux
    from krux.context import Context

    # Avoid pylint `invalid-name` warning
    # 0103: Variable name "c" doesn't conform to snake_case naming style
    context = Context()

    assert context.log == krux.context.logger


# pylint: disable=unused-argument
def test_clear_clears_printer(mocker, m5stickv):
    """
    Test the initialization and cleanup of :class:`krux.context.Printer`
    inside the :class:`krux.context.Context`


    :param mocker: the mocker
    :param m5stickv: the device
    """
    mock_modules(mocker)
    from krux.context import Context

    # TODO: cleanup krux.printer.Printer?
    # tests go well without calling it
    # pylint calls warning `unused-import`
    # W0611: Unused Printer imported from krux.printers (unused-import)
    # from krux.printers import Printer

    # Avoid pylint `invalid-name` warning
    # 0103: Variable name "c" doesn't conform to snake_case naming style
    context = Context()
    context.printer = mocker.MagicMock(clear=mocker.MagicMock())

    context.clear()

    assert context.wallet is None
    context.printer.clear.assert_called()


# pylint: disable=unused-argument
def test_screensaver(mocker, m5stickv):
    """
    Test whether the screensaver is animating and changing color over time
    inside the :class:`krux.context.Context`

    :param mocker: the mocker
    :param m5stickv: the device
    """
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

    # Avoid pylint `invalid-name` warning
    # 0103: Variable name "c" doesn't conform to snake_case naming style
    context = Context(logo)

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

    context.input.wait_for_button = mocker.MagicMock(side_effect=btn_seq)
    time.ticks_ms = mocker.MagicMock(side_effect=time_seq)

    context.screensaver()

    # TODO: check if the pylint warn is because the method is mocked
    # pylint throws
    # E1101: Method 'draw_line_hcentered_with_fullw_bg' has no 'assert_any_call' member (no-member)
    # pylint: disable=no-member
    context.display.draw_line_hcentered_with_fullw_bg.assert_any_call(
        logo[10], 10, theme.fg_color, theme.bg_color
    )

    # pylint: disable=no-member
    context.display.draw_line_hcentered_with_fullw_bg.assert_any_call(
        logo[5], 5, theme.bg_color, theme.fg_color
    )

    # pylint: disable=no-member
    context.input.wait_for_button.assert_called()

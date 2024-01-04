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
    mocker.patch("krux.context.Input", new=mocker.MagicMock())
    mocker.patch("krux.context.Camera", new=mocker.MagicMock())
    mocker.patch("krux.context.Light", new=mocker.MagicMock())


# pylint: disable=unused-argument
def test_init(mocker, m5stickv):
    """
    Test the initialization of :class:`krux.context.Context`
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

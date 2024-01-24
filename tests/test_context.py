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

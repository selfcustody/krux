from .shared_mocks import get_mock_open


def mock_modules(mocker):
    mocker.patch("krux.context.logger", new=mocker.MagicMock())
    mocker.patch("krux.context.Display", new=mocker.MagicMock())
    mocker.patch("krux.context.Input", new=mocker.MagicMock())
    mocker.patch("krux.context.Camera", new=mocker.MagicMock())
    mocker.patch("krux.context.Light", new=mocker.MagicMock())


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


def test_sd_card(mocker, m5stickv):
    mock_modules(mocker)
    from krux.context import Context

    c = Context()

    mocker.patch("os.remove", new=mocker.MagicMock())
    mocker.patch(
        "builtins.open",
        new=get_mock_open(
            {
                "/sd/.chkmnt": "",
            }
        ),
    )

    assert c.sd_card is not None

    mocker.patch("builtins.open", new=mocker.MagicMock(side_effect=Exception))

    assert c.sd_card is None

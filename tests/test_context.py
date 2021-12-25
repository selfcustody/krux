from .shared_mocks import *

def mock_modules(mocker):
    mocker.patch('krux.context.Logger', new=mock.MagicMock())
    mocker.patch('krux.context.Settings', new=mock.MagicMock())
    mocker.patch('krux.context.Display', new=mock.MagicMock())
    mocker.patch('krux.context.Input', new=mock.MagicMock())
    mocker.patch('krux.context.Camera', new=mock.MagicMock())
    mocker.patch('krux.context.Light', new=mock.MagicMock())
    mocker.patch('krux.printers.printer.Printer', new=mock.MagicMock())

def test_init(mocker):
    mock_modules(mocker)
    from krux.context import Context

    c = Context()

    assert isinstance(c, Context)

def test_clear(mocker):
    mock_modules(mocker)
    from krux.context import Context
    c = Context()

    c.clear()
    
    assert c.wallet is None
    
def test_clear_clears_printer(mocker):
    mock_modules(mocker)
    from krux.context import Context
    from krux.printers.printer import Printer
    c = Context()
    c.printer = mock.MagicMock(clear=mock.MagicMock())

    c.clear()
    
    assert c.wallet is None
    c.printer.clear.assert_called()

from .shared_mocks import *
from unittest import mock

@mock.patch('krux.context.Logger', new=mock.MagicMock())
@mock.patch('krux.context.Settings', new=mock.MagicMock())
@mock.patch('krux.context.Display', new=mock.MagicMock())
@mock.patch('krux.context.Input', new=mock.MagicMock())
@mock.patch('krux.context.Camera', new=mock.MagicMock())
@mock.patch('krux.context.Light', new=mock.MagicMock())
def test_init():
    from krux.context import Context

    c = Context()

    assert isinstance(c, Context)

@mock.patch('krux.context.Logger', new=mock.MagicMock())
@mock.patch('krux.context.Settings', new=mock.MagicMock())
@mock.patch('krux.context.Display', new=mock.MagicMock())
@mock.patch('krux.context.Input', new=mock.MagicMock())
@mock.patch('krux.context.Camera', new=mock.MagicMock())
@mock.patch('krux.context.Light', new=mock.MagicMock())
def test_clear():
    from krux.context import Context
    c = Context()

    c.clear()
    
    assert c.wallet is None
    
@mock.patch('krux.context.Logger', new=mock.MagicMock())
@mock.patch('krux.context.Settings', new=mock.MagicMock())
@mock.patch('krux.context.Display', new=mock.MagicMock())
@mock.patch('krux.context.Input', new=mock.MagicMock())
@mock.patch('krux.context.Camera', new=mock.MagicMock())
@mock.patch('krux.context.Light', new=mock.MagicMock())
@mock.patch('krux.printer.Printer', new=mock.MagicMock())
def test_clear_clears_printer(mocker):
    from krux.context import Context
    from krux.printer import Printer
    c = Context()
    c.printer = Printer(1, 1)
    mocker.spy(c.printer, 'clear')

    c.clear()
    
    assert c.wallet is None
    c.printer.clear.assert_called()

from .shared_mocks import *

def test_init(mocker):
    mocker.patch('krux.display.lcd', new=mock.MagicMock())
    import krux
    from krux.display import Display
    import board
    mocker.spy(Display, 'initialize_lcd')

    d = Display()

    assert isinstance(d, Display)
    d.initialize_lcd.assert_called()
    
    krux.display.lcd.init.assert_called_once()
    assert 'type' in krux.display.lcd.init.call_args.kwargs
    assert (
        krux.display.lcd.init.call_args.kwargs['type'] ==
        board.config['lcd']['lcd_type']
    )

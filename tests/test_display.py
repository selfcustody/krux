from .shared_mocks import *

def test_init(mocker):
    import board
    import lcd
    from krux.display import Display
    mocker.spy(Display, 'initialize_lcd')

    d = Display()

    assert isinstance(d, Display)
    d.initialize_lcd.assert_called()
    
    lcd.init.assert_called_once()
    assert 'type' in lcd.init.call_args.kwargs
    assert (
        lcd.init.call_args.kwargs['type'] ==
        board.config['lcd']['lcd_type']
    )

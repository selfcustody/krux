from .shared_mocks import *

def mock_modules(mocker):
    mocker.patch('krux.light.fm.register', new=mock.MagicMock())
    mocker.patch('krux.light.GPIO', new=mock.MagicMock())
    
def test_init(mocker):
    mock_modules(mocker)
    import krux
    from krux.light import Light
    import board
    mocker.spy(Light, 'turn_off')

    light = Light()

    assert isinstance(light, Light)
    krux.light.fm.register.assert_called_with(board.config['krux.pins']['LED_W'], mock.ANY)
    assert (
        krux.light.fm.register.call_args.args[1]._extract_mock_name() ==
        'mock.fm.fpioa.GPIO3'
    )
    assert light.led_w is not None
    krux.light.GPIO.assert_called()
    assert (
        krux.light.GPIO.call_args.args[0]._extract_mock_name() ==
        'mock.GPIO3'
    )
    light.turn_off.assert_called()

def test_is_on(mocker):
    mock_modules(mocker)
    from krux.light import Light
    light = Light()
    mocker.spy(light.led_w, 'value')

    on = light.is_on()

    assert isinstance(on, bool)
    light.led_w.value.assert_called_with()
    
def test_turn_on(mocker):
    mock_modules(mocker)
    from krux.light import Light
    light = Light()
    mocker.spy(light.led_w, 'value')

    light.turn_on()

    light.led_w.value.assert_called_with(0)

def test_turn_off(mocker):
    mock_modules(mocker)
    from krux.light import Light
    light = Light()
    mocker.spy(light.led_w, 'value')

    light.turn_off()

    light.led_w.value.assert_called_with(1)

def test_toggle_from_off(mocker):
    mock_modules(mocker)
    from krux.light import Light
    light = Light()
    mocker.patch.object(light, 'is_on', new=lambda: False)
    mocker.spy(light, 'turn_on')

    light.toggle()

    light.turn_on.assert_called()

def test_toggle_from_on(mocker):
    mock_modules(mocker)
    from krux.light import Light
    light = Light()
    mocker.patch.object(light, 'is_on', new=lambda: True)
    mocker.spy(light, 'turn_off')

    light.toggle()

    light.turn_off.assert_called()

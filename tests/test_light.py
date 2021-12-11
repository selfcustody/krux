from .shared_mocks import *

def test_init(mocker):
    import fpioa_manager
    import board
    import Maix
    from krux.light import Light
    mocker.spy(Light, 'turn_off')

    light = Light()

    assert isinstance(light, Light)
    fpioa_manager.fm.register.assert_called_once()
    assert (
        fpioa_manager.fm.register.call_args.args[0] ==
        board.config['krux.pins']['LED_W']
    )
    assert (
        fpioa_manager.fm.register.call_args.args[1]._extract_mock_name() ==
        'mock.fm.fpioa.GPIO3'
    )
    assert light.led_w is not None
    Maix.GPIO.assert_called()
    assert (
        Maix.GPIO.call_args.args[0]._extract_mock_name() ==
        'mock.GPIO.GPIO3'
    )
    light.turn_off.assert_called()

def test_is_on(mocker):
    from krux.light import Light
    light = Light()
    mocker.spy(light.led_w, 'value')

    on = light.is_on()

    assert isinstance(on, bool)
    light.led_w.value.assert_called_with()
    
def test_turn_on(mocker):
    from krux.light import Light
    light = Light()
    mocker.spy(light.led_w, 'value')

    light.turn_on()

    light.led_w.value.assert_called_with(0)

def test_turn_off(mocker):
    from krux.light import Light
    light = Light()
    mocker.spy(light.led_w, 'value')

    light.turn_off()

    light.led_w.value.assert_called_with(1)

def test_toggle_from_off(mocker):
    from krux.light import Light
    light = Light()
    mocker.patch.object(light, 'is_on', new=lambda: False)
    mocker.spy(light, 'turn_on')

    light.toggle()

    light.turn_on.assert_called()

def test_toggle_from_on(mocker):
    from krux.light import Light
    light = Light()
    mocker.patch.object(light, 'is_on', new=lambda: True)
    mocker.spy(light, 'turn_off')

    light.toggle()

    light.turn_off.assert_called()

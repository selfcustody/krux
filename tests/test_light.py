def mock_modules(mocker):
    mocker.patch("krux.light.fm.register", new=mocker.MagicMock())
    mocker.patch("krux.light.GPIO", new=mocker.MagicMock())


def test_init(mocker, m5stickv):
    mock_modules(mocker)
    import krux
    from krux.light import Light
    import board

    mocker.spy(Light, "turn_off")

    light = Light()

    assert isinstance(light, Light)
    krux.light.fm.register.assert_called_with(
        board.config["krux"]["pins"]["LED_W"], mocker.ANY
    )
    assert (
        krux.light.fm.register.call_args.args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIO3"
    )
    assert light.circuit is not None
    krux.light.GPIO.assert_called()
    assert krux.light.GPIO.call_args.args[0]._extract_mock_name() == "mock.GPIO3"
    light.turn_off.assert_called()


def test_turn_on(mocker, m5stickv):
    mock_modules(mocker)
    from krux.light import Light

    light = Light()
    mocker.spy(light.circuit, "value")

    light.turn_on()

    light.circuit.value.assert_called_with(0)


def test_turn_off(mocker, m5stickv):
    mock_modules(mocker)
    from krux.light import Light

    light = Light()
    mocker.spy(light.circuit, "value")

    light.turn_off()

    light.circuit.value.assert_called_with(1)

import pytest


def test_init(mocker, m5stickv):
    from krux.camera import Camera

    c = Camera()
    c.initialize_sensor()

    assert isinstance(c, Camera)


def test_initialize_sensor(mocker, m5stickv):
    import krux
    from krux.camera import Camera, OV7740_ID

    mocker.patch("krux.camera.sensor.get_id", lambda: OV7740_ID)

    c = Camera()

    mocker.spy(c, "config_ov_7740")

    c.initialize_sensor()

    c.config_ov_7740.assert_called()
    krux.camera.sensor.reset.assert_called()
    krux.camera.sensor.set_pixformat.assert_called()
    assert (
        krux.camera.sensor.set_pixformat.call_args.args[0]._extract_mock_name()
        == "mock.RGB565"
    )
    krux.camera.sensor.set_framesize.assert_called()
    assert (
        krux.camera.sensor.set_framesize.call_args.args[0]._extract_mock_name()
        == "mock.QVGA"
    )


def test_initialize_sensor_ov2640(mocker, m5stickv):
    import krux
    from krux.camera import Camera, OV2640_ID

    mocker.patch("krux.camera.sensor.get_id", lambda: OV2640_ID)

    c = Camera()

    mocker.spy(c, "config_ov_2640")

    c.initialize_sensor()

    c.config_ov_2640.assert_called()

    krux.camera.sensor.reset.assert_called()
    krux.camera.sensor.set_pixformat.assert_called()
    assert (
        krux.camera.sensor.set_pixformat.call_args.args[0]._extract_mock_name()
        == "mock.RGB565"
    )
    krux.camera.sensor.set_framesize.assert_called()
    assert (
        krux.camera.sensor.set_framesize.call_args.args[0]._extract_mock_name()
        == "mock.QVGA"
    )
    krux.camera.sensor.set_vflip.assert_called()

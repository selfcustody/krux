import pytest


def test_init(mocker, m5stickv):
    from krux.camera import Camera

    c = Camera()
    c.initialize_sensor()

    assert isinstance(c, Camera)


def test_initialize_sensors(mocker, m5stickv):
    import krux
    from krux.camera import Camera, OV7740_ID, OV2640_ID, GC0328_ID, GC2145_ID

    SENSORS_LIST = [
        (OV7740_ID, "config_ov_7740"),
        (OV2640_ID, "config_ov_2640"),
        (GC0328_ID, None),
        (GC2145_ID, "config_gc_2145"),
    ]

    for sensor_id, config_method in SENSORS_LIST:
        mocker.patch("krux.camera.sensor.get_id", lambda: sensor_id)
        c = Camera()
        if config_method:
            mocker.spy(c, config_method)
        c.initialize_sensor()
        if config_method:
            getattr(c, config_method).assert_called()

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


def test_toggle_antiglare(mocker, m5stickv):
    import krux
    from krux.camera import Camera, OV7740_ID, OV2640_ID, GC0328_ID, GC2145_ID

    SENSORS_LIST = [OV7740_ID, OV2640_ID, GC0328_ID, GC2145_ID]

    for sensor_id in SENSORS_LIST:
        mocker.patch("krux.camera.sensor.get_id", lambda: sensor_id)
        c = Camera()
        mocker.spy(c, "enable_antiglare")
        mocker.spy(c, "disable_antiglare")
        mocker.spy(c, "has_antiglare")
        c.initialize_sensor()
        if c.has_antiglare():
            assert c.antiglare_enabled == False
            c.enable_antiglare.assert_not_called()
            c.toggle_antiglare()
            c.enable_antiglare.assert_called()
            assert c.antiglare_enabled == True
            c.toggle_antiglare()
            c.enable_antiglare.assert_called()
            c.disable_antiglare.assert_called()
            assert c.antiglare_enabled == False
        else:
            c.enable_antiglare.assert_not_called()
            c.disable_antiglare.assert_not_called()

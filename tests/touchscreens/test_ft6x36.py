def test_init(mocker, m5stickv):
    from krux.touchscreens.ft6x36 import FT6X36

    t = FT6X36()

    assert isinstance(t, FT6X36)


def test_point_read(mocker, m5stickv):
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    # four bytes
    reg_point = [0x00, 0x09, 0x00, 0x09]
    point = (0x09, 0x09)
    mocker.patch("krux.i2c.i2c_bus.readfrom_mem", side_effect=([0x01], reg_point))
    data = touch.current_point()
    assert data == point


def test_gesture_discarded(mocker, m5stickv):
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    # four bytes
    reg_point = [0x00, 0x09, 0x00, 0x09]
    mocker.patch("krux.i2c.i2c_bus.readfrom_mem", side_effect=([0x02], reg_point))
    data = touch.current_point()
    assert data is None


def test_point_read_error(mocker, m5stickv):
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    # four bytes
    e = Exception("mocked error")
    mocker.patch("krux.i2c.i2c_bus.readfrom_mem", side_effect=([0x01], e))
    data = touch.current_point()
    assert data == e

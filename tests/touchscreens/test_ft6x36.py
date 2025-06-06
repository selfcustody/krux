import pytest


@pytest.fixture
def mock_ft6x36(mocker):
    from krux.touchscreens.ft6x36 import fm, touch_control, TD_STATUS, PN_XH

    mocker.patch.object(fm, "register")
    mock_gpio = mocker.MagicMock()
    mocker.patch("Maix.GPIO", return_value=mock_gpio)

    def fake_activate_irq(irq_pin):
        touch_control.touch_irq_pin = mock_gpio

    def fake_write_reg(reg_addr, buf):
        pass

    def fake_read_reg(reg_addr, buf_len):
        if reg_addr == TD_STATUS:
            # single touch
            return [0x1]

        elif reg_addr == PN_XH:
            # Mock coordinates (x, y)
            return [0x01, 0x40, 0x00, 0xF0]

        return [0x00]

    mocker.patch.object(touch_control, "write_reg", fake_write_reg)
    mocker.patch.object(touch_control, "read_reg", fake_read_reg)
    mocker.patch.object(touch_control, "activate_irq", fake_activate_irq)

    touch_control.event_flag = False
    touch_control.irq_point = None
    mocker.spy(touch_control, "trigger_event")

    return touch_control


def test_handler(mocker, amigo, mock_ft6x36):
    from krux.touchscreens.ft6x36 import __handler__

    # The pin numbers are arbitrary, just for testing
    # and they will be ignored in the handler
    calls = []
    for pin in [10, 11, 12]:
        __handler__(pin)
        calls.append(mocker.call())

    mock_ft6x36.trigger_event.assert_has_calls(calls)
    assert mock_ft6x36.event_flag
    assert mock_ft6x36.irq_point is not None

    # get the event event flag and cleans it
    assert mock_ft6x36.event()
    assert not mock_ft6x36.event_flag


def test_init(mocker, amigo):
    from krux.touchscreens.ft6x36 import FT6X36

    t = FT6X36()

    assert isinstance(t, FT6X36)


def test_point_not_read(mocker, dock):
    # Dock does not set i2c_bus because it does not
    # use I2C_SCL or I2C_SDA pins
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    data = touch.current_point()

    assert not data


def test_point_read(mocker, amigo):
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    # four bytes
    reg_point = [0x00, 0x09, 0x00, 0x09]
    point = (0x09, 0x09)
    mocker.patch("krux.i2c.i2c_bus.readfrom_mem", side_effect=([0x01], reg_point))
    data = touch.current_point()
    assert data == point


def test_gesture_discarded(mocker, amigo):
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    # four bytes
    reg_point = [0x00, 0x09, 0x00, 0x09]
    mocker.patch("krux.i2c.i2c_bus.readfrom_mem", side_effect=([0x02], reg_point))
    data = touch.current_point()
    assert data is None


def test_point_read_error(mocker, amigo):
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    # four bytes
    e = Exception("mocked error")
    mocker.patch("krux.i2c.i2c_bus.readfrom_mem", side_effect=([0x01], e))
    data = touch.current_point()
    assert data == e

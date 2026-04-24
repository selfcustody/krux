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

    # Trigger the handler (pin number is arbitrary and ignored)
    __handler__(10)

    # Verify trigger_event was called
    mock_ft6x36.trigger_event.assert_called_once()

    # Verify event flag was set and point was captured
    assert mock_ft6x36.event_flag
    assert mock_ft6x36.irq_point is not None

    # Verify event() returns flag and clears it
    assert mock_ft6x36.event()
    assert not mock_ft6x36.event_flag


def test_init(mocker, amigo):
    from krux.touchscreens.ft6x36 import FT6X36, FT6X36_ADDR

    t = FT6X36()

    # Verify initial state
    assert t.touch_irq_pin is None
    assert t.event_flag is False
    assert t.irq_point is None
    assert t.addr == FT6X36_ADDR


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


@pytest.mark.parametrize(
    "touch_points,expected_result",
    [
        (0x00, None),  # No touch
        (0x01, (0x09, 0x09)),  # Single touch (valid)
        (0x02, None),  # Two touches (not supported)
        (0x03, None),  # Three touches (not supported)
    ],
)
def test_touch_point_counts(mocker, amigo, touch_points, expected_result):
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    reg_point = [0x00, 0x09, 0x00, 0x09]
    mocker.patch(
        "krux.i2c.i2c_bus.readfrom_mem", side_effect=([touch_points], reg_point)
    )
    data = touch.current_point()
    assert data == expected_result


def test_point_read_error(mocker, amigo):
    from krux.touchscreens.ft6x36 import FT6X36

    touch = FT6X36()
    e = Exception("mocked error")
    mocker.patch("krux.i2c.i2c_bus.readfrom_mem", side_effect=([0x01], e))
    data = touch.current_point()
    assert data is None


def test_activate_irq(mocker, amigo):
    from krux.touchscreens.ft6x36 import FT6X36, fm

    mock_fm_register = mocker.patch.object(fm, "register")
    mock_gpio = mocker.MagicMock()
    mocker.patch("Maix.GPIO", return_value=mock_gpio)

    touch = FT6X36()
    test_pin = 20

    # Before activation, IRQ pin should be None
    assert touch.touch_irq_pin is None

    touch.activate_irq(test_pin)

    # After activation, verify:
    # 1. Pin was registered with fpioa manager
    mock_fm_register.assert_called_with(test_pin, fm.fpioa.GPIOHS1)

    # 2. IRQ pin was configured
    assert touch.touch_irq_pin is not None


def test_threshold(mocker, amigo):
    from krux.touchscreens.ft6x36 import FT6X36, FT_ID_G_THGROUP

    mock_writeto = mocker.patch("krux.i2c.i2c_bus.writeto_mem")

    touch = FT6X36()
    test_threshold = 30

    touch.threshold(test_threshold)

    # Verify write_reg was called with correct threshold value
    # write_reg should have been called during __init__ and when setting threshold
    calls = mock_writeto.call_args_list
    # Find the call that sets our test threshold
    threshold_calls = [
        call
        for call in calls
        if call[0][1] == FT_ID_G_THGROUP and call[0][2] == test_threshold
    ]
    assert len(threshold_calls) >= 1

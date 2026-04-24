import pytest


@pytest.fixture
def mock_gt911(mocker):
    from krux.touchscreens.gt911 import (
        fm,
        touch_control,
        GT911_COORD_ADDR,
        GT911_PRODUCT_ID,
    )

    mocker.patch.object(fm, "register")
    mock_gpio = mocker.MagicMock()
    mocker.patch("Maix.GPIO", return_value=mock_gpio)
    mocker.patch("time.sleep_ms")  # Mock sleep to avoid delays in tests

    def fake_activate(irq_pin, res_pin):
        touch_control.irq_pin = mock_gpio
        touch_control.reset_pin = mock_gpio

    def fake_write_reg(reg_addr, buf):
        pass

    def fake_read_reg(reg_addr, buf_len):
        if reg_addr == GT911_PRODUCT_ID:
            # Mock product ID (4 bytes: "911")
            return [0x39, 0x31, 0x31, 0x00]  # "911" in ASCII

        elif reg_addr == GT911_COORD_ADDR:
            # Mock status byte: 0x81 = buffer ready (0x80) + 1 touch point (0x01)
            return [0x81]

        elif reg_addr == GT911_COORD_ADDR + 1:
            # Mock touch data: 8 bytes
            # [track_id, x_low, x_high, y_low, y_high, size_low, size_high, reserved]
            x_coord = 0x0064  # X = 100
            y_coord = 0x00C8  # Y = 200
            return [
                0x00,  # track_id
                x_coord & 0xFF,  # x_low
                (x_coord >> 8) & 0xFF,  # x_high
                y_coord & 0xFF,  # y_low
                (y_coord >> 8) & 0xFF,  # y_high
                0x00,  # size_low
                0x00,  # size_high
                0x00,  # reserved
            ]

        return [0x00]

    mocker.patch.object(touch_control, "write_reg", fake_write_reg)
    mocker.patch.object(touch_control, "read_reg", fake_read_reg)
    mocker.patch.object(touch_control, "activate", fake_activate)

    touch_control.event_flag = False
    touch_control.irq_point = None
    touch_control.last_touch_time = 0
    mocker.spy(touch_control, "trigger_event")

    return touch_control


def test_handler(mocker, wonder_k, mock_gt911):
    from krux.touchscreens.gt911 import __handler__, ACTIVITY_THRESHOLD

    # Mock time to ensure debounce criteria is met
    mocker.patch("time.ticks_ms", return_value=ACTIVITY_THRESHOLD + 100)

    # Trigger the handler (pin number is arbitrary and ignored)
    __handler__(10)

    # Verify trigger_event was called
    mock_gt911.trigger_event.assert_called_once()

    # Verify event flag was set and point was captured
    assert mock_gt911.event_flag
    assert mock_gt911.irq_point is not None

    # Verify event() returns flag and clears it
    assert mock_gt911.event()
    assert not mock_gt911.event_flag


def test_init(mocker, wonder_k):
    from krux.touchscreens.gt911 import GT911, GT911_ADDR

    t = GT911()

    # Verify initial state
    assert t.irq_pin is None
    assert t.reset_pin is None
    assert t.event_flag is False
    assert t.irq_point is None
    assert t.addr == GT911_ADDR
    assert t.last_touch_time == 0


def test_point_not_read(mocker, dock):
    # Dock does not set i2c_bus because it does not
    # use I2C_SCL or I2C_SDA pins
    from krux.touchscreens.gt911 import GT911

    touch = GT911()
    data = touch.current_point()

    assert not data


def test_point_read(mocker, wonder_k):
    from krux.touchscreens.gt911 import GT911

    touch = GT911()

    # Mock time to ensure we're within activity threshold
    mocker.patch("time.ticks_ms", return_value=1000)
    touch.last_touch_time = 950  # 50ms ago, within threshold

    # Mock coordinate data: X=100, Y=200
    x_coord = 0x0064
    y_coord = 0x00C8
    coord_data = [
        0x00,
        x_coord & 0xFF,
        (x_coord >> 8) & 0xFF,
        y_coord & 0xFF,
        (y_coord >> 8) & 0xFF,
        0x00,
        0x00,
        0x00,
    ]

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("krux.i2c.i2c_bus.readfrom", return_value=coord_data)

    data = touch.current_point()
    assert data == (x_coord, y_coord)


def test_point_validate_read(mocker, wonder_k):
    from krux.touchscreens.gt911 import GT911

    touch = GT911()

    # Mock status: 0x81 (buffer ready + 1 touch point)
    # Mock coordinates: X=150, Y=250
    x_coord = 0x0096
    y_coord = 0x00FA
    coord_data = [
        0x00,
        x_coord & 0xFF,
        (x_coord >> 8) & 0xFF,
        y_coord & 0xFF,
        (y_coord >> 8) & 0xFF,
        0x00,
        0x00,
        0x00,
    ]

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch(
        "krux.i2c.i2c_bus.readfrom",
        side_effect=[[0x81], coord_data],  # First call: status, second: coords
    )

    data = touch.current_point_validate()
    assert data == (x_coord, y_coord)


@pytest.mark.parametrize(
    "status,expected",
    [
        (0x00, None),  # No touch, buffer not ready
        (0x80, None),  # Buffer ready but no touch points
        (0x01, None),  # Touch point but buffer not ready
        (0x81, (100, 200)),  # Valid: buffer ready + touch point
        (
            0x82,
            (100, 200),
        ),  # Valid: buffer ready + 2 touch points (first point returned)
    ],
)
def test_status_validation(mocker, wonder_k, status, expected):
    """Test different status register values"""
    from krux.touchscreens.gt911 import GT911

    touch = GT911()

    # Mock coordinates: X=100, Y=200
    coord_data = [0x00, 0x64, 0x00, 0xC8, 0x00, 0x00, 0x00, 0x00]

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch(
        "krux.i2c.i2c_bus.readfrom",
        side_effect=[[status], coord_data],
    )

    data = touch.current_point_validate()
    assert data == expected


def test_point_read_error(mocker, wonder_k):
    from krux.touchscreens.gt911 import GT911

    touch = GT911()

    # Mock time to ensure we're within activity threshold
    mocker.patch("time.ticks_ms", return_value=1000)
    touch.last_touch_time = 950

    # Simulate error
    e = Exception("mocked error")
    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("krux.i2c.i2c_bus.readfrom", side_effect=e)

    data = touch.current_point()
    assert data is None


def test_point_outside_threshold(mocker, wonder_k):
    from krux.touchscreens.gt911 import GT911, ACTIVITY_THRESHOLD

    touch = GT911()

    # Mock time to ensure we're outside activity threshold
    mocker.patch("time.ticks_ms", return_value=1000)
    touch.last_touch_time = 1000 - ACTIVITY_THRESHOLD - 10  # Outside threshold

    data = touch.current_point()
    assert data is None


def test_activate(mocker, wonder_k):
    from krux.touchscreens.gt911 import GT911, fm

    mock_fm_register = mocker.patch.object(fm, "register")
    mock_gpio = mocker.MagicMock()
    mocker.patch("Maix.GPIO", return_value=mock_gpio)
    mocker.patch("time.sleep_ms")

    touch = GT911()
    test_irq_pin = 21
    test_reset_pin = 22

    # Before activation
    assert touch.irq_pin is None
    assert touch.reset_pin is None

    touch.activate(test_irq_pin, test_reset_pin)

    # After activation, verify pins were registered
    assert mock_fm_register.call_count == 2
    calls = mock_fm_register.call_args_list
    assert calls[0][0] == (test_irq_pin, fm.fpioa.GPIOHS1)
    assert calls[1][0] == (test_reset_pin, fm.fpioa.GPIOHS2)

    # Verify pins were configured
    assert touch.irq_pin is not None
    assert touch.reset_pin is not None


def test_threshold(mocker, wonder_k):
    from krux.touchscreens.gt911 import GT911, GT911_CONFIG_DATA

    mock_writeto = mocker.patch("krux.i2c.i2c_bus.writeto")

    touch = GT911()
    test_threshold = 50

    touch.threshold(test_threshold)

    # Verify write_reg was called with correct threshold value
    calls = mock_writeto.call_args_list
    # Find the call that sets our test threshold
    # GT911 uses 16-bit addresses, so payload is [addr_high, addr_low, value]
    threshold_calls = [
        call
        for call in calls
        if len(call[0]) >= 2
        and len(call[0][1]) >= 3
        and call[0][1][0] == (GT911_CONFIG_DATA >> 8)
        and call[0][1][1] == (GT911_CONFIG_DATA & 0xFF)
        and call[0][1][2] == test_threshold
    ]
    assert len(threshold_calls) >= 1


@pytest.mark.parametrize(
    "x_coord,y_coord",
    [
        (0x0000, 0x0000),  # Min coordinates
        (0x0064, 0x00C8),  # Mid coordinates: (100, 200)
        (0x01E0, 0x0320),  # Large coordinates: (480, 800)
        (0x00FF, 0x00FF),  # Equal X,Y: (255, 255)
    ],
)
def test_coordinate_reading(mocker, wonder_k, x_coord, y_coord):
    """Test coordinate extraction from touch data"""
    from krux.touchscreens.gt911 import GT911

    touch = GT911()

    coord_data = [
        0x00,
        x_coord & 0xFF,
        (x_coord >> 8) & 0xFF,
        y_coord & 0xFF,
        (y_coord >> 8) & 0xFF,
        0x00,
        0x00,
        0x00,
    ]

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch(
        "krux.i2c.i2c_bus.readfrom",
        side_effect=[[0x81], coord_data],
    )

    data = touch.current_point_validate()
    assert data == (x_coord, y_coord)


def test_trigger_event_clears_irq_flag(mocker, wonder_k):
    """Verify that trigger_event clears the interrupt flag"""
    from krux.touchscreens.gt911 import GT911, ACTIVITY_THRESHOLD, GT911_COORD_ADDR

    mock_writeto = mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("time.ticks_ms", return_value=ACTIVITY_THRESHOLD + 100)

    touch = GT911()

    # Mock valid touch data
    mocker.patch(
        "krux.i2c.i2c_bus.readfrom",
        side_effect=[[0x81], [0x00, 0x64, 0x00, 0xC8, 0x00, 0x00, 0x00, 0x00]],
    )

    touch.trigger_event()

    # Verify interrupt flag was cleared
    # Should write 0x00 to GT911_COORD_ADDR
    clear_calls = [
        call
        for call in mock_writeto.call_args_list
        if len(call[0]) >= 2
        and len(call[0][1]) >= 3
        and call[0][1][0] == (GT911_COORD_ADDR >> 8)
        and call[0][1][1] == (GT911_COORD_ADDR & 0xFF)
        and call[0][1][2] == 0x00
    ]
    assert len(clear_calls) >= 1

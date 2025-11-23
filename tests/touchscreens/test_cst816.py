import pytest


@pytest.fixture
def mock_cst816(mocker):
    from krux.touchscreens.cst816 import (
        fm,
        touch_control,
        CST816S_TOUCH_DATA,
        CST816S_VERSION,
        EVENT_TOUCH_CONTACT,
        SCREEN_WIDTH,
    )

    mocker.patch.object(fm, "register")
    mock_gpio = mocker.MagicMock()
    mocker.patch("Maix.GPIO", return_value=mock_gpio)

    def fake_activate(irq_pin):
        touch_control.irq_pin = mock_gpio

    def fake_write_reg(reg_addr, buf):
        pass

    def fake_read_reg(reg_addr, buf_len):
        if reg_addr == CST816S_VERSION:
            return [0x01]
        elif reg_addr == CST816S_TOUCH_DATA:
            from .helpers import create_cst816_touch_data

            return create_cst816_touch_data(
                points=0x01, event=EVENT_TOUCH_CONTACT, x_coord=0x0050, y_coord=0x00A0
            )
        return [0x00]

    mocker.patch.object(touch_control, "_write_reg", fake_write_reg)
    mocker.patch.object(touch_control, "_read_reg", fake_read_reg)
    mocker.patch.object(touch_control, "activate", fake_activate)

    touch_control.event_flag = False
    touch_control.irq_point = None
    touch_control.last_touch_time = 0
    mocker.spy(touch_control, "trigger_event")

    return touch_control


def test_handler(mocker, embed_fire, mock_cst816):
    from krux.touchscreens.cst816 import __handler__, ACTIVITY_THRESHOLD

    mocker.patch("time.ticks_ms", return_value=ACTIVITY_THRESHOLD + 100)
    __handler__(10)

    mock_cst816.trigger_event.assert_called_once()
    assert mock_cst816.event_flag
    assert mock_cst816.irq_point is not None
    assert mock_cst816.event()
    assert not mock_cst816.event_flag


def test_debounce_trigger_event_too_soon(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816, ACTIVITY_THRESHOLD

    touch = CST816()
    touch.last_touch_time = 1000

    mocker.patch("time.ticks_ms", return_value=1000 + ACTIVITY_THRESHOLD - 10)
    mock_validate = mocker.patch.object(touch, "current_point_validate")

    touch.trigger_event()

    assert not touch.event_flag
    assert touch.irq_point is None
    mock_validate.assert_not_called()
    assert touch.last_touch_time == 1000 + ACTIVITY_THRESHOLD - 10


def test_init(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816

    t = CST816()

    assert t.irq_pin is None
    assert t.event_flag is False
    assert t.irq_point is None
    assert t.last_touch_time == 0


def test_point_not_read(mocker, dock):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    data = touch.current_point()

    assert not data


def test_point_read(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816, EVENT_TOUCH_CONTACT, SCREEN_WIDTH
    from .helpers import create_cst816_touch_data

    touch = CST816()
    mocker.patch("time.ticks_ms", return_value=1000)
    touch.last_touch_time = 950

    x_coord = 0x0050
    y_coord = 0x00A0
    touch_data = create_cst816_touch_data(0x01, EVENT_TOUCH_CONTACT, x_coord, y_coord)

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("krux.i2c.i2c_bus.readfrom", return_value=touch_data)

    data = touch.current_point()
    expected = (SCREEN_WIDTH - x_coord, y_coord)
    assert data == expected


def test_point_validate_read(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816, EVENT_TOUCH_CONTACT, SCREEN_WIDTH
    from .helpers import create_cst816_touch_data

    touch = CST816()
    x_coord = 0x0028
    y_coord = 0x0078
    touch_data = create_cst816_touch_data(0x01, EVENT_TOUCH_CONTACT, x_coord, y_coord)

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("krux.i2c.i2c_bus.readfrom", return_value=touch_data)

    data = touch.current_point_validate()
    expected = (SCREEN_WIDTH - x_coord, y_coord)
    assert data == expected


def test_no_touch_points(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816, EVENT_TOUCH_CONTACT
    from .helpers import create_cst816_touch_data

    touch = CST816()
    touch_data = create_cst816_touch_data(0x00, EVENT_TOUCH_CONTACT, 0x00, 0x00)

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("krux.i2c.i2c_bus.readfrom", return_value=touch_data)

    data = touch.current_point_validate()
    assert data is None


def test_wrong_event_type(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    points = 0x01
    event = 0x01 << 6
    touch_data = [0x00, points, event, 0x50, 0x00, 0xA0]

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("krux.i2c.i2c_bus.readfrom", return_value=touch_data)

    data = touch.current_point_validate()
    assert data is None


def test_point_read_error(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    mocker.patch("time.ticks_ms", return_value=1000)
    touch.last_touch_time = 950

    e = Exception("mocked error")
    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("krux.i2c.i2c_bus.readfrom", side_effect=e)

    data = touch.current_point()
    assert data is None


def test_read_touch_data_parsing_error(mocker, embed_fire, capsys):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    mocker.patch.object(
        touch, "_read_reg", side_effect=Exception("Touch data parsing error")
    )

    data = touch._read_touch_data()

    assert data is None
    captured = capsys.readouterr()
    assert "CST816S touch data read error:" in captured.out
    assert "Touch data parsing error" in captured.out


def test_point_outside_threshold(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816, ACTIVITY_THRESHOLD

    touch = CST816()
    mocker.patch("time.ticks_ms", return_value=1000)
    touch.last_touch_time = 1000 - ACTIVITY_THRESHOLD - 10

    data = touch.current_point()
    assert data is None


def test_activate(mocker, embed_fire):
    from krux.touchscreens.cst816 import CST816, fm

    mock_fm_register = mocker.patch.object(fm, "register")
    mock_gpio = mocker.MagicMock()
    mocker.patch("Maix.GPIO", return_value=mock_gpio)

    touch = CST816()
    test_pin = 21

    assert touch.irq_pin is None

    touch.activate(test_pin)

    mock_fm_register.assert_called_with(test_pin, fm.fpioa.GPIOHS1)
    assert touch.irq_pin is not None


def test_init_cst816_read_error(mocker, embed_fire, capsys):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    mocker.patch.object(touch, "_read_reg", side_effect=Exception("I2C read error"))
    mock_write = mocker.patch.object(touch, "_write_reg")

    touch._init_cst816()

    captured = capsys.readouterr()
    assert "CST816S initialization error:" in captured.out
    assert "I2C read error" in captured.out
    mock_write.assert_not_called()


def test_init_cst816_write_error(mocker, embed_fire, capsys):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    mocker.patch.object(touch, "_read_reg", return_value=[0x01])
    mocker.patch.object(touch, "_write_reg", side_effect=Exception("I2C write error"))

    touch._init_cst816()

    captured = capsys.readouterr()
    assert "CST816S initialization error:" in captured.out
    assert "I2C write error" in captured.out


def test_write_reg_exception(mocker, embed_fire, capsys):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    mocker.patch("krux.i2c.i2c_bus.writeto", side_effect=Exception("I2C write failed"))

    touch._write_reg(0x00, bytearray([0x01]))

    captured = capsys.readouterr()
    assert "CST816S write error:" in captured.out
    assert "I2C write failed" in captured.out


def test_write_reg_no_i2c_bus(dock):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    touch._write_reg(0x00, bytearray([0x01]))


def test_read_reg_exception(mocker, embed_fire, capsys):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    mocker.patch("krux.i2c.i2c_bus.writeto", side_effect=Exception("I2C read failed"))

    result = touch._read_reg(0x00, 1)

    captured = capsys.readouterr()
    assert "CST816S read error:" in captured.out
    assert "I2C read failed" in captured.out
    assert result is None


def test_read_reg_no_i2c_bus(dock):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    result = touch._read_reg(0x00, 1)

    assert result is None


def test_threshold(mocker, embed_fire, capsys):
    from krux.touchscreens.cst816 import CST816

    touch = CST816()
    touch.threshold(30)

    captured = capsys.readouterr()
    assert "Threshold setting not supported" in captured.out


@pytest.mark.parametrize(
    "x_coord,y_coord,expected_x",
    [
        (0x0000, 0x0000, 240),
        (0x0050, 0x00A0, 160),
        (0x00F0, 0x0140, 0),
        (0x0078, 0x0140, 120),
    ],
)
def test_coordinate_mirroring(mocker, embed_fire, x_coord, y_coord, expected_x):
    from krux.touchscreens.cst816 import CST816, EVENT_TOUCH_CONTACT
    from .helpers import create_cst816_touch_data

    touch = CST816()
    touch_data = create_cst816_touch_data(0x01, EVENT_TOUCH_CONTACT, x_coord, y_coord)

    mocker.patch("krux.i2c.i2c_bus.writeto")
    mocker.patch("krux.i2c.i2c_bus.readfrom", return_value=touch_data)

    data = touch.current_point_validate()
    assert data == (expected_x, y_coord)

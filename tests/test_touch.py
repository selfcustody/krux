import pytest
import time


@pytest.fixture
def mock_settings(mocker):
    """Mock Settings to avoid dependency on hardware config"""
    mock_settings_obj = mocker.MagicMock()
    mock_settings_obj.hardware.touch.threshold = 40
    # Ensure hardware doesn't have display attribute to avoid coordinate flipping
    del mock_settings_obj.hardware.display
    mock_settings_class = mocker.patch("krux.touch.Settings")
    mock_settings_class.return_value = mock_settings_obj
    return mock_settings_obj


@pytest.fixture
def mock_touch_driver(mocker):
    """Mock a generic touch driver"""
    driver = mocker.MagicMock()
    driver.current_point.return_value = None
    driver.event.return_value = False
    driver.irq_point = None
    return driver


def test_touch_init_ft6x36(mocker, amigo, mock_settings):
    """Test Touch initialization with FT6X36 driver (default case)"""
    from krux.touch import Touch

    mock_control = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_control)

    # No res_pin = FT6X36
    touch = Touch(width=240, height=135, irq_pin=20)

    assert touch.width == 240
    assert touch.height == 135
    assert touch.state == 0  # IDLE
    mock_control.activate_irq.assert_called_once_with(20)
    mock_control.threshold.assert_called_once_with(40)


def test_touch_init_cst816(mocker, embed_fire, mock_settings):
    """Test Touch initialization with CST816 driver (embed_fire board)"""
    from krux.touch import Touch

    mock_control = mocker.MagicMock()
    mocker.patch("krux.touchscreens.cst816.touch_control", mock_control)

    # embed_fire = CST816
    touch = Touch(width=240, height=135, irq_pin=21)

    assert touch.touch_driver == mock_control
    mock_control.activate.assert_called_once_with(21)
    mock_control.threshold.assert_called_once_with(40)


def test_touch_init_gt911(mocker, wonder_k, mock_settings):
    """Test Touch initialization with GT911 driver (res_pin provided)"""
    from krux.touch import Touch

    mock_control = mocker.MagicMock()
    mocker.patch("krux.touchscreens.gt911.touch_control", mock_control)

    # res_pin != None = GT911
    touch = Touch(width=240, height=135, irq_pin=21, res_pin=22)

    assert touch.touch_driver == mock_control
    mock_control.activate.assert_called_once_with(21, 22)
    mock_control.threshold.assert_called_once_with(40)


def test_clear_regions(mocker, amigo, mock_settings):
    """Test clearing touch regions"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.y_regions = [50, 100, 150]
    touch.x_regions = [60, 120]

    touch.clear_regions()

    assert touch.y_regions == []
    assert touch.x_regions == []


def test_add_y_delimiter(mocker, amigo, mock_settings):
    """Test adding Y delimiters"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)

    touch.add_y_delimiter(50)
    touch.add_y_delimiter(100)

    assert touch.y_regions == [50, 100]


def test_add_y_delimiter_out_of_bounds(mocker, amigo, mock_settings):
    """Test adding Y delimiter outside display area raises error"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)

    with pytest.raises(ValueError, match="outside display area"):
        touch.add_y_delimiter(250)  # width = 240


def test_add_x_delimiter(mocker, amigo, mock_settings):
    """Test adding X delimiters"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)

    touch.add_x_delimiter(45)
    touch.add_x_delimiter(90)

    assert touch.x_regions == [45, 90]


def test_add_x_delimiter_out_of_bounds(mocker, amigo, mock_settings):
    """Test adding X delimiter outside display area raises error"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)

    with pytest.raises(ValueError, match="outside display area"):
        touch.add_x_delimiter(140)  # height = 135


def test_set_regions(mocker, amigo, mock_settings):
    """Test setting regions with lists"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)

    touch.set_regions(x_list=[30, 60, 90], y_list=[60, 120, 180])

    assert touch.x_regions == [30, 60, 90]
    assert touch.y_regions == [60, 120, 180]


def test_set_regions_invalid_type(mocker, amigo, mock_settings):
    """Test setting regions with non-list raises error"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)

    with pytest.raises(ValueError, match="must be a list"):
        touch.set_regions(x_list="not a list")

    with pytest.raises(ValueError, match="must be a list"):
        touch.set_regions(y_list=123)


@pytest.mark.parametrize(
    "data,x_regions,y_regions,expected_valid",
    [
        ((100, 100), [], [], True),  # No regions = always valid
        ((100, 100), [], [50, 150], True),  # Within y bounds
        ((100, 100), [40, 120], [], True),  # Within x bounds
        ((100, 100), [40, 120], [50, 150], True),  # Within both bounds
        ((30, 100), [40, 120], [], False),  # Below x lower bound
        ((130, 100), [40, 120], [], False),  # Above x upper bound
        ((100, 30), [], [50, 150], False),  # Below y lower bound
        ((100, 160), [], [50, 150], False),  # Above y upper bound
    ],
)
def test_valid_position(
    mocker, amigo, mock_settings, data, x_regions, y_regions, expected_valid
):
    """Test position validation against regions"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.x_regions = x_regions
    touch.y_regions = y_regions

    assert touch.valid_position(data) == expected_valid


@pytest.mark.parametrize(
    "y_regions,x_regions,touch_point,expected_index",
    [
        ([60, 120], [], (100, 50), 0),  # y=50 < 60: index 0
        ([60, 120], [], (100, 80), 0),  # y=80 between 60 and 120: index 0
        ([60, 120], [], (100, 130), 1),  # y=130 > 120: index 1
        ([40, 80, 120], [], (50, 30), 0),  # y=30 < 40: index 0
        ([40, 80, 120], [], (50, 50), 0),  # y=50 between 40-80: index 0
        ([40, 80, 120], [], (50, 90), 1),  # y=90 between 80-120: index 1
        ([40, 80, 120], [], (50, 130), 2),  # y=130 > 120: index 2
    ],
)
def test_extract_index(
    mocker, amigo, mock_settings, y_regions, x_regions, touch_point, expected_index
):
    """Test index extraction from touch coordinates"""
    from krux.touch import Touch

    mocker.patch("krux.touchscreens.ft6x36.touch_control", mocker.MagicMock())

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.y_regions = y_regions
    touch.x_regions = x_regions

    index = touch._extract_index(touch_point)
    assert index == expected_index


def test_current_state_idle_to_pressed(mocker, amigo, mock_settings):
    """Test state transition from IDLE to PRESSED"""
    from krux.touch import Touch, IDLE, PRESSED

    mock_driver = mocker.MagicMock()
    mock_driver.current_point.return_value = (100, 100)
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.y_regions = [60, 120]

    assert touch.state == IDLE

    state = touch.current_state()

    assert state == PRESSED
    assert len(touch.press_point) == 1
    assert touch.press_point[0] == (100, 100)


def test_current_state_pressed_to_released(mocker, amigo, mock_settings):
    """Test state transition from PRESSED to RELEASED"""
    from krux.touch import Touch, PRESSED, RELEASED

    mock_driver = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.state = PRESSED
    touch.press_point = [(100, 100)]
    touch.release_point = (105, 105)

    # Return None to simulate touch release
    mock_driver.current_point.return_value = None

    state = touch.current_state()

    assert state == RELEASED


def test_current_state_released_to_idle(mocker, amigo, mock_settings):
    """Test state transition from RELEASED to IDLE"""
    from krux.touch import Touch, RELEASED, IDLE

    mock_driver = mocker.MagicMock()
    mock_driver.current_point.return_value = None
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.state = RELEASED

    state = touch.current_state()

    assert state == IDLE


@pytest.mark.parametrize(
    "press_point,release_point,expected_gesture",
    [
        ((100, 100), (160, 100), 1),  # SWIPE_RIGHT (lateral = 60)
        ((160, 100), (100, 100), 2),  # SWIPE_LEFT (lateral = -60)
        ((100, 100), (100, 160), 4),  # SWIPE_DOWN (vertical = 60 > lateral)
        ((100, 160), (100, 100), 3),  # SWIPE_UP (vertical = -60 > lateral)
        ((100, 100), (105, 105), None),  # No gesture (< threshold)
    ],
)
def test_gesture_detection(
    mocker, amigo, mock_settings, press_point, release_point, expected_gesture
):
    """Test swipe gesture detection"""
    from krux.touch import Touch, PRESSED

    mock_driver = mocker.MagicMock()
    mock_driver.current_point.return_value = None
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.state = PRESSED
    touch.press_point = [press_point]
    touch.release_point = release_point

    touch.current_state()

    assert touch.gesture == expected_gesture


def test_event_with_validation(mocker, amigo, mock_settings):
    """Test event detection with position validation"""
    from krux.touch import Touch

    mock_driver = mocker.MagicMock()
    mock_driver.event.return_value = True
    mock_driver.irq_point = (100, 100)
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.y_regions = [50, 150]
    touch.sample_time = 900  # 100ms ago

    result = touch.event(validate_position=True)

    assert result is True


def test_event_invalid_position(mocker, amigo, mock_settings):
    """Test event detection with invalid position"""
    from krux.touch import Touch

    mock_driver = mocker.MagicMock()
    mock_driver.event.return_value = True
    mock_driver.irq_point = (100, 30)  # Below y_regions[0]
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.y_regions = [50, 150]
    touch.sample_time = 900

    result = touch.event(validate_position=True)

    assert result is False


def test_event_without_validation(mocker, amigo, mock_settings):
    """Test event detection without position validation"""
    from krux.touch import Touch

    mock_driver = mocker.MagicMock()
    mock_driver.event.return_value = True
    mock_driver.irq_point = (100, 30)  # Would be invalid if validated
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.y_regions = [50, 150]
    touch.sample_time = 900

    result = touch.event(validate_position=False)

    assert result is True


def test_event_sample_period_not_elapsed(mocker, amigo, mock_settings):
    """Test event not triggered if sample period hasn't elapsed"""
    from krux.touch import Touch

    mock_driver = mocker.MagicMock()
    mock_driver.event.return_value = True
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1010)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.sample_time = 1000  # 10ms ago (< TOUCH_S_PERIOD=20)

    result = touch.event()

    assert result is False


def test_value(mocker, amigo, mock_settings):
    """Test value() method returns button-like behavior"""
    from krux.touch import Touch, IDLE, PRESSED

    mock_driver = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)

    # IDLE state returns 1
    mock_driver.current_point.return_value = None
    touch.state = IDLE
    assert touch.value() == 1

    # Non-IDLE state returns 0
    # When touch is pressed, driver returns coordinates
    mock_driver.current_point.return_value = (100, 100)
    touch.state = IDLE  # Start from IDLE
    result = touch.value()
    # State becomes PRESSED, so value returns 0
    assert result == 0


def test_swipe_right_value(mocker, amigo, mock_settings):
    """Test swipe right detection and reset"""
    from krux.touch import Touch, SWIPE_RIGHT

    mock_driver = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)

    touch = Touch(width=240, height=135, irq_pin=20)

    touch.gesture = SWIPE_RIGHT
    assert touch.swipe_right_value() == 0
    assert touch.gesture is None  # Gesture cleared

    assert touch.swipe_right_value() == 1  # No gesture


def test_swipe_left_value(mocker, amigo, mock_settings):
    """Test swipe left detection and reset"""
    from krux.touch import Touch, SWIPE_LEFT

    mock_driver = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)

    touch = Touch(width=240, height=135, irq_pin=20)

    touch.gesture = SWIPE_LEFT
    assert touch.swipe_left_value() == 0
    assert touch.gesture is None


def test_swipe_up_value(mocker, amigo, mock_settings):
    """Test swipe up detection and reset"""
    from krux.touch import Touch, SWIPE_UP

    mock_driver = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)

    touch = Touch(width=240, height=135, irq_pin=20)

    touch.gesture = SWIPE_UP
    assert touch.swipe_up_value() == 0
    assert touch.gesture is None


def test_swipe_down_value(mocker, amigo, mock_settings):
    """Test swipe down detection and reset"""
    from krux.touch import Touch, SWIPE_DOWN

    mock_driver = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)

    touch = Touch(width=240, height=135, irq_pin=20)

    touch.gesture = SWIPE_DOWN
    assert touch.swipe_down_value() == 0
    assert touch.gesture is None


def test_current_index(mocker, amigo, mock_settings):
    """Test getting current touch index"""
    from krux.touch import Touch

    mock_driver = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.index = 5

    assert touch.current_index() == 5


def test_press_point_averaging(mocker, amigo, mock_settings):
    """Test that multiple touch samples are averaged"""
    from krux.touch import Touch, PRESSED

    mock_driver = mocker.MagicMock()
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)
    mocker.patch("time.ticks_ms", return_value=1000)

    touch = Touch(width=240, height=135, irq_pin=20)
    touch.state = PRESSED
    touch.press_point = [(100, 100), (102, 102), (98, 98)]

    # Add another point
    mock_driver.current_point.return_value = (100, 100)
    touch.current_state()

    # Should have 4 points now
    assert len(touch.press_point) == 4

    # Index should be calculated from average
    # Average = (100+102+98+100)/4, (100+102+98+100)/4 = (100, 100)
    # (Note: actual index depends on regions set)


def test_touch_event_integration(mocker, amigo, mock_settings):
    """Integration test: full event sequence with touch point averaging and index calculation"""
    from krux.touch import Touch
    import board

    Y_REGIONS = (0, 40, 80, 120, 160, 200)

    # Simulate touch points on region 3 - 120 to 160
    TOUCH_POINT_1 = (75, 150)
    TOUCH_POINT_2 = (77, 152)

    EVENTS = [False, True, False, False]
    POINTS = [TOUCH_POINT_1, TOUCH_POINT_2, None, None]

    mock_driver = mocker.MagicMock()
    mock_driver.event.side_effect = EVENTS
    mock_driver.current_point.side_effect = POINTS
    mocker.patch("krux.touchscreens.ft6x36.touch_control", mock_driver)

    # Mock time advancing
    tick_time = [10000]

    def mock_time_advance():
        tick_time[0] += 100
        return tick_time[0] - 100

    mocker.patch.object(time, "ticks_ms", side_effect=mock_time_advance)

    touch = Touch(
        board.config["lcd"]["width"],
        board.config["lcd"]["height"],
        board.config["krux"]["pins"]["TOUCH_IRQ"],
    )
    touch.y_regions = Y_REGIONS
    mock_driver.irq_point = TOUCH_POINT_1  # Simulate touch event

    event_result = None
    for _ in range(len(EVENTS)):
        event_result = touch.event(validate_position=True)

    assert event_result is False
    assert touch.current_index() == 3

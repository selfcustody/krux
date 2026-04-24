import pytest
import time


def mock_timer_ticks(step=100):
    """Mocks the time.ticks_ms() function to simulate time passing"""
    tick_time = [10000]  # Start time

    def side_effect():
        tick_time[0] += step
        return tick_time[0] - step

    return side_effect


def reset_input_states(mocker, input):
    """Reset the input states to avoid any previous state to interfere with the tests"""
    from krux.input import RELEASED

    if input.enter:
        mocker.patch.object(input, "enter_value", return_value=RELEASED)
        mocker.patch.object(input, "enter_event", return_value=False)
    if input.page:
        mocker.patch.object(input, "page_value", return_value=RELEASED)
        mocker.patch.object(input, "page_event", return_value=False)
    if input.page_prev:
        mocker.patch.object(input, "page_prev_value", return_value=RELEASED)
        mocker.patch.object(input, "page_prev_event", return_value=False)
    if input.touch:
        mocker.patch.object(
            input.touch.touch_driver, "current_point", return_value=None
        )
        mocker.patch.object(input.touch, "event", return_value=False)
    return input


def test_init_m5stickv(mocker, m5stickv):
    mocker.patch("krux.buttons.fm.register", new=mocker.MagicMock())
    mocker.patch("krux.buttons.GPIO", new=mocker.MagicMock())
    import krux
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)
    krux.buttons.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["BUTTON_A"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_B"], mocker.ANY),
        ]
    )
    assert (
        krux.buttons.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS21"
    )
    assert (
        krux.buttons.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert input.enter is not None
    assert input.page is not None

    assert krux.buttons.GPIO.call_count == 2
    assert (
        krux.buttons.GPIO.call_args_list[0].args[0]._extract_mock_name()
        == "mock.GPIOHS21"
    )
    assert (
        krux.buttons.GPIO.call_args_list[1].args[0]._extract_mock_name()
        == "mock.GPIOHS22"
    )


def test_init_amigo(mocker, amigo):
    mocker.patch("krux.buttons.fm.register", new=mocker.MagicMock())
    mocker.patch("krux.buttons.GPIO", new=mocker.MagicMock())
    import krux
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)
    krux.buttons.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["BUTTON_A"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_B"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_C"], mocker.ANY),
        ]
    )
    assert (
        krux.buttons.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS21"
    )
    assert (
        krux.buttons.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert (
        krux.buttons.fm.register.call_args_list[2].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS0"
    )
    assert input.enter is not None
    assert input.page is not None
    assert input.page_prev is not None

    assert krux.buttons.GPIO.call_count == 3
    assert (
        krux.buttons.GPIO.call_args_list[0].args[0]._extract_mock_name()
        == "mock.GPIOHS21"
    )
    assert (
        krux.buttons.GPIO.call_args_list[1].args[0]._extract_mock_name()
        == "mock.GPIOHS22"
    )
    assert (
        krux.buttons.GPIO.call_args_list[2].args[0]._extract_mock_name()
        == "mock.GPIOHS0"
    )


def test_init_dock(mocker, dock):
    mocker.patch("krux.buttons.fm.register", new=mocker.MagicMock())
    mocker.patch("krux.buttons.GPIO", new=mocker.MagicMock())
    import krux
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)
    krux.buttons.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["BUTTON_A"], mocker.ANY),
        ]
    )
    krux.rotary.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["ENCODER"][0], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["ENCODER"][1], mocker.ANY),
        ]
    )
    assert (
        krux.buttons.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS21"
    )
    assert (
        krux.rotary.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert (
        krux.rotary.fm.register.call_args_list[2].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS0"
    )
    assert input.enter is not None
    assert input.page is not None
    assert input.page_prev is not None

    assert krux.buttons.GPIO.call_count == 1
    assert krux.rotary.GPIO.call_count == 2
    assert (
        krux.buttons.GPIO.call_args_list[0].args[0]._extract_mock_name()
        == "mock.GPIOHS21"
    )
    assert (
        krux.rotary.GPIO.call_args_list[0].args[0]._extract_mock_name()
        == "mock.GPIO.GPIOHS22"
    )
    assert (
        krux.rotary.GPIO.call_args_list[1].args[0]._extract_mock_name()
        == "mock.GPIO.GPIOHS0"
    )


def test_init_cube(mocker, cube):
    mocker.patch("krux.buttons.fm.register", new=mocker.MagicMock())
    mocker.patch("krux.buttons.GPIO", new=mocker.MagicMock())
    from krux import buttons
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)

    for button in buttons.fm.register.call_args_list:
        print(button)

    buttons.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["BUTTON_A"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_B"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_C"], mocker.ANY),
        ]
    )

    assert (
        buttons.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS21"
    )
    assert (
        buttons.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert (
        buttons.fm.register.call_args_list[2].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS0"
    )

    assert input.enter is not None
    assert input.page is not None
    assert input.page_prev is not None

    assert buttons.GPIO.call_count == 3
    assert (
        buttons.GPIO.call_args_list[0].args[0]._extract_mock_name() == "mock.GPIOHS21"
    )
    assert (
        buttons.GPIO.call_args_list[1].args[0]._extract_mock_name() == "mock.GPIOHS22"
    )


def test_init_yahboom(mocker, yahboom):
    mocker.patch("krux.buttons.fm.register", new=mocker.MagicMock())
    mocker.patch("krux.buttons.GPIO", new=mocker.MagicMock())
    from krux import buttons
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)

    buttons.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["BUTTON_B"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_C"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["TOUCH_IRQ"], mocker.ANY),
        ]
    )

    assert (
        buttons.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert (
        buttons.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS0"
    )
    assert (
        buttons.fm.register.call_args_list[2].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS1"
    )

    assert input.enter is None
    assert input.page is not None
    assert input.page_prev is not None

    assert buttons.GPIO.call_count == 2
    assert (
        buttons.GPIO.call_args_list[0].args[0]._extract_mock_name() == "mock.GPIOHS22"
    )
    assert buttons.GPIO.call_args_list[1].args[0]._extract_mock_name() == "mock.GPIOHS0"


def test_init_wonder_mv(mocker, wonder_mv):
    mocker.patch("krux.buttons.fm.register", new=mocker.MagicMock())
    mocker.patch("krux.buttons.GPIO", new=mocker.MagicMock())
    from krux import buttons
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)

    buttons.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["BUTTON_A"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_B"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["TOUCH_IRQ"], mocker.ANY),
        ]
    )

    assert (
        buttons.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS21"
    )
    assert (
        buttons.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert (
        buttons.fm.register.call_args_list[2].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS1"
    )

    assert input.enter is not None
    assert input.page is not None
    assert input.page_prev is None

    assert buttons.GPIO.call_count == 2
    assert (
        buttons.GPIO.call_args_list[0].args[0]._extract_mock_name() == "mock.GPIOHS21"
    )
    assert (
        buttons.GPIO.call_args_list[1].args[0]._extract_mock_name() == "mock.GPIOHS22"
    )


def test_enter_value_released_when_none(mocker, m5stickv):
    from krux.input import Input, RELEASED

    input = Input()
    input.enter = None
    assert input.enter_value() == RELEASED


def test_page_value_released_when_none(mocker, m5stickv):
    from krux.input import Input, RELEASED

    input = Input()
    input.page = None
    assert input.page_value() == RELEASED


def test_page_prev_value_released_when_none(mocker, m5stickv):
    from krux.input import Input, RELEASED

    input = Input()
    input.page_prev = None
    assert input.page_prev_value() == RELEASED


def test_touch_value_released_when_none(mocker, m5stickv):
    from krux.input import Input, RELEASED

    input = Input()
    input.touch = None
    assert input.touch_value() == RELEASED


def test_swipe_right_value_released_when_none(mocker, m5stickv):
    from krux.input import Input, RELEASED

    input = Input()
    input.touch = None
    assert input.swipe_right_value() == RELEASED


def test_swipe_left_value_released_when_none(mocker, m5stickv):
    from krux.input import Input, RELEASED

    input = Input()
    input.touch = None
    assert input.swipe_left_value() == RELEASED


def test_swipe_up_value_released_when_none(mocker, m5stickv):
    from krux.input import Input, RELEASED

    input = Input()
    input.touch = None
    assert input.swipe_up_value() == RELEASED


def test_swipe_down_value_released_when_none(mocker, m5stickv):
    from krux.input import Input, RELEASED

    input = Input()
    input.touch = None
    assert input.swipe_down_value() == RELEASED


def test_wait_for_release(mocker, m5stickv):
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_ENTER

    input = Input()
    input = reset_input_states(mocker, input)
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "enter_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "enter_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0
    assert input.wait_for_button() == BUTTON_ENTER
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_release_page_yahboom(mocker, yahboom):
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_PAGE, BUTTON_PAGE_PREV

    input = Input()
    input = reset_input_states(mocker, input)
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "page_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "page_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0
    input.wait_for_button() == BUTTON_PAGE
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_release_page_prev_yahboom(mocker, yahboom):
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_PAGE

    input = Input()
    input = reset_input_states(mocker, input)
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "page_prev_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "page_prev_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    # Test with BUTTON_PAGE_PREV, expect it to be PAGE on yahboom
    input.wait_for_button() == BUTTON_PAGE
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_debounce_presses_with_greater_interval(mocker, m5stickv):
    from krux.input import Input, RELEASED, PRESSED, BUTTON_ENTER

    # First test button presses at an interval greater than the debounce time
    input = Input()
    input = reset_input_states(mocker, input)
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "enter_event", side_effect=[False, True, False] * 2)
    mocker.patch.object(
        input, "enter_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED] * 2
    )
    mocker.spy(input, "flush_events")

    assert input.entropy == 0
    btn = input.wait_for_button()
    for _ in range(5):
        # Runs ticks_ms() 5 times to simulate elapsed time greater than debounce
        time.ticks_ms()
    assert btn == BUTTON_ENTER
    btn = input.wait_for_button()
    assert btn == BUTTON_ENTER
    assert input.entropy > 0
    # Assert that the flush_events was called only once for each button read
    assert input.flush_events.call_count == 2


def test_debounce_presses_with_smaller_interval(mocker, m5stickv):
    from krux.input import Input, RELEASED, PRESSED
    from krux.krux_settings import Settings

    input = Input()
    interval = 10  # ms
    input = reset_input_states(mocker, input)
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks(interval))
    mocker.patch.object(input, "enter_event", side_effect=[False, True, False] * 5)
    mocker.patch.object(
        input, "enter_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED] * 2
    )
    mocker.spy(input, "flush_events")

    btn = input.wait_for_button()
    assert btn == 0
    btn = input.wait_for_button()
    assert btn == 0
    assert input.entropy > 0
    # Assert that the flush_events was called debounce / interval times
    # meaning that the debounce time was respected
    assert (
        input.flush_events.call_count == Settings().hardware.buttons.debounce / interval
    )


def test_wait_for_button_blocks_until_enter_released(mocker, m5stickv):
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_ENTER

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "enter_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "enter_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert btn == BUTTON_ENTER
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_page_released(mocker, m5stickv):
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_PAGE

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "page_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "page_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert btn == BUTTON_PAGE
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_page_prev_released(mocker, m5stickv):
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_PAGE_PREV

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "page_prev_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "page_prev_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert btn == BUTTON_PAGE_PREV
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_touch_released(mocker, amigo):
    import krux
    from krux.input import Input, BUTTON_TOUCH, PRESSED, RELEASED

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "touch_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "touch_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert btn == BUTTON_TOUCH
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_returns_when_nonblocking(mocker, m5stickv):
    import krux
    from krux.input import Input, QR_ANIM_PERIOD

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(
        time, "ticks_ms", side_effect=mock_timer_ticks(step=QR_ANIM_PERIOD + 1)
    )

    btn = input.wait_for_button(False)

    assert btn is None
    krux.input.wdt.feed.assert_called()


def test_long_press_page_simulates_fast_forward(mocker, m5stickv):
    import krux
    from krux.input import Input, RELEASED, PRESSED, FAST_FORWARD

    input = Input()
    input = reset_input_states(mocker, input)

    # Create a table of states for button events, values and time ticks
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks(step=1000))
    mocker.patch.object(input, "page_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "page_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert btn == FAST_FORWARD
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_long_press_page_prev_simulates_fast_backwar(mocker, m5stickv):
    import krux
    from krux.input import Input, RELEASED, PRESSED, FAST_BACKWARD

    input = Input()
    input = reset_input_states(mocker, input)

    # Create a table of states for button events, values and time ticks
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks(step=1000))
    mocker.patch.object(input, "page_prev_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "page_prev_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert btn == FAST_BACKWARD
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_touch_indexing(mocker, amigo):
    import krux
    from krux.input import Input, BUTTON_TOUCH

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())

    def mock_points(point1, point2):
        mocker.patch.object(input.touch, "event", side_effect=[False, True, False])
        mocker.patch.object(input.touch.touch_driver, "irq_point", return_value=point1)
        mocker.patch.object(
            input.touch.touch_driver,
            "current_point",
            side_effect=[None, point1, point2, None, None],
        )

    # Full screen as single touch button
    input.touch.clear_regions()
    mock_points((75, 150), (77, 152))
    btn = input.wait_for_button(True)
    assert btn == BUTTON_TOUCH
    assert input.touch.current_index() == 0
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()

    # 2x2 array (4 quadrants) 200x200 pxls
    mock_points((75, 150), (77, 152))
    input.touch.add_y_delimiter(50)
    input.touch.add_y_delimiter(100)
    input.touch.add_y_delimiter(200)
    input.touch.add_x_delimiter(50)
    input.touch.add_x_delimiter(100)
    input.touch.add_x_delimiter(200)
    print("2nd case")
    btn = input.wait_for_button(True)

    assert btn == BUTTON_TOUCH
    assert input.touch.current_index() == 2  # (3º quadrant)


def test_touch_gestures(mocker, amigo):
    import krux
    from krux.input import Input, SWIPE_LEFT, SWIPE_RIGHT, SWIPE_UP, SWIPE_DOWN

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())

    def mock_points(point1, point2):
        mocker.patch.object(input.touch, "event", side_effect=[False, True, False])
        mocker.patch.object(input.touch.touch_driver, "irq_point", return_value=point1)
        mocker.patch.object(
            input.touch.touch_driver,
            "current_point",
            side_effect=[None, point1, point2, None, None],
        )

    # Swipe Right
    input.touch.clear_regions()
    mock_points((75, 150), (175, 152))
    btn = input.wait_for_button(True)
    assert btn == SWIPE_RIGHT
    krux.input.wdt.feed.assert_called()

    # Swipe Left
    input.touch.clear_regions()
    mock_points((175, 150), (75, 152))
    btn = input.wait_for_button(True)
    assert btn == SWIPE_LEFT
    krux.input.wdt.feed.assert_called()

    # Swipe Up
    input.touch.clear_regions()
    mock_points((75, 150), (75, 50))
    btn = input.wait_for_button(True)
    assert btn == SWIPE_UP
    krux.input.wdt.feed.assert_called()

    # Swipe Down
    input.touch.clear_regions()
    mock_points((75, 50), (75, 150))
    btn = input.wait_for_button(True)
    assert btn == SWIPE_DOWN
    krux.input.wdt.feed.assert_called()


def test_invalid_touch_delimiter(mocker, amigo):
    # Tries to add a delimiter outside screen area
    from krux.input import Input

    input = Input()

    mocker.patch.object(input.touch, "width", 200)
    mocker.patch.object(input.touch, "height", 200)
    with pytest.raises(ValueError):
        input.touch.add_x_delimiter(250)
    with pytest.raises(ValueError):
        input.touch.add_y_delimiter(250)


def test_rotary_encoder_handler(mocker, dock):
    from src.krux.rotary import RotaryEncoder, __handler__

    # Mock the encoder instance
    mock_encoder = mocker.MagicMock(spec=RotaryEncoder)
    mock_encoder.pin_1 = mocker.MagicMock()
    mock_encoder.pin_2 = mocker.MagicMock()

    for case in [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]:

        mock_encoder.pin_1.value.return_value = case[0]
        mock_encoder.pin_2.value.return_value = case[1]
        mocker.patch("src.krux.rotary.encoder", mock_encoder)
        __handler__()

    mock_encoder.process.assert_has_calls(
        [
            mocker.call((0, 0)),
            mocker.call((0, 1)),
            mocker.call((1, 0)),
            mocker.call((1, 1)),
        ]
    )


def test_encoder_spin_right(mocker, dock):
    import threading
    import krux
    from krux.input import Input, RELEASED, BUTTON_PAGE

    input = Input()
    mocker.patch.object(input.enter, "value", return_value=RELEASED)
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())

    def spin():
        # Here it will count a PAGE press
        time.sleep(0.1)
        krux.rotary.encoder.process((0, 1))

        # Keep spinning through all modes
        time.sleep(0.1)
        krux.rotary.encoder.process((1, 1))

        time.sleep(0.1)
        krux.rotary.encoder.process((1, 0))

        time.sleep(0.1)
        krux.rotary.encoder.process((0, 0))

    t = threading.Thread(target=spin)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_encoder_spin_left(mocker, dock):
    import threading
    import krux
    from krux.input import Input, RELEASED, BUTTON_PAGE_PREV

    input = Input()
    mocker.patch.object(input.enter, "value", return_value=RELEASED)
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())

    def spin():
        # Here it will change direction to Left
        time.sleep(0.1)
        krux.rotary.encoder.process((1, 0))

        # Here it will count a PAGE_PREV press
        time.sleep(0.1)
        krux.rotary.encoder.process((1, 1))

        # Keep spining through all modes
        time.sleep(0.1)
        krux.rotary.encoder.process((0, 1))

        time.sleep(0.1)
        krux.rotary.encoder.process((0, 0))

    t = threading.Thread(target=spin)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE_PREV
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_enter_button_press_when_buttons_not_active(mocker, amigo):
    import krux
    from krux.input import Input, RELEASED, PRESSED, ACTIVATING_BUTTONS

    input = Input()
    input = reset_input_states(mocker, input)
    input.buttons_active = False
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "enter_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "enter_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert input.buttons_active
    assert btn is ACTIVATING_BUTTONS
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_page_button_press_when_buttons_not_active(mocker, amigo):
    import krux
    from krux.input import Input, RELEASED, PRESSED, ACTIVATING_BUTTONS

    input = Input()
    input = reset_input_states(mocker, input)
    input.buttons_active = False
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "page_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "page_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert input.buttons_active
    assert btn is ACTIVATING_BUTTONS
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_page_prev_button_press_when_buttons_not_active(mocker, amigo):
    import krux
    from krux.input import Input, RELEASED, PRESSED, ACTIVATING_BUTTONS

    input = Input()
    input = reset_input_states(mocker, input)
    input.buttons_active = False
    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())
    mocker.patch.object(input, "enter_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "enter_value", side_effect=[RELEASED, PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert input.buttons_active
    assert btn is ACTIVATING_BUTTONS
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_enter_button_damaged(mocker, m5stickv):
    from krux.input import Input, PRESSED

    mocker.patch("krux.input.Input.enter_value", return_value=PRESSED)
    mocker.spy(Input, "button_integrity_check")

    input = Input()

    # Button enter is damaged, so the input.enter should be None
    # (but assert the button_integrity_check and enter_value was called too)
    input.button_integrity_check.assert_called_once()
    input.enter_value.assert_called_once()
    assert input.enter is None

    # Should return False since button is damaged
    assert not input.enter_event()


def test_page_button_damaged(mocker, m5stickv):
    from krux.input import Input, PRESSED

    mocker.patch("krux.input.Input.page_value", return_value=PRESSED)
    mocker.spy(Input, "button_integrity_check")

    input = Input()

    # Button page is damaged, so the input.page should be None
    # (but assert the button_integrity_check and page_value was called too)
    input.button_integrity_check.assert_called_once()
    input.page_value.assert_called_once()
    assert input.page is None

    # Should return False since button is damaged
    assert not input.page_event()


def test_page_prev_button_damaged(mocker, m5stickv):
    from krux.input import Input, PRESSED

    mocker.patch("krux.input.Input.page_prev_value", return_value=PRESSED)
    mocker.spy(Input, "button_integrity_check")

    input = Input()

    # Button page_prev is damaged, so the input.page_prev should be None
    # (but assert the button_integrity_check and page_prev_value was called too)
    input.button_integrity_check.assert_called_once()
    input.page_prev_value.assert_called_once()
    assert input.page_prev is None

    # Should return False since button is damaged
    assert not input.page_prev_event()


def test_touch_damaged(mocker, amigo):
    from krux.input import Input, PRESSED

    mocker.patch("krux.input.Input.touch_value", return_value=PRESSED)
    mocker.spy(Input, "button_integrity_check")

    input = Input()

    # Touch is damaged, so the input.touch should be None
    # (but assert the button_integrity_check and touch_value was called too)
    input.button_integrity_check.assert_called_once()
    input.touch_value.assert_called_once()
    assert input.touch is None

    # Should return False since touch is damaged, sowy!
    assert not input.touch_event()


def test_amigo_fast_forward_from_start(mocker, amigo):
    from krux.input import Input, BUTTON_PAGE, ACTIVATING_BUTTONS

    mocker.patch("time.ticks_ms", return_value=10)

    input = Input()
    # input.page_value = lambda: PRESSED
    value = input._detect_press_type(BUTTON_PAGE)
    assert value == ACTIVATING_BUTTONS


def test_fast_forward(mocker, m5stickv):
    from krux.input import Input, PRESSED, FAST_FORWARD, FAST_BACKWARD

    input = Input()
    input.page_value = mocker.MagicMock(return_value=PRESSED)

    assert input.wait_for_fastnav_button() == FAST_FORWARD

    input.page_value = mocker.MagicMock(return_value=None)

    input.page_prev_value = mocker.MagicMock(return_value=PRESSED)

    assert input.wait_for_fastnav_button() == FAST_BACKWARD


def test_fast_forward_yahboom(mocker, yahboom):
    from krux.input import Input, PRESSED, FAST_FORWARD

    input = Input()
    input.page_value = mocker.MagicMock(return_value=PRESSED)

    assert input.wait_for_fastnav_button() == FAST_FORWARD

    input.page_value = mocker.MagicMock(return_value=None)
    input.page_prev_value = mocker.MagicMock(return_value=PRESSED)

    # Test with BUTTON_PAGE_PREV PRESSED expect it to be FAST_FORWARD on yahboom
    assert input.wait_for_fastnav_button() == FAST_FORWARD


def test_fast_forward_no_pressed(mocker, m5stickv):
    from krux.input import Input, BUTTON_ENTER

    input = Input()
    input.wait_for_button = mocker.MagicMock(return_value=BUTTON_ENTER)

    assert input.wait_for_fastnav_button() == BUTTON_ENTER

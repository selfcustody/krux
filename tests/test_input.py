import pytest
import time


def reset_input_states(mocker, input):
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


def test_init(mocker, m5stickv):
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


def test_init_amigo_tft(mocker, amigo_tft):
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
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED

    input = Input()
    input = reset_input_states(mocker, input)
    mocker.patch.object(input, "enter_event", return_value=True)
    mocker.patch.object(input, "enter_value", return_value=PRESSED)

    def release():
        mocker.patch.object(time, "ticks_ms", return_value=1000)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=2000)
        time.sleep(0.1)
        mocker.patch.object(input, "enter_value", return_value=RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    input.wait_for_button()
    t.join()

    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_enter_released(mocker, m5stickv):
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_ENTER

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(input, "enter_event", return_value=True)
    mocker.patch.object(input, "enter_value", return_value=PRESSED)

    def release():
        mocker.patch.object(time, "ticks_ms", return_value=1000)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=1100)
        time.sleep(0.1)
        mocker.patch.object(input, "enter_value", return_value=RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_ENTER
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_page_released(mocker, m5stickv):
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_PAGE

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(input, "page_event", return_value=True)
    mocker.patch.object(input, "page_value", return_value=PRESSED)

    def release():
        mocker.patch.object(time, "ticks_ms", return_value=1000)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=1100)
        time.sleep(0.1)
        mocker.patch.object(input, "page_value", return_value=RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_page_prev_released(mocker, m5stickv):
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_PAGE_PREV

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(input, "page_prev_event", return_value=True)
    mocker.patch.object(input, "page_prev_value", return_value=PRESSED)

    def release():
        mocker.patch.object(time, "ticks_ms", return_value=1000)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=1100)
        time.sleep(0.1)
        mocker.patch.object(input, "page_prev_value", return_value=RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE_PREV
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_touch_released(mocker, amigo_tft):
    import threading
    import krux
    from krux.input import Input, BUTTON_TOUCH, PRESSED, RELEASED

    input = Input()
    input = reset_input_states(mocker, input)

    mocker.patch.object(input.touch, "event", return_value=True)
    mocker.patch.object(input, "touch_value", return_value=PRESSED)

    def release():
        mocker.patch.object(time, "ticks_ms", return_value=1000)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=1100)
        time.sleep(0.1)
        mocker.patch.object(input, "touch_value", return_value=RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_TOUCH
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_returns_when_nonblocking(mocker, m5stickv):
    import threading
    import krux
    from krux.input import Input, QR_ANIM_PERIOD

    input = Input()
    input = reset_input_states(mocker, input)

    def nothing():
        mocker.patch.object(time, "ticks_ms", return_value=0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=QR_ANIM_PERIOD + 1)

    t = threading.Thread(target=nothing)
    t.start()
    btn = input.wait_for_button(False)
    t.join()

    assert btn is None
    krux.input.wdt.feed.assert_called()


def test_long_press_page_simulates_swipe_left(mocker, m5stickv):
    import krux
    from krux.input import Input, RELEASED, PRESSED, SWIPE_LEFT

    input = Input()
    input = reset_input_states(mocker, input)

    # Create a table of states for button events, values and time ticks
    mocker.patch.object(time, "ticks_ms", side_effect=[0, 100, 200, 300, 1400, 1500])
    mocker.patch.object(input, "page_event", side_effect=[False, True, False])
    mocker.patch.object(input, "page_value", side_effect=[PRESSED, PRESSED, RELEASED])

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert btn == SWIPE_LEFT
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_long_press_page_prev_simulates_swipe_right(mocker, m5stickv):
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, SWIPE_RIGHT, LONG_PRESS_PERIOD

    input = Input()
    input = reset_input_states(mocker, input)

    # Create a table of states for button events, values and time ticks
    mocker.patch.object(time, "ticks_ms", side_effect=[0, 100, 200, 300, 1400, 1500])
    mocker.patch.object(input, "page_prev_event", side_effect=[False, True, False])
    mocker.patch.object(
        input, "page_prev_value", side_effect=[PRESSED, PRESSED, RELEASED]
    )

    assert input.entropy == 0

    btn = input.wait_for_button(True)

    assert btn == SWIPE_RIGHT
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_touch_indexing(mocker, amigo_tft):
    import threading
    import krux
    from krux.input import Input, BUTTON_TOUCH

    input = Input()
    input = reset_input_states(mocker, input)

    elapsed_time = 0

    def time_control(point1, point2):
        nonlocal elapsed_time
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)
        time.sleep(0.1)
        elapsed_time += 200
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)
        # touch on 3º quadrant
        mocker.patch.object(input.touch, "event", return_value=True)
        mocker.patch.object(input.touch.touch_driver, "irq_point", return_value=point1)
        mocker.patch.object(
            input.touch.touch_driver, "current_point", return_value=point1
        )
        time.sleep(0.1)
        mocker.patch.object(input.touch, "event", return_value=False)
        time.sleep(0.1)
        elapsed_time += 200
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)
        # touch slightly sideways before release
        mocker.patch.object(
            input.touch.touch_driver, "current_point", return_value=point2
        )
        time.sleep(0.1)
        elapsed_time += 200
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)
        # release touch
        mocker.patch.object(
            input.touch.touch_driver, "current_point", return_value=None
        )
        time.sleep(0.1)
        elapsed_time += 200
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)

    # full screen as single touch button
    input.touch.clear_regions()
    t = threading.Thread(target=time_control, args=((75, 150), (77, 152)))
    t.start()
    btn = input.wait_for_button(True)
    t.join()
    assert btn == BUTTON_TOUCH
    assert input.touch.current_index() == 0
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()

    # 2x2 array (4 quadrants) 200x200 pxls
    input.touch.add_y_delimiter(50)
    input.touch.add_y_delimiter(100)
    input.touch.add_y_delimiter(200)
    input.touch.add_x_delimiter(50)
    input.touch.add_x_delimiter(100)
    input.touch.add_x_delimiter(200)
    t = threading.Thread(target=time_control, args=((75, 150), (77, 152)))
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_TOUCH
    assert input.touch.current_index() == 2  # (3º quadrant)


def test_touch_gestures(mocker, amigo_tft):
    # TODO: Replace threads by side_effect for stability
    import threading
    import krux
    from krux.input import Input, SWIPE_LEFT, SWIPE_RIGHT, SWIPE_UP, SWIPE_DOWN

    input = Input()
    input = reset_input_states(mocker, input)

    elapsed_time = 0

    def time_control(point1, point2):
        nonlocal elapsed_time

        elapsed_time += 200
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)
        mocker.patch.object(input.touch, "event", return_value=True)
        mocker.patch.object(input.touch.touch_driver, "irq_point", return_value=point1)
        mocker.patch.object(
            input.touch.touch_driver, "current_point", return_value=point1
        )
        time.sleep(0.1)
        # Detect press event
        elapsed_time += 200
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)
        time.sleep(0.1)
        mocker.patch.object(input.touch.touch_driver, "event", return_value=False)
        time.sleep(0.1)
        # Swipe
        mocker.patch.object(
            input.touch.touch_driver, "current_point", return_value=point2
        )
        time.sleep(0.1)
        # Release
        elapsed_time += 200
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)
        mocker.patch.object(
            input.touch.touch_driver, "current_point", return_value=None
        )
        time.sleep(0.1)
        elapsed_time += 200
        mocker.patch.object(time, "ticks_ms", return_value=elapsed_time)

    # Swipe Right
    input.touch.clear_regions()
    t = threading.Thread(target=time_control, args=((75, 150), (175, 152)))
    t.start()
    btn = input.wait_for_button(True)
    t.join()
    assert btn == SWIPE_RIGHT
    krux.input.wdt.feed.assert_called()

    # Swipe Left
    input.touch.clear_regions()
    t = threading.Thread(target=time_control, args=((175, 150), (75, 152)))
    t.start()
    btn = input.wait_for_button(True)
    t.join()
    assert btn == SWIPE_LEFT
    krux.input.wdt.feed.assert_called()

    # Swipe Up
    input.touch.clear_regions()
    t = threading.Thread(target=time_control, args=((75, 150), (75, 50)))
    t.start()
    btn = input.wait_for_button(True)
    t.join()
    assert btn == SWIPE_UP
    krux.input.wdt.feed.assert_called()

    # Swipe Down
    input.touch.clear_regions()
    t = threading.Thread(target=time_control, args=((75, 50), (75, 150)))
    t.start()
    btn = input.wait_for_button(True)
    t.join()
    assert btn == SWIPE_DOWN
    krux.input.wdt.feed.assert_called()


def test_invalid_touch_delimiter(mocker, amigo_tft):
    # Tries to add a delimiter outside screen area
    from krux.input import Input

    input = Input()

    mocker.patch.object(input.touch, "width", 200)
    mocker.patch.object(input.touch, "height", 200)
    with pytest.raises(ValueError):
        input.touch.add_x_delimiter(250)
    with pytest.raises(ValueError):
        input.touch.add_y_delimiter(250)


def test_encoder_spin_right(mocker, dock):
    import threading
    import krux
    from krux.input import Input, RELEASED, BUTTON_PAGE

    input = Input()
    mocker.patch.object(input.enter, "value", return_value=RELEASED)

    def spin():
        mocker.patch.object(time, "ticks_ms", return_value=0)

        # Here it will count a PAGE press
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=100)
        krux.rotary.encoder.process((0, 1))

        # Keep spining through all modes
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=200)
        krux.rotary.encoder.process((1, 1))

        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=300)
        krux.rotary.encoder.process((1, 0))

        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=400)
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

    def spin():
        mocker.patch.object(time, "ticks_ms", return_value=0)

        # Here it will change direction to Left
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=100)
        krux.rotary.encoder.process((1, 0))

        # Here it will count a PAGE_PREV press
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=200)
        krux.rotary.encoder.process((1, 1))

        # Keep spining through all modes
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=300)
        krux.rotary.encoder.process((0, 1))

        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=400)
        krux.rotary.encoder.process((0, 0))

    t = threading.Thread(target=spin)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE_PREV
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_enter_button_press_when_buttons_not_active(mocker, amigo_tft):
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, ACTIVATING_BUTTONS

    input = Input()
    input = reset_input_states(mocker, input)
    input.buttons_active = False

    def release():
        mocker.patch.object(time, "ticks_ms", return_value=0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=100)
        mocker.patch.object(input, "enter_event", return_value=True)
        mocker.patch.object(input, "enter_value", return_value=PRESSED)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=200)
        mocker.patch.object(input, "enter_event", return_value=False)
        time.sleep(0.1)
        mocker.patch.object(input, "enter_value", return_value=RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert input.buttons_active
    assert btn is ACTIVATING_BUTTONS
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_page_button_press_when_buttons_not_active(mocker, amigo_tft):
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, ACTIVATING_BUTTONS

    input = Input()
    input = reset_input_states(mocker, input)
    input.buttons_active = False

    def release():
        mocker.patch.object(time, "ticks_ms", return_value=0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=100)
        mocker.patch.object(input, "page_event", return_value=True)
        mocker.patch.object(input, "page_value", return_value=PRESSED)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=200)
        mocker.patch.object(input, "page_event", return_value=False)
        mocker.patch.object(input, "page_value", return_value=RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert input.buttons_active
    assert btn is ACTIVATING_BUTTONS
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_page_prev_button_press_when_buttons_not_active(mocker, amigo_tft):
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, ACTIVATING_BUTTONS

    input = Input()
    input = reset_input_states(mocker, input)
    input.buttons_active = False

    def release():
        mocker.patch.object(time, "ticks_ms", return_value=0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=100)
        mocker.patch.object(input, "page_prev_event", return_value=True)
        mocker.patch.object(input, "page_prev_value", return_value=PRESSED)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", return_value=200)
        mocker.patch.object(input, "page_prev_event", return_value=False)
        mocker.patch.object(input, "page_prev_value", return_value=RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert input.buttons_active
    assert btn is ACTIVATING_BUTTONS
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()

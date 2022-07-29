import pytest


def mock_modules(mocker):
    mocker.patch("krux.input.fm.register", new=mocker.MagicMock())
    mocker.patch("krux.input.GPIO", new=mocker.MagicMock())


def test_init(mocker, m5stickv):
    mock_modules(mocker)
    import krux
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)
    krux.input.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["BUTTON_A"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_B"], mocker.ANY),
        ]
    )
    assert (
        krux.input.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS21"
    )
    assert (
        krux.input.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert input.enter is not None
    assert input.page is not None

    assert krux.input.GPIO.call_count == 2
    assert (
        krux.input.GPIO.call_args_list[0].args[0]._extract_mock_name()
        == "mock.GPIOHS21"
    )
    assert (
        krux.input.GPIO.call_args_list[1].args[0]._extract_mock_name()
        == "mock.GPIOHS22"
    )


def test_init_amigo(mocker, amigo):
    mock_modules(mocker)
    import krux
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)
    krux.input.fm.register.assert_has_calls(
        [
            mocker.call(board.config["krux"]["pins"]["BUTTON_A"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_B"], mocker.ANY),
            mocker.call(board.config["krux"]["pins"]["BUTTON_C"], mocker.ANY),
        ]
    )
    assert (
        krux.input.fm.register.call_args_list[0].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS21"
    )
    assert (
        krux.input.fm.register.call_args_list[1].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS22"
    )
    assert (
        krux.input.fm.register.call_args_list[2].args[1]._extract_mock_name()
        == "mock.fm.fpioa.GPIOHS0"
    )
    assert input.enter is not None
    assert input.page is not None
    assert input.page_prev is not None

    assert krux.input.GPIO.call_count == 3
    assert (
        krux.input.GPIO.call_args_list[0].args[0]._extract_mock_name()
        == "mock.GPIOHS21"
    )
    assert (
        krux.input.GPIO.call_args_list[1].args[0]._extract_mock_name()
        == "mock.GPIOHS22"
    )
    assert (
        krux.input.GPIO.call_args_list[2].args[0]._extract_mock_name() == "mock.GPIOHS0"
    )


def test_init_dock(mocker, dock):
    mock_modules(mocker)

    import krux
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)
    krux.input.fm.register.assert_has_calls(
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
        krux.input.fm.register.call_args_list[0].args[1]._extract_mock_name()
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

    assert krux.input.GPIO.call_count == 1
    assert krux.rotary.GPIO.call_count == 2
    assert (
        krux.input.GPIO.call_args_list[0].args[0]._extract_mock_name()
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


def test_wait_for_button_blocks_until_enter_released(mocker, m5stickv):
    mock_modules(mocker)
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_ENTER

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)

    def release():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 100)
        mocker.patch.object(input.enter, "value", new=lambda: PRESSED)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 200)
        mocker.patch.object(input.enter, "value", new=lambda: RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_ENTER
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_page_released(mocker, m5stickv):
    mock_modules(mocker)
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_PAGE

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)

    def release():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 100)
        mocker.patch.object(input, "page_value", new=lambda: PRESSED)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 200)
        mocker.patch.object(input, "page_value", new=lambda: RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_page_prev_released(mocker, amigo):
    mock_modules(mocker)
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_PAGE_PREV

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)
    mocker.patch.object(input.touch, "current_state", new=lambda: 0)

    def click():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(0.5)
        mocker.patch.object(time, "ticks_ms", new=lambda: 500)
        # if input.page_prev, "value" is mocked, in what apparently is bug,
        # other input buttons get the same "value", invalidating the test
        mocker.patch.object(input, "page_prev_value", new=lambda: PRESSED)
        time.sleep(0.5)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1000)
        mocker.patch.object(input, "page_prev_value", new=lambda: RELEASED)

    assert input.entropy == 0

    # first one click to enable physical buttons
    t = threading.Thread(target=click)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    # than other click to be counted
    t = threading.Thread(target=click)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE_PREV
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_touch_released(mocker, amigo):
    mock_modules(mocker)
    import threading
    import krux
    from krux.input import Input, RELEASED, BUTTON_TOUCH

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)
    mocker.patch.object(input.touch, "current_state", new=lambda: 0)

    def click():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(0.5)
        mocker.patch.object(time, "ticks_ms", new=lambda: 500)
        mocker.patch.object(input.touch, "current_state", new=lambda: 1)
        time.sleep(0.5)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1000)
        mocker.patch.object(input.touch, "current_state", new=lambda: 0)

    assert input.entropy == 0

    t = threading.Thread(target=click)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_TOUCH
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_waits_for_existing_press_to_release(mocker, m5stickv):
    mock_modules(mocker)
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, BUTTON_ENTER

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)

    def release():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 100)
        mocker.patch.object(input.page, "value", new=lambda: RELEASED)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 200)
        mocker.patch.object(input.enter, "value", new=lambda: PRESSED)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 300)
        mocker.patch.object(input.enter, "value", new=lambda: RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_ENTER
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_returns_when_nonblocking(mocker, m5stickv):
    mock_modules(mocker)
    import threading
    import krux
    from krux.input import Input, RELEASED

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)

    def time_control():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1000)

    t = threading.Thread(target=time_control)
    t.start()
    btn = input.wait_for_button(False)
    t.join()

    assert btn is None
    krux.input.wdt.feed.assert_called()


def test_long_press_page_simulates_swipe_left(mocker, m5stickv):
    mock_modules(mocker)
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, SWIPE_LEFT

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)

    def release():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 100)
        mocker.patch.object(input, "page_value", new=lambda: PRESSED)
        time.sleep(1.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1200)
        mocker.patch.object(input, "page_value", new=lambda: RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == SWIPE_LEFT
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_long_press_page_prev_simulates_swipe_right(mocker, m5stickv):
    mock_modules(mocker)
    import threading
    import krux
    from krux.input import Input, RELEASED, PRESSED, SWIPE_RIGHT

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)

    def release():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 100)
        mocker.patch.object(input, "page_prev_value", new=lambda: PRESSED)
        time.sleep(1.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1200)
        mocker.patch.object(input, "page_prev_value", new=lambda: RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == SWIPE_RIGHT
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_touch_indexing(mocker, amigo):
    import threading
    import krux
    from krux.input import Input, RELEASED, BUTTON_TOUCH

    input = Input()

    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)
    mocker.patch.object(input.touch.touch_driver, "current_point", new=lambda: None)

    mocker.elapsed_time = 0
    mocker.point = (75, 150)
    mocker.point_2 = (77, 152)

    def time_control():
        import time

        def timed_sleep(period):
            time.sleep(period)
            mocker.elapsed_time += period * 1000

        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)
        timed_sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)
        # touch on 3º quadrant
        mocker.patch.object(
            input.touch.touch_driver, "current_point", new=lambda: mocker.point
        )
        timed_sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)
        # touch slightly sideways before release
        mocker.patch.object(
            input.touch.touch_driver, "current_point", new=lambda: mocker.point_2
        )
        timed_sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)
        mocker.patch.object(input.touch.touch_driver, "current_point", new=lambda: None)
        timed_sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)

    # full screen as single touch button
    input.touch.clear_regions()
    t = threading.Thread(target=time_control)
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
    t = threading.Thread(target=time_control)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_TOUCH
    assert input.touch.current_index() == 2  # (3º quadrant)

    # Touch inside - 50 < x < 200
    mocker.patch.object(input.touch, "state", input.touch.idle)
    input.touch.extract_index((60, 60))
    assert input.touch.state == input.touch.press

    # Touch outside - x > 200
    input.touch.state = input.touch.idle
    input.touch.extract_index((250, 60))
    assert input.touch.state == input.touch.release

    # Touch outside - y > 200
    input.touch.state = input.touch.idle
    input.touch.extract_index((60, 250))
    assert input.touch.state == input.touch.release


def test_touch_gestures(mocker, amigo):
    import threading
    import krux
    from krux.input import Input, RELEASED, SWIPE_LEFT, SWIPE_RIGHT

    input = Input()

    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)
    mocker.patch.object(input.touch.touch_driver, "current_point", new=lambda: None)

    mocker.elapsed_time = 0
    mocker.point = (75, 150)
    mocker.point_2 = (175, 152)

    def time_control():
        import time

        def timed_sleep(period):
            time.sleep(period)
            mocker.elapsed_time += period * 1000

        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)
        timed_sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)
        # touch on 3º quadrant
        mocker.patch.object(
            input.touch.touch_driver, "current_point", new=lambda: mocker.point
        )
        timed_sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)
        # swipe 100 pixels to right
        mocker.patch.object(
            input.touch.touch_driver, "current_point", new=lambda: mocker.point_2
        )
        timed_sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)
        mocker.patch.object(input.touch.touch_driver, "current_point", new=lambda: None)
        timed_sleep(0.1)
        mocker.patch.object(time, "ticks_ms", new=lambda: mocker.elapsed_time)

    # Swipe Right
    input.touch.clear_regions()
    t = threading.Thread(target=time_control)
    t.start()
    btn = input.wait_for_button(True)
    t.join()
    assert btn == SWIPE_RIGHT
    krux.input.wdt.feed.assert_called()

    # Swipe Left
    mocker.point = (175, 150)
    mocker.point_2 = (75, 152)
    input.touch.clear_regions()
    t = threading.Thread(target=time_control)
    t.start()
    btn = input.wait_for_button(True)
    t.join()
    assert btn == SWIPE_LEFT
    krux.input.wdt.feed.assert_called()


def test_invalid_touch_delimiter(mocker, amigo):
    """Tries to add a delimiter outside screen area"""
    import krux
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
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)

    def spin():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)

        # Here it will count a PAGE press
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 200)
        krux.rotary.encoder.process((0, 1))

        # Keep spining through all modes
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 400)
        krux.rotary.encoder.process((1, 1))

        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 600)
        krux.rotary.encoder.process((1, 0))

        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 800)
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
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)

    def spin():
        import time

        mocker.patch.object(time, "ticks_ms", new=lambda: 0)

        # Here it will change direction to Left
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1000)
        krux.rotary.encoder.process((1, 0))

        # Here it will count a PAGE_PREV press
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1200)
        krux.rotary.encoder.process((1, 1))

        # Keep spining through all modes
        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1400)
        krux.rotary.encoder.process((0, 1))

        time.sleep(0.2)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1600)
        krux.rotary.encoder.process((0, 0))

    t = threading.Thread(target=spin)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE_PREV
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()

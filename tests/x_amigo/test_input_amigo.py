from ..shared_mocks import *
from krux.input import BUTTON_PAGE_PREV, BUTTON_TOUCH, PRESSED, RELEASED
import threading
import sys


def mock_modules(mocker):
    mocker.patch("krux.input.fm.register", new=mock.MagicMock())
    mocker.patch("krux.input.GPIO", new=mock.MagicMock())


def test_init(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input
    import board

    input = Input()

    assert isinstance(input, Input)
    krux.input.fm.register.assert_has_calls(
        [
            mock.call(board.config["krux"]["pins"]["BUTTON_A"], mock.ANY),
            mock.call(board.config["krux"]["pins"]["BUTTON_B"], mock.ANY),
            mock.call(board.config["krux"]["pins"]["BUTTON_C"], mock.ANY),
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


def test_wait_for_button_blocks_until_touch_released(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)
    mocker.patch.object(input.touch, "current_state", new=lambda: 0)

    def click():
        time.sleep(0.5)
        mocker.patch.object(input.touch, "current_state", new=lambda: 1)
        time.sleep(0.5)
        mocker.patch.object(input.touch, "current_state", new=lambda: 0)

    assert input.entropy == 0

    t = threading.Thread(target=click)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_TOUCH
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_page_prev_released(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)
    mocker.patch.object(input.touch, "current_state", new=lambda: 0)

    def click():
        time.sleep(0.5)
        # if input.page_prev, "value" is mocked, in what apparently is bug,
        # other input buttons get the same "value", invalidating the test
        mocker.patch.object(input, "page_prev_value", new=lambda: PRESSED)
        time.sleep(0.5)
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


def test_touch_indexing(mocker):
    import krux
    from krux.input import Input

    input = Input()

    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page_prev, "value", new=lambda: RELEASED)
    mocker.patch.object(input.touch.touch_driver, "current_point", new=lambda: None)

    mocker.elapsed_time = 0
    mocker.point = (75, 150)
    mocker.point_2 = (77, 152)

    def time_control():
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
    input.touch.add_y_delimiter(0)
    input.touch.add_y_delimiter(100)
    input.touch.add_y_delimiter(200)
    input.touch.add_x_delimiter(0)
    input.touch.add_x_delimiter(100)
    input.touch.add_x_delimiter(200)
    t = threading.Thread(target=time_control)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_TOUCH
    assert input.touch.current_index() == 2  # (3º quadrant)

from krux.input import BUTTON_ENTER, BUTTON_PAGE, PRESSED, RELEASED
from .shared_mocks import *
import threading


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


def test_wait_for_button_blocks_until_enter_released(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)

    def release():
        time.sleep(1)
        mocker.patch.object(input.enter, "value", new=lambda: PRESSED)
        time.sleep(1)
        mocker.patch.object(input.enter, "value", new=lambda: RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_ENTER
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_blocks_until_page_released(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)

    def release():
        time.sleep(1)
        mocker.patch.object(input, "page_value", new=lambda: PRESSED)
        time.sleep(1)
        mocker.patch.object(input, "page_value", new=lambda: RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_PAGE
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_waits_for_existing_press_to_release(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: PRESSED)

    def release():
        time.sleep(1)
        mocker.patch.object(input.page, "value", new=lambda: RELEASED)
        time.sleep(1)
        mocker.patch.object(input.enter, "value", new=lambda: PRESSED)
        time.sleep(1)
        mocker.patch.object(input.enter, "value", new=lambda: RELEASED)

    assert input.entropy == 0

    t = threading.Thread(target=release)
    t.start()
    btn = input.wait_for_button(True)
    t.join()

    assert btn == BUTTON_ENTER
    assert input.entropy > 0
    krux.input.wdt.feed.assert_called()


def test_wait_for_button_returns_when_nonblocking(mocker):
    mock_modules(mocker)
    import krux
    from krux.input import Input

    input = Input()
    mocker.patch.object(input.enter, "value", new=lambda: RELEASED)
    mocker.patch.object(input.page, "value", new=lambda: RELEASED)

    def time_control():
        mocker.patch.object(time, "ticks_ms", new=lambda: 0)
        time.sleep(1)
        mocker.patch.object(time, "ticks_ms", new=lambda: 1000)

    t = threading.Thread(target=time_control)
    t.start()
    btn = input.wait_for_button(False)
    t.join()

    assert btn is None
    krux.input.wdt.feed.assert_called()

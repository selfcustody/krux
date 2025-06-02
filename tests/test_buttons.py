import pytest


@pytest.fixture
def mock_tactile_buttons(mocker):
    from krux.buttons import fm, buttons_control

    mocker.patch.object(fm, "register")
    mock_gpio = mocker.MagicMock()
    mocker.patch("Maix.GPIO", return_value=mock_gpio)

    def fake_init_enter(pin):
        buttons_control.enter = mock_gpio

    def fake_init_page(pin):
        buttons_control.page = mock_gpio

    def fake_init_page_prev(pin):
        buttons_control.page_prev = mock_gpio

    mocker.patch.object(buttons_control, "init_enter", fake_init_enter)
    mocker.patch.object(buttons_control, "init_page", fake_init_page)
    mocker.patch.object(buttons_control, "init_page_prev", fake_init_page_prev)

    buttons_control.enter_event_flag = False
    buttons_control.page_event_flag = False
    buttons_control.page_prev_event_flag = False

    mocker.spy(buttons_control, "event_handler")

    return buttons_control


def test_handler(mocker, m5stickv, mock_tactile_buttons):
    from krux.buttons import __handler__

    calls = []
    for pin in [10, 11, 12]:
        __handler__(pin)
        calls.append(mocker.call(pin))

    mock_tactile_buttons.event_handler.assert_has_calls(calls)


def test_tactile_buttons_initialization(mocker, m5stickv):
    from krux.buttons import buttons_control

    assert buttons_control.enter is None
    assert buttons_control.page is None
    assert buttons_control.page_prev is None
    assert not buttons_control.enter_event_flag
    assert not buttons_control.page_event_flag
    assert not buttons_control.page_prev_event_flag


def test_generic_button_default_values(mocker, m5stickv, mock_tactile_buttons):
    from krux.buttons import Button, RELEASED

    button = Button()

    # Assert button methods return default values
    assert button.value() == RELEASED
    assert not button.event()
    mock_tactile_buttons.event_handler.assert_not_called()


def test_generic_button_enter_default_values(mocker, m5stickv, mock_tactile_buttons):
    from krux.buttons import ButtonEnter, RELEASED

    mocker.patch.object(mock_tactile_buttons, "init_enter", lambda pin: None)
    button = ButtonEnter(mock_tactile_buttons.enter)

    # Assert button enter methods return default values
    assert button.value() == RELEASED
    assert not button.event()
    mock_tactile_buttons.event_handler.assert_not_called()


def test_generic_button_page_default_values(mocker, m5stickv, mock_tactile_buttons):
    from krux.buttons import ButtonPage, RELEASED

    mocker.patch.object(mock_tactile_buttons, "init_page", lambda pin: None)
    button = ButtonPage(mock_tactile_buttons.enter)

    # Assert button page methods return default values
    assert button.value() == RELEASED
    assert not button.event()
    mock_tactile_buttons.event_handler.assert_not_called()


def test_generic_button_page_prev_default_values(
    mocker, m5stickv, mock_tactile_buttons
):
    from krux.buttons import ButtonPagePrev, RELEASED

    mocker.patch.object(mock_tactile_buttons, "init_page_prev", lambda pin: None)
    button = ButtonPagePrev(mock_tactile_buttons.enter)

    # Assert button page prev methods return default values
    assert button.value() == RELEASED
    assert not button.event()
    mock_tactile_buttons.event_handler.assert_not_called()


def test_button_enter(mocker, m5stickv, mock_tactile_buttons):
    from krux.buttons import ButtonEnter

    mock_tactile_buttons.enter = 10
    button = ButtonEnter(mock_tactile_buttons.enter)

    # Simulate button pressed
    mock_tactile_buttons.event_handler(mock_tactile_buttons.enter)

    # When button is pressed, an interrupt is generated and button_event_flag is set.
    # When button.event() method is called, it will return True if there has been an event,
    # but before returning, it will clear button_event_flag.
    assert button.event()
    assert not mock_tactile_buttons.enter_event_flag
    mock_tactile_buttons.event_handler.assert_called_once_with(
        mock_tactile_buttons.enter
    )


def test_button_page(mocker, m5stickv, mock_tactile_buttons):
    from krux.buttons import ButtonPage

    mock_tactile_buttons.page = 11
    button = ButtonPage(mock_tactile_buttons.page)

    # Simulate button pressed
    mock_tactile_buttons.event_handler(mock_tactile_buttons.page)

    # When button is pressed, an interrupt is generated and button_event_flag is set.
    # When button.event() method is called, it will return True if there has been an event,
    # but before returning, it will clear button_event_flag.
    assert button.event()
    assert not mock_tactile_buttons.page_event_flag
    mock_tactile_buttons.event_handler.assert_called_once_with(
        mock_tactile_buttons.page
    )


def test_button_page_prev(mocker, m5stickv, mock_tactile_buttons):
    from krux.buttons import ButtonPagePrev

    mock_tactile_buttons.page_prev = 12
    button = ButtonPagePrev(mock_tactile_buttons.page_prev)

    # Simulate button pressed
    mock_tactile_buttons.event_handler(mock_tactile_buttons.page_prev)

    # When button is pressed, an interrupt is generated and button_event_flag is set.
    # When button.event() method is called, it will return True if there has been an event,
    # but before returning, it will clear button_event_flag.
    assert button.event()
    assert not mock_tactile_buttons.page_prev_event_flag
    mock_tactile_buttons.event_handler.assert_called_once_with(
        mock_tactile_buttons.page_prev
    )

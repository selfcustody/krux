
def test_tactile_buttons_initialization(mocker, m5stickv):
    from krux.buttons import buttons_control

    assert buttons_control.enter is None
    assert buttons_control.page is None
    assert buttons_control.page_prev is None
    assert not buttons_control.enter_event_flag
    assert not buttons_control.page_event_flag
    assert not buttons_control.page_prev_event_flag

def test_button_enter_event(mocker, m5stickv):
    from krux.buttons import ButtonEnter, buttons_control
    # Simulate button enter pin
    mocked_pin = 10
    pin = mocked_pin
    button_enter = ButtonEnter(pin)
    # Overwrite the pin's MagicMock with the mocked pin number
    buttons_control.enter = mocked_pin
    
    # Simulate button press
    buttons_control.event_handler(pin)
    assert button_enter.event()
    # Assert that the event flag is reset
    assert not button_enter.event()

def test_button_page_event(mocker, m5stickv):
    from krux.buttons import ButtonPage, buttons_control
    # Simulate button page pin
    mocked_pin = 11
    pin = mocked_pin
    button_page = ButtonPage(pin)
    # Overwrite the pin's MagicMock with the mocked pin number
    buttons_control.page = mocked_pin
    
    # Simulate button press
    buttons_control.event_handler(pin)
    assert button_page.event()
    # Assert that the event flag is reset
    assert not button_page.event()

def test_button_page_prev_event(mocker, m5stickv):
    from krux.buttons import ButtonPagePrev, buttons_control
    # Simulate button page pin
    mocked_pin = 12
    pin = mocked_pin
    button_page_prev = ButtonPagePrev(pin)
    # Overwrite the pin's MagicMock with the mocked pin number
    buttons_control.page_prev = mocked_pin
    
    # Simulate button press
    buttons_control.event_handler(pin)
    assert button_page_prev.event()
    # Assert that the event flag is reset
    assert not button_page_prev.event()

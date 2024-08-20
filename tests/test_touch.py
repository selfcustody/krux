import time
from .test_input import mock_timer_ticks


def test_touch_event(mocker, amigo):
    from krux.touch import Touch
    import board

    Y_REGIONS = (0, 40, 80, 120, 160, 200)

    # Simulate touch points on region 3 - 120 to 160
    TOUCH_POINT_1 = (75, 150)
    TOUCH_POINT_2 = (77, 152)

    EVENTS = [False, True, False, False]
    POINTS = [TOUCH_POINT_1, TOUCH_POINT_2, None, None]

    mocker.patch("krux.touchscreens.ft6x36.FT6X36.event", side_effect=EVENTS)
    mocker.patch("krux.touchscreens.ft6x36.FT6X36.current_point", side_effect=POINTS)

    mocker.patch.object(time, "ticks_ms", side_effect=mock_timer_ticks())

    touch = Touch(
        board.config["lcd"]["width"],
        board.config["lcd"]["height"],
        board.config["krux"]["pins"]["TOUCH_IRQ"],
    )
    touch.y_regions = Y_REGIONS
    touch.touch_driver.irq_point = TOUCH_POINT_1  # Simulate touch event

    for _ in range(len(EVENTS)):
        event = touch.event(validate_position=True)
    assert event == False
    assert touch.current_index() == 3

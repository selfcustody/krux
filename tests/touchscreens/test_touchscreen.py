import pytest


@pytest.fixture
def bad_touch_cls():
    from krux.touchscreens import Touchscreen

    class BadTouch(Touchscreen):
        def __init__(self):
            pass

    return BadTouch


def test_init_fails(mocker, amigo_tft):
    from krux.touchscreens import Touchscreen

    with pytest.raises(NotImplementedError):
        Touchscreen()


def test_current_point_fails(mocker, amigo_tft, bad_touch_cls):
    touch = bad_touch_cls()

    with pytest.raises(NotImplementedError):
        touch.current_point()

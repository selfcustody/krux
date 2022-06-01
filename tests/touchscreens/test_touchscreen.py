import pytest
from krux.touchscreens import Touchscreen


class BadTouch(Touchscreen):
    def __init__(self):
        pass


def test_init_fails():
    with pytest.raises(NotImplementedError):
        Touchscreen()


def test_current_point_fails():
    touch = BadTouch()

    with pytest.raises(NotImplementedError):
        touch.current_point()

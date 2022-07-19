from ..shared_mocks import *
import sys


def test_change_to_dock(mocker):
    if "board" in sys.modules:
        del sys.modules["board"]
    sys.modules["board"] = board_dock()
    import board

    import krux.input
    importlib.reload(krux.input)

    krux.input.GPIO.reset_mock()
    krux.input.fm.register.reset_mock()

    import krux.pages

    importlib.reload(krux.pages)

    assert "ENCODER" in board.config["krux"]["pins"]

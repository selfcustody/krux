from ..shared_mocks import *
import sys


def test_change_to_amigo(mocker):
    if "board" in sys.modules:
        del sys.modules["board"]
    sys.modules["board"] = board_amigo()
    import board
    import krux.input

    importlib.reload(krux.input)
    import krux.pages

    importlib.reload(krux.pages)

    assert board.config["krux"]["pins"]["BUTTON_C"] == 23
    assert board.config["lcd"]["invert"] == 1

def test_init(mocker, m5stickv):
    from krux.power import _PowerManager

    manager = _PowerManager()

    assert isinstance(manager, _PowerManager)


def test_init_with_amigo(mocker, amigo):
    from krux.power import _PowerManager

    manager = _PowerManager()

    assert isinstance(manager, _PowerManager)


def test_init_without_pmu(mocker, m5stickv):
    import sys

    if "pmu" in sys.modules:
        del sys.modules["pmu"]
    from krux.power import _PowerManager

    manager = _PowerManager()

    assert isinstance(manager, _PowerManager)
    assert manager.pmu is None


def test_init_with_amigo_without_pmu(mocker, amigo):
    import sys

    if "pmu" in sys.modules:
        del sys.modules["pmu"]
    from krux.power import _PowerManager

    manager = _PowerManager()

    assert isinstance(manager, _PowerManager)
    assert manager.pmu is None


def test_shutdown(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    from krux.power import _PowerManager
    import machine
    import sys

    manager = _PowerManager()

    manager.shutdown()

    machine.reset.assert_called()
    sys.exit.assert_called()


def test_shutdown_with_amigo(mocker, amigo):
    mocker.patch("sys.exit")
    import krux
    from krux.power import _PowerManager
    import machine
    import sys

    manager = _PowerManager()

    manager.shutdown()

    machine.reset.assert_called()
    sys.exit.assert_called()


def test_shutdown_without_pmu(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    import machine
    import sys

    if "pmu" in sys.modules:
        del sys.modules["pmu"]
    from krux.power import _PowerManager

    manager = _PowerManager()

    manager.shutdown()

    machine.reset.assert_called()
    sys.exit.assert_called()


def test_reboot(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    from krux.power import _PowerManager
    import machine
    import sys

    manager = _PowerManager()

    manager.reboot()

    machine.reset.assert_called()
    sys.exit.assert_called()


def test_reboot_with_amigo(mocker, amigo):
    mocker.patch("sys.exit")
    import krux
    from krux.power import _PowerManager
    import machine
    import sys

    manager = _PowerManager()

    manager.reboot()

    machine.reset.assert_called()
    sys.exit.assert_called()


def test_reboot_without_pmu(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    import sys
    import machine
    import sys

    if "pmu" in sys.modules:
        del sys.modules["pmu"]
    from krux.power import _PowerManager

    manager = _PowerManager()

    manager.reboot()

    machine.reset.assert_called()
    sys.exit.assert_called()

from .shared_mocks import *


def test_init_without_pmu():
    from krux.power import PowerManager

    manager = PowerManager()

    assert isinstance(manager, PowerManager)
    assert manager.pmu is None


def test_shutdown_without_pmu(mocker):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.shutdown()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_reboot_without_pmu(mocker):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.reboot()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()

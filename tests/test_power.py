import pytest


def test_init(mocker, multiple_devices):
    from krux.power import PowerManager

    manager = PowerManager()

    assert isinstance(manager, PowerManager)


def test_pmu(mocker, multiple_devices):
    from krux.power import PowerManager
    import board

    manager = PowerManager()

    if board.config["type"] in ("dock", "yahboom", "wonder_mv", "bit"):
        assert manager.pmu is None
        assert manager.has_battery() is False
    else:
        assert manager.pmu is not None
        assert manager.has_battery() is True


def test_charge_remaining(mocker, multiple_devices):
    from krux.power import PowerManager
    import board

    manager = PowerManager()

    if manager.pmu is not None:
        manager.pmu.get_battery_voltage = mocker.MagicMock(return_value=4000)

    if board.config["type"] == "amigo":
        assert manager.battery_charge_remaining() == 0.9
    elif board.config["type"] in ("m5stickv", "cube"):
        assert round(manager.battery_charge_remaining(), 2) == 0.75


def test_charge_has_no_battery(mocker, multiple_devices):
    from krux.power import PowerManager
    import board

    manager = PowerManager()

    # M5StickV, Amigo and Cube have battery
    # and calls get_battery_voltage
    if board.config["type"] in ("amigo", "m5stickv", "cube"):
        manager.pmu.get_battery_voltage = mocker.MagicMock(return_value=0)
        assert not manager.has_battery()
        manager.pmu.get_battery_voltage.assert_called_once()

    # Dock, Yahboom and WonderMV do not have battery
    # it just raises an exception and returns False
    else:
        with pytest.raises(AttributeError) as exc_info:
            assert not manager.has_battery()
            assert (
                str(exc_info.exception)
                == "get_battery_voltage() not implemented for this board"
            )


def test_shutdown(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.shutdown()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_shutdown_with_amigo(mocker, amigo):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.shutdown()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_shutdown_without_pmu(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    import sys

    if "pmu" in sys.modules:
        del sys.modules["pmu"]
    from krux.power import PowerManager

    manager = PowerManager()

    manager.shutdown()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_reboot(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.reboot()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_reboot_with_amigo(mocker, amigo):
    mocker.patch("sys.exit")
    import krux
    from krux.power import PowerManager

    manager = PowerManager()

    manager.reboot()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_reboot_without_pmu(mocker, m5stickv):
    mocker.patch("sys.exit")
    import krux
    import sys

    if "pmu" in sys.modules:
        del sys.modules["pmu"]
    from krux.power import PowerManager

    manager = PowerManager()

    manager.reboot()

    krux.power.machine.reset.assert_called()
    krux.power.sys.exit.assert_called()


def test_battery_charge_m5stickv(mocker, m5stickv):
    from krux.power import PowerManager

    manager = PowerManager()

    # (voltage, expected_charge)
    cases = [
        (4200, 1.0),
        (4000, 1.0),
        (3600, 0.593),
        (3000, 0.0),
    ]

    for voltage, expected in cases:
        manager.pmu.get_battery_voltage = mocker.MagicMock(return_value=voltage)
        manager.pmu.charging = mocker.MagicMock(return_value=False)

        voltage_spy = mocker.spy(manager.pmu, "get_battery_voltage")
        charging_spy = mocker.spy(manager.pmu, "charging")

        charge = manager.battery_charge_remaining()

        assert charge == pytest.approx(expected, abs=0.001)
        voltage_spy.assert_called_once()
        charging_spy.assert_called_once()


def test_battery_charge_amigo(mocker, amigo):
    from krux.power import PowerManager

    manager = PowerManager()

    # (voltage, expected_charge)
    cases = [
        (4200, 1.0),
        (4000, 1.0),
        (3600, 0.494),
        (3000, 0.0),
    ]

    for voltage, expected in cases:
        manager.pmu.get_battery_voltage = mocker.MagicMock(return_value=voltage)
        manager.pmu.charging = mocker.MagicMock(return_value=False)

        voltage_spy = mocker.spy(manager.pmu, "get_battery_voltage")
        charging_spy = mocker.spy(manager.pmu, "charging")

        charge = manager.battery_charge_remaining()

        assert charge == pytest.approx(expected, abs=0.001)
        voltage_spy.assert_called_once()
        charging_spy.assert_called_once()


def test_battery_charge_cube(mocker, cube):
    from krux.power import PowerManager

    manager = PowerManager()

    # (voltage, expected_charge)
    cases = [
        (4200, 1.0),
        (4000, 1.0),
        (3600, 0.593),
        (3000, 0.0),
    ]

    for voltage, expected in cases:
        manager.pmu.get_battery_voltage = mocker.MagicMock(return_value=voltage)
        manager.pmu.charging = mocker.MagicMock(return_value=False)

        voltage_spy = mocker.spy(manager.pmu, "get_battery_voltage")
        charging_spy = mocker.spy(manager.pmu, "charging")

        charge = manager.battery_charge_remaining()

        assert charge == pytest.approx(expected, abs=0.001)
        voltage_spy.assert_called_once()
        charging_spy.assert_called_once()


# This test is for potentially new devices
# that are not implemented yet in the firmware
# and do not have the necessary linear approximation
# to calculate the battery charge remaining
# It will use the MAX_BATTERY_MV and MIN_BATTERY_MV
# to calculate the charge remaining and work
# as fallback.
def test_battery_charge_potentially_new_device(mocker, m5stickv):
    from krux.power import PowerManager
    from krux.kboard import kboard

    # Mock the kboard to simulate a new device
    kboard.is_m5stickv = False
    manager = PowerManager()

    # (voltage, expected_charge)
    cases = [
        (4200, 1.0),  # Fully charged
        (4000, 0.833),  # Partially charged
        (3600, 0.5),  # Half charged
        (3000, 0.0),  # Empty
    ]

    for voltage, expected in cases:
        manager.pmu.get_battery_voltage = mocker.MagicMock(return_value=voltage)
        manager.pmu.charging = mocker.MagicMock(return_value=False)

        voltage_spy = mocker.spy(manager.pmu, "get_battery_voltage")
        charging_spy = mocker.spy(manager.pmu, "charging")

        charge = manager.battery_charge_remaining()

        assert charge == pytest.approx(expected, abs=0.001)
        voltage_spy.assert_called_once()
        charging_spy.assert_called_once()


def test_usb_connected_m5stickv(mocker, m5stickv):
    from krux.power import PowerManager

    manager = PowerManager()
    manager.pmu.usb_connected = mocker.MagicMock(return_value=True)
    assert manager.usb_connected()
    manager.pmu.usb_connected.assert_called_once()


def test_usb_disconnected_m5stickv(mocker, m5stickv):
    from krux.power import PowerManager

    manager = PowerManager()
    manager.pmu.usb_connected = mocker.MagicMock(return_value=False)
    assert not manager.usb_connected()
    manager.pmu.usb_connected.assert_called_once()


def test_usb_connected_amigo(mocker, amigo):
    from krux.power import PowerManager

    manager = PowerManager()
    manager.pmu.usb_connected = mocker.MagicMock(return_value=True)
    assert manager.usb_connected()
    manager.pmu.usb_connected.assert_called_once()


def test_usb_disconnected_amigo(mocker, amigo):
    from krux.power import PowerManager

    manager = PowerManager()
    manager.pmu.usb_connected = mocker.MagicMock(return_value=False)
    assert not manager.usb_connected()
    manager.pmu.usb_connected.assert_called_once()


def test_usb_connected_cube(mocker, cube):
    from krux.power import PowerManager

    manager = PowerManager()
    manager.pmu.usb_connected = mocker.MagicMock(return_value=True)
    assert manager.usb_connected()
    manager.pmu.usb_connected.assert_called_once()


def test_usb_disconnected_cube(mocker, cube):
    from krux.power import PowerManager

    manager = PowerManager()
    manager.pmu.usb_connected = mocker.MagicMock(return_value=False)
    assert not manager.usb_connected()
    manager.pmu.usb_connected.assert_called_once()

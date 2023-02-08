import pytest


@pytest.fixture
def mocker_config_unset(mocker):
    # Read a mocked /etc/release file
    mocked_data = mocker.mock_open(read_data='')
    mocker.patch('builtins.open', mocked_data)


@pytest.fixture
def mocker_config_set(mocker):
    # Read a mocked /etc/release file
    mocked_data = mocker.mock_open(read_data='{"type": "dock", "board_info": {"LED_G": 12, "MIC0_WS": 19, "LED_B": 14, "BOOT_KEY": 16, "LED_R": 13, "MIC0_DATA": 20, "MIC0_BCK": 18}}')
    mocker.patch('builtins.open', mocked_data)


@pytest.fixture
def mocker_config_set_false(mocker):
    # Read a mocked /etc/release file
    mocked_data = mocker.mock_open(read_data='{"WATCHDOG_DISABLE": 0, "type": "dock", "board_info": {"LED_G": 12, "MIC0_WS": 19, "LED_B": 14, "BOOT_KEY": 16, "LED_R": 13, "MIC0_DATA": 20, "MIC0_BCK": 18}}')
    mocker.patch('builtins.open', mocked_data)


@pytest.fixture
def mocker_config_set_true(mocker):
    # Read a mocked /etc/release file
    mocked_data = mocker.mock_open(read_data='{"WATCHDOG_DISABLE": 1, "type": "dock", "board_info": {"LED_G": 12, "MIC0_WS": 19, "LED_B": 14, "BOOT_KEY": 16, "LED_R": 13, "MIC0_DATA": 20, "MIC0_BCK": 18}}')
    mocker.patch('builtins.open', mocked_data)


def test_watchdog_config_set_true(m5stickv, mocker_config_set_true):
    import krux
    from krux import wdt

    krux.wdt.machine.WDT.assert_called()
    krux.wdt.wdt.stop.assert_called()


def test_watchdog_config_unset(m5stickv, mocker_config_unset):
    import krux
    from krux import wdt

    krux.wdt.machine.WDT.assert_called()
    krux.wdt.wdt.stop.assert_not_called()


def test_watchdog_config_set(m5stickv, mocker_config_set):
    import krux
    from krux import wdt

    krux.wdt.machine.WDT.assert_called()
    krux.wdt.wdt.stop.assert_not_called()


def test_watchdog_config_set_false(m5stickv, mocker_config_set_false):
    import krux
    from krux import wdt

    krux.wdt.machine.WDT.assert_called()
    krux.wdt.wdt.stop.assert_not_called()
    
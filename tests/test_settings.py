import sys
import pytest
from unittest import mock
from Crypto.Cipher import AES
from .pages.test_login import create_ctx

if "ucryptolib" not in sys.modules:
    sys.modules["ucryptolib"] = mock.MagicMock(
        aes=AES.new, MODE_ECB=AES.MODE_ECB, MODE_CBC=AES.MODE_CBC
    )


def test_init(mocker, m5stickv):
    from krux.krux_settings import Settings

    s = Settings()

    assert isinstance(s, Settings)


def test_store_init(mocker, m5stickv):
    from krux.settings import Store, SETTINGS_FILENAME, SD_PATH

    cases = [
        (None, {}),
        ("""{"settings":{"network":"test"}}""", {"settings": {"network": "test"}}),
    ]
    for case in cases:
        mo = mocker.mock_open(read_data=case[0])
        mocker.patch("builtins.open", mo)
        s = Store()

        assert isinstance(s, Store)
        mo.assert_called_with("/" + SD_PATH + "/" + SETTINGS_FILENAME, "r")
        assert s.settings == case[1]


def test_store_get():
    from krux.settings import Store

    s = Store()

    cases = [
        ("ns1", "setting", "call1_defaultvalue1", "call2_defaultvalue1"),
        ("ns1.ns2", "setting", "call1_defaultvalue2", "call2_defaultvalue2"),
        ("ns1.ns2.ns3", "setting", "call1_defaultvalue3", "call2_defaultvalue3"),
    ]
    for i, case in enumerate(cases):
        # First call, setting does not exist, so default value becomes the value
        assert s.get(case[0], case[1], case[2]) == case[2]

        # Getter does not populate settings dict. if nothing is set then settings is empty
        if i == 0:
            assert s.settings == {}

        # Second call, setting does exist, so default value is ignored
        s.set(case[0], case[1], case[2])
        assert s.get(case[0], case[1], case[3]) == case[2]


def test_store_set():
    from krux.settings import Store

    s = Store()

    cases = [
        ("ns1", "setting", "call1_value1", 1, "call3_value1"),
        ("ns1.ns2", "setting", "call1_value2", 2, "call3_value2"),
        ("ns1.ns2.ns3", "setting", "call1_value3", 3, "call3_value3"),
    ]

    assert s.dirty == False

    for case in cases:
        s.set(case[0], case[1], case[2])
        assert s.get(case[0], case[1], "default") == case[2]

        s.set(case[0], case[1], case[3])
        assert s.get(case[0], case[1], "default") == case[3]

        s.set(case[0], case[1], case[4])
        assert s.get(case[0], case[1], "default") == case[4]

    assert s.dirty == True


def test_store_delete():
    from krux.settings import Store

    s = Store()

    cases = [
        ("ns1", "setting1", "value1"),
        ("ns1.ns2", "setting2", "value2"),
    ]

    assert s.dirty == False

    for case in cases:
        s.set(case[0], case[1], case[2])

    for i, case in enumerate(cases):
        s.delete(case[0], case[1])

        # value of deleted setting is its default
        assert s.get(case[0], case[1], "default") == "default"

        # when deleting a setting, its empty namespaces are deleted too
        if i == len(cases) - 1:
            assert s.settings == {}

    assert s.dirty == True


def test_store_update_file_location(mocker):
    ms, mr = mocker.Mock(), mocker.Mock()
    mocker.patch("os.stat", ms)
    mocker.patch("os.remove", mr)
    from krux.settings import Store, SD_PATH, FLASH_PATH, SETTINGS_FILENAME

    s = Store()

    # default is /flash/
    assert s.file_location == "/" + FLASH_PATH + "/"

    # from flash to sd removes /flash/settings.json
    s.update_file_location(SD_PATH)
    assert s.file_location == "/" + SD_PATH + "/"
    ms.assert_called_once_with("/" + FLASH_PATH + "/" + SETTINGS_FILENAME)
    mr.assert_called_once_with("/" + FLASH_PATH + "/" + SETTINGS_FILENAME)
    ms.reset_mock()
    mr.reset_mock()

    # from sd to flash removes /sd/settings.json
    s.update_file_location(FLASH_PATH)
    assert s.file_location == "/" + FLASH_PATH + "/"
    ms.assert_called_once_with("/" + SD_PATH + "/" + SETTINGS_FILENAME)
    mr.assert_called_once_with("/" + SD_PATH + "/" + SETTINGS_FILENAME)
    ms.reset_mock()
    mr.reset_mock()

    # updating with existing file_location does nothing
    s.update_file_location(FLASH_PATH)
    assert s.file_location == "/" + FLASH_PATH + "/"
    ms.assert_not_called()
    mr.assert_not_called()


def test_store_save_settings(mocker):
    mo = mocker.mock_open()
    mocker.patch("builtins.open", mo)
    from krux.settings import Store, SETTINGS_FILENAME

    s = Store()
    filename = s.file_location + SETTINGS_FILENAME

    # new setting change: is dirty, save_settings() persists, file written
    s.set("name.space", "setting", "custom_value")
    assert s.dirty == True
    assert s.save_settings() == True
    mo.assert_called_with(filename, "w")

    # no setting change: not dirty, save_settings() doesn't persist, file not even read
    mo.reset_mock()
    assert s.dirty == False
    assert s.save_settings() == False
    mo.assert_not_called()

    # settings changed to original: dirty but save_settings() doesn't persist, file read -- not written
    mo = mocker.mock_open(read_data='{"name": {"space": {"setting": "custom_value"}}}')
    mocker.patch("builtins.open", mo)
    s.set("name.space", "setting", "new_custom_value")
    s.set("name.space", "setting", "custom_value")
    assert s.dirty == True
    assert s.save_settings() == False
    mo.assert_called_once()
    assert s.dirty == False


def test_setting(mocker, m5stickv):
    mo = mocker.mock_open()
    mocker.patch("builtins.open", mo)
    from krux.settings import Setting

    class TestClass:
        namespace = "test"
        some_setting = Setting("some_setting", 1)

    t = TestClass()

    assert t.some_setting == 1
    t.some_setting = 2
    assert t.some_setting == 2


def test_all_labels(mocker, m5stickv):
    from krux.krux_settings import (
        BitcoinSettings,
        I18nSettings,
        LoggingSettings,
        EncryptionSettings,
        PrinterSettings,
        ThermalSettings,
        AdafruitPrinterSettings,
        CNCSettings,
        GRBLSettings,
        PersistSettings,
        ThemeSettings,
        TouchSettings,
        EncoderSettings,
    )

    bitcoin = BitcoinSettings()
    i18n = I18nSettings()
    logging = LoggingSettings()
    encryption = EncryptionSettings()
    printer = PrinterSettings()
    thermal = ThermalSettings()
    adafruit = AdafruitPrinterSettings()
    cnc = CNCSettings()
    gbrl = GRBLSettings()
    persist = PersistSettings()
    appearance = ThemeSettings()
    touch = TouchSettings()
    encoder = EncoderSettings()

    assert bitcoin.label("network")
    assert i18n.label("locale")
    assert logging.label("level")
    assert encryption.label("version")
    assert printer.label("thermal")
    assert thermal.label("adafruit")
    assert adafruit.label("tx_pin")
    assert cnc.label("invert")
    assert gbrl.label("tx_pin")
    assert persist.label("location")
    assert appearance.label("theme")
    assert appearance.label("screensaver_time")
    assert touch.label("threshold")
    assert encoder.label("debounce")

# Tests for krux.settings


def test_init(mocker, m5stickv):
    from krux.krux_settings import Settings, SettingsNamespace
    import pytest

    s = Settings()

    assert isinstance(s, Settings)

    sn = SettingsNamespace()

    with pytest.raises(NotImplementedError):
        sn.label("test")


def test_stored_i18n_settings(mocker, m5stickv):
    # mock store singleton creation before import
    stored_settings = """{"settings": {"i18n": {"locale": "pt-BR"}}}"""
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    # import will create store singleton with mocked values
    from krux.krux_settings import I18nSettings

    i18n = I18nSettings()

    assert i18n.locale == "pt-BR"


def test_wrong_stored_i18n_settings(mocker, m5stickv):
    # mock store singleton creation before import
    stored_settings = """{"settings": {"i18n": {"locale": "aa-AA"}}}"""
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    # import will create store singleton with mocked values
    from krux.krux_settings import I18nSettings

    i18n = I18nSettings()

    assert i18n.locale == "en-US"


def test_stored_adafruit_printer_settings(mocker, m5stickv):
    print("")

    # mock store singleton creation before import
    stored_settings = (
        """{"settings": {"printer": {"thermal": {"adafruit": {"line_delay": 35}}}}}"""
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    # import will create store singleton with mocked values
    from krux.krux_settings import AdafruitPrinterSettings

    ada = AdafruitPrinterSettings()
    assert ada.line_delay == 35


def test_wrong_stored_adafruit_printer_settings(mocker, m5stickv):
    print("")

    # mock store singleton creation before import
    stored_settings = (
        """{"settings": {"printer": {"thermal": {"adafruit": {"line_delay": 511}}}}}"""
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    # import will create store singleton with mocked values
    from krux.krux_settings import AdafruitPrinterSettings

    ada = AdafruitPrinterSettings()
    assert ada.line_delay == 20


def test_float_stored_adafruit_printer_settings(mocker, m5stickv):
    print("")

    # mock store singleton creation before import
    stored_settings = (
        """{"settings": {"printer": {"thermal": {"adafruit": {"line_delay": 21.2}}}}}"""
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    # import will create store singleton with mocked values
    from krux.krux_settings import AdafruitPrinterSettings

    ada = AdafruitPrinterSettings()
    assert ada.line_delay == 20


def test_string_stored_adafruit_printer_settings(mocker, m5stickv):
    print("")

    # mock store singleton creation before import
    stored_settings = """{"settings": {"printer": {"thermal": {"adafruit": {"line_delay": 1,abc}}}}}"""
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    # import will create store singleton with mocked values
    from krux.krux_settings import AdafruitPrinterSettings

    ada = AdafruitPrinterSettings()
    assert ada.line_delay == 20


def test_stored_cnc_settings(mocker, m5stickv):
    print("")

    # mock store singleton creation before import
    stored_settings = """{"settings": {"printer": {"cnc": {"border_padding": 127}}}}"""
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    # import will create store singleton with mocked values
    from krux.krux_settings import CNCSettings

    cnc = CNCSettings()
    assert cnc.border_padding == 127


def test_wrong_stored_cnc_settings(mocker, m5stickv):
    print("")

    # mock store singleton creation before import
    stored_settings = """{"settings": {"printer": {"thermal": {"adafruit": {"line_delay": 1.abc}}}}}"""
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    # import will create store singleton with mocked values
    from krux.krux_settings import CNCSettings

    cnc = CNCSettings()
    assert cnc.border_padding == 0.0625


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
        DefaultWallet,
        I18nSettings,
        EncryptionSettings,
        PrinterSettings,
        ThermalSettings,
        AdafruitPrinterSettings,
        CNCSettings,
        GRBLSettings,
        PersistSettings,
        ThemeSettings,
        TouchSettings,
        ButtonsSettings,
        DisplayAmgSettings,
        DisplaySettings,
        HardwareSettings,
        SecuritySettings,
        Settings,
    )

    wallet = DefaultWallet()
    i18n = I18nSettings()
    thermal = ThermalSettings()
    adafruit = AdafruitPrinterSettings()
    cnc = CNCSettings()
    gbrl = GRBLSettings()
    printer = PrinterSettings()
    buttons = ButtonsSettings()
    touch = TouchSettings()
    amigo_display = DisplayAmgSettings()
    display = DisplaySettings()
    hardware = HardwareSettings()
    persist = PersistSettings()
    encryption = EncryptionSettings()
    appearance = ThemeSettings()
    security = SecuritySettings()
    settings = Settings()

    assert wallet.label("network")
    assert i18n.label("locale")
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
    assert buttons.label("debounce")
    assert amigo_display.label("flipped_x")
    assert display.label("brightness")
    assert hardware.label("printer")
    assert security.label("auto_shutdown")
    assert settings.label("persist")

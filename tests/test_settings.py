# Tests for krux.settings


def test_setting_get_method_return_self_when_obj_is_none(mocker, m5stickv):
    from krux.settings import Setting

    # this will test __get__ method
    # of Setting class. When the given
    # object is None, it must return
    # the same instance of Setting.
    s = Setting("krux_has_no_owner", "default")
    result = s.__get__(None)

    assert isinstance(result, Setting)
    assert result is s


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


def test_oversized_settings_file_is_rejected(mocker, m5stickv):
    """A settings.json larger than MAX_SETTINGS_FILE_SIZE must be discarded."""
    from krux.settings import MAX_SETTINGS_FILE_SIZE

    # Build a syntactically valid JSON object whose serialized form exceeds the cap
    padding = "A" * (MAX_SETTINGS_FILE_SIZE + 100)
    stored_settings = (
        '{"settings": {"i18n": {"locale": "pt-BR"}}, "junk": "%s"}' % padding
    )
    assert len(stored_settings) > MAX_SETTINGS_FILE_SIZE

    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    from krux.settings import Store

    store = Store()
    # Oversized payload must be ignored: nothing loaded
    assert store.settings == {}


def test_non_dict_settings_file_is_rejected(mocker, m5stickv):
    """A settings.json whose top-level JSON value isn't an object must be discarded."""
    stored_settings = '["settings", "i18n", "pt-BR"]'
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    from krux.settings import Store

    store = Store()
    assert store.settings == {}


def test_malformed_settings_file_is_rejected(mocker, m5stickv):
    """Invalid JSON must not crash the loader and must leave settings empty."""
    stored_settings = "{not valid json"
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    from krux.settings import Store

    store = Store()
    assert store.settings == {}


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
    from krux.settings import Store, SETTINGS_FILENAME, SD_PATH, FLASH_PATH
    import json

    DEFAULT = None
    data_dict = None

    def open_side_effect(name, read_mode):
        print("open_side_effect", name)
        return mocker.mock_open(read_data=data_dict.get(name, DEFAULT))()

    mocker.patch("builtins.open", side_effect=open_side_effect)

    sd_file = Store.get_vfs_location(SD_PATH) + SETTINGS_FILENAME
    flash_file = Store.get_vfs_location(FLASH_PATH) + SETTINGS_FILENAME
    sd_settings_without_key_persist = """{"settings":{"network":"test"}}"""
    sd_settings_with_key_persist = (
        """{"settings":{"network":"test", "persist":{"location": "sd"}}}"""
    )
    flash_setting = """{"settings":{"test":"True"}}"""

    # 1- SD has settings, key 'persist.location' not set, flash settings None
    data_dict = {sd_file: sd_settings_without_key_persist, flash_file: None}

    s = Store()
    assert isinstance(s, Store)

    # flash location as default, loaded from SD because settings file is present
    assert s.settings == json.loads(data_dict[sd_file])

    # 2- SD has settings, key 'persist.location' not set, flash settings SET
    data_dict = {sd_file: sd_settings_without_key_persist, flash_file: flash_setting}

    s = Store()

    # settings is set to flash contents
    assert s.settings == json.loads(data_dict[flash_file])

    # 3- SD has settings, key 'persist.location' SET, flash settings SET
    data_dict = {sd_file: sd_settings_with_key_persist, flash_file: flash_setting}

    s = Store()

    # settings is set to SD ('persist.location' is king!)
    assert s.settings == json.loads(data_dict[sd_file])

    # 4- SD settings None, flash settings SET
    data_dict = {sd_file: None, flash_file: flash_setting}

    s = Store()

    # settings is set to flash contents
    assert s.settings == json.loads(data_dict[flash_file])


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


def test_store_get_malformed_namespace_returns_default():
    """A non-dict intermediate namespace must return the default, not raise.

    Covers BOTH a non-dict at the first level AND a non-dict reached after a
    valid descent (proves traversal stays safe mid-walk). Only reachable via a
    corrupted/hand-edited settings file; set() never creates this state.
    Approved behavior change: graceful degradation.
    """
    from krux.settings import Store

    s = Store()

    # Case 1: non-dict at the very first level.
    s.settings = {"settings": "not_a_dict"}
    assert s.get("settings.i18n", "locale", "en-US") == "en-US"
    assert s.settings == {"settings": "not_a_dict"}  # no mutation

    # Case 2: non-dict reached AFTER successfully descending a valid dict.
    s.settings = {"settings": {"printer": "not_a_dict"}}
    assert s.get("settings.printer.thermal", "baudrate", 9600) == 9600
    assert s.settings == {"settings": {"printer": "not_a_dict"}}  # no mutation


def test_store_init_survives_non_dict_settings_namespace(mocker, m5stickv):
    """Store.__init__ must not crash when the persisted 'settings' value is a
    non-dict.

    The loader only validates the top level is a dict, so a corrupted file like
    {"settings": "not_a_dict"} passes load. The location read in __init__ walks
    settings.persist.location and must degrade gracefully instead of raising
    AttributeError. Reads through the malformed namespace return defaults.
    """
    stored_settings = '{"settings": "not_a_dict"}'
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    from krux.settings import Store, FLASH_PATH

    store = Store()  # must not raise
    assert FLASH_PATH in store.file_location
    assert store.get("settings.i18n", "locale", "en-US") == "en-US"


def test_store_init_survives_bogus_persist_location(mocker, m5stickv):
    """Store.__init__ must not crash on a bogus persist.location value.

    The structure is well-formed but `location` holds an unexpected value
    (non-string, or an unknown string). `_persisted_location` must return only a
    known location (SD/flash) and otherwise fall back to the default, so the
    `SD_PATH not in self.file_location` membership test never sees a non-string.
    """
    from krux.settings import Store, FLASH_PATH

    # Non-string location (would raise "argument of type 'int' is not iterable").
    mocker.patch(
        "builtins.open",
        mocker.mock_open(read_data='{"settings": {"persist": {"location": 123}}}'),
    )
    store = Store()  # must not raise
    assert FLASH_PATH in store.file_location

    # Unknown string location -> also falls back to flash.
    mocker.patch(
        "builtins.open",
        mocker.mock_open(read_data='{"settings": {"persist": {"location": "xyz"}}}'),
    )
    store = Store()  # must not raise
    assert FLASH_PATH in store.file_location


def test_store_get_recovers_from_malformed_persisted_namespace(mocker, m5stickv):
    """End-to-end: a persisted settings file with a well-formed top level but a
    non-dict nested namespace loads, and reads through it degrade gracefully.

    The top level, `settings`, and `settings.persist` are well-formed (the
    constructor reads `persist` to pick the file location), but the `i18n`
    namespace is a string instead of a dict. get() must return the default
    rather than raising. Covers the file -> __init__ -> get() chain, not just
    direct Store.get() calls.
    """
    stored_settings = '{"settings": {"i18n": "not_a_dict"}}'
    mocker.patch("builtins.open", mocker.mock_open(read_data=stored_settings))

    from krux.settings import Store

    store = Store()
    assert store.settings == {"settings": {"i18n": "not_a_dict"}}
    assert store.get("settings.i18n", "locale", "en-US") == "en-US"


def test_store_get_deep_nesting():
    """A 4-level namespace returns stored value when set, default when unset."""
    from krux.settings import Store

    s = Store()
    ns = "settings.printer.thermal.adafruit"

    # Unset -> default.
    assert s.get(ns, "tx_pin", 35) == 35
    # Getter must not populate the settings dict on a miss.
    assert s.settings == {}

    # Set then get returns the stored value, ignoring the default.
    s.set(ns, "tx_pin", 21)
    assert s.get(ns, "tx_pin", 35) == 21


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
    mr = mocker.Mock()
    mocker.patch("os.remove", mr)
    from krux.settings import Store, SD_PATH, FLASH_PATH, SETTINGS_FILENAME

    s = Store()

    # default is /flash/
    assert s.file_location == Store.get_vfs_location(FLASH_PATH)

    # from flash to sd removes /flash/settings.json
    s.update_file_location(SD_PATH)
    assert s.file_location == Store.get_vfs_location(SD_PATH)
    mr.assert_called_once_with(Store.get_vfs_location(FLASH_PATH) + SETTINGS_FILENAME)
    mr.reset_mock()

    # from sd to flash removes /sd/settings.json
    s.update_file_location(FLASH_PATH)
    assert s.file_location == Store.get_vfs_location(FLASH_PATH)
    mr.assert_called_once_with(Store.get_vfs_location(SD_PATH) + SETTINGS_FILENAME)
    mr.reset_mock()

    # updating with existing file_location also tries to remove from the other location
    # case flash
    s.update_file_location(FLASH_PATH)
    assert s.file_location == Store.get_vfs_location(FLASH_PATH)
    mr.assert_called_once_with(Store.get_vfs_location(SD_PATH) + SETTINGS_FILENAME)
    mr.reset_mock()

    # case SD
    s.update_file_location(SD_PATH)
    assert s.file_location == Store.get_vfs_location(SD_PATH)
    mr.assert_called_once_with(Store.get_vfs_location(FLASH_PATH) + SETTINGS_FILENAME)


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


def test_linked_settings(mocker, m5stickv):
    from krux.krux_settings import SettingsNamespace
    from krux.settings import CategorySetting
    from krux.settings import LinkedCategorySetting

    FRUITS = ["apple", "banana"]
    VEGETABLES = ["arugula", "cabbage"]
    MEATS = ["beef", "pork"]
    ALL = FRUITS + VEGETABLES + MEATS

    class DefaultFoods(SettingsNamespace):
        namespace = "test"
        food_type = CategorySetting(
            "some_setting", "fruit", ["fruit", "vegetable", "meat"]
        )
        food = LinkedCategorySetting(
            "linked_setting",
            FRUITS[0],
            ALL,
            food_type,
            [
                lambda x, y: (
                    x == (FRUITS, FRUITS[0])
                    if x == "fruit"
                    else (y.categories, y.default_value)
                ),
                lambda x, y: (
                    x == (VEGETABLES, VEGETABLES[0])
                    if x == "vegetable"
                    else (y.categories, y.default_value)
                ),
                lambda x, y: (
                    x == (MEATS, MEATS[0])
                    if x == "meat"
                    else (y.categories, y.default_value)
                ),
            ],
        )

    a = DefaultFoods()

    assert a.food_type == "fruit"
    assert a.food == "apple"

    # try setting valid linked value
    a.food = "juice"

    # since juice is not in fruits, food becomes default
    assert a.food == "apple"


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

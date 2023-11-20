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


# @pytest.fixture
# def mocker_sd_card(mocker):
#     mocker.patch(
#         "os.listdir",
#         new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
#     )


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


def test_store_get(mocker, m5stickv):
    mo = mocker.mock_open()
    mocker.patch("builtins.open", mo)
    from krux.settings import Store

    s = Store()

    cases = [
        ("ns1", "setting", "call1_defaultvalue1", "call2_defaultvalue1"),
        ("ns1.ns2", "setting", "call1_defaultvalue2", "call2_defaultvalue2"),
        ("ns1.ns2.ns3", "setting", "call1_defaultvalue3", "call2_defaultvalue3"),
    ]
    for case in cases:
        # First call, setting does not exist, so default value becomes the value
        assert s.get(case[0], case[1], case[2]) == case[2]
        # Second call, setting does exist, so default value is ignored
        assert s.get(case[0], case[1], case[3]) == case[2]


def test_store_set(mocker, m5stickv):
    mo = mocker.mock_open()
    mocker.patch("builtins.open", mo)
    from krux.settings import Store

    s = Store()

    cases = [
        ("ns1", "setting", "call1_value1", 1, "call3_value1"),
        ("ns1.ns2", "setting", "call1_value2", 2, "call3_value2"),
        ("ns1.ns2.ns3", "setting", "call1_value3", 3, "call3_value3"),
    ]
    for case in cases:
        s.set(case[0], case[1], case[2])
        assert s.get(case[0], case[1], "default") == case[2]

        s.set(case[0], case[1], case[3])
        assert s.get(case[0], case[1], "default") == case[3]

        s.set(case[0], case[1], case[4])
        assert s.get(case[0], case[1], "default") == case[4]


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


def test_encryption_pbkdf2_setting(m5stickv, mocker):
    from krux.pages.login import Login
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.krux_settings import Settings, NumberSetting

    cases = [
        (  # 0
            (
                BUTTON_PAGE,
                # Encryption
                BUTTON_ENTER,
                # pbkdf2
                BUTTON_ENTER,
                # go to "<" keypad position
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                # delete last 0
                BUTTON_ENTER,
                # go to "1" keypad
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                # Enter "1"
                BUTTON_ENTER,
                # go to "Go" keypad position
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                # Go
                BUTTON_ENTER,
                # Leave Encryption settings
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
            ),
            # Assert iterations didn't change to 100,001 (not multiple of 10,000)
            lambda: Settings().encryption.pbkdf2_iterations == 100000,
            NumberSetting,
        ),
        (  # 0
            (
                BUTTON_PAGE,
                # Encryption
                BUTTON_ENTER,
                # pbkdf2
                BUTTON_ENTER,
                # go to "<" keypad position
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                # delete last 5 zeros
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                # go to "1" keypad
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                BUTTON_PAGE,
                # Enter "1"
                BUTTON_ENTER,
                # Go to Zero
                BUTTON_PAGE_PREV,
                # Enter 4 zeros
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                BUTTON_ENTER,
                # go to "Go" keypad position
                BUTTON_PAGE_PREV,
                # Go
                BUTTON_ENTER,
                # Leave Encryption settings
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
                # Leave Settings
                BUTTON_PAGE_PREV,
                BUTTON_PAGE_PREV,
                BUTTON_ENTER,
            ),
            # Assert iterations changed to a multiple of 10,000
            lambda: Settings().encryption.pbkdf2_iterations == 110000,
            NumberSetting,
        ),
    ]
    for case in cases:
        ctx = create_ctx(mocker, case[0])
        login = Login(ctx)

        login.settings()

        assert ctx.input.wait_for_button.call_count == len(case[0])

        assert case[1]()

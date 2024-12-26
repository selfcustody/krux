import pytest
from unittest.mock import patch
from . import create_ctx


def test_parse_all_flash_apps(m5stickv, mocker):
    from krux.pages.kapps import Kapps
    from krux.sd_card import MPY_FILE_EXTENSION
    from krux.input import BUTTON_PAGE, BUTTON_ENTER
    import os
    from krux.settings import FLASH_PATH

    #################################
    print("Case 1: no file with MPY_FILE_EXTENSION")

    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )

    ctx = create_ctx(mocker, None)
    kapps = Kapps(ctx)

    signed_apps = kapps.parse_all_flash_apps()
    assert len(signed_apps) == 0


    ################################
    print("Case 2: unsigned file, prompt for deletion, user deny, ValueError")

    # one unsigned file
    unsigned_file = "somefile" + MPY_FILE_EXTENSION
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=[unsigned_file]),
    )

    # User deny prompt
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_PAGE])

    # unsigned file
    with pytest.raises(ValueError, match="Unsigned apps found in flash"):
        signed_apps = kapps.parse_all_flash_apps()
        assert len(signed_apps) == 0


    ################################
    print("Case 3: unsigned file, prompt for deletion, user allow, remove unsigned file")

    # User accept prompt
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_ENTER])

    # Mock file remove
    mocker.patch("os.remove", new=mocker.MagicMock())

    signed_apps = kapps.parse_all_flash_apps()
    assert len(signed_apps) == 0

    flash_path_prefix = "/%s/" % FLASH_PATH
    os.remove.assert_called_with(flash_path_prefix + unsigned_file)


    ################################
    print("Case 4: signed file")

    # one unsigned file
    signed_file = "sigfile" + MPY_FILE_EXTENSION
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=[signed_file]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"signature data"))
    mocker.patch.object(kapps, "valid_signature", new=lambda data, hash: True)

    signed_apps = kapps.parse_all_flash_apps()
    assert len(signed_apps) == 1
    assert signed_file in signed_apps


def test_valid_signature(m5stickv, mocker):
    from krux.pages.kapps import Kapps

    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=[]),
    )

    ctx = create_ctx(mocker, None)
    kapps = Kapps(ctx)

    ########################################
    print("Case 1: invalid pubkey()")

    mocker.patch("krux.firmware.get_pubkey", new=lambda: None)

    with pytest.raises(ValueError, match="Invalid public key"):
        kapps.valid_signature(None, None)


    ########################################
    print("Case 2: valid signature")

    mocker.patch("krux.firmware.get_pubkey", new=lambda: "Valid pubkey")
    mocker.patch("krux.firmware.check_signature", new=lambda pubk, sig, hash: True)

    sig = kapps.valid_signature(None, None)
    assert sig


def test_execute_flash_kapp(m5stickv, mocker):
    from krux.pages.kapps import Kapps
    from krux.pages import MENU_CONTINUE
    from krux.input import BUTTON_PAGE, BUTTON_ENTER
    import os, sys
    from krux.settings import FLASH_PATH
    from krux.themes import theme

    btn_seq = [
        BUTTON_PAGE, # case 1 skip prompt
        BUTTON_ENTER, # case 2 accept prompt to execute
        BUTTON_PAGE, # case 2 dismiss error msg
        BUTTON_ENTER, # case 3 accept prompt to execute
        ]

    ##########################################
    print("Case 1: Exit when prompted to execute the app")
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=[]),
    )

    ctx = create_ctx(mocker, btn_seq)
    kapps = Kapps(ctx)

    mocker.spy(kapps, "prompt")

    kapp_name = "anykappname"
    result = kapps.execute_flash_kapp(kapp_name)

    assert result == MENU_CONTINUE
    assert kapps.prompt.called
    kapps.prompt.assert_called_with("Execute %s Krux app?" % kapp_name, ctx.display.height() // 2)


    #########################################
    print("Case 2: Continue to execut the app, skip error msg")

    mocker.patch(
        "os.chdir",
        new=mocker.MagicMock(),
    )

    # avoid call sys.exit() after app execution otherwise will exit test and fail
    mocker.patch(
        "sys.exit",
        new=mocker.MagicMock(),
    )

    mocker.spy(ctx.display, "draw_centered_text")

    kapps.execute_flash_kapp(kapp_name)
    assert os.chdir.called
    
    # First changed to flash path and execut app, then return to / when error appear
    os.chdir.assert_has_calls(
        [
            mocker.call(
                "/" + FLASH_PATH
            ),
            mocker.call(
                "/"
            ),
        ]
    )

    assert sys.exit.called

    assert ctx.display.draw_centered_text.called
    ctx.display.draw_centered_text.assert_called_with("Error:" + "\n" + "Could not execute %s" % kapp_name, theme.error_color)


    #######################################
    print("Case 3: app executed")

    mocker.spy(ctx.display, "draw_centered_text")

    sys.path.append(os.getcwd() + "/tests/files")

    kapps.execute_flash_kapp("kapp")
    assert os.chdir.called
    
    # First changed to flash path and execut app, then return to / when error appear
    os.chdir.assert_has_calls(
        [
            mocker.call(
                "/" + FLASH_PATH
            ),
            mocker.call(
                "/"
            ),
        ]
    )

    assert sys.exit.called

    assert not ctx.display.draw_centered_text.called


def test_load_sd_kapp(m5stickv, mocker):
    # TODO: make this

    assert True
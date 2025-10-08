from . import create_ctx


def test_erase_users_data(amigo, mocker):
    """Test that the device is wiped when the user confirms the wipe."""
    from krux.pages.flash_tools import FlashTools
    from krux.input import BUTTON_ENTER

    BTN_SEQUENCE = [BUTTON_ENTER]  # Confirm wipe

    mocker.spy(FlashTools, "erase_spiffs")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    test_tools = FlashTools(ctx)
    test_tools.erase_users_data()

    assert test_tools.erase_spiffs.call_count == 1
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_flash_map(multiple_devices, mocker):
    """Test that the flash map is displayed."""
    from krux.pages.flash_tools import FlashTools
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    import flash

    # Start from submenu
    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Flash Map
        BUTTON_ENTER,  # Confirm flash map
        BUTTON_PAGE_PREV,  # Go to back
        BUTTON_ENTER,  # Confirm back
    ]

    mocker.spy(FlashTools, "flash_map")
    mocker.spy(flash, "read")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    test_tools = FlashTools(ctx)
    test_tools.flash_tools_menu()

    assert test_tools.flash_map.call_count == 1
    assert flash.read.call_count == 4096
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_tc_flash_hash_no_code_set(amigo, mocker):
    """Test if error message is displayed when no code is set."""
    from krux.pages.flash_tools import FlashTools
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    # Start from submenu
    BTN_SEQUENCE = [
        BUTTON_PAGE,  # TC Flash Hash
        BUTTON_ENTER,  # Confirm TC Flash Hash
        # Error: Set TC Code first
        *([BUTTON_PAGE] * 2),  # Go to back
        BUTTON_ENTER,  # Confirm back
    ]

    mocker.spy(FlashTools, "tc_flash_hash")
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    ctx.tc_code_enabled = False
    test_tools = FlashTools(ctx)
    mocker.spy(test_tools, "flash_error")
    test_tools.flash_tools_menu()

    assert test_tools.tc_flash_hash.call_count == 1
    test_tools.flash_error.assert_called_with("Set a tamper check code first")
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_tc_flash_hash(multiple_devices, mocker):
    """Test the display of TC Flash Hash ."""
    import flash
    import board
    from krux.themes import LIGHTBLUE
    from krux.pages.flash_tools import FlashTools
    from krux.input import BUTTON_ENTER
    from krux.pages.tc_code_verification import TCCodeVerification

    BTN_SEQUENCE = [BUTTON_ENTER]

    DOCK_FW_POS = 228
    DOCK_USER_POS = 244

    fw_words_positions = {
        "amigo": 307,
        "m5stickv": 147,
        "dock": DOCK_FW_POS,
        "cube": 208,
        "yahboom": DOCK_FW_POS,
        "wonder_mv": DOCK_FW_POS,
        "bit": DOCK_FW_POS,
        "wonder_k": DOCK_FW_POS,
    }
    users_data_words_positions = {
        "amigo": 331,
        "m5stickv": 161,
        "dock": DOCK_USER_POS,
        "cube": 222,
        "yahboom": DOCK_USER_POS,
        "wonder_mv": DOCK_USER_POS,
        "bit": DOCK_USER_POS,
        "wonder_k": DOCK_USER_POS,
    }
    fw_words_pos = fw_words_positions[board.config["type"]]
    u_data_words_pos = users_data_words_positions[board.config["type"]]

    cases = [
        # TC Code Hash
        # UID
        # Flash bytes value
        # Words firmware, position, color
        # Words users's data, position
        (
            b'V\xfb\xc9\xe1\x98\xc5?\xd3+\xbe"\xb8\xb8\xbe\x0b5I@R\x1a\xc5\x08\xe1\xf6\x04\x8aD8\x04;\xcf\x93',
            b"\x01" * 32,
            b"\x0f" * 4096,
            mocker.call("below cave", fw_words_pos, color=LIGHTBLUE),
            mocker.call("arrive flock", u_data_words_pos),
        ),
        (
            b"\x0a" * 32,
            b"\x02" * 32,
            b"\x11" * 4096,
            mocker.call("keen net", fw_words_pos, color=LIGHTBLUE),
            mocker.call("pigeon hood", u_data_words_pos),
        ),
    ]
    for case in cases:
        mocker.patch.object(TCCodeVerification, "capture", return_value=case[0])
        mocker.patch("machine.unique_id", return_value=case[1])
        mocker.patch.object(flash, "read", return_value=case[2])
        ctx = create_ctx(mocker, BTN_SEQUENCE)
        ctx.tc_code_enabled = True
        test_tools = FlashTools(ctx)
        test_tools.tc_flash_hash()

        assert flash.read.call_count == 4096
        assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
        ctx.display.draw_hcentered_text.assert_has_calls([case[3]], [case[4]])

import pytest
from tests.pages import create_ctx


@pytest.fixture
def mock_sd_handler(mocker):
    """Mock SDHandler for all file operations tests"""
    mock_sd = mocker.MagicMock()
    mocker.patch("krux.pages.file_operations.SDHandler", return_value=mock_sd)
    mocker.patch("krux.pages.file_operations.SDHandler.__enter__", return_value=mock_sd)
    mocker.patch("krux.pages.file_operations.SDHandler.__exit__", return_value=None)
    return mock_sd


def test_save_file_decline_save(m5stickv, mocker, mock_sd_handler):
    """User declines to save to SD card"""
    from krux.input import BUTTON_PAGE
    from krux.pages.file_operations import SaveFile

    BTN_SEQUENCE = [
        BUTTON_PAGE,  # Any non-ENTER key cancels
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    save_file = SaveFile(ctx)
    result = save_file.save_file(b"test_data", "default_name", prompt=True)

    assert result == False
    mock_sd_handler.write_binary.assert_not_called()


def test_save_file_cancel_filename(m5stickv, mocker, mock_sd_handler):
    """User accepts save but cancels during filename entry"""
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.file_operations import SaveFile

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Accept save prompt
        BUTTON_ENTER,  # Type 'a' (already at index 0)
        *([BUTTON_PAGE_PREV] * 11),
        BUTTON_ENTER,  # Move to to 't'
        *([BUTTON_PAGE] * 15),
        BUTTON_ENTER,  # Move to 'e'
        *([BUTTON_PAGE_PREV] * 6),
        BUTTON_ENTER,  # Move to ESC
        BUTTON_ENTER,  # Press ENTER to cancel
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    save_file = SaveFile(ctx)
    result = save_file.save_file(b"test_data", "default_name", prompt=True)

    assert result == False
    mock_sd_handler.write_binary.assert_not_called()
    ctx.display.clear.assert_called()


def test_save_file_empty_filename_retry(m5stickv, mocker, mock_sd_handler):
    """User enters empty filename, system continues, then cancels"""
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.pages.file_operations import SaveFile

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Accept save prompt
        # Delete all 4 characters of default name
        *([BUTTON_PAGE_PREV] * 3),
        BUTTON_ENTER,  # Move to Delete key
        *([BUTTON_ENTER] * 4),  # Delete all 4 characters
        *([BUTTON_PAGE_PREV] * 1),
        BUTTON_ENTER,  # Move to Go and press
        # System rejects empty filename and shows keypad again
        *([BUTTON_PAGE_PREV] * 2),
        BUTTON_ENTER,  # Move to ESC and press
        BUTTON_ENTER,  # Press ENTER to cancel
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    save_file = SaveFile(ctx)
    result = save_file.save_file(b"test_data", "xpub", prompt=True)

    assert result == False
    mock_sd_handler.write_binary.assert_not_called()
    ctx.display.clear.assert_called()


def test_save_file_dots_filename_retry(m5stickv, mocker, mock_sd_handler):
    """User enters dots-only filename, system continues, then cancels"""
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, BUTTON_PAGE
    from krux.pages.file_operations import SaveFile

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Accept save prompt
        *([BUTTON_PAGE_PREV] * 4),
        BUTTON_ENTER,  # Move to ABC and press
        *([BUTTON_PAGE_PREV] * 4),
        BUTTON_ENTER,  # Move to abc and press
        # Delete default text
        *([BUTTON_PAGE_PREV] * 3),
        BUTTON_ENTER,  # Move to Delete
        *([BUTTON_ENTER] * 4),  # Delete all 4 characters of "xpub"
        *([BUTTON_PAGE_PREV] * 6),
        BUTTON_ENTER,  # Move to '.' and type
        *([BUTTON_ENTER] * 2),  # Type '.' two more times
        *([BUTTON_PAGE] * 8),
        BUTTON_ENTER,  # Move to Go and press
        # System rejects and returns to original text
        *([BUTTON_PAGE_PREV] * 2),
        BUTTON_ENTER,  # Move to ESC and press
        BUTTON_ENTER,  # Press ENTER to cancel
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    save_file = SaveFile(ctx)
    result = save_file.save_file(b"test_data", "xpub", prompt=True)

    assert result == False
    mock_sd_handler.write_binary.assert_not_called()
    ctx.display.clear.assert_called()


def test_save_file_decline_overwrite(m5stickv, mocker, mock_sd_handler):
    """File exists, user declines overwrite - 100% real test"""
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages.file_operations import SaveFile

    mocker.patch(
        "krux.pages.file_operations.SDHandler.file_exists", side_effect=[False, True]
    )

    # First save
    BTN_SEQUENCE_SAVE = [
        BUTTON_ENTER,  # Accept save prompt
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,  # Move to Go and press
    ]

    # Second save
    BTN_SEQUENCE_DECLINE = [
        BUTTON_ENTER,  # Accept save prompt
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,  # Move to Go and press
        # File exists prompt - decline overwrite
        BUTTON_PAGE,
        BUTTON_ENTER,  # Move down and press
    ]

    ctx1 = create_ctx(mocker, BTN_SEQUENCE_SAVE)
    save_file1 = SaveFile(ctx1)
    result1 = save_file1.save_file(b"test_data", "xpub", prompt=True)
    assert result1 == True

    ctx2 = create_ctx(mocker, BTN_SEQUENCE_DECLINE)
    save_file2 = SaveFile(ctx2)
    result2 = save_file2.save_file(b"test_data", "xpub", prompt=True)
    assert result2 == False


@pytest.mark.parametrize(
    "suggested, saved_as",
    [
        ("_UR:bytes", "_UR_bytes"),  # Datum Tool title of a scanned UR
        ('a:b*c?d"e<f>g|h', "a_b_c_d_e_f_g_h"),
        ("My wallet", "My wallet"),  # FAT accepts it, kept as is
        ("docs/message", "docs/message"),  # a file in a folder, kept as is
        ("docs\\wallet", "docs\\wallet"),  # FAT reads "\\" as "/", kept as is
    ],
)
def test_save_file_suggestion_has_no_fat_forbidden_chars(
    m5stickv, mocker, mock_sd_handler, suggested, saved_as
):
    """A suggested name FAT would refuse is fixed before the user accepts it"""
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV
    from krux.pages.file_operations import SaveFile

    mocker.patch("krux.pages.file_operations.SDHandler.file_exists", return_value=False)
    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # Move to Go
        BUTTON_ENTER,  # Accept the suggested filename
    ]

    for kwargs in ({}, {"filename": suggested}):
        ctx = create_ctx(mocker, BTN_SEQUENCE)
        save_file = SaveFile(ctx)
        mocker.spy(save_file, "flash_success")
        sd = mock_sd_handler.__enter__.return_value
        sd.write_binary.reset_mock()

        assert save_file.save_file(b"test_data", suggested, prompt=False, **kwargs)

        assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
        sd.write_binary.assert_called_once_with(saved_as, b"test_data")
        save_file.flash_success.assert_called_once_with(
            "Saved to SD card:\n\n" + saved_as, highlight_prefix=":"
        )

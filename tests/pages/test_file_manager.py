import pytest
from . import create_ctx


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["first_file", "second_file"]),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=""))
    mocker.patch("os.remove", mocker.mock_open(read_data=""))


def test_file_exploring(m5stickv, mocker, mock_file_operations):
    from krux.pages.file_manager import FileManager
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # Move to second file
        + [BUTTON_ENTER]  # Check file details
        + [BUTTON_ENTER]  # Leave file details
        + [BUTTON_PAGE]  # Go to "back"
        + [BUTTON_ENTER]  # Leave file explorer
    )
    mocker.patch(
        "krux.sd_card.SDHandler.dir_exists", mocker.MagicMock(side_effect=[True, False])
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    file_manager = FileManager(ctx)
    file_manager.select_file(select_file_handler=file_manager.show_file_details)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "second_file\n\nSize: 1.1 KB\n\nCreated: 1969-12-31 21:00\n\nModified: 1969-12-31 21:00"
            )
        ]
    )


def test_folders_exploring(m5stickv, mocker, mock_file_operations):
    from krux.pages.file_manager import FileManager
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # Move to second folder
        + [BUTTON_ENTER]  # Enter folder
        + [BUTTON_ENTER]  # Parent Folder
        + [BUTTON_PAGE_PREV]  # Move to "Back"
        + [BUTTON_ENTER]  # Leave
    )
    mocker.patch(
        "krux.sd_card.SDHandler.dir_exists", mocker.MagicMock(return_value=True)
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    file_manager = FileManager(ctx)
    file_manager.select_file(select_file_handler=file_manager.show_file_details)
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

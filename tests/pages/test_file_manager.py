import pytest
from . import create_ctx


@pytest.fixture
def mock_file_operations(mocker):
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(
            return_value=[
                "file1",  # third entry
                "file2_has_a_long_name",  # fourth entry
                "subdir2",  # second entry
                "subdir1_has_a_long_name",  # first entry
            ]
        ),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data=""))
    mocker.patch("os.remove", mocker.mock_open(read_data=""))


def test_file_exploring(m5stickv, mocker, mock_file_operations):
    from krux.pages.file_manager import FileManager
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    import time
    from krux.display import DEFAULT_PADDING
    from krux.themes import theme

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # move to second entry, last directory
        + [BUTTON_PAGE]  # move to third entry, first file
        + [BUTTON_PAGE]  # move to fourth entry, last file
        + [BUTTON_ENTER]  # Check file details
        + [BUTTON_ENTER]  # Leave file details
        + [BUTTON_PAGE]  # move to Back
        + [BUTTON_ENTER]  # Leave file explorer
    )

    def mock_localtime(timestamp):
        return time.gmtime(timestamp)

    # selected file has this timestamp
    mocker.patch("time.localtime", side_effect=mock_localtime)

    # to view this directory, selected file isn't a directory
    mocker.patch(
        "krux.sd_card.SDHandler.dir_exists", mocker.MagicMock(side_effect=[True])
    )
    # first 2 entries are files, next 2 are directories
    mocker.patch(
        "krux.sd_card.SDHandler.file_exists",
        mocker.MagicMock(side_effect=[True, True, False, False]),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    file_manager = FileManager(ctx)
    file_manager.select_file(select_file_handler=file_manager.show_file_details)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "file2_has_a_long_name\n\nSize: 1.1 KB",
                DEFAULT_PADDING,
                highlight_prefix=":",
            ),
            mocker.call(
                "Created:",
                38,
                color=theme.highlight_color,
            ),
            mocker.call("1970-01-01 00:00\n\n", 52),
            mocker.call(
                "Modified:",
                66,
                color=theme.highlight_color,
            ),
            mocker.call("1970-01-01 00:00", 80),
        ]
    )


def test_file_load(m5stickv, mocker, mock_file_operations):
    from krux.pages.file_manager import FileManager
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.sd_card import DESCRIPTOR_FILE_EXTENSION
    import time
    from krux.display import DEFAULT_PADDING
    from krux.themes import theme

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # move to second entry, last directory
        + [BUTTON_PAGE]  # move to third entry, first file
        + [BUTTON_PAGE]  # move to fourth entry, last file
        + [BUTTON_ENTER]  # load file
        + [BUTTON_ENTER]  # confirm file details
    )

    def mock_localtime(timestamp):
        return time.gmtime(timestamp)

    # specific types
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(
            return_value=[
                "file1.txt",  # third entry
                "file1.err",  # not entry
                "file2_has_a_long_name.txt",  # fourth entry
                "subdir2",  # second entry
                "subdir1_has_a_long_name",  # first entry
            ]
        ),
    )

    # selected file has this timestamp
    mocker.patch("time.localtime", side_effect=mock_localtime)

    # to view this directory, selected file isn't a directory
    mocker.patch(
        "krux.sd_card.SDHandler.dir_exists",
        mocker.MagicMock(side_effect=[True, False]),
    )
    # first 3 entries are files, next 2 are directories
    mocker.patch(
        "krux.sd_card.SDHandler.file_exists",
        mocker.MagicMock(side_effect=[True, True, True, False, False]),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    file_manager = FileManager(ctx)
    file_manager.select_file(
        select_file_handler=file_manager.load_file,
        file_extension=[".abc", DESCRIPTOR_FILE_EXTENSION],
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "file2_has_a_long_name.txt\n\nSize: 1.1 KB",
                DEFAULT_PADDING,
                highlight_prefix=":",
            ),
            mocker.call(
                "Created:",
                38,
                color=theme.highlight_color,
            ),
            mocker.call("1970-01-01 00:00\n\n", 52),
            mocker.call(
                "Modified:",
                66,
                color=theme.highlight_color,
            ),
            mocker.call("1970-01-01 00:00", 80),
        ]
    )


def test_file_load_cancel(m5stickv, mocker, mock_file_operations):
    from krux.pages.file_manager import FileManager
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.sd_card import DESCRIPTOR_FILE_EXTENSION
    import time
    from krux.display import DEFAULT_PADDING
    from krux.themes import theme

    BTN_SEQUENCE = (
        [BUTTON_PAGE]  # move to second entry, last directory
        + [BUTTON_PAGE]  # move to third entry, first file
        + [BUTTON_PAGE]  # move to fourth entry, last file
        + [BUTTON_ENTER]  # load file
        + [BUTTON_PAGE]  # cancel load
        + [BUTTON_ENTER]  # load file
        + [BUTTON_ENTER]  # confirm
    )

    def mock_localtime(timestamp):
        return time.gmtime(timestamp)

    # specific types
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(
            return_value=[
                "file1.txt",  # third entry
                "file1.err",  # not entry
                "file2_has_a_long_name.txt",  # fourth entry
                "subdir2",  # second entry
                "subdir1_has_a_long_name",  # first entry
            ]
        ),
    )

    # selected file has this timestamp
    mocker.patch("time.localtime", side_effect=mock_localtime)

    # to view this directory, selected file isn't a directory
    mocker.patch(
        "krux.sd_card.SDHandler.dir_exists",
        mocker.MagicMock(side_effect=[True, False]),
    )
    # first 3 entries are files, next 2 are directories
    _listing_returns = [True, True, True, False, False]
    mocker.patch(
        "krux.sd_card.SDHandler.file_exists",
        mocker.MagicMock(side_effect=_listing_returns),
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    file_manager = FileManager(ctx)
    file_manager.select_file(
        select_file_handler=file_manager.load_file,
        file_extension=[".abc", DESCRIPTOR_FILE_EXTENSION],
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "file2_has_a_long_name.txt\n\nSize: 1.1 KB",
                DEFAULT_PADDING,
                highlight_prefix=":",
            ),
            mocker.call(
                "Created:",
                38,
                color=theme.highlight_color,
            ),
            mocker.call("1970-01-01 00:00\n\n", 52),
            mocker.call(
                "Modified:",
                66,
                color=theme.highlight_color,
            ),
            mocker.call("1970-01-01 00:00", 80),
        ]
    )


def test_files_and_folders_with_long_filenames(m5stickv, mocker, mock_file_operations):
    from krux.pages.file_manager import FileManager
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    # to view this directory
    mocker.patch(
        "krux.sd_card.SDHandler.dir_exists", mocker.MagicMock(side_effect=[True])
    )
    # first 2 entries are files, next 2 are directories
    mocker.patch(
        "krux.sd_card.SDHandler.file_exists",
        mocker.MagicMock(side_effect=[True, True, False, False]),
    )
    ctx = create_ctx(mocker, ([BUTTON_PAGE_PREV, BUTTON_ENTER]))  # to back and out
    file_manager = FileManager(ctx)
    file_manager.select_file()
    ctx.display.to_lines.assert_has_calls(
        [
            mocker.call("subdi..ong_name/"),
            mocker.call("subdir2/"),
            mocker.call("file1"),
            mocker.call("file2..long_name"),
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

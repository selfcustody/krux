from . import create_ctx
from .test_tools import mock_file_operations, SEEDS_JSON


def test_load_file(m5stickv, mocker, mock_file_operations):
    from krux.pages.utils import Utils
    from krux.input import BUTTON_ENTER
    from unittest.mock import mock_open, patch

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Pick first file
        BUTTON_ENTER,  # Confirm load
    ]
    ONLY_GET_FILENAME_OPTIONS = [True, False]
    for only_get_filename in ONLY_GET_FILENAME_OPTIONS:
        mocker.patch(
            "krux.sd_card.SDHandler.dir_exists",
            mocker.MagicMock(side_effect=[True, False]),
        )
        mocker.patch(
            "krux.sd_card.SDHandler.file_exists",
            mocker.MagicMock(side_effect=[True, True]),
        )
        ctx = create_ctx(mocker, BTN_SEQUENCE)
        with patch("builtins.open", mock_open(read_data=SEEDS_JSON)):
            utils = Utils(ctx)
            file_name, data = utils.load_file(
                prompt=False, only_get_filename=only_get_filename
            )

        assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
        assert file_name == "otherfile"
        if only_get_filename:
            assert data is None
        else:
            assert data == SEEDS_JSON


def test_load_file_with_no_sd(m5stickv, mocker):
    from krux.pages.utils import Utils

    mocker.patch(
        "krux.sd_card.SDHandler.dir_exists",
        mocker.MagicMock(return_value=False),
    )
    ctx = create_ctx(mocker, None)
    utils = Utils(ctx)
    file_name, data = utils.load_file(prompt=False)

    assert file_name == ""
    assert data is None

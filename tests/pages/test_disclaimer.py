from unittest.mock import patch
from . import create_ctx

TEXT = (
    "Krux is a research and development project, made by nerds building"
    " tools for their own interests, open to the world."
    + "\n\n"
    + "Innovative features may have undiscovered flaws that endanger funds."
)
WARNING = "Use it at your own risk."


def test_show(mocker, multiple_devices):
    from krux.pages.disclaimer import Disclaimer
    from krux.input import BUTTON_ENTER

    BTN_SEQUENCE = [BUTTON_ENTER]  # past the disclaimer

    ctx = create_ctx(mocker, BTN_SEQUENCE)

    Disclaimer(ctx).show()

    drawn_texts = [
        call.args[0] for call in ctx.display.draw_hcentered_text.call_args_list
    ]
    assert TEXT in drawn_texts
    assert WARNING in drawn_texts
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_show_paginated(m5stickv, mocker):
    from krux.pages.disclaimer import Disclaimer
    from krux.input import BUTTON_ENTER

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # past the first page
        BUTTON_ENTER,  # past the second page
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    # Text too long for the display, it will be split in two pages
    ctx.display.to_lines = mocker.MagicMock(return_value=[""] * 20)

    Disclaimer(ctx).show()

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_acknowledge_stores_version(mocker, multiple_devices):
    from krux.pages.disclaimer import Disclaimer
    from krux.metadata import VERSION
    from krux.input import BUTTON_ENTER
    from ..shared_mocks import MockFile, mock_open

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # past the disclaimer
        BUTTON_ENTER,  # "I understand"
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    mock_file = MockFile()

    with patch("builtins.open", mock_open(mock_file)):
        Disclaimer(ctx).show(acknowledge=True)

    drawn_texts = [
        call.args[0] for call in ctx.display.draw_hcentered_text.call_args_list
    ]
    assert TEXT in drawn_texts
    assert WARNING in drawn_texts
    assert mock_file.write_data == VERSION


def test_shutdown_instead_of_acknowledging(mocker, multiple_devices):
    from krux.pages.disclaimer import Disclaimer
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from ..shared_mocks import MockFile, mock_open

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # past the disclaimer
        BUTTON_PAGE,  # move to "Shutdown"
        BUTTON_ENTER,  # select it
        BUTTON_ENTER,  # confirm "Are you sure?"
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    mock_file = MockFile()

    with patch("builtins.open", mock_open(mock_file)):
        assert Disclaimer(ctx).show(acknowledge=True) is False

    # Nothing stored, disclaimer will be shown again on the next boot
    assert not mock_file.write_data


def test_acknowledged(m5stickv):
    from krux.pages.disclaimer import acknowledged
    from krux.metadata import VERSION
    from ..shared_mocks import MockFile, mock_open

    with patch("builtins.open", mock_open(MockFile(VERSION))):
        assert acknowledged() is True

    # Disclaimer acknowledged for an older version
    with patch("builtins.open", mock_open(MockFile("0.0.0"))):
        assert acknowledged() is False


def test_acknowledged_without_storage(m5stickv):
    from krux.pages.disclaimer import acknowledged, store_acknowledgment

    with patch("builtins.open", side_effect=OSError):
        assert acknowledged() is False
        # Does not raise, disclaimer will be shown again on the next boot
        store_acknowledgment()

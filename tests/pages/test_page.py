import pytest
from ..shared_mocks import mock_context
from . import create_ctx

TEST_QR_DATA = "test"
TEST_QR_DATA_IMAGE = bytearray(
    b"\x7f\xd3?H\nvU\xdd\xae\xa4\xdbut\x83\x80\xe0_\xf5\x070\x00O%7\x97\xd2\xd6\xd1\xe7\xc6\x1ae\xe5\xb2\x00J\xd5\x1f\xd9\t\xd23]N\xbckdu\xb5\x94\xa0\xaf\xf9\xb7\t\x00"
)


@pytest.fixture
def mock_page_cls(mocker):
    from krux.pages import Page, Menu

    class MockPage(Page):
        def __init__(self, ctx):
            Page.__init__(
                self,
                ctx,
                Menu(
                    ctx,
                    [
                        (("Test"), mocker.MagicMock()),
                    ],
                ),
            )

    return MockPage


def test_init(mocker, m5stickv, mock_page_cls):
    from krux.pages import Page

    page = mock_page_cls(mock_context(mocker))

    assert isinstance(page, Page)


def test_flash_text(mocker, m5stickv, mock_page_cls):
    from krux.display import FLASH_MSG_TIME
    from krux.themes import WHITE, RED

    ctx = mock_context(mocker)
    mocker.patch("time.ticks_ms", new=lambda: 0)
    page = mock_page_cls(ctx)

    page.flash_text("Hello world", duration=1000)

    ctx.display.flash_text.assert_called_with("Hello world", WHITE, 1000)

    page.flash_error("Error")

    assert ctx.display.flash_text.call_count == 2
    ctx.display.flash_text.assert_called_with("Error", RED, FLASH_MSG_TIME)


def test_prompt_m5stickv(mocker, m5stickv, mock_page_cls):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    # Enter pressed
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_ENTER])
    assert page.prompt("test prompt") == True

    # Page pressed
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_PAGE])
    assert page.prompt("test prompt") == False


def test_prompt_amigo(mocker, amigo, mock_page_cls):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_TOUCH

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    # Enter pressed
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_ENTER])
    assert page.prompt("test prompt") == True

    # Page, than Enter pressed
    page_press = [BUTTON_PAGE, BUTTON_ENTER]
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=page_press)
    assert page.prompt("test prompt") == False

    ctx.input.buttons_active = False
    # Index 1 = YES pressed
    ctx.input.touch = mocker.MagicMock(current_index=mocker.MagicMock(side_effect=[1]))
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_TOUCH])
    assert page.prompt("test prompt") == True

    # Index 0 = No pressed
    ctx.input.touch = mocker.MagicMock(current_index=mocker.MagicMock(side_effect=[0]))
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=[BUTTON_TOUCH])
    assert page.prompt("test prompt") == False


def test_display_qr_code(mocker, m5stickv, mock_page_cls):
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE

    ctx = create_ctx(mocker, [BUTTON_ENTER])
    page = mock_page_cls(ctx)

    # Test QR code display
    page.display_qr_codes(TEST_QR_DATA, FORMAT_NONE)

    assert ctx.input.wait_for_button.call_count == 1
    assert ctx.display.draw_qr_code.call_count == 1
    assert ctx.display.draw_qr_code.call_args == mocker.call(0, TEST_QR_DATA_IMAGE)


def test_display_qr_code_light_theme(mocker, m5stickv, mock_page_cls):
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.themes import theme, WHITE

    ctx = create_ctx(mocker, [BUTTON_ENTER])
    page = mock_page_cls(ctx)

    # Mock light theme background color
    theme.bg_color = WHITE
    # Test QR code display
    page.display_qr_codes(TEST_QR_DATA, FORMAT_NONE)

    assert ctx.input.wait_for_button.call_count == 1
    assert ctx.display.draw_qr_code.call_count == 1
    assert ctx.display.draw_qr_code.call_args == mocker.call(
        0, TEST_QR_DATA_IMAGE, light_color=WHITE
    )


def test_display_qr_code_loop_through_brightness(mocker, m5stickv, mock_page_cls):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE
    from krux.themes import WHITE, DARKGREY

    BTN_SEQUENCE = [
        *([BUTTON_PAGE] * 3),  # Loop through brightness
        BUTTON_ENTER,  # Exit
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = mock_page_cls(ctx)

    # Test QR code display
    page.display_qr_codes(TEST_QR_DATA, FORMAT_NONE)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_args_list == [
        mocker.call(0, TEST_QR_DATA_IMAGE),  # Default
        mocker.call(0, TEST_QR_DATA_IMAGE, light_color=WHITE),  # Brighter
        mocker.call(0, TEST_QR_DATA_IMAGE, light_color=DARKGREY),  # Darker
        mocker.call(0, TEST_QR_DATA_IMAGE),  # Default
    ]

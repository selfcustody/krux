import pytest
from ..shared_mocks import mock_context


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

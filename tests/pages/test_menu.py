from krux.input import BUTTON_ENTER, BUTTON_PAGE
from ..shared_mocks import *


def test_init(mocker):
    from krux.pages import Menu

    menu = Menu(mock.MagicMock(), [])

    assert isinstance(menu, Menu)


def test_run_loop(mocker):
    from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, MENU_SHUTDOWN

    ctx = mock.MagicMock()

    def exception_raiser():
        raise ValueError("oops")

    menu = Menu(
        ctx,
        [
            ("Option", lambda: MENU_CONTINUE),
            ("Long Option", lambda: MENU_EXIT),
            ("Longer Option", lambda: MENU_SHUTDOWN),
            ("The Longest Option", exception_raiser),
        ],
    )

    ctx.input.wait_for_button.side_effect = [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]
    ctx.display.to_lines.side_effect = [
        ["Option"],
        ["- Option -"],
        ["Long Option"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["Option"],
        ["- Option -"],
        ["Long Option"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["Option"],
        ["Long Option"],
        ["- Long Option -"],
        ["Longer Option"],
        ["The Longest", "Option"],
    ]

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT

    ctx.input.wait_for_button.side_effect = [BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER]
    ctx.display.to_lines.side_effect = [
        ["Option"],
        ["- Option -"],
        ["Long Option"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["Option"],
        ["Long Option"],
        ["- Long Option -"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["Option"],
        ["Long Option"],
        ["Longer Option"],
        ["- Longer Option -"],
        ["The Longest", "Option"],
    ]

    index, status = menu.run_loop()
    assert index == 2
    assert status == MENU_SHUTDOWN

    ctx.input.wait_for_button.side_effect = [
        BUTTON_PAGE,
        BUTTON_PAGE,
        BUTTON_PAGE,
        BUTTON_ENTER,
        BUTTON_ENTER,
        BUTTON_PAGE,
        BUTTON_PAGE,
        BUTTON_ENTER,
    ]
    ctx.display.to_lines.side_effect = [
        ["Option"],
        ["- Option -"],
        ["Long Option"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["Option"],
        ["Long Option"],
        ["- Long Option -"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["Option"],
        ["Long Option"],
        ["Longer Option"],
        ["- Longer Option -"],
        ["The Longest", "Option"],
        ["Option"],
        ["Long Option"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["- The", "Longest -"],
        ["Option"],
        ["Long Option"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["- The", "Longest -"],
        ["Option"],
        ["- Option -"],
        ["Long Option"],
        ["Longer Option"],
        ["The Longest", "Option"],
        ["Option"],
        ["Long Option"],
        ["- Long Option -"],
        ["Longer Option"],
        ["The Longest", "Option"],
    ]

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT

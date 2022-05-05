from ..shared_mocks import *
from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH


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

    ctx.input.wait_for_button.side_effect = [
        BUTTON_ENTER,
        BUTTON_PAGE,
        BUTTON_PAGE_PREV,
        BUTTON_PAGE,
        BUTTON_ENTER,
    ]

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT

    ctx.input.wait_for_button.side_effect = [
        BUTTON_PAGE_PREV,
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
    ]

    index, status = menu.run_loop()
    assert index == 2
    assert status == MENU_SHUTDOWN

    mocker.patch.object(ctx.input.touch, "current_index", new=lambda: 1)
    mocker.patch.object(ctx.input, "buttons_active", False)
    ctx.input.wait_for_button.side_effect = [BUTTON_TOUCH]
    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT

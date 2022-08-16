def test_init(mocker, m5stickv):
    from krux.pages import Menu, MENU_EXIT

    menu = Menu(
        mocker.MagicMock(
            display=mocker.MagicMock(
                font_width=8,
                font_height=14,
                width=mocker.MagicMock(return_value=135),
                height=mocker.MagicMock(return_value=240),
                to_lines=mocker.MagicMock(return_value=[""]),
            ),
        ),
        [("Long Option", lambda: MENU_EXIT)],
    )

    assert isinstance(menu, Menu)


def test_run_loop(mocker, m5stickv):
    import board
    from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, MENU_SHUTDOWN
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mocker.MagicMock(
        display=mocker.MagicMock(
            font_width=8,
            font_height=14,
            width=mocker.MagicMock(return_value=135),
            height=mocker.MagicMock(return_value=240),
            to_lines=mocker.MagicMock(return_value=[""]),
        ),
    )

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

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT

    ctx.input.wait_for_button.side_effect = [BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER]

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

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT


def test_run_loop_on_amigo_tft(mocker, amigo_tft):
    from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, MENU_SHUTDOWN
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH

    ctx = mocker.MagicMock(
        display=mocker.MagicMock(
            font_width=8,
            font_height=14,
            width=mocker.MagicMock(return_value=135),
            height=mocker.MagicMock(return_value=240),
            to_lines=mocker.MagicMock(return_value=[""]),
        ),
    )

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

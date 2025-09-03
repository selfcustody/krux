from tests.shared_mocks import mock_context


def test_init(mocker, m5stickv):
    from krux.pages import Menu, MENU_EXIT

    menu = Menu(
        mock_context(mocker),
        [("Long Option", lambda: MENU_EXIT)],
    )

    assert isinstance(menu, Menu)


def test_run_loop(mocker, m5stickv):
    from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, MENU_SHUTDOWN
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mock_context(mocker)

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
        back_label=None,
    )

    BTN_SEQUENCE = [BUTTON_ENTER, BUTTON_PAGE, BUTTON_ENTER]
    call_count = len(BTN_SEQUENCE)
    ctx.input.wait_for_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT
    assert ctx.input.wait_for_button.call_count == call_count

    BTN_SEQUENCE = [BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER]
    call_count += len(BTN_SEQUENCE)
    ctx.input.wait_for_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 2
    assert status == MENU_SHUTDOWN
    assert ctx.input.wait_for_button.call_count == call_count

    BTN_SEQUENCE = [
        BUTTON_PAGE,
        BUTTON_PAGE,
        BUTTON_PAGE,
        BUTTON_ENTER,
        BUTTON_ENTER,
        BUTTON_PAGE,
        BUTTON_PAGE,
        BUTTON_ENTER,
    ]
    call_count += len(BTN_SEQUENCE)
    ctx.input.wait_for_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT
    assert ctx.input.wait_for_button.call_count == call_count


def test_run_loop_on_amigo_tft(mocker, amigo):
    from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, MENU_SHUTDOWN
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH

    ctx = mock_context(mocker)

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
        back_label=None,
    )

    BTN_SEQUENCE = [
        BUTTON_ENTER,
        BUTTON_PAGE,
        BUTTON_PAGE_PREV,
        BUTTON_PAGE,
        BUTTON_ENTER,
    ]
    call_count = len(BTN_SEQUENCE)
    ctx.input.wait_for_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT
    assert ctx.input.wait_for_button.call_count == call_count

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
    ]
    call_count += len(BTN_SEQUENCE)
    ctx.input.wait_for_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 2
    assert status == MENU_SHUTDOWN
    assert ctx.input.wait_for_button.call_count == call_count

    mocker.patch.object(ctx.input.touch, "current_index", new=lambda: 1)
    mocker.patch.object(ctx.input, "buttons_active", False)

    BTN_SEQUENCE = [BUTTON_TOUCH]
    call_count += len(BTN_SEQUENCE)
    ctx.input.wait_for_button.side_effect = BTN_SEQUENCE
    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT
    assert ctx.input.wait_for_button.call_count == call_count


def test_two_screens_menu(mocker, amigo):
    from krux.pages import Menu, MENU_CONTINUE, MENU_EXIT, MENU_SHUTDOWN
    from krux.input import (
        BUTTON_ENTER,
        BUTTON_PAGE,
        BUTTON_PAGE_PREV,
        SWIPE_UP,
        SWIPE_DOWN,
    )

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # click index 0
        + [BUTTON_PAGE]
        + [BUTTON_ENTER]  # click index 1
        + [BUTTON_ENTER]  # click index 1
        + [BUTTON_PAGE]
        + [BUTTON_ENTER]  # click index 2
        + [BUTTON_PAGE] * 2
        + [BUTTON_ENTER]  # click 4
        + [BUTTON_PAGE] * 2
        + [BUTTON_ENTER]  # click 0
        + [BUTTON_PAGE_PREV]  # back
        + [BUTTON_ENTER]  # click back
    )
    ctx = mock_context(mocker)
    ctx.input.wait_for_button.side_effect = BTN_SEQUENCE
    # each menu page has 3 items
    ctx.display.max_menu_lines.return_value = 3
    print(ctx.display.max_menu_lines())

    menu_items = []
    seq_clicked = []

    def _click(i="a", seq=None):
        seq.append(i)
        print("click", i, seq)
        return MENU_CONTINUE

    # 3 items first page, 2 items + back second page
    menu_qtd = 5
    for i in range(menu_qtd):
        menu_items += [(str(i), lambda i=i, seq=seq_clicked: _click(i, seq))]
    menu = Menu(
        ctx,
        menu_items,
    )
    index, status = menu.run_loop()
    first_seq_clicked = [0, 1, 1, 2, 4, 0]
    assert seq_clicked == first_seq_clicked
    assert index == menu.back_index
    assert status == MENU_EXIT
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # click index 0
        + [BUTTON_PAGE]
        + [BUTTON_ENTER]  # click index 1
        + [BUTTON_ENTER]  # click index 1
        + [SWIPE_DOWN]  # go to last index on new menu page
        + [BUTTON_PAGE_PREV]  # go to one before back
        + [BUTTON_ENTER]  # click index 4
        + [SWIPE_UP]  # go to first index on new menu page
        + [BUTTON_ENTER]  # click 0
        + [None]  # waited sufficient time to start screensaver
        + [BUTTON_ENTER]  # Dismiss screensaver
        + [BUTTON_PAGE_PREV]  # back
        + [BUTTON_ENTER]  # click back
    )

    ctx.input.wait_for_button.side_effect = BTN_SEQUENCE
    ctx.input.wait_for_button.call_count = 0
    seq_clicked = []

    menu_items = []
    for i in range(menu_qtd):
        menu_items += [(str(i), lambda i=i, seq=seq_clicked: _click(i, seq))]
    menu = Menu(
        ctx,
        menu_items,
    )
    index, status = menu.run_loop()
    assert seq_clicked == [0, 1, 1, 4, 0]
    assert index == menu.back_index
    assert status == MENU_EXIT
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

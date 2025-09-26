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
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT
    assert ctx.input.wait_for_fastnav_button.call_count == call_count

    BTN_SEQUENCE = [BUTTON_PAGE, BUTTON_PAGE, BUTTON_ENTER]
    call_count += len(BTN_SEQUENCE)
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 2
    assert status == MENU_SHUTDOWN
    assert ctx.input.wait_for_fastnav_button.call_count == call_count

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
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT
    assert ctx.input.wait_for_fastnav_button.call_count == call_count


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
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT
    assert ctx.input.wait_for_fastnav_button.call_count == call_count

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
    ]
    call_count += len(BTN_SEQUENCE)
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    ctx.power_manager.battery_charge_remaining.return_value = 1

    index, status = menu.run_loop()
    assert index == 2
    assert status == MENU_SHUTDOWN
    assert ctx.input.wait_for_fastnav_button.call_count == call_count

    mocker.patch.object(ctx.input.touch, "current_index", new=lambda: 1)
    mocker.patch.object(ctx.input, "buttons_active", False)

    BTN_SEQUENCE = [BUTTON_TOUCH]
    call_count += len(BTN_SEQUENCE)
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    index, status = menu.run_loop()
    assert index == 1
    assert status == MENU_EXIT
    assert ctx.input.wait_for_fastnav_button.call_count == call_count


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
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
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
    assert ctx.input.wait_for_fastnav_button.call_count == len(BTN_SEQUENCE)

    BTN_SEQUENCE = (
        [BUTTON_ENTER]  # click index 0
        + [BUTTON_PAGE]
        + [BUTTON_ENTER]  # click index 1
        + [BUTTON_ENTER]  # click index 1
        + [SWIPE_DOWN]  # go to last index on new menu page #5
        + [BUTTON_PAGE_PREV]  # go to one before back
        + [BUTTON_ENTER]  # click index 4
        + [SWIPE_UP]  # go to first index on new menu page
        + [BUTTON_ENTER]  # click 0
        + [None]  # waited sufficient time to start screensaver
        + [BUTTON_ENTER]  # Dismiss screensaver
        + [BUTTON_PAGE_PREV]  # back
        + [BUTTON_ENTER]  # click back
    )

    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    ctx.input.wait_for_fastnav_button.call_count = 0
    ctx.input.wait_for_button = (
        ctx.input.wait_for_fastnav_button
    )  # screensaver will call for wait_for_button
    seq_clicked = []

    menu_items = []
    for i in range(menu_qtd):
        menu_items += [(str(i), lambda i=i, seq=seq_clicked: _click(i, seq))]
    menu = Menu(
        ctx,
        menu_items,
    )
    print(menu_items)
    index, status = menu.run_loop()
    assert seq_clicked == [0, 1, 1, 4, 0]
    assert index == menu.back_index
    assert status == MENU_EXIT
    assert ctx.input.wait_for_fastnav_button.call_count == len(BTN_SEQUENCE)


def test_swipe_up(mocker, amigo):
    from krux.pages import Menu, MENU_EXIT, MENU_CONTINUE
    from krux.input import SWIPE_UP

    ctx = mock_context(mocker)
    menu = Menu(ctx, [])

    def swipe_fnc():
        return (1, MENU_EXIT)

    assert menu._process_swipe_up(0, swipe_up_fnc=swipe_fnc) == (1, MENU_EXIT)
    assert menu._process_swipe_down(0, swipe_down_fnc=swipe_fnc) == (1, MENU_EXIT)

    BTN_SEQUENCE = [
        SWIPE_UP,
    ]
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    index, status = menu.run_loop(swipe_up_fnc=swipe_fnc)
    assert index == 1
    assert status == MENU_EXIT

    def swipe_fnc_continue():
        return (2, MENU_CONTINUE)

    assert menu._process_swipe_up(0, swipe_up_fnc=swipe_fnc_continue) == 0
    assert menu._process_swipe_down(0, swipe_down_fnc=swipe_fnc_continue) == 0


def test_start_from(mocker, m5stickv):
    from krux.pages import Menu, MENU_EXIT, MENU_CONTINUE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    ctx = mock_context(mocker)

    mock_fnc = mocker.MagicMock(return_value=MENU_CONTINUE)
    menu_items = [
        ("1", mock_fnc),
        ("2", lambda: MENU_EXIT),
    ]
    menu = Menu(ctx, menu_items)
    # test start menu clicking on index 1 that will exit
    index, status = menu.run_loop(start_from_index=1)
    assert index == 1
    assert status == MENU_EXIT

    # test start menu clicking on index 0 that will NOT exit
    BTN_SEQUENCE = [BUTTON_PAGE_PREV] + [BUTTON_ENTER]  # go to back  # click back
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    index, status = menu.run_loop(start_from_index=0)
    assert index == menu.back_index
    assert status == MENU_EXIT
    mock_fnc.assert_called()
    assert ctx.input.wait_for_fastnav_button.call_count == len(BTN_SEQUENCE)


def test_disabled_entry(mocker, m5stickv):
    from krux.pages import Menu, MENU_EXIT
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mock_context(mocker)
    menu_items = [("Disabled", None)]
    BTN_SEQUENCE = (
        [BUTTON_ENTER] + [BUTTON_PAGE] + [BUTTON_ENTER]  # click disabled  # click back
    )
    ctx.input.wait_for_fastnav_button.side_effect = BTN_SEQUENCE
    menu = Menu(ctx, menu_items)
    index, status = menu.run_loop()
    assert index == menu.back_index
    assert status == MENU_EXIT
    assert ctx.input.wait_for_fastnav_button.call_count == len(BTN_SEQUENCE)

import pytest

from . import create_ctx


def test_load_key_menu_is_format_first(m5stickv, mocker):
    from krux.pages import MENU_CONTINUE
    from krux.pages.login import Login

    ctx = create_ctx(mocker, [])
    login = Login(ctx)
    menu = mocker.patch("krux.pages.mnemonic_loader.Menu")
    menu.return_value.back_index = 4
    menu.return_value.run_loop.return_value = (4, MENU_CONTINUE)

    login.load_key()

    items = menu.call_args.args[1]
    assert [label for label, _ in items] == [
        "QR Code",
        "Words",
        "From Storage",
        "Other Formats",
    ]
    assert [handler for _, handler in items] == [
        login.load_key_from_qr_code,
        login.load_key_from_text,
        login.load_mnemonic_from_storage,
        login.load_other_formats,
    ]


def test_load_key_translates_other_formats(m5stickv, mocker):
    from krux.krux_settings import locale_control
    from krux.pages import MENU_CONTINUE
    from krux.pages.login import Login

    locale_control.load_locale("pt-BR")
    ctx = create_ctx(mocker, [])
    login = Login(ctx)
    menu = mocker.patch("krux.pages.mnemonic_loader.Menu")
    menu.return_value.back_index = 4
    menu.return_value.run_loop.return_value = (4, MENU_CONTINUE)

    login.load_key()

    items = menu.call_args.args[1]
    assert items[3][0] == "Outros Formatos"


def test_other_formats_menu_routes_existing_handlers(m5stickv, mocker):
    from krux.pages import MENU_CONTINUE
    from krux.pages.login import Login

    ctx = create_ctx(mocker, [])
    login = Login(ctx)
    menu = mocker.patch("krux.pages.mnemonic_loader.Menu")
    menu.return_value.back_index = 6
    menu.return_value.run_loop.return_value = (6, MENU_CONTINUE)
    mocker.patch.object(
        login,
        "load_key_from_tiny_seed_image",
        side_effect=lambda grid_type: "scan " + grid_type,
    )
    mocker.patch.object(login, "load_key_from_tiny_seed", return_value="bits")
    mocker.patch.object(login, "pre_load_key_from_digits", return_value="numbers")
    mocker.patch.object(login, "load_key_from_1248", return_value="stackbit")

    login.load_other_formats()

    items = menu.call_args.args[1]
    assert [label for label, _ in items] == [
        "Tinyseed (scan)",
        "Binary Grid (manual)",
        "OneKey KeyTag (scan)",
        "Binary Grid (scan)",
        "Word Numbers",
        "Stackbit 1248",
    ]
    assert [handler() for _, handler in items] == [
        "scan Tinyseed",
        "bits",
        "scan OneKey KeyTag",
        "scan Binary Grid",
        "numbers",
        "stackbit",
    ]


def test_other_formats_translates_input_methods(m5stickv, mocker):
    from krux.krux_settings import locale_control
    from krux.pages import MENU_CONTINUE
    from krux.pages.login import Login

    locale_control.load_locale("pt-BR")
    ctx = create_ctx(mocker, [])
    login = Login(ctx)
    menu = mocker.patch("krux.pages.mnemonic_loader.Menu")
    menu.return_value.back_index = 6
    menu.return_value.run_loop.return_value = (6, MENU_CONTINUE)

    login.load_other_formats()

    items = menu.call_args.args[1]
    assert [label for label, _ in items[:4]] == [
        "Tinyseed (escanear)",
        "Grade binária (manual)",
        "OneKey KeyTag (escanear)",
        "Grade binária (escanear)",
    ]


@pytest.mark.parametrize(
    "item_index,handler_name",
    [
        (0, "load_key_from_qr_code"),
        (1, "load_key_from_text"),
        (2, "load_mnemonic_from_storage"),
    ],
)
def test_cancel_direct_format_returns_to_load_menu(
    m5stickv, mocker, item_index, handler_name
):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages import MENU_CONTINUE
    from krux.pages.login import Login

    buttons = (
        [BUTTON_PAGE] * item_index
        + [BUTTON_ENTER]
        + [BUTTON_PAGE_PREV] * (item_index + 1)
        + [BUTTON_ENTER]
    )
    ctx = create_ctx(mocker, buttons)
    login = Login(ctx)
    mocker.patch.object(login, handler_name, return_value=MENU_CONTINUE)

    assert login.load_key() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(buttons)


def test_cancel_specialist_format_returns_through_both_menus(m5stickv, mocker):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.pages import MENU_CONTINUE
    from krux.pages.login import Login

    buttons = (
        [BUTTON_PAGE] * 3
        + [BUTTON_ENTER]  # Other Formats
        + [BUTTON_ENTER]  # Tinyseed
        + [BUTTON_PAGE_PREV, BUTTON_ENTER]  # Back from Other Formats
        + [BUTTON_PAGE, BUTTON_ENTER]  # Back from Load Mnemonic
    )
    ctx = create_ctx(mocker, buttons)
    login = Login(ctx)
    mocker.patch.object(
        login, "load_key_from_tiny_seed_image", return_value=MENU_CONTINUE
    )

    assert login.load_key() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(buttons)

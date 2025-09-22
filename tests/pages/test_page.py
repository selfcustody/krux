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

    ctx.display.flash_text.assert_called_with(
        "Hello world", WHITE, 1000, highlight_prefix=""
    )

    page.flash_error("Error")

    assert ctx.display.flash_text.call_count == 2
    ctx.display.flash_text.assert_called_with(
        "Error", RED, FLASH_MSG_TIME, highlight_prefix=""
    )


def test_prompt_m5stickv(mocker, m5stickv, mock_page_cls):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    # Enter pressed
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=BTN_SEQUENCE)
    assert page.prompt("test prompt") == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Page pressed
    BTN_SEQUENCE = [BUTTON_PAGE]
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=BTN_SEQUENCE)
    assert page.prompt("test prompt") == False
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_prompt_amigo(mocker, amigo, mock_page_cls):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_TOUCH

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    # Enter pressed
    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=BTN_SEQUENCE)
    assert page.prompt("test prompt") == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Page, than Enter pressed
    page_press = [BUTTON_PAGE, BUTTON_ENTER]
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=page_press)
    assert page.prompt("test prompt") == False
    assert ctx.input.wait_for_button.call_count == len(page_press)

    ctx.input.buttons_active = False
    # Index 1 = YES pressed
    BTN_SEQUENCE = [BUTTON_TOUCH]
    ctx.input.touch = mocker.MagicMock(current_index=mocker.MagicMock(side_effect=[1]))
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=BTN_SEQUENCE)
    assert page.prompt("test prompt") == True
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)

    # Index 0 = No pressed
    ctx.input.touch = mocker.MagicMock(current_index=mocker.MagicMock(side_effect=[0]))
    ctx.input.wait_for_button = mocker.MagicMock(side_effect=BTN_SEQUENCE)
    assert page.prompt("test prompt") == False
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_display_qr_code(mocker, m5stickv, mock_page_cls):
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE

    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = mock_page_cls(ctx)

    # Test QR code display
    page.display_qr_codes(TEST_QR_DATA, FORMAT_NONE)

    assert ctx.input.wait_for_button.call_count == 1
    assert ctx.display.draw_qr_code.call_count == 1
    assert ctx.display.draw_qr_code.call_args == mocker.call(
        TEST_QR_DATA_IMAGE, 0, 0, 0
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_display_qr_code_light_theme(mocker, m5stickv, mock_page_cls):
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.themes import theme, WHITE

    BTN_SEQUENCE = [BUTTON_ENTER]
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = mock_page_cls(ctx)

    # Mock light theme background color
    theme.bg_color = WHITE
    # Test QR code display
    page.display_qr_codes(TEST_QR_DATA, FORMAT_NONE)

    assert ctx.input.wait_for_button.call_count == 1
    assert ctx.display.draw_qr_code.call_count == 1
    assert ctx.display.draw_qr_code.call_args == mocker.call(
        TEST_QR_DATA_IMAGE, 0, 0, 0, light_color=WHITE
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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
        mocker.call(TEST_QR_DATA_IMAGE, 0, 0, 0),  # Default
        mocker.call(TEST_QR_DATA_IMAGE, 0, 0, 0, light_color=WHITE),  # Brighter
        mocker.call(TEST_QR_DATA_IMAGE, 0, 0, 0, light_color=DARKGREY),  # Darker
        mocker.call(TEST_QR_DATA_IMAGE, 0, 0, 0),  # Default
    ]


def get_frame_titles_resulting_from_input(
    mocker, mock_page_cls, title, input_seq, use_buttons=False, has_touch=True
):
    from krux.input import BUTTON_TOUCH, SWIPE_RIGHT, BUTTON_PAGE, BUTTON_ENTER
    from krux.pages.keypads import Keypad
    from krux.kboard import kboard

    def get_button_seq(key_index):
        return [*([BUTTON_PAGE] * (key_index - 1))] + [BUTTON_ENTER]

    keysets = ["123", "456"]  # both should be the same length
    pad = Keypad(create_ctx(mocker, None), keysets, None)

    button_seq = []
    touch_seq = [] if has_touch else None
    input_seq.append("go key")  # to exit capture_from_keypad

    if has_touch and not use_buttons:
        for i in input_seq:
            if i == "more key":
                button_seq.append(BUTTON_TOUCH)
                touch_seq.append(pad.more_index)
            elif i == "go key":
                button_seq.append(BUTTON_TOUCH)
                touch_seq.append(pad.go_index)
            elif i == "normal key":
                button_seq.append(BUTTON_TOUCH)
                touch_seq.append(1)
            elif i == "swipe":
                button_seq.append(SWIPE_RIGHT)
    else:
        for i in input_seq:
            if i == "more key":
                button_seq = button_seq + get_button_seq(pad.more_index)
            elif i == "go key":
                button_seq = button_seq + get_button_seq(pad.go_index)
            elif i == "normal key":
                button_seq = button_seq + get_button_seq(1)

    ctx = create_ctx(mocker, button_seq, None, None, touch_seq)
    if not has_touch:
        ctx.input.touch = None
        kboard.has_touchscreen = False
    page = mock_page_cls(ctx)
    captured = page.capture_from_keypad(title, keysets)
    frame_titles = [
        t[0][0] for t in ctx.display.draw_hcentered_text.call_args_list if t[0][1] == 10
    ]
    return frame_titles


def test_keypad_esc_no_exit(mocker, amigo):
    from krux.pages import Page, LETTERS
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    btn_seq = (
        [BUTTON_PAGE_PREV] * 2  # go to ESC
        + [BUTTON_ENTER]  # press ESC to exit
        + [BUTTON_PAGE_PREV, BUTTON_ENTER]  # No
        + [BUTTON_ENTER]  # press ESC to exit
        + [BUTTON_ENTER]  # Yes
    )

    ctx = create_ctx(mocker, btn_seq)
    assert ctx.input.touch is not None

    page = Page(ctx)
    page.capture_from_keypad("test", [LETTERS])

    assert ctx.input.touch.set_regions.call_count == 4
    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_keypad_swipe_hint_is_shown_after_more_keypress_and_cleared_after_other_keypress(
    mocker, amigo, mock_page_cls
):
    from krux.pages import SWIPE_L_CHAR, SWIPE_R_CHAR

    initial_txt = "title"
    swipe_txt = SWIPE_L_CHAR + " swipe " + SWIPE_R_CHAR
    frame_titles = get_frame_titles_resulting_from_input(
        mocker,
        mock_page_cls,
        initial_txt,
        ["more key", "normal key", "normal key", "more key"],
    )

    assert frame_titles[0] == initial_txt  # initial
    assert frame_titles[1] == swipe_txt  # after more key
    assert frame_titles[2] == initial_txt  # after normal key
    assert frame_titles[3] == initial_txt  # after normal key
    assert frame_titles[4] == swipe_txt  # after more key


def test_keypad_swipe_hint_is_not_shown_once_user_has_swiped(
    mocker, amigo, mock_page_cls
):
    from krux.pages import SWIPE_L_CHAR, SWIPE_R_CHAR

    initial_txt = "title"
    swipe_txt = SWIPE_L_CHAR + " swipe " + SWIPE_R_CHAR
    frame_titles = get_frame_titles_resulting_from_input(
        mocker,
        mock_page_cls,
        initial_txt,
        ["normal key", "more key", "normal key", "swipe", "more key"],
    )
    assert frame_titles[0] == initial_txt  # initial
    assert frame_titles[1] == initial_txt  # after normal key
    assert frame_titles[2] == swipe_txt  # after more key
    assert frame_titles[3] == initial_txt  # after normal key
    assert frame_titles[4] == initial_txt  # after swipe
    assert frame_titles[5] == initial_txt  # after more key (NO MORE HINT)


def test_keypad_swipe_hint_is_not_shown_on_nontouch_device(
    mocker, amigo, mock_page_cls
):
    from krux.pages import SWIPE_L_CHAR, SWIPE_R_CHAR

    initial_txt = "title"
    swipe_txt = SWIPE_L_CHAR + " swipe " + SWIPE_R_CHAR

    # first check we get a hint if we have a touchscreen
    frame_titles = get_frame_titles_resulting_from_input(
        mocker,
        mock_page_cls,
        initial_txt,
        ["more key"],
        use_buttons=True,  # force use of buttons so that we're using non-touch input
        has_touch=True,
    )
    assert swipe_txt in frame_titles

    # now check that the same input does *not* show hint if we don't have a touchscreen
    frame_titles = get_frame_titles_resulting_from_input(
        mocker,
        mock_page_cls,
        initial_txt,
        ["more key"],
        use_buttons=True,
        has_touch=False,  # this time no touch screen
    )
    assert swipe_txt not in frame_titles


def test_fit_to_line_text(mocker, multiple_devices, mock_page_cls):
    import board
    from krux.display import FONT_WIDTH

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    TXT = "text"
    AMIGO = "amigo"
    M5 = "m5stickv"
    DOCK = "dock"

    cases = [
        {
            TXT: "0123456789abcdefghijklmnopqrstuvwxyz",
            AMIGO: "0123456789ab…opqrstuvwxyz",
            M5: "0123456…tuvwxyz",
            DOCK: "0123456789abc…nopqrstuvwxyz",
        },
        {
            TXT: "0123456789abcdefghijklmnopqrstuvwxy",
            AMIGO: "0123456789ab…nopqrstuvwxy",
            M5: "0123456…stuvwxy",
            DOCK: "0123456789abc…mnopqrstuvwxy",
        },
        {
            TXT: "0123456789abcdefghijklmnopqrstuvwx",
            AMIGO: "0123456789ab…mnopqrstuvwx",
            M5: "0123456…rstuvwx",
            DOCK: "0123456789abc…lmnopqrstuvwx",
        },
        {
            TXT: "0123456789abcdefghijklmnopqrstuvw",
            AMIGO: "0123456789ab…lmnopqrstuvw",
            M5: "0123456…qrstuvw",
            DOCK: "0123456789abc…klmnopqrstuvw",
        },
        {
            TXT: "0123456789abcdefghijklmnopqr",
            AMIGO: "0123456789ab…ghijklmnopqr",
            M5: "0123456…lmnopqr",
            DOCK: "0123456789abc…fghijklmnopqr",
        },
        {
            TXT: "0123456789abcdefghijklmnopq",
            AMIGO: "0123456789ab…fghijklmnopq",
            M5: "0123456…klmnopq",
            DOCK: "0123456789abcdefghijklmnopq",
        },
        {
            TXT: "0123456789abcdefghijklmnop",
            AMIGO: "0123456789ab…efghijklmnop",
            M5: "0123456…jklmnop",
            DOCK: "0123456789abcdefghijklmnop",
        },
        {
            TXT: "0123456789abcdefghijklmno",
            AMIGO: "0123456789abcdefghijklmno",
            M5: "0123456…ijklmno",
            DOCK: "0123456789abcdefghijklmno",
        },
        {
            TXT: "0123456789abcdefghijklmn",
            AMIGO: "0123456789abcdefghijklmn",
            M5: "0123456…hijklmn",
            DOCK: "0123456789abcdefghijklmn",
        },
        {
            TXT: "0123456789abcdefghijklm",
            AMIGO: "0123456789abcdefghijklm",
            M5: "0123456…ghijklm",
            DOCK: "0123456789abcdefghijklm",
        },
        {
            TXT: "0123456789abcdefghij",
            AMIGO: "0123456789abcdefghij",
            M5: "0123456…defghij",
            DOCK: "0123456789abcdefghij",
        },
        {
            TXT: "0123456789abcdefg",
            AMIGO: "0123456789abcdefg",
            M5: "0123456…abcdefg",
            DOCK: "0123456789abcdefg",
        },
        {
            TXT: "0123456789abcdef",
            AMIGO: "0123456789abcdef",
            M5: "0123456789abcdef",
            DOCK: "0123456789abcdef",
        },
        {
            TXT: "0123456789abcde",
            AMIGO: "0123456789abcde",
            M5: "0123456789abcde",
            DOCK: "0123456789abcde",
        },
    ]

    curr_device = board.config["type"]
    device_type = curr_device if curr_device in (AMIGO, M5) else DOCK
    max_chars_in_line = ctx.display.ascii_chars_per_line()

    for i, case in enumerate(cases):
        print(i)
        formatted_text = page.fit_to_line(case[TXT])
        assert len(formatted_text) <= max_chars_in_line
        assert formatted_text == case[device_type]


def test_fit_to_line_prefix(mocker, multiple_devices, mock_page_cls):
    import board
    from krux.display import FONT_WIDTH

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    PREFIX = "prefix"
    TXT = "text"
    AMIGO = "amigo"
    M5 = "m5stickv"
    DOCK = "dock"

    cases = [
        {
            PREFIX: "1 .",
            TXT: "0123456789abcdefghijklmnopqrstuvwxyz",
            AMIGO: "1 .0123456789…qrstuvwxyz",
            M5: "1 .012345…uvwxyz",
            DOCK: "1 .0123456789a…pqrstuvwxyz",
        },
        {
            PREFIX: "1234567890abcd .",
            TXT: "0123456789abcdefghijklmnopqrstuvwxyz",
            AMIGO: "1234567890abcd .0123…wxyz",
            M5: "1234567890abcd .",
            DOCK: "1234567890abcd .01234…vwxyz",
        },
        {
            PREFIX: "1234567890abcdefghi .",
            TXT: "jjkkll",
            AMIGO: "1234567890abcdefghi .",
            M5: "1234567…efghi .",
            DOCK: "1234567890abcdefghi .jjkkll",
        },
        {
            PREFIX: "1234567890abcdefgh .",
            TXT: "jjkkll",
            AMIGO: "1234567890abcdefgh .jj…ll",
            M5: "1234567…defgh .",
            DOCK: "1234567890abcdefgh .jjkkll",
        },
    ]

    curr_device = board.config["type"]
    device_type = curr_device if curr_device in (AMIGO, M5) else DOCK
    max_chars_in_line = ctx.display.ascii_chars_per_line()

    for i, case in enumerate(cases):
        print(i)
        formatted_text = page.fit_to_line(case[TXT], case[PREFIX])
        assert len(formatted_text) <= max_chars_in_line
        assert formatted_text == case[device_type]


def test_fit_to_line_not_crop_middle(mocker, multiple_devices, mock_page_cls):
    import board
    from krux.display import FONT_WIDTH

    ctx = mock_context(mocker)
    page = mock_page_cls(ctx)

    PREFIX = "prefix"
    TXT = "text"
    AMIGO = "amigo"
    M5 = "m5stickv"
    DOCK = "dock"

    cases = [
        {
            PREFIX: "",
            TXT: "0123456789abcdefghijklmnopqrstuvwxyz",
            AMIGO: "0123456789abcdefghijklmn…",
            M5: "0123456789abcde…",
            DOCK: "0123456789abcdefghijklmnop…",
        },
        {
            PREFIX: "",
            TXT: "0123456789abcdefghijklmno",
            AMIGO: "0123456789abcdefghijklmno",
            M5: "0123456789abcde…",
            DOCK: "0123456789abcdefghijklmno",
        },
        {
            PREFIX: "",
            TXT: "0123456789abcdef",
            AMIGO: "0123456789abcdef",
            M5: "0123456789abcdef",
            DOCK: "0123456789abcdef",
        },
        {
            PREFIX: "1 .",
            TXT: "0123456789abcdefghijklmnopqrstuvwxyz",
            AMIGO: "1 .0123456789abcdefghijk…",
            M5: "1 .0123456789ab…",
            DOCK: "1 .0123456789abcdefghijklm…",
        },
        {
            PREFIX: "1234567890abcd .",
            TXT: "0123456789abcdefghijklmnopqrstuvwxyz",
            AMIGO: "1234567890abcd .01234567…",
            M5: "1234567890abcd .",
            DOCK: "1234567890abcd .0123456789…",
        },
        {
            PREFIX: "1234567890abcdefghi .",
            TXT: "jjkkll",
            AMIGO: "1234567890abcdefghi .",
            M5: "1234567890abcde…",
            DOCK: "1234567890abcdefghi .jjkkll",
        },
        {
            PREFIX: "1234567890abcdefgh .",
            TXT: "jjkkll",
            AMIGO: "1234567890abcdefgh .jjkk…",
            M5: "1234567890abcde…",
            DOCK: "1234567890abcdefgh .jjkkll",
        },
    ]

    curr_device = board.config["type"]
    device_type = curr_device if curr_device in (AMIGO, M5) else DOCK
    max_chars_in_line = ctx.display.ascii_chars_per_line()

    for i, case in enumerate(cases):
        print(i)
        formatted_text = page.fit_to_line(case[TXT], case[PREFIX], crop_middle=False)
        assert len(formatted_text) <= max_chars_in_line
        assert formatted_text == case[device_type]

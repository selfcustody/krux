from ..shared_mocks import mock_context
from . import create_ctx
from .home_pages.test_home import tdata
from unittest.mock import patch

SINGLE_SIG_12W_BINARY_QR = bytearray(
    b"\x7fT\xc8?\xa8P\nvA$\xdd\xae\xdb\xab\xdb%\x84t\x83\xb6\xa3\xe0_U\xf5\x07p\x0e\x00\xdf\xbb\xb7*\xb4\x0ei.Q\x96\xa4\x07H\xcc\xa8\xe4z\xeb.\xb2\x94\xa2s%\xe1\xca\x85\xe6\xc8V\xa6\xb7\xaeGKi\x16A\xd2\xbcX(\x18Pwz\xff\x00\xfa0\xea\xdf%V\n\xb2\xa2H]\xa1\xf7\xaf+\x0bUv\xc5\x16\xbd\xa0'\xfe\xf4\x17zr\x00"
)
TEST_DATA = "test code"
TEST_DATA_QR_SIZE = 21
TEST_DATA_QR_SIZE_FRAMED = 23
TEST_TITLE = "Test QR Code"
TEST_CODE_BINARY_QR = bytearray(
    b'\x7f\xdd?\x88\tv-\xdd\xae\xa9\xdb\x95t\x83\xbc\xe0_\xf5\x07\xc0\x00O?\xd7T\xf7R1c\x9cFUF\xb5\x00\xd2\xd6\x1f\xe6\t"x]T\xa4kIuM\x91\xa0\x11\xf9\x17R\x00'
)
FRAMED_TEST_CODE_BINARY_QR = bytearray(
    b"\x00\x00\x00\x7f\xdd\x9f &H\xd7\xd2\xa5k\xea\xd2\x95t\t\xf2\x82\xfcU\x7f\x000\x00O?\x17S\xdd\x0b\x153\x06\xa7QQF\xb5\x00H[\xfca\x1e\x82\x08\x1e]T\x84\xae%E\xd7\x14!hD\xf2\x17R\x00\x00\x00\x00"
)
PBM_TEST_CODE_BINARY_QR = bytearray(
    b"P4\n23 23\n\x00\x00\x00\x7f]\xfcA\x19\x04]it]et]ItA=\x04\x7fU\xfc\x00\x0c\x00y~t2\xae\xf4\x15\x19\x8c\x0eX\xa8S\x15h\x00Kh\x7f\x0c\xf0A\x10x]\x15\x10]i(]e\x10Ab$\x7fBP\x00\x00\x00"
)


def test_load_qr_view(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT

    BTN_SEQUENCE = [
        SWIPE_LEFT,  # lines mode
        BUTTON_ENTER,  # move to line 1
        SWIPE_LEFT,  # zoomed regions mode
        SWIPE_LEFT,  # regions mode
        SWIPE_LEFT,  # grided mode
        SWIPE_LEFT,  # back to standard mode
        SWIPE_LEFT,  # lines mode again
        SWIPE_RIGHT,  # back to standard mode
        BUTTON_ENTER,  # leave
        BUTTON_PAGE_PREV,  # move to "Back to Menu"
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    data = TEST_DATA
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    seed_qr_view.display_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 8
    assert ctx.display.draw_qr_code.call_args[0][1] == TEST_CODE_BINARY_QR


def test_load_seed_qr(amigo, mocker, tdata):
    from krux.pages.qr_view import SeedQRView
    from krux.themes import WHITE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT
    from krux.wallet import Wallet

    BTN_SEQUENCE = [
        SWIPE_LEFT,  # lines mode
        BUTTON_ENTER,  # move to line 1
        SWIPE_LEFT,  # zoomed regions mode
        SWIPE_LEFT,  # regions mode
        SWIPE_LEFT,  # grided mode
        SWIPE_LEFT,  # back to standard mode
        SWIPE_LEFT,  # lines mode again
        SWIPE_RIGHT,  # back to standard mode
        BUTTON_ENTER,  # Enter QR menu
        BUTTON_PAGE_PREV,  # move to "Back to Menu"
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY), None)
    seed_qr_view = SeedQRView(ctx, binary=False)
    seed_qr_view.display_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 8
    ctx.display.draw_qr_code.assert_called_with(
        0,
        # Standard SeedQR
        SINGLE_SIG_12W_BINARY_QR,
    )


def test_loop_through_regions(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT
    from ..test_encryption import CBC_ENCRYPTED_QR

    BTN_SEQUENCE = (
        [
            SWIPE_LEFT,  # lines mode
            BUTTON_ENTER,  # move to line 1
            SWIPE_LEFT,  # zoomed regions mode
            SWIPE_LEFT,  # regions mode
        ]
        + [BUTTON_ENTER] * 49  # Loop through regions and return to A1
        + [
            SWIPE_LEFT,  # grided mode
            SWIPE_LEFT,  # back to standard mode
            SWIPE_LEFT,  # lines mode again
            SWIPE_RIGHT,  # back to standard mode
            BUTTON_ENTER,  # leave
            BUTTON_PAGE_PREV,  # move to Back to Menu
            BUTTON_ENTER,  # confirm
        ]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    data = CBC_ENCRYPTED_QR  # Will produce an QR code with 48 regions, max=G7
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    seed_qr_view.display_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 57


def test_loop_through_brightness(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.themes import WHITE, DARKGREY
    from krux.input import BUTTON_TOUCH
    from krux.wallet import Wallet

    TOUCH_SEQ = [
        # Open touch menu
        1,  # Toggle brightness to bright
        # Open touch menu
        1,  # Toggle brightness to dark
        # Open touch menu
        1,  # Toggle brightness to default
        # Open touch menu
        4,  # Exit
    ]

    BTN_SEQUENCE = [BUTTON_TOUCH] * 8

    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQ)
    data = TEST_DATA
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    seed_qr_view.display_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 4
    assert ctx.display.draw_qr_code.call_args_list == [
        mocker.call(0, TEST_CODE_BINARY_QR),  # Default
        mocker.call(0, TEST_CODE_BINARY_QR, light_color=WHITE),  # Brighter
        mocker.call(0, TEST_CODE_BINARY_QR, light_color=DARKGREY),  # Darker
        mocker.call(0, TEST_CODE_BINARY_QR),  # Default
    ]


def test_add_frame(amigo, mocker):
    from krux.pages.qr_view import SeedQRView

    ctx = mock_context(mocker)
    framed_code, new_size = SeedQRView(ctx, data=TEST_DATA, title=TEST_TITLE).add_frame(
        TEST_CODE_BINARY_QR, TEST_DATA_QR_SIZE
    )

    assert new_size == TEST_DATA_QR_SIZE_FRAMED
    assert framed_code == FRAMED_TEST_CODE_BINARY_QR


def test_save_pbm_image(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.sd_card import PBM_IMAGE_EXTENSION
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # move to "Back to Menu"
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)

    mocker.patch("os.listdir", new=mocker.MagicMock(return_value=["file1"]))
    with patch("krux.sd_card.SDHandler.write_binary") as mock_write_binary:
        qr_viewer = SeedQRView(ctx, data=TEST_DATA, title="Test QR Code")
        qr_viewer.save_pbm_image(TEST_TITLE)

        mock_write_binary.assert_called_once_with(
            TEST_TITLE + PBM_IMAGE_EXTENSION, PBM_TEST_CODE_BINARY_QR
        )


def test_save_bmp_image(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.sd_card import BMP_IMAGE_EXTENSION
    import sys
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # move to "Back to Menu"
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)

    qr_viewer = SeedQRView(ctx, data=TEST_DATA, title="Test QR Code")
    qr_viewer.save_bmp_image(TEST_TITLE, TEST_DATA_QR_SIZE_FRAMED * 2)
    sys.modules["image"].Image.return_value.save.assert_called_once_with(
        "/sd/" + TEST_TITLE + BMP_IMAGE_EXTENSION
    )


def test_save_qr_image_menu_pbm(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Enter QR menu
        BUTTON_PAGE,
        BUTTON_PAGE,  # Move to "Save QR image to SD card"
        BUTTON_ENTER,  # Save QR image to SD card
        BUTTON_ENTER,  # Confirm first resolution - PBM format
        BUTTON_PAGE,
        BUTTON_PAGE,  # Move to "Back to Menu"
        BUTTON_ENTER,  # Confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    data = TEST_DATA
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    mocker.patch.object(seed_qr_view, "has_sd_card", new=lambda: True)

    mock_save_pbm_image = mocker.patch.object(seed_qr_view, "save_pbm_image")
    seed_qr_view.display_qr(allow_export=True)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 1
    mock_save_pbm_image.assert_called_once_with(
        TEST_TITLE.replace(" ", "_")[:10]
    )  # 10 is the max length for a suggested filename


def save_qr_image_menu_pbm(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # enter QR menu
        BUTTON_PAGE,
        BUTTON_PAGE,  # Move to "Save QR image to SD card"
        BUTTON_ENTER,  # Save QR image to SD card
        BUTTON_PAGE_PREV,  # On filename prompt, move to "Go"
        BUTTON_ENTER,  # Confirm
        BUTTON_PAGE,  # Go to first resolution - BMP format
        BUTTON_ENTER,  # Confirm first resolution - BMP format
        BUTTON_ENTER,  # Enter QR menu again
        BUTTON_PAGE_PREV,  # Move to "Back to Menu"
        BUTTON_ENTER,  # Confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    data = TEST_DATA
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    mocker.patch.object(seed_qr_view, "has_sd_card", new=lambda: True)

    mock_save_bmp_image = mocker.patch.object(seed_qr_view, "save_bmp_image")
    seed_qr_view.display_qr(allow_export=True)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 2  # 1 for before, 1 for after saving
    mock_save_bmp_image.assert_called_once_with(
        TEST_TITLE.replace(" ", "_")[:10]
    )  # 10 is the max length for a suggested filename

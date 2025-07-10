from .. import create_ctx
from .test_home import tdata
import pytest


PBM_XPUB_SINGLESIG_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7fHs\xa7\x1f\xc0Ak^&\xd0@]M\xee\xda\x17@]S\xb2\x13\x17@]\x18P7\x97@AkOa\x90@\x7fUUU_\xc0\x00!n\xca\xc0\x00g\x1e\xe3\xe0\x8b\xc0l\x02\xeb$u\x00Y8\xd5\xbev@|\x89b\x0f\xc6\x00a\xf4\r\xc2*\x80 \xc2h7~\xc0O\xd2\xa7\xcb,\xc0\x10U\xff\xc7~@\x19\x18o\x06\xc2\x800\xa9\x91\xa6u\xc0k\xfe\xa7\xbd\x19\xc0 @\xa2\xda0\x00\x0f\xa0\xb9\x06D\x00\x06\xd6\xc8\xc7\xbe\xc0\x13\\\xa3\x8a\x1b\xc0\x16\xd9\xf2\x02>\x00!\x82\x01\xa2c@l;\xd9\xb6\x1e\x80e\x18\x82\x8e0@f\xc4\xa7\xc3\x12@!\\JB\xae\x80|q\xd1\xbdL\x80\x05B\xf6\xfe-@\x18d\xb3Zz\x00\x7fm&\xe6\xfc\x00\x00pI\x9aE\x00\x7f\x1c\xe2\xcc\xd5@Ax\xf6\x86F@]f+P\xfe\x80]'@\x8c\n\x00]\x1f\xa7\xdb\xe9\x80Ay\xae\x9bV\xc0\x7fvo\x02d\x80\x00\x00\x00\x00\x00\x00"
)
PBM_ZPUB_SINGLESIG_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7fY\xe2)\x1f\xc0AE\x1cS\xd0@]h\xbe\x8a\x17@]I\xf5\x1f\x17@]:\xeb\xbe\x97@AW\x19%\x90@\x7fUUU_\xc0\x00\x197\xce\xc0\x00g\x00b\x84\x8b\xc0\n\xf4\xab\xbcu\xc0w\xf8\xa7\xebv@D\x9dvG\xd6\x80\tuEV*@\\b\x90\x87E\xc0U\x91\xb2\xef-\xc0(\xc4{\x0f>@-}mf\xc3\x80lh\xc1\xb8u\x00/\xe8\x85\x8b9@(|s\x16\x00@\x19r\xefd,@\x12D\xd8\x06\x8f\xc0)\xdc\xc0\xacS\xc0@)\xf2\x86\xb2\x00+\xf1\xb5\x96\xe0@\x06\x18\xc2\x8e\x1e\x80c\x08\xd0\xce @R\x99\xa6\x832\x80\x13,}\x83\xa2@v\x03\xe1\xb4M\x80\x15\xb1\xe3\xbel@\x00%*B\xba\x00a\x18/\xc6\xff\x00\x00Nr\x98E\xc0\x7f\x0e\xe5\xfe\xd5@AU\xbb\x07F@]T\x0eB\xfe\x80]\x16\xe95\n\x00]-\xa3\xbb\xeb\x80AdvO\xe6\xc0\x7fp{\xea\xc7\x80\x00\x00\x00\x00\x00\x00"
)
PBM_XPUB_MULTISIG_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7f@\xcf\x0f\xdf\xc0A22\xd2P@]^\xc0\xe8\x97@]w\xed\x1cW@]H\xeaT\x17@A%-4\xd0@\x7fUUU_\xc0\x00\x15\xb9\x86@\x00yA\xdb\xf2g@\x16\x0cM\x01\x96@A\x01\x02\xf3\x17\x80Z\x0f\xc1=\\\x00yE%8\xc9\x00@\xc8}\xed\xa0\xc0mVjG\xba@\x0c5R\\\xe2\x00##C\xe0N\x80\x18\x97\x1c\x8b \xc0)r\xb5\r%\x00\x1aH5\x16q\x00MoTR}\x00$\x88v\xe0\x8d@1\x1a!\xc4\x11\x00 \xc6\x89\xf0V\x80\x03\x17\xe4^\x03\xc0N\x84m^\x90\xc0k\xf6\x0bf\x8a\xc0~\x99\x87X.\x80#\xcaSg@\x80\x1c\xaf'\xce\xeb\xc0U%\xf6mp\x00\x16Ey\xce\x8b@-Y\xf2q\xff\xc0\x00A\\\x14\xc6@\x7f\x1cq\xd0\xd4\x00A\x0b\xd0\xf5\xc4@]\x16\xa1r}\xc0]tx\xe4\x87\x00]B\x18!B\x00Aa\x8e\\\x88\x80\x7f~r\x8d\xfa\x80\x00\x00\x00\x00\x00\x00"
)
PBM_ZPUB_MULTISIG_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7fKI\xb1\xdf\xc0A+0\xf6P@]g\x888\x97@]o\xa5\xfaW@]D`]\x17@A\x16;t\x90@\x7fUUU_\xc0\x00$\xfdV\x80\x00yItR\xe7@|\xe2\xea\xf1\x96@o\xcfA\xb3'\x004FU|L\x00w/\xc5\xeb\xc1\x00j\xdbh\xc5\xf0\xc0Q\xf2xw\xb2@6)K\x04\"\x00]\xda\x16\x88\xcc\x80J|4Y \x80y\xc3\xa1\x0c%\x80\x04\xfc\xec\xc7a\xc0?\xef\x1eUu\x00X\x98\x0f\x9d\xde@+\xcfV\x90Z\x00\n\x16\x14$\xd0\x80\x7f?\xe9\xae\x02\xc0.\xb5p\xcc\x90@\x15\xa5m$\x9a\xc0&\xed\x12I>@} \xf7\xc5$\x00*\xee\x07z\xd8\xc0_\x90\x96\x19w\x00\x06Td\x1a\x8b@3\xe1T\xc9\xfd\xc0\x00SX\x96\xc6\x80\x7f\x0fv\x90\xd4\x80A\x06\x14l\xc4\x00]-u\xd0}\x80]~P\xd5\x85\x00]F|QB\x00AT\xd7\x14Z\x80\x7f@\x17\x07\xeb\x80\x00\x00\x00\x00\x00\x00"
)
PBM_XPUB_NESTEDSW_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7flI\xad\xdf\xc0A(&\x86\x10@]s\x1d\xa4\x97@]E\xc4\x9aW@]jQ\xe4\x17@A#J\x04\xd0@\x7fUUU_\xc0\x00(\xad\x9e\x00\x00ya\x1e\xb1\xe7@4\x11_\x82\x96@\x1b\x81G\x84'\x80~N\xcc\xb4L@\x17\xadC\xbe\xcd\x00\x14\x1c\xb0\xdc \xc0)X(Q\xfc@jhV\x9cf\x00\x13\x97\x03\xa1O\x80B_\x10\xe9 @\x15\xc6\xb1/%\x00t\x01`Zq\x80\x15\xb5>Q5\x00\x1a\x14\xfa\xef\xcd@\x19\x7f!\xe6S\x00*#\xdc\xa0\xb4\x80SSe\x92\x82\xc0Z7O\x05\x90\xc0%\xc0-4\x9a\xc0t\x0c\x83\xc5\x0e\x00\x0b\xa8\x8f!$\x80\x1e\xa4\xb5aK\xc0K}\xb4m6\x00\x10\xe4\xb8N\x8d\xc0%\t\xdcs\xfd@\x00Zz\"\xc6\x80\x7f\tf\xa2\xd4\x80A&\x85\xfd\xc4\xc0]\x05\xec\x9c}\xc0]xa\xdb\x84\x00]Bl\x15@\x00AI\x13\x08*\x80\x7f|\x1f\x89\xea\x80\x00\x00\x00\x00\x00\x00"
)
PBM_YPUB_NESTEDSW_QRCODE_43 = bytearray(
    b"P4\n43 43\n\x00\x00\x00\x00\x00\x00\x7f6\xd7\xc7\xdf\xc0Al\xd1\x1fP@]\t\x82\xc5\x17@]~\xf7|\x17@]+-\x16W@AN\xb6mP@\x7fUUU_\xc0\x00<\x1b\x85@\x00}\xce\xf48j\x80,\x05\x05\xdc\x96\xc0g3\x96}z\x00\x1c\xc9B\xd9\xfa@a\xbf\xc7\\\xed\xc0,\x91\xfe\x0e_@cm\xd28M\x80T8\x83\x98n\x00#\xbf\x01V!\x00.A\xf6\x9c\x96\x80A\x81\x85z\x05\x00:]\x93\xc8<\xc0[sOv\x87\x80*\xf5%\x97O@a0\xf4Y>\x80\x1au_\x84\xc2@A\x91G^\x01\xc0t\x88z\xae\xfd@[a\xb5i<\x80:\x15\x97\x85\x0e\x80G\xfd-\x1eM\xc0f\xd0W\xa1\xff\x00Q\xac\xb7\x195\x00V\t\x8e\x15b@_y0\x9e\x7f\x80\x00YG\xf0\xc6@\x7fU\xb6[\xd5\x80A\x11\x02\x10F\x00]^%n}@]e\xeb\x95\xe8\x80]E\xd4H\xf4\xc0Aa\x12\x9c\xa8\x80\x7fe\x87*\xb7\x00\x00\x00\x00\x00\x00\x00"
)


@pytest.fixture
def mock_save_file(mocker):
    mocker.patch(
        "krux.pages.qr_view.SeedQRView.has_sd_card",
        return_value=True,
    )
    mocker.patch(
        "krux.pages.home_pages.pub_key_view.PubkeyView.has_sd_card", return_value=True
    )
    return mocker.patch("krux.pages.file_operations.SaveFile.save_file")


@pytest.fixture
def mock_seed_qr_view(mocker):
    return mocker.patch("krux.pages.qr_view.SeedQRView")


def test_public_key_show_text(mocker, m5stickv, tdata):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    btn_sequence = [
        BUTTON_ENTER,  # Enter XPUB - text
        BUTTON_PAGE,  # Move to Back
        BUTTON_ENTER,  # Press Back
        *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
        BUTTON_ENTER,  # Enter ZPUB/YPUB - text
        BUTTON_PAGE,  # Move to Back
        BUTTON_ENTER,  # Press Back
        BUTTON_PAGE_PREV,  # Move to Back
        BUTTON_ENTER,  # Leave the page
    ]

    cases = [
        # Case parameters: [Wallet, Button Sequence]
        # 0 - Singlesig - Show all text
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            btn_sequence,
        ),
        # 1 - Multisig - Show all text
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            btn_sequence,
        ),
        # 2 - Singlesig Nested Segwit - Show all text
        (
            Wallet(tdata.NESTEDSW1_KEY),
            btn_sequence,
        ),
    ]

    for wallet, sequence in cases:
        ctx = create_ctx(mocker, sequence, wallet, None)
        pub_key_viewer = PubkeyView(ctx)

        mocker.patch.object(ctx.display, "FONT_HEIGHT", 14)
        mocker.spy(ctx.display, "clear")
        mocker.spy(ctx.display, "draw_hcentered_text")

        pub_key_viewer.public_key()

        # Build expected `clear` and `draw_hcentered_text` calls
        clear_calls = []
        draw_text_calls = []

        clear_calls.append(mocker.call())
        draw_text_calls.append(
            mocker.call(
                "\n\n"
                + ctx.wallet.key.derivation_str(pretty=True)
                + "\n\n"
                + ctx.wallet.key.account_pubkey_str(None),
                offset_y=ctx.display.FONT_HEIGHT,
                info_box=True,
            ),
        )

        # Be sure that the display was cleared and show correct master pubkeys
        ctx.display.clear.assert_has_calls(clear_calls, any_order=True)
        ctx.display.draw_hcentered_text.assert_has_calls(
            draw_text_calls, any_order=True
        )


def test_public_key_show_qrcode(
    mocker,
    m5stickv,
    tdata,
    mock_seed_qr_view,
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.key import TYPE_MULTISIG

    btn_sequence = [
        BUTTON_PAGE,  # Move to XPUB - QR Code
        BUTTON_ENTER,  # Enter XPUB - QR Code
        BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
        BUTTON_PAGE_PREV,  # Move to Back to Menu
        BUTTON_ENTER,  # Press Back to Menu
        *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR Code
        BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
        BUTTON_ENTER,  # Exit the qrcode and enter in QR Menu
        BUTTON_PAGE_PREV,  # Move to Back to Menu
        BUTTON_ENTER,  # Press Back to Menu
        BUTTON_PAGE_PREV,  # Move Back
        BUTTON_ENTER,  # Press Back to leave
    ]

    cases = [
        # Case parameters: [Wallet, Button Sequence, Show XPUB, Show ZPUB, Show YPUB]
        # 0 - Singlesig - Show all QR codes
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 1 - Multisig - Show all QR codes
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 2 - Singlesig Nested Segwit - Show all QR codes
        (
            Wallet(tdata.NESTEDSW1_KEY),
            btn_sequence,
            False,
            False,
            True,
        ),
    ]

    for case in cases:

        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)

        pub_key_viewer.public_key()

        # Build expected QR view calls
        qr_view_calls = []

        if case[2]:  # Show XPUB
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=ctx.wallet.key.key_expression(None),
                    title="XPUB",
                ),
            )

        if case[3]:  # Show ZPUB
            version = "Zpub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "zpub"
            zpub = ctx.wallet.key.key_expression(ctx.wallet.key.network[version])
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=zpub,
                    title="ZPUB",
                ),
            )

        if case[4]:  # Show YPUB
            version = "Ypub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "ypub"
            ypub = ctx.wallet.key.key_expression(ctx.wallet.key.network[version])
            qr_view_calls.append(
                mocker.call(
                    ctx,
                    data=ypub,
                    title="YPUB",
                ),
            )

        mock_seed_qr_view.assert_has_calls(qr_view_calls, any_order=True)
        assert ctx.input.wait_for_button.call_count == len(btn_sequence)


def test_public_key_save_text(
    mocker,
    m5stickv,
    tdata,
    mock_save_file,
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.key import TYPE_MULTISIG

    btn_sequence = [
        BUTTON_ENTER,  # Enter XPUB - Text
        BUTTON_ENTER,  # Enter Save to SD Card
        BUTTON_ENTER,  # Accept Save to SD Card
        BUTTON_PAGE_PREV,  # Move to Go
        BUTTON_ENTER,  # Press Go
        *([BUTTON_PAGE] * 2),  # Move to ZPUB/YPUB - text
        BUTTON_ENTER,  # Enter ZPUB/YPUB - text
        BUTTON_ENTER,  # Enter Save to SD card
        BUTTON_ENTER,  # Accept Save to SD Card
        BUTTON_PAGE_PREV,  # Move to Go
        BUTTON_ENTER,  # Press Go
        BUTTON_PAGE_PREV,  # Move Back
        BUTTON_ENTER,  # Press Back to leave
    ]

    cases = [
        # Case parameters: [Wallet, Button Sequence, Show XPUB, Show ZPUB, Show YPUB]
        # 0 - Singlesig - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 1 - Multisig - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 2 - Nested Segwit - Save XPUB and YPUB to SD card
        (
            Wallet(tdata.NESTEDSW1_KEY),
            btn_sequence,
            True,
            False,
            True,
        ),
    ]

    for case in cases:
        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)

        mocker.patch.object(ctx.display, "FONT_HEIGHT", 14)
        mocker.spy(ctx.display, "clear")
        mocker.spy(ctx.display, "draw_hcentered_text")

        pub_key_viewer.public_key()

        # Build expected QR view calls
        clear_calls = []
        draw_text_calls = []
        sd_card_save_calls = []

        clear_calls.append(mocker.call())
        if case[2]:  # Show XPUB
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(None),
                    "XPUB",
                    "XPUB",
                    "XPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        if case[3]:  # Show ZPUB
            version = "Zpub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "zpub"
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(ctx.wallet.key.network[version]),
                    "ZPUB",
                    "ZPUB",
                    "ZPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        if case[4]:  # Show YPUB
            version = "Ypub" if ctx.wallet.key.policy_type == TYPE_MULTISIG else "ypub"
            sd_card_save_calls.append(
                mocker.call(
                    ctx.wallet.key.key_expression(ctx.wallet.key.network[version]),
                    "YPUB",
                    "YPUB",
                    "YPUB:",
                    ".pub",
                    save_as_binary=False,
                )
            )

        draw_text_calls.append(
            mocker.call(
                "\n\n"
                + ctx.wallet.key.derivation_str(pretty=True)
                + "\n\n"
                + ctx.wallet.key.account_pubkey_str(None),
                offset_y=ctx.display.FONT_HEIGHT,
                info_box=True,
            ),
        )

        mock_save_file.assert_has_calls(sd_card_save_calls, any_order=True)
        ctx.display.clear.assert_has_calls(clear_calls, any_order=True)
        ctx.display.draw_hcentered_text.assert_has_calls(
            draw_text_calls, any_order=True
        )
        assert ctx.input.wait_for_button.call_count == len(case[1])


def test_public_key_save_qr_codes(
    mocker,
    m5stickv,
    tdata,
    mock_save_file,
):
    from krux.pages.home_pages.pub_key_view import PubkeyView
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.key import TYPE_MULTISIG, P2SH_P2WPKH
    from krux.sd_card import PBM_IMAGE_EXTENSION

    btn_sequence = [
        BUTTON_PAGE,  # Move to XPUB - QR code
        BUTTON_ENTER,  # Enter XPUB - QR code
        BUTTON_ENTER,  # Enter QR Menu
        *([BUTTON_PAGE] * 2),  # Move to Save QR Image
        BUTTON_ENTER,  # Press Save QR Image
        BUTTON_ENTER,  # Press 43x43 PBM
        *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
        BUTTON_ENTER,  # Press Back to Menu
        *([BUTTON_PAGE] * 3),  # Move to ZPUB/YPUB - QR code
        BUTTON_ENTER,  # Enter ZPUB/YPUB - QR code
        BUTTON_ENTER,  # Enter QR Menu
        *([BUTTON_PAGE] * 2),  # Move to Save QR Image
        BUTTON_ENTER,  # Press Save QR Image
        BUTTON_ENTER,  # Press 43x43 PBM
        *([BUTTON_PAGE_PREV] * 3),  # Move to Back to Menu
        BUTTON_ENTER,  # Press Back to Menu
        BUTTON_PAGE_PREV,  # Move Back
        BUTTON_ENTER,  # Press Back to leave
    ]

    cases = [
        # Case parameters: [Wallet, Button Sequence, Show XPUB, Show ZPUB, Show YPUB]
        # 0 - Singlesig - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.SINGLESIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 1 - Multisig - Save XPUB and ZPUB to SD card
        (
            Wallet(tdata.MULTISIG_12_WORD_KEY),
            btn_sequence,
            True,
            True,
            False,
        ),
        # 2 - Nested Segwit - Save XPUB and YPUB to SD card
        (
            Wallet(tdata.NESTEDSW1_KEY),
            btn_sequence,
            True,
            False,
            True,
        ),
    ]

    for case in cases:
        ctx = create_ctx(mocker, case[1], case[0], None)
        pub_key_viewer = PubkeyView(ctx)
        pub_key_viewer.public_key()

        # Build expected QR save calls
        sd_card_save_calls = []

        # Show XPUB and ZPUB for singlesig
        if case[2] and not case[4]:
            qrcode = (
                PBM_XPUB_SINGLESIG_QRCODE_43
                if not ctx.wallet.key.policy_type == TYPE_MULTISIG
                else PBM_XPUB_MULTISIG_QRCODE_43
            )
            sd_card_save_calls.append(
                mocker.call(
                    qrcode,
                    "XPUB",
                    file_extension=PBM_IMAGE_EXTENSION,
                    save_as_binary=True,
                    prompt=False,
                )
            )

        # Show XPUB and ZPUB for multisig
        if case[3]:
            qrcode = (
                PBM_ZPUB_SINGLESIG_QRCODE_43
                if not ctx.wallet.key.policy_type == TYPE_MULTISIG
                else PBM_ZPUB_MULTISIG_QRCODE_43
            )
            sd_card_save_calls.append(
                mocker.call(
                    qrcode,
                    "ZPUB",
                    file_extension=PBM_IMAGE_EXTENSION,
                    save_as_binary=True,
                    prompt=False,
                )
            )

        # Show XPUB and YPUB for singlesig nested segwit
        if case[2] and case[4]:
            qrcode = (
                PBM_XPUB_NESTEDSW_QRCODE_43
                if not ctx.wallet.key.script_type == P2SH_P2WPKH
                else PBM_YPUB_NESTEDSW_QRCODE_43
            )
            prefix = "XPUB" if not ctx.wallet.key.script_type == P2SH_P2WPKH else "YPUB"
            sd_card_save_calls.append(
                mocker.call(
                    qrcode,
                    prefix,
                    file_extension=PBM_IMAGE_EXTENSION,
                    save_as_binary=True,
                    prompt=False,
                )
            )

        mock_save_file.assert_has_calls(sd_card_save_calls, any_order=True)
        assert ctx.input.wait_for_button.call_count == len(case[1])

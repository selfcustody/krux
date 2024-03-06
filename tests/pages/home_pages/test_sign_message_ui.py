from ...shared_mocks import MockPrinter, get_mock_open
from .. import create_ctx
from .test_home import tdata


def test_sign_message(mocker, m5stickv, tdata):
    import binascii
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE

    cases = [
        # 0 Hex-encoded hash, Sign, No print prompt
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",  # 0 data for capture_qr_code
            FORMAT_NONE,  # 1 qr_format for capture_qr_code
            None,  # 2 printer
            # 3 btn_seq
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to Sign SHA
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_ENTER,  # Hex Public Key Text
                BUTTON_ENTER,  # PK QR code
            ],
            "MEQCID/PulsmI+E1HhJ55HdJJnKoMbUHw3c1WZnSrHqW5jlKAiB+vPbnRtmw6R9ZP8jUB8o02n+6QsX9uKy3hDiv9R2SuA==",  # 4 base64 for display_qr_codes / print_qr_prompt
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",  # 5 pubkey for display_qr_codes / print_qr_prompt
            None,  # 6 SD file
        ),
        # 1 Hash, Sign, No print prompt
        (
            binascii.unhexlify(
                "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7"
            ),
            FORMAT_NONE,
            None,
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to Sign SHA
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_ENTER,  # Hex Public Key Text
                BUTTON_ENTER,  # PK QR code
            ],
            "MEQCID/PulsmI+E1HhJ55HdJJnKoMbUHw3c1WZnSrHqW5jlKAiB+vPbnRtmw6R9ZP8jUB8o02n+6QsX9uKy3hDiv9R2SuA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
            None,
        ),
        # 2 Message, Sign, No print prompt
        (
            "hello world",
            FORMAT_NONE,
            None,
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to Sign SHA
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_ENTER,  # Hex Public Key Text
                BUTTON_ENTER,  # PK QR code
            ],
            "MEQCIHKmpv1+vgPpFTN0JXjyrMK2TtLHVeJJ2TydPYmEt0RnAiBJVt/Y61ef5VlWjG08zf92AeF++BWdYm1Yd9IEy2cSqA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
            None,
        ),
        # 3 64-byte message, Sign, No print prompt
        (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
            FORMAT_NONE,
            None,
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to Sign SHA
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_ENTER,  # Hex Public Key Text
                BUTTON_ENTER,  # PK QR code
            ],
            "MEQCIEHpCMfQ+5mBAOH//OCxF6iojpVtIS6G7X+3r3qB/0CaAiAkbjW2SGrPLvju+O05yH2x/4EKL2qlkdWnquiVkUY3jQ==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
            None,
        ),
        # 4 Hex-encoded hash, Sign, Print
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",
            FORMAT_NONE,
            MockPrinter(),
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to Sign SHA
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_ENTER,  # Print - Yes
                BUTTON_ENTER,  # Hex Public Key Text
                BUTTON_ENTER,  # PK QR code
                BUTTON_ENTER,  # Print - Yes
            ],
            "MEQCID/PulsmI+E1HhJ55HdJJnKoMbUHw3c1WZnSrHqW5jlKAiB+vPbnRtmw6R9ZP8jUB8o02n+6QsX9uKy3hDiv9R2SuA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
            None,
        ),
        # 5 Hex-encoded hash, Sign, Decline to print
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",
            FORMAT_NONE,
            MockPrinter(),
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to Sign SHA
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_PAGE,  # Print - No
                BUTTON_ENTER,  # Hex Public Key Text
                BUTTON_ENTER,  # PK QR code
                BUTTON_PAGE,  # Print - No
            ],
            "MEQCID/PulsmI+E1HhJ55HdJJnKoMbUHw3c1WZnSrHqW5jlKAiB+vPbnRtmw6R9ZP8jUB8o02n+6QsX9uKy3hDiv9R2SuA==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
            None,
        ),
        # 6 Hex-encoded hash, Decline to sign
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",
            FORMAT_NONE,
            None,
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_PAGE,  # Decline to sign
            ],
            None,
            None,
            None,
        ),
        # 7 Failed to capture message QR
        (None, FORMAT_NONE, None, [BUTTON_ENTER], None, None, None),
        # 8 Message, Sign, Save to SD, No print prompt
        (
            "hello world",  # 0 data for capture_qr_code
            FORMAT_NONE,  # 1 qr_format for capture_qr_code
            None,  # 2 printer
            # 3 btn_seq
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to Sign SHA
                BUTTON_ENTER,  # Check signature
                BUTTON_PAGE,  # Move to "Sign to SD card"
                BUTTON_ENTER,  # Sign to SD card
                BUTTON_ENTER,  # Confirm to save sig to SD card
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Confirm sig file name
                BUTTON_ENTER,  # Confirm to save PK to SD card
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Confirm PK file name
            ],
            "MEQCIHKmpv1+vgPpFTN0JXjyrMK2TtLHVeJJ2TydPYmEt0RnAiBJVt/Y61ef5VlWjG08zf92AeF++BWdYm1Yd9IEy2cSqA==",  # 4 base64 for display_qr_codes / print_qr_prompt
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",  # 5 pubkey for display_qr_codes / print_qr_prompt
            # 6 SD file
            binascii.b2a_base64(
                "MEQCIHKmpv1+vgPpFTN0JXjyrMK2TtLHVeJJ2TydPYmEt0RnAiBJVt/Y61ef5VlWjG08zf92AeF++BWdYm1Yd9IEy2cSqA==".encode(
                    "utf-8"
                ),
                newline=False,
            ),
        ),
    ]
    num = 0
    for case in cases:
        print("test_sign_message case: ", num)
        num += 1
        wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)

        ctx = create_ctx(mocker, case[3], wallet, case[2])
        home = SignMessage(ctx)
        mocker.patch.object(home, "capture_qr_code", new=lambda: (case[0], case[1]))
        mocker.patch.object(
            home,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(home.utils, "print_standard_qr")
        mocker.spy(home, "capture_qr_code")
        mocker.spy(home, "display_qr_codes")
        if case[6] is not None:
            mocker.patch("os.listdir", new=mocker.MagicMock(return_value=[]))
            mocker.patch(
                "builtins.open",
                new=get_mock_open(
                    {
                        "/sd/signed-message.sig": case[6],
                    }
                ),
            )
        else:
            mocker.patch("os.listdir", new=mocker.MagicMock(side_effect=OSError))
            mocker.patch("builtins.open", new=mocker.MagicMock(side_effect=OSError))

        home.sign_message()

        home.capture_qr_code.assert_called_once()
        signed_qr_message = (
            len(case[3]) > 1
            and case[3][0] == BUTTON_ENTER
            and case[3][1] == BUTTON_ENTER
        )
        if case[0] and signed_qr_message and case[6] is None:
            home.display_qr_codes.assert_has_calls(
                [
                    mocker.call(case[4], case[1], "Signed Message"),
                    mocker.call(case[5], case[1], "Hex Public Key"),
                ]
            )
            home.utils.print_standard_qr.assert_has_calls(
                [
                    mocker.call(case[4], case[1], "Signed Message"),
                    mocker.call(case[5], case[1], "Hex Public Key"),
                ]
            )
        else:
            home.display_qr_codes.assert_not_called()
            home.utils.print_standard_qr.assert_not_called()

        assert ctx.input.wait_for_button.call_count == len(case[3])


def test_sign_message_at_address(mocker, m5stickv, tdata):
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.themes import theme

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Confirm to sign message
        BUTTON_ENTER,  # Check signature
        BUTTON_ENTER,  # Sign to QR code
        BUTTON_ENTER,  # Check QR code
    ]
    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, BTN_SEQUENCE, wallet)
    mocker.patch.object(ctx.display, "width", new=lambda: 135)
    message_signer = SignMessage(ctx)
    mocker.spy(message_signer, "display_qr_codes")
    mocker.patch.object(
        message_signer,
        "capture_qr_code",
        new=lambda: ("signmessage m/84h/1h/0h/0/3 ascii:a test message", FORMAT_NONE),
    )
    message_signer.sign_message()

    ctx.display.draw_hcentered_text.assert_has_calls(
        [mocker.call("Message:", 10, theme.highlight_color)]
    )
    ctx.display.draw_hcentered_text.assert_has_calls(
        [mocker.call("a test message", mocker.ANY, max_lines=10)]
    )
    ctx.display.draw_hcentered_text.assert_has_calls(
        [mocker.call("Address:", mocker.ANY, theme.highlight_color)]
    )
    ctx.display.draw_hcentered_text.assert_has_calls(
        [mocker.call("3. bc1qgl..cn3", mocker.ANY)],
    )
    message_signer.display_qr_codes.assert_called_once_with(
        "HzRkfdy2sqvszgCn1jLkq3KfqP6Zd1wwG0v+95zfIz0WNizoXjjFBmB7ZxOHXSj4qAhwoNgUPJHDqzFaOq30URA=",
        0,
        "Signed Message",
    )

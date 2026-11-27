from tests.shared_mocks import MockPrinter, get_mock_open
from tests.pages import create_ctx, assert_not_flashed
from tests.pages.home_pages.test_home import tdata


def test_sign_message(mocker, m5stickv, tdata):
    import binascii
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture
    from unittest.mock import mock_open, patch

    cases = [
        # 0 Hex-encoded hash, Sign, No print prompt
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",  # 0 data for capture_qr_code
            FORMAT_NONE,  # 1 qr_format for capture_qr_code
            None,  # 2 printer
            # 3 btn_seq
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Raw hash warning - Proceed
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
                BUTTON_ENTER,  # Raw hash warning - Proceed
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
                BUTTON_ENTER,  # Raw hash warning - Proceed
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
                BUTTON_ENTER,  # Raw hash warning - Proceed
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
        # 6 Hex-encoded hash, Decline at raw hash warning
        (
            "1af9487b14714080ce5556b4455fd06c4e0a5f719d8c0ea2b5a884e5ebfc6de7",
            FORMAT_NONE,
            None,
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_PAGE,  # Decline raw hash warning
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
                BUTTON_ENTER,  # Confirm to Sign SHA256
                BUTTON_ENTER,  # Dismiss signature info
                BUTTON_PAGE,  # Move to "Sign to SD card"
                BUTTON_ENTER,  # Press "Sign to SD card"
                BUTTON_ENTER,  # Press letter 'a' on keypad
                BUTTON_ENTER,  # Press letter 'a' on keypad
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Press "Go" (saved signature to SD)
                BUTTON_ENTER,  # Confirm Hex Public Key "Save to SD card?"
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Press "Go" (saved pubkey to SD)
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
        mocker.patch.object(
            QRCodeCapture, "qr_capture_loop", new=lambda self: (case[0], case[1])
        )
        qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")
        mocker.patch.object(
            home,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.spy(home, "display_qr_codes")

        # SAVE to SD
        if case[6] is not None:
            mocker.patch("os.listdir", new=mocker.MagicMock(return_value=[]))
            mocker.patch(
                "krux.pages.file_operations.open", mock_open(read_data=case[6])
            )
            with patch(
                "builtins.open", new=get_mock_open({"/sd/signed-message.sig": case[6]})
            ) as mock_file:

                # function being tested
                home.sign_message()

                mock_file.assert_has_calls(
                    [
                        mocker.call("/sd/message-signedaa.sig", "wb"),
                        mocker.call("/sd/pubkey.pub", "w"),
                    ]
                )
        else:
            # function being tested
            home.sign_message()

        qr_capturer.assert_called_once()
        signed_qr_message = (
            len(case[3]) > 1
            and case[3][0] == BUTTON_ENTER
            and case[3][1] == BUTTON_ENTER
        )
        if case[0] is not None and signed_qr_message and case[6] is None:
            home.display_qr_codes.assert_has_calls(
                [
                    mocker.call(case[4], case[1], "Signed Message"),
                    mocker.call(case[5], case[1], "Hex Public Key:"),
                ]
            )
        else:
            home.display_qr_codes.assert_not_called()

        assert ctx.input.wait_for_button.call_count == len(case[3])


def test_sign_message_invalid_derivations(mocker, m5stickv, tdata):
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    # These edge cases will be treated as pure text and the
    # stuff `signmessage <derivation> ascii:<message>` will
    # not be parsed and be linked to the address on display
    # (they will be treated as a whole message)
    cases = [
        (
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "signmessage m84h ascii:hello",
            "m84h",
            "MEQCIA7DCCFox6tQqC3GE9a5IMvm8cVu1Zh6OWcUE1gls77gAiAzLncevU9FFJRvG83ahSJ8hISimgtSSdRHye2rmijwlg==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
        (
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "signmessage m/8xh/0/0 ascii:hello",
            "m/8xh/0/0",
            "MEQCIDL/XdIRF+v0wnN/JDOu2XYMTYqJaAyjuIDdSG4E/909AiASARSc1zfJsvUKC6MDQlM3E2lrkTx3iYfpJUWRZy/Vpg==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
        (  # 2 - QR invalid (empty segment)
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
                BUTTON_ENTER,
                BUTTON_ENTER,
            ],
            "signmessage m//0 ascii:hello",
            "m//0",
            "MEQCIDx4K8atJhGiaFdCCsgaUqFv22ncJ3AFHczFsNLZmbcGAiBuQdB5/pztOHjyQt0DKmuMKo799raQuRrXMVKK69ELjQ==",
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",
        ),
    ]

    n = 0
    for case in cases:
        print("Case: ", n)
        n = 0

        # A mainnet wallet
        wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
        ctx = create_ctx(mocker, case[0], wallet)
        mocker.patch.object(ctx.display, "width", new=lambda: 135)
        message_signer = SignMessage(ctx)
        mocker.spy(message_signer, "_is_valid_derivation_path")
        mocker.spy(message_signer, "_display_and_export_pubkey")
        mocker.spy(message_signer, "display_qr_codes")
        mocker.patch.object(
            QRCodeCapture,
            "qr_capture_loop",
            new=lambda self: (
                case[1],
                FORMAT_NONE,
            ),
        )

        qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")

        message_signer.sign_message()
        qr_capturer.assert_called_once()

        # ensure _is_valid_derivation_path was called with expected derivation
        message_signer._is_valid_derivation_path.assert_called_once_with(case[2])
        message_signer.display_qr_codes.assert_has_calls(
            [
                mocker.call(case[3], FORMAT_NONE, "Signed Message"),
                mocker.call(case[4], FORMAT_NONE, "Hex Public Key:"),
            ]
        )

        # Address message should not be called, because our derivation is invalid
        assert not any(
            len(call.args) > 0 and call.args[0] == "Address:"
            for call in ctx.display.draw_hcentered_text.call_args_list
        )

        assert ctx.input.wait_for_button.call_count == len(case[0])


def test_sign_message_at_address(mocker, m5stickv, tdata):
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
    from krux.qr import FORMAT_NONE
    from krux.themes import theme
    from krux.pages.qr_capture import QRCodeCapture

    cases = [
        # Button sequence
        # QR raw message
        # SD raw message
        # Sign to SD
        # Message content
        # Displayed address
        # Signature
        (  # 0 - Sign P2WPKH Mainnet
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
            ],
            "signmessage m/84'/0h/0H/0/3 ascii:a test message with a colon ':' character.",
            None,
            False,
            "a test message with a colon ':' character.",
            "3. bc1qgl5…3cn3",  # bc1qgl5vlg0zdl7yvprgxj9fevsc6q6x5dmcyk3cn3
            "IN/4LmcGRaI5sgvBP2mrTXQFvD6FecXd8La03SixPabsb/255ElRGTcXhicT3KFsNJbfQ9te909ZXeKMaqUcaPM=",
        ),
        (  # 1 - Sign P2WPKH Testnet
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
            ],
            "signmessage m/84'/1h/0H/0/3 ascii:A test message.",
            None,
            False,
            "A test message.",
            "3. tb1qynp…m5km",
            "ILc30ti8OPSpCtzfj7sNnftANBCuVpyRX7pnM3iAgOk9F9IUtnXNPus0+MF12y5HKYHAB6IVYr66sLmL3Vi3oEE=",
        ),
        (  # 2 - Sign P2TR Mainnet
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
            ],
            "signmessage m/86'/0h/0H/0/3 ascii:a test message with a colon ':' character.",
            None,
            False,
            "a test message with a colon ':' character.",
            "3. bc1py0v…xler",
            "H3Z5VioeLaC0rpdI2CflUu34IANgGxum0Rr9lmCziQRfUQv+vFND+nHvxHmJZA0uvLLI1/mTEEHD2bBfN6Y2d6w=",
        ),
        (  # 3 - Sign Legacy Mainnet
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
            ],
            "signmessage m/44'/0h/0H/0/3 ascii:a test message with a colon ':' character.",
            None,
            False,
            "a test message with a colon ':' character.",
            "3. 1MVGa13…yrsJ",
            "IEpq8rUwSmDxO3GgwaZ75tw3DArtHtLi08kgQuRNXdteMI5KNEAWbpzsY8gRzGkspZN4YFiRu4RNCM+IsKkWys8=",
        ),
        (  # 4 - Sign Nested Segwit Mainnet
            [
                BUTTON_ENTER,  # Load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Check signature
                BUTTON_ENTER,  # Sign to QR code
                BUTTON_ENTER,  # Check QR code
            ],
            "signmessage m/49'/0h/0H/0/3 ascii:a test message with a colon ':' character.",
            None,
            False,
            "a test message with a colon ':' character.",
            "3. 38CahkV…sEAN",
            "HyH8898c2S6eF8hTPGhRqLC6UQrJrhw/fdguBeFG0cCrOFkbG8TCVURXOgxXaEV93vrFlHyxNGEvL10IcsLtvvI=",
        ),
        (  # 5 - Sign P2WPKH Mainnet - Save to SD card
            [
                BUTTON_ENTER,  # Confirm load from camera
                BUTTON_ENTER,  # Confirm to sign message
                BUTTON_ENTER,  # Dismiss signature
                BUTTON_PAGE,  # Sign to SD card
                BUTTON_ENTER,  # Press sign to SD card
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Press "Go"
            ],
            "signmessage m/84'/0h/0H/0/3 ascii:A test message.",
            None,
            True,  # Sign to SD
            "A test message.",
            "3. bc1qgl5…3cn3",
            "IN/4LmcGRaI5sgvBP2mrTXQFvD6FecXd8La03SixPabsb/255ElRGTcXhicT3KFsNJbfQ9te909ZXeKMaqUcaPM=",
        ),
        (  # 6 - Sign P2WPKH Mainnet - Load from and save to SD card
            [
                BUTTON_PAGE,  # Load from SD card
                BUTTON_ENTER,  # Press load from SD card
                # file loaded by mock
                BUTTON_ENTER,  # Confirm message sign at addr
                BUTTON_ENTER,  # Dismiss signature
                BUTTON_PAGE,  # move to Sign to SD card
                BUTTON_ENTER,  # Press sign to SD card
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Press "Go"
            ],
            None,
            b"A test message.\nm/84'/0h/0H/0/3\nP2WPKH",
            True,  # Sign to SD
            "A test message.",
            "3. bc1qgl5…3cn3",
            "IN/4LmcGRaI5sgvBP2mrTXQFvD6FecXd8La03SixPabsb/255ElRGTcXhicT3KFsNJbfQ9te909ZXeKMaqUcaPM=",
        ),
        (  # 7 - Sign empty - Load from and save to SD card
            [
                BUTTON_PAGE,  # Load from SD card
                BUTTON_ENTER,  # Press load from SD card
                # file loaded by mock
                BUTTON_ENTER,  # confirm SHA256 Sign
                BUTTON_ENTER,  # Dismiss signature
                BUTTON_PAGE,  # move to Sign to SD card
                BUTTON_ENTER,  # Press sign to SD card
                BUTTON_PAGE_PREV,  # Move to "Go"
                BUTTON_ENTER,  # Press "Go"
                BUTTON_PAGE,  # No to save hex pub key
            ],
            None,
            b"",
            True,  # Sign to SD
            "A test message.",
            "3. bc1qgl…cn3",
            "IN/4LmcGRaI5sgvBP2mrTXQFvD6FecXd8La03SixPabsb/255ElRGTcXhicT3KFsNJbfQ9te909ZXeKMaqUcaPM=",
        ),
    ]
    case_count = 0
    for case in cases:
        print("Case: ", case_count)
        # A mainnet wallet
        wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
        ctx = create_ctx(mocker, case[0], wallet)
        mocker.patch.object(ctx.display, "width", new=lambda: 135)
        message_signer = SignMessage(ctx)

        if case[1]:
            mocker.spy(message_signer, "display_qr_codes")
            mocker.patch.object(
                QRCodeCapture,
                "qr_capture_loop",
                new=lambda self: (
                    case[1],
                    FORMAT_NONE,
                ),
            )
            qr_capturer = mocker.spy(QRCodeCapture, "qr_capture_loop")
        mocker.patch.object(message_signer, "has_sd_card", new=lambda: True)
        if case[2] is not None:  # Load from SD card
            mocker.patch.object(
                message_signer, "load_file", return_value=("signmessage.txt", case[2])
            )

        # SD available
        mocker.patch.object(message_signer, "has_sd_card", new=lambda: True)

        #  mock SDHandler listdir call
        mocker.patch(
            "os.listdir",
            new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
        )

        message_signer.sign_message()

        qr_capturer.assert_called_once()

        if case[2] != b"":
            ctx.display.draw_hcentered_text.assert_has_calls(
                [mocker.call("Message:", 10, theme.highlight_color)]
            )
            ctx.display.draw_hcentered_text.assert_has_calls(
                [mocker.call(case[4], mocker.ANY, max_lines=10)]
            )
            ctx.display.draw_hcentered_text.assert_has_calls(
                [mocker.call("Address:", mocker.ANY, theme.highlight_color)]
            )
            ctx.display.draw_hcentered_text.assert_has_calls(
                [mocker.call(case[5], mocker.ANY)],
            )
        if not case[3]:
            message_signer.display_qr_codes.assert_called_once_with(
                case[6],
                0,
                "Signed Message",
            )

        assert ctx.input.wait_for_button.call_count == len(case[0])

        case_count += 1


def test_load_from_sd_card(mocker, m5stickv, tdata):
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.input import BUTTON_ENTER
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    filename = "my_file"
    file_content = b"0E\x02 ,\xe6z\xc4("

    btn_seq = [
        BUTTON_ENTER,  # Confirm to Sign SHA
        BUTTON_ENTER,  # Check signature
        BUTTON_ENTER,  # Sign to QR code
        BUTTON_ENTER,  # Check QR code
        BUTTON_ENTER,  # Hex Public Key Text
        BUTTON_ENTER,  # PK QR code
    ]

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)

    ctx = create_ctx(mocker, btn_seq, wallet)
    sign_msg = SignMessage(ctx)

    # test sign at address with binary content (it can't be decoded to UTF8 and it is not sign to address)
    sign_msg._sign_at_address_from_sd(file_content) == None

    # mock load of file
    sign_msg._load_message = lambda: (file_content, FORMAT_NONE, filename)

    mocker.spy(sign_msg, "_export_signature")
    mocker.spy(sign_msg, "_export_to_qr")

    # Successful sign a binary (that can't be decoded) from sd card
    sign_msg.sign_message()

    # Assert signature sucessfully exported to QR
    sign_msg._export_signature.assert_called()
    sign_msg._export_to_qr.assert_called()

    assert ctx.input.wait_for_button.call_count == len(btn_seq)


def test_sign_message_sd_back_is_silent(mocker, m5stickv, tdata):
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.pages import MENU_CONTINUE
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    btn_seq = [
        BUTTON_PAGE,  # Go to "Load from SD card"
        BUTTON_ENTER,  # Select "Load from SD card"
    ]

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)
    sign_msg = SignMessage(ctx)
    mocker.patch.object(sign_msg, "has_sd_card", new=lambda: True)
    # user backed out of the SD file browser
    mocker.patch.object(sign_msg, "load_file", return_value=("", None))

    assert sign_msg.sign_message() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)

    # "Back" is not a failure - it must not flash an error
    assert_not_flashed(ctx, "Failed to load")


def test_sign_message_camera_back_is_silent(mocker, m5stickv, tdata):
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.pages import MENU_CONTINUE
    from krux.pages.qr_capture import QRCodeCapture
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER

    btn_seq = [BUTTON_ENTER]  # Select "Load from camera"

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)
    # user left the QR scanner without scanning anything
    mocker.patch.object(QRCodeCapture, "qr_capture_loop", new=lambda self: (None, None))

    assert SignMessage(ctx).sign_message() == MENU_CONTINUE
    assert ctx.input.wait_for_button.call_count == len(btn_seq)

    # "Back" is not a failure - it must not flash an error
    assert_not_flashed(ctx, "Failed to load")


LONG_MESSAGE_PATH = "m/84h/1h/0h/0/3"
LONG_MESSAGE = (
    "Proof of ownership for exchange withdrawal #4471.\n\n"
    + "I agree to pay 10000 sats to Bob on delivery. " * 12
    + "\nref:"
    + "0123456789abcdef" * 9
    + "\n"
    + "Reference data follows, nothing to see here. " * 12
    + "I ALSO ASSIGN ALL COINS IN THIS WALLET TO MALLORY."
)


def _long_message_signer(mocker, btn_seq, prompt_answers, touch_seq=()):
    """A SignMessage page whose display wraps text with the real Display of
    the board in use and records what is drawn, one list of lines per screen"""
    import board
    from embit.networks import NETWORKS
    from krux.display import Display
    from krux.key import Key, TYPE_SINGLESIG
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet

    display = Display()
    # portrait: the short side of the panel is the width
    mocker.patch.object(display, "width", return_value=board.config["lcd"]["height"])
    mocker.patch.object(display, "height", return_value=board.config["lcd"]["width"])
    screens = []

    def draw_hcentered_text(text, *args, **kwargs):
        lines = display.to_lines(text, kwargs.get("max_lines", 100))
        screens[-1].extend(lines)
        return len(lines)

    mocker.patch.object(display, "clear", side_effect=lambda: screens.append([]))
    mocker.patch.object(display, "draw_hcentered_text", side_effect=draw_hcentered_text)

    ctx = mocker.MagicMock()
    ctx.display = display
    ctx.wallet = Wallet(Key(tdata_mnemonic(), TYPE_SINGLESIG, NETWORKS["test"]))
    ctx.input.wait_for_fastnav_button.side_effect = btn_seq
    ctx.input.touch.current_index.side_effect = touch_seq
    page = SignMessage(ctx)
    mocker.patch.object(page, "draw_proceed_menu")
    mocker.patch.object(page, "prompt", side_effect=prompt_answers)
    mocker.patch.object(page, "_display_signature")
    mocker.spy(ctx.wallet.key, "sign_at")
    return page, screens


def tdata_mnemonic():
    return " ".join(["abandon"] * 11 + ["about"])


def _message_pages(screens):
    """The body of each "Message: n/m" screen, keyed by page number"""
    pages = {}
    for screen in screens:
        if screen and screen[0].startswith("Message: "):
            number, total = screen[0][len("Message: ") :].split("/")
            pages[int(number)] = screen[1:]
            assert len(pages) <= int(total)
    return pages


def _assert_whole_message_shown(mocker, message):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.settings import ELLIPSIS

    # More PAGE presses than pages: extra ones stay on the last page
    page, screens = _long_message_signer(
        mocker, [BUTTON_PAGE] * 60 + [BUTTON_ENTER], [True]
    )
    qr = ("signmessage %s ascii:%s" % (LONG_MESSAGE_PATH, message)).encode()
    sig, signed_text, _ = page._sign_at_address_from_qr(qr)

    assert sig is not None
    assert signed_text == message
    pages = _message_pages(screens)
    assert len(pages) > 1
    shown = [line for number in sorted(pages) for line in pages[number]]
    assert not any(ELLIPSIS in line for line in shown)
    # Wrapping only drops the space or newline a line was broken at
    assert "".join(shown).replace(" ", "") == message.replace(" ", "").replace("\n", "")
    return pages


def test_long_message_pages_show_every_char(mocker, multiple_devices):
    _assert_whole_message_shown(mocker, LONG_MESSAGE)


def test_long_message_page_ending_at_a_space(mocker, amigo):
    from krux.display import Display, TOTAL_LINES

    columns = Display().ascii_chars_per_line()
    amount = "I agree to pay 10000"
    # the amount ends exactly where the last line of the first page does
    line = "x" * (columns - len(amount) - 1) + " " + amount
    filler = ("y" * columns + " ") * (TOTAL_LINES - 6)
    message = filler + line + " sats to Bob on delivery. " + "z " * 400

    pages = _assert_whole_message_shown(mocker, message)

    assert pages[1][-1] == line
    assert pages[2][0].startswith("sats to Bob on delivery.")


def test_long_message_navigation(mocker, m5stickv):
    from krux.input import (
        BUTTON_ENTER,
        BUTTON_PAGE,
        BUTTON_PAGE_PREV,
        FAST_FORWARD,
        FAST_BACKWARD,
        SWIPE_LEFT,
        SWIPE_RIGHT,
    )

    btn_seq = [
        BUTTON_PAGE_PREV,  # already on the first page
        BUTTON_PAGE,  # 2
        SWIPE_LEFT,  # 3
        SWIPE_RIGHT,  # 2
        FAST_BACKWARD,  # 1
        BUTTON_ENTER,  # leave? No
        FAST_FORWARD,  # 2
        BUTTON_ENTER,  # leave? Yes
    ]
    page, screens = _long_message_signer(mocker, btn_seq, [False, True])
    qr = ("signmessage %s ascii:%s" % (LONG_MESSAGE_PATH, LONG_MESSAGE)).encode()
    sig, _, _ = page._sign_at_address_from_qr(qr)

    assert sig is None
    page.ctx.wallet.key.sign_at.assert_not_called()
    assert page.ctx.input.wait_for_fastnav_button.call_count == len(btn_seq)
    titles = [s[0].split("/")[0] for s in screens if s and s[0].startswith("Message: ")]
    assert titles == ["Message: %d" % n for n in (1, 1, 2, 3, 2, 1, 1, 2)]
    # "Sign?" was never asked, only "Are you sure?"
    assert [call.args[0] for call in page.prompt.call_args_list] == [
        "Are you sure?"
    ] * 2


def test_long_message_declined_at_sign_prompt(mocker, m5stickv):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    page, _ = _long_message_signer(mocker, [BUTTON_PAGE] * 60 + [BUTTON_ENTER], [False])
    qr = ("signmessage %s ascii:%s" % (LONG_MESSAGE_PATH, LONG_MESSAGE)).encode()
    sig, _, _ = page._sign_at_address_from_qr(qr)

    assert sig is None
    page.ctx.wallet.key.sign_at.assert_not_called()


def _sign_message_declined(mocker, loaded):
    """Runs sign_message on a loaded sign-at-address request and answers No
    at the "Sign?" prompt. Returns the page"""
    from embit.networks import NETWORKS
    from krux.key import Key, TYPE_SINGLESIG
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet

    wallet = Wallet(Key(tdata_mnemonic(), TYPE_SINGLESIG, NETWORKS["test"]))
    page = SignMessage(create_ctx(mocker, [], wallet))
    mocker.patch.object(page, "_load_message", return_value=loaded)
    mocker.patch.object(page, "prompt", return_value=False)
    mocker.patch.object(page, "_export_signature")
    mocker.spy(page, "sign_standard_message")
    mocker.spy(wallet.key, "sign_at")

    page.sign_message()

    page.prompt.assert_called_once()
    wallet.key.sign_at.assert_not_called()
    return page


def test_declined_qr_message_is_not_exported(mocker, m5stickv):
    from krux.qr import FORMAT_NONE

    qr = b"signmessage " + LONG_MESSAGE_PATH.encode() + b" ascii:hello world"
    page = _sign_message_declined(mocker, (qr, FORMAT_NONE, ""))

    page._export_signature.assert_not_called()
    # and the request is not signed as a standard message instead
    page.sign_standard_message.assert_not_called()


def test_declined_sd_message_is_not_exported(mocker, m5stickv):
    from krux.qr import FORMAT_NONE

    content = ("hello world\n%s\nP2WPKH" % LONG_MESSAGE_PATH).encode()
    page = _sign_message_declined(mocker, (content, FORMAT_NONE, "message.txt"))

    page._export_signature.assert_not_called()
    page.sign_standard_message.assert_not_called()


def test_message_over_max_len_is_refused(mocker, m5stickv):
    import pytest
    from krux.pages.home_pages.sign_message_ui import MESSAGE_MAX_LEN

    page, screens = _long_message_signer(mocker, [], [])
    prefix = "signmessage %s ascii:" % LONG_MESSAGE_PATH

    with pytest.raises(ValueError, match="Maximum length exceeded"):
        page._sign_at_address_from_qr((prefix + "a" * (MESSAGE_MAX_LEN + 1)).encode())

    # nothing was shown and nothing was signed
    assert screens == []
    page.prompt.assert_not_called()
    page.ctx.wallet.key.sign_at.assert_not_called()


def test_message_of_max_len_is_paged_and_signed(mocker, m5stickv):
    from krux.input import BUTTON_ENTER, FAST_FORWARD
    from krux.pages.home_pages.sign_message_ui import MESSAGE_MAX_LEN

    page, screens = _long_message_signer(
        mocker, [FAST_FORWARD] * 200 + [BUTTON_ENTER], [True]
    )
    message = ("All work and no play makes Jack a dull boy. " * 300)[:MESSAGE_MAX_LEN]
    qr = ("signmessage %s ascii:%s" % (LONG_MESSAGE_PATH, message)).encode()

    sig, signed_text, _ = page._sign_at_address_from_qr(qr)

    assert sig is not None
    assert signed_text == message
    pages = _message_pages(screens)
    shown = "".join(line for number in sorted(pages) for line in pages[number])
    assert shown.replace(" ", "") == message.replace(" ", "")


def test_big_message_is_paged_from_bounded_slices(mocker, m5stickv):
    from krux.display import TOTAL_LINES

    page, _ = _long_message_signer(mocker, [], [])
    text = "All work and no play makes Jack a dull boy. " * 2500  # 110 kB
    to_lines = mocker.spy(page.ctx.display, "to_lines")

    starts = page._message_page_starts(text, TOTAL_LINES - 4)

    assert len(starts) > 500
    assert starts == sorted(set(starts))
    # no call was handed the rest of the text, only about a page of it
    assert max(len(call.args[0]) for call in to_lines.call_args_list) < 300


def test_message_paging_stops_if_nothing_fits(mocker, m5stickv):
    from krux.pages.home_pages.sign_message_ui import SignMessage

    # The mocked display wraps any text to a single empty line
    page = SignMessage(create_ctx(mocker, []))

    assert page._message_page_starts("abc", 13) == [0]


def test_long_message_footer_offers_go_on_last_page_only(mocker, m5stickv):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    page, screens = _long_message_signer(
        mocker, [BUTTON_PAGE] * 60 + [BUTTON_ENTER], [True]
    )
    qr = ("signmessage %s ascii:%s" % (LONG_MESSAGE_PATH, LONG_MESSAGE)).encode()
    page._sign_at_address_from_qr(qr)

    total = len(_message_pages(screens))
    calls = page.draw_proceed_menu.call_args_list
    assert len(calls) == 61
    for number, call in enumerate(calls[:total], 1):
        assert call.args[:2] == ("Go", "Esc")
        # ENTER is outlined as "Esc" (0) until the last page, then "Go" (1)
        assert call.args[3] == (1 if number == total else 0)
        assert call.kwargs["go_enabled"] == (number == total)
    # the footer starts below the last line of text the page can hold
    from krux.display import DEFAULT_PADDING, FONT_HEIGHT, TOTAL_LINES

    assert calls[0].args[2] == DEFAULT_PADDING + (TOTAL_LINES - 3) * FONT_HEIGHT
    assert max(len(lines) for lines in _message_pages(screens).values()) == (
        TOTAL_LINES - 5
    )


def test_long_message_touch_navigation(mocker, amigo):
    from krux.input import BUTTON_TOUCH

    touch_seq = [
        0,  # previous: already on the first page
        1,  # next: 2
        1,  # next: 3
        0,  # previous: 2
        3,  # "Go": disabled before the last page
        2,  # "Esc": No
        2,  # "Esc": Yes
    ]
    page, screens = _long_message_signer(
        mocker, [BUTTON_TOUCH] * len(touch_seq), [False, True], touch_seq
    )
    qr = ("signmessage %s ascii:%s" % (LONG_MESSAGE_PATH, LONG_MESSAGE)).encode()
    sig, _, _ = page._sign_at_address_from_qr(qr)

    assert sig is None
    page.ctx.wallet.key.sign_at.assert_not_called()
    titles = [s[0].split("/")[0] for s in screens if s and s[0].startswith("Message: ")]
    # neither the disabled "Go" nor an unconfirmed "Esc" leaves page 2
    assert titles == ["Message: %d" % n for n in (1, 1, 2, 3, 2, 2, 2)]
    display = page.ctx.display
    page.ctx.input.touch.set_regions.assert_called_with(
        [0, display.width() // 2, display.width()],
        [0, page.draw_proceed_menu.call_args.args[2], display.height()],
    )


def test_long_message_touch_go_and_esc_on_last_page(mocker, amigo):
    from krux.input import BUTTON_PAGE, BUTTON_TOUCH

    qr = ("signmessage %s ascii:%s" % (LONG_MESSAGE_PATH, LONG_MESSAGE)).encode()

    # "Esc" still leaves when the last page is on the screen
    page, _ = _long_message_signer(
        mocker, [BUTTON_PAGE] * 60 + [BUTTON_TOUCH], [True], [2]
    )
    assert page._sign_at_address_from_qr(qr)[0] is None
    assert [call.args[0] for call in page.prompt.call_args_list] == ["Are you sure?"]

    # "Go" moves on to the sign prompt
    page, _ = _long_message_signer(
        mocker, [BUTTON_PAGE] * 60 + [BUTTON_TOUCH], [True], [3]
    )
    assert page._sign_at_address_from_qr(qr)[0] is not None
    assert [call.args[0] for call in page.prompt.call_args_list] == ["Sign?"]
    page.ctx.input.touch.clear_regions.assert_called()


def test_long_message_footer_is_drawn(mocker, amigo):
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    page, _ = _long_message_signer(mocker, [BUTTON_PAGE] * 60 + [BUTTON_ENTER], [True])
    drawn = mocker.spy(page.ctx.display, "draw_string")
    mocker.patch.object(
        page,
        "draw_proceed_menu",
        side_effect=type(page).draw_proceed_menu.__get__(page),
    )
    mocker.patch("krux.pages.lcd.string_width_px", side_effect=lambda s: 12 * len(s))
    qr = ("signmessage %s ascii:%s" % (LONG_MESSAGE_PATH, LONG_MESSAGE)).encode()
    page._sign_at_address_from_qr(qr)

    labels = [call.args[2] for call in drawn.call_args_list]
    assert "Esc" in labels and "Go" in labels
    # nothing of the footer is drawn past the bottom of the screen
    assert max(call.args[1] for call in drawn.call_args_list) < (
        page.ctx.display.height() - 24
    )

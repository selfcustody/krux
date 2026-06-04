import pytest
from ...shared_mocks import MockPrinter, get_mock_open
from .. import create_ctx
from .test_home import tdata

# Pre-built BIP-322 Simple PSBTs for tdata.SINGLESIG_SIGNING_KEY,
BIP322_P2PKH_PSBT = "cHNidP8BAD0CAAAAAQCT8JL2BtAApmsl1B/zBHFH8tXf9qPfLSK7A6gLAhQsAAAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEBIgAAAAAAAAAAGXapFNmG7QG3oiIlpw7b8rp8+2OhXLOqiKwiBgOq61LddJTDYQSd5nzGgOg+vLu9vrE2N9ks2EX3AwivXhhzxdoKLAAAgAAAAIAAAACAAAAAAAAAAAAAAA=="

BIP322_P2SH_P2WPKH_PSBT = "cHNidP8BAD0CAAAAAdnOujvnNBB4CCjtIYSFBflzrpwyNFOW3QgYqsYSwwlVAAAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEBIAAAAAAAAAAAF6kUP7bpWBLle7RpH5pKYohiphpPdpuHIgYDmztpS4/FteB/sGnHg8rHVPXTjD4IvtGWDjH9sd2jXCQYc8XaCjEAAIAAAACAAAAAgAAAAAAAAAAAAAA="

BIP322_P2WPKH_PSBT = "cHNidP8BAD0CAAAAAZEdpOdV7S+h47f+ubX6I4iaALKOjpPS6Xud3m2i7JLaAAAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEBHwAAAAAAAAAAFgAUwM681sPTyox13F7GLr5VMw75EOIiBgMw1U/Q3UIKbl+NNiT180gsrjUPedXwdTv1vu+cLZGvPBhzxdoKVAAAgAAAAIAAAACAAAAAAAAAAAAAAA=="

BIP322_P2TR_PSBT = "cHNidP8BAD0CAAAAAQ8eLSqZ9cH1Pi5bqoN9Rrwe7JbtPh8nZ+GhDGQTSR9pAAAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEBKwAAAAAAAAAAIlEgpghp8NvPHcZZyc7Lr4BQE16p6M3EhwU/HcaICUncaEwhFsyKS8ZNiXvdxfvC9nD3qLoLOGd5EGzxIjxvxdfNb8EVGQBzxdoKVgAAgAAAAIAAAACAAAAAAAAAAAAAAA=="

INVALID_BIP322_PSBT = "cHNidP8BAFICAAAAARERERERERERERERERERERERERERERERERERERERERERAAAAAAD/////AaCGAQAAAAAAFgAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
INVALID_BIP322_TWO_VINS_PSBT = "cHNidP8BAGYCAAAAApEdpOdV7S+h47f+ubX6I4iaALKOjpPS6Xud3m2i7JLaAAAAAAD/////kR2k51XtL6Hjt/65tfojiJoAso6Ok9Lpe53ebaLsktoAAAAAAP////8BAAAAAAAAAAABagAAAAABCQxoZWxsbyBiaXAzMjIAAQEfAAAAAAAAAAAWABTAzrzWw9PKjHXcXsYuvlUzDvkQ4gABAR8AAAAAAAAAABYAFMDOvNbD08qMddxexi6+VTMO+RDiAAA="
INVALID_BIP322_WRONG_PREVN_PSBT = "cHNidP8BAD0CAAAAAZEdpOdV7S+h47f+ubX6I4iaALKOjpPS6Xud3m2i7JLaAQAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEBHwAAAAAAAAAAFgAUwM681sPTyox13F7GLr5VMw75EOIAAA=="
INVALID_BIP322_FUNDED_PSBT = "cHNidP8BAD0CAAAAAZEdpOdV7S+h47f+ubX6I4iaALKOjpPS6Xud3m2i7JLaAAAAAAD/////AQEAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEBHwAAAAAAAAAAFgAUwM681sPTyox13F7GLr5VMw75EOIAAA=="
INVALID_BIP322_NON_OP_RETURN_PSBT = "cHNidP8BAFICAAAAAZEdpOdV7S+h47f+ubX6I4iaALKOjpPS6Xud3m2i7JLaAAAAAAD/////AQAAAAAAAAAAFgAUwM681sPTyox13F7GLr5VMw75EOIAAAAAAQkMaGVsbG8gYmlwMzIyAAEBHwAAAAAAAAAAFgAUwM681sPTyox13F7GLr5VMw75EOIAAA=="
INVALID_BIP322_NO_UTXO_PSBT = "cHNidP8BAD0CAAAAAZEdpOdV7S+h47f+ubX6I4iaALKOjpPS6Xud3m2i7JLaAAAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAAA"

# P2PKH with non_witness_utxo (parent tx vout[0] = address spk) instead of witness_utxo.
BIP322_P2PKH_NON_WITNESS_UTXO_PSBT = "cHNidP8BAD0CAAAAAQCT8JL2BtAApmsl1B/zBHFH8tXf9qPfLSK7A6gLAhQsAAAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEAVQAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/////AAAAAAABAAAAAAAAAAAZdqkU2YbtAbeiIiWnDtvyunz7Y6Fcs6qIrAAAAAAiBgOq61LddJTDYQSd5nzGgOg+vLu9vrE2N9ks2EX3AwivXhhzxdoKLAAAgAAAAIAAAACAAAAAAAAAAAAAAA=="

# Prepared for fingerprint b8688df1 — tdata's fp 73c5da0a doesn't match.
BIP322_OTHER_WALLET_PSBT = "cHNidP8BAD0CAAAAAcGgKxwXL1jXcIP4vdKJAPjw6N8+KaBi+XHCxdO9slW6AAAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEBHwAAAAAAAAAAFgAURaXKkYxfBPgdgJnj4ES6lkXFXPkiBgLh6Dn3camvYFVOBD3posWvbavFvR0y8zGXCX3KVI6JVxi4aI3xVAAAgAAAAIAAAACAAAAAAAAAAAAAAA=="

# Valid BIP-322 p2wpkh shape but bip32_derivations stripped.
BIP322_P2WPKH_NO_DERIV_PSBT = "cHNidP8BAD0CAAAAAZEdpOdV7S+h47f+ubX6I4iaALKOjpPS6Xud3m2i7JLaAAAAAAD/////AQAAAAAAAAAAAWoAAAAAAQkMaGVsbG8gYmlwMzIyAAEBHwAAAAAAAAAAFgAUwM681sPTyox13F7GLr5VMw75EOIAAA=="


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
            "J2uqv81L1L/J00MeVf57Qu2i79if0LN5wxx0vU6Fv5D5TIZBIJArt4k6rt0dgNZiIdHU15qeEF7CQJYtQwfHJeo=",  # 4 base64 for display_qr_codes / print_qr_prompt
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
            "J1fZldA6aYktc2yN/oRmmSEFZDHgF7ekX76bltaIkr8lChzU1lPe/1mSBFHTJAaQHsoFOGneJwo4fxkbIjFpsqM=",
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
            "KNDYjnAavccLPKVJ7u6RjWs9n2NzN+kHc8MHrrUiQRq9TEoXa3UAbwsjESNCi7wcAZ9Vw1N7K+ujZzasgEgsvL0=",
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
            "KIyFNagItWNotujcQQ7AoXLO90ndVEmsQvXeJbaTnFKufb2eq+G1RKvxRw+eR887Rn0UgqAKyrji4GQQYGfxvkw=",
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
            "J2uqv81L1L/J00MeVf57Qu2i79if0LN5wxx0vU6Fv5D5TIZBIJArt4k6rt0dgNZiIdHU15qeEF7CQJYtQwfHJeo=",
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
            "J2uqv81L1L/J00MeVf57Qu2i79if0LN5wxx0vU6Fv5D5TIZBIJArt4k6rt0dgNZiIdHU15qeEF7CQJYtQwfHJeo=",
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
            "KNDYjnAavccLPKVJ7u6RjWs9n2NzN+kHc8MHrrUiQRq9TEoXa3UAbwsjESNCi7wcAZ9Vw1N7K+ujZzasgEgsvL0=",  # 4 base64 for display_qr_codes / print_qr_prompt
            "02707a62fdacc26ea9b63b1c197906f56ee0180d0bcf1966e1a2da34f5f3a09a9b",  # 5 pubkey for display_qr_codes / print_qr_prompt
            # 6 SD file
            binascii.b2a_base64(
                "KNDYjnAavccLPKVJ7u6RjWs9n2NzN+kHc8MHrrUiQRq9TEoXa3UAbwsjESNCi7wcAZ9Vw1N7K+ujZzasgEgsvL0=".encode(
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
            "J7jAswueRmlhh64HDmfIuVvo5pcMMgBYdSCXAnMh2NQsQUwYkyI1O8G0F/8ChIiOz2pfCiQwE0FfOXWTAtMsMDE=",
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
            "JwdAF2MY6uglo4E3Wxbbi9G6NyrEna4LyYBsUueJg8yoLQm39BHDJ+ulgRhXl2RI/BManG05oTmRyXOqjDfDrs0=",
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
            "J0yYgnVLwEditYd+QwmJrXqFRplrBqfUfUHOpAF4m+EEW9MYf4BVp/SWPujLDYfQKWxbpRPVZdaYuyGm77bNSsE=",
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
            "KN/4LmcGRaI5sgvBP2mrTXQFvD6FecXd8La03SixPabsb/255ElRGTcXhicT3KFsNJbfQ9te909ZXeKMaqUcaPM=",
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
            "KLc30ti8OPSpCtzfj7sNnftANBCuVpyRX7pnM3iAgOk9F9IUtnXNPus0+MF12y5HKYHAB6IVYr66sLmL3Vi3oEE=",
        ),
        (  # 2 (was 3) - Sign Legacy Mainnet
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
            "IyH8898c2S6eF8hTPGhRqLC6UQrJrhw/fdguBeFG0cCrOFkbG8TCVURXOgxXaEV93vrFlHyxNGEvL10IcsLtvvI=",
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
            "KN/4LmcGRaI5sgvBP2mrTXQFvD6FecXd8La03SixPabsb/255ElRGTcXhicT3KFsNJbfQ9te909ZXeKMaqUcaPM=",
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
            "KN/4LmcGRaI5sgvBP2mrTXQFvD6FecXd8La03SixPabsb/255ElRGTcXhicT3KFsNJbfQ9te909ZXeKMaqUcaPM=",
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
            "KN/4LmcGRaI5sgvBP2mrTXQFvD6FecXd8La03SixPabsb/255ElRGTcXhicT3KFsNJbfQ9te909ZXeKMaqUcaPM=",
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
                [mocker.call("Message:", mocker.ANY, theme.highlight_color)]
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


def test_sign_bip322_psbt_menu(mocker, m5stickv, tdata):
    from krux import bip137, bip322
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture
    from krux.pages import Menu

    btn_seq = [
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Confirm Sign?
        BUTTON_ENTER,  # Dismiss QR display
    ]

    # (script_type, opaque pre-built PSBT, signing module)
    cases = [
        ("p2pkh", BIP322_P2PKH_PSBT, bip137),
        ("p2sh-p2wpkh", BIP322_P2SH_P2WPKH_PSBT, bip137),
        ("p2wpkh", BIP322_P2WPKH_PSBT, bip322),
        ("p2tr", BIP322_P2TR_PSBT, bip322),
    ]

    # `mocker.spy` wraps the live module attribute; re-running it on a
    # later iteration would try to spy the previous spy and fail with
    # InvalidSpecError.
    original_bip137_sign = bip137.sign
    original_bip322_sign = bip322.sign
    for i, case in enumerate(cases):
        print("case %d (%s)" % (i, case[0]))
        bip137.sign = original_bip137_sign
        bip322.sign = original_bip322_sign

        run_loop = iter([(0, None), (0, None)])
        mocker.patch.object(Menu, "run_loop", new=lambda self: next(run_loop))

        wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
        ctx = create_ctx(mocker, btn_seq, wallet)
        home = SignMessage(ctx)
        mocker.patch.object(
            QRCodeCapture,
            "qr_capture_loop",
            new=lambda self: (case[1], FORMAT_NONE),
        )
        mocker.patch.object(home, "has_sd_card", new=lambda: False)
        mocker.patch.object(
            home,
            "display_qr_codes",
            new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
        )
        mocker.patch.object(home, "print_standard_qr", new=lambda *a, **kw: None)
        sign_spy = mocker.spy(case[2], "sign")
        home.sign_message()
        sign_spy.assert_called_once()


def test_sign_non_bip322_psbt_fail(mocker, m5stickv, tdata):
    import pytest
    from krux import bip322
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    cases = [
        INVALID_BIP322_PSBT,
        INVALID_BIP322_TWO_VINS_PSBT,
        INVALID_BIP322_WRONG_PREVN_PSBT,
        INVALID_BIP322_FUNDED_PSBT,
        INVALID_BIP322_NON_OP_RETURN_PSBT,
        INVALID_BIP322_NO_UTXO_PSBT,
    ]

    original_check = bip322.check_bip322_psbt
    for i, psbt_b64 in enumerate(cases):
        print("Case %d" % i)
        bip322.check_bip322_psbt = original_check

        wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
        ctx = create_ctx(mocker, [BUTTON_ENTER], wallet)
        home = SignMessage(ctx)
        mocker.patch.object(
            QRCodeCapture,
            "qr_capture_loop",
            new=lambda self, b=psbt_b64: (b, FORMAT_NONE),
        )
        check_spy = mocker.spy(bip322, "check_bip322_psbt")
        with pytest.raises(ValueError, match="Invalid BIP-322 PSBT"):
            home.sign_message()
        check_spy.assert_called_once()
        assert check_spy.spy_return is False


def test_sign_bip322_psbt_accepts_non_witness_utxo(mocker, m5stickv, tdata):
    from krux import bip322
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, [BUTTON_ENTER], wallet)
    home = SignMessage(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (BIP322_P2PKH_NON_WITNESS_UTXO_PSBT, FORMAT_NONE),
    )
    check_spy = mocker.spy(bip322, "check_bip322_psbt")
    flash_spy = mocker.spy(home, "flash_text")
    try:
        home.sign_message()
    except AttributeError:
        pass

    check_spy.assert_called_once()
    assert check_spy.spy_return is True
    assert all(c.args[0] != "Not a BIP-322 PSBT" for c in flash_spy.call_args_list)


def test_sign_bip322_psbt_from_ur(mocker, m5stickv, tdata):
    import base64
    from ur.ur import UR
    from urtypes.crypto import PSBT as URPSBT
    from krux import bip322
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_UR
    from krux.pages.qr_capture import QRCodeCapture
    from krux.pages import Menu

    raw = base64.b64decode(BIP322_P2WPKH_PSBT)
    ur_psbt = UR("crypto-psbt", URPSBT(raw).to_cbor())

    btn_seq = [
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Confirm Sign?
        BUTTON_ENTER,  # Dismiss QR display
    ]
    run_loop = iter([(0, None), (0, None)])
    mocker.patch.object(Menu, "run_loop", new=lambda self: next(run_loop))

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)
    home = SignMessage(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (ur_psbt, FORMAT_UR),
    )
    mocker.patch.object(home, "has_sd_card", new=lambda: False)
    mocker.patch.object(
        home,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    mocker.patch.object(home, "print_standard_qr", new=lambda *a, **kw: None)
    sign_spy = mocker.spy(bip322, "sign")

    home.sign_message()

    sign_spy.assert_called_once()


def test_sign_bip322_psbt_from_bbqr(mocker, m5stickv, tdata):
    import base64
    from krux import bip322
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_BBQR
    from krux.pages.qr_capture import QRCodeCapture
    from krux.pages import Menu

    raw = base64.b64decode(BIP322_P2WPKH_PSBT)

    btn_seq = [
        BUTTON_ENTER,  # Load from camera
        BUTTON_ENTER,  # Confirm Sign?
        BUTTON_ENTER,  # Dismiss QR display
    ]
    run_loop = iter([(0, None), (0, None)])
    mocker.patch.object(Menu, "run_loop", new=lambda self: next(run_loop))

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, btn_seq, wallet)
    home = SignMessage(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (raw, FORMAT_BBQR),
    )
    mocker.patch.object(home, "has_sd_card", new=lambda: False)
    mocker.patch.object(
        home,
        "display_qr_codes",
        new=lambda data, qr_format, title=None: ctx.input.wait_for_button(),
    )
    mocker.patch.object(home, "print_standard_qr", new=lambda *a, **kw: None)
    sign_spy = mocker.spy(bip322, "sign")

    home.sign_message()

    sign_spy.assert_called_once()


def test_sign_bip322_psbt_fail_missing_derivations(mocker, m5stickv, tdata):
    import pytest
    from krux import bip322
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, [BUTTON_ENTER, BUTTON_ENTER], wallet)
    home = SignMessage(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (BIP322_P2WPKH_NO_DERIV_PSBT, FORMAT_NONE),
    )
    sign_spy = mocker.spy(bip322, "sign")
    with pytest.raises(ValueError):
        home.sign_message()
    sign_spy.assert_called_once()


def test_sign_bip322_psbt_decline_sign(mocker, m5stickv, tdata):
    from krux import bip137, bip322
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER, BUTTON_PAGE
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, [BUTTON_ENTER, BUTTON_PAGE], wallet)
    home = SignMessage(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (BIP322_P2WPKH_PSBT, FORMAT_NONE),
    )
    bip137_spy = mocker.spy(bip137, "sign")
    bip322_spy = mocker.spy(bip322, "sign")

    home.sign_message()

    bip137_spy.assert_not_called()
    bip322_spy.assert_not_called()


def test_sign_bip322_psbt_fail_wrong_wallet(mocker, m5stickv, tdata):
    from krux import bip322
    from krux.pages.home_pages.sign_message_ui import SignMessage
    from krux.wallet import Wallet
    from krux.input import BUTTON_ENTER
    from krux.qr import FORMAT_NONE
    from krux.pages.qr_capture import QRCodeCapture
    from krux.pages import Menu

    run_loop = iter([(0, None), (0, "simple")])
    mocker.patch.object(Menu, "run_loop", new=lambda self: next(run_loop))

    wallet = Wallet(tdata.SINGLESIG_SIGNING_KEY)
    ctx = create_ctx(mocker, [BUTTON_ENTER, BUTTON_ENTER], wallet)
    home = SignMessage(ctx)
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        new=lambda self: (BIP322_OTHER_WALLET_PSBT, FORMAT_NONE),
    )
    mocker.patch.object(home, "has_sd_card", new=lambda: False)
    sign_spy = mocker.spy(bip322, "sign")
    with pytest.raises(ValueError):
        home.sign_message()
    sign_spy.assert_called_once()

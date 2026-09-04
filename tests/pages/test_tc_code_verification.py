import pytest

from . import create_ctx


@pytest.fixture
def device_secret(mocker):
    mocker.patch("machine.unique_id", return_value=b"\x01" * 32)


def test_tc_code_verification(amigo, mocker, device_secret):
    from krux.pages import (
        LETTERS,
        UPPERCASE_LETTERS,
        NUM_SPECIAL_1,
        NUM_SPECIAL_2,
    )
    from krux.pages.tc_code_verification import TCCodeVerification
    from unittest.mock import mock_open, patch

    cases = [
        # TC Code
        # TC Code Extended hash
        # Should pass True/False
        # Is changing TC Code True/False
        # Return TC Code single hash Hash/False
        (
            "123456",
            b"z\xc0\x99\xac\x01\x1f\xef\x91\xb6\xd5\xbd\xa8\xdc\xfc\x14\xcco-A\x9d\xba\xde\xaf\xe3\xe1{@0t\xb2\x85{",
            True,
            False,
            False,
        ),
        (
            "aBcDeF%@14",
            b"\x98\x99kJ\x03\x98r\xec \x9d\xd6\xbaG\xc2P\xbb9\x00\xe53(\x98\xb9\x1a,\x13-.\x1e\xe6Z\xc8",
            True,
            False,
            False,
        ),
        (
            " secret ",
            b"\xb5\xa0\x88z\x98\xb8_\\\xf9`>\xb6\xf5\xefo\x82Q\x8a\xea!A\x8a\xc0\xf6\xd2\x96R\x1f\x7f,\xfa\xd3",
            True,
            False,
            False,
        ),
        (
            "aBcDeF%@14",
            b"\x98\x99kJ\x03\x98r\xec \x9d\xd6\xbaG\xc2P\xbb9\x00\xe53(\x98\xb9\x1a,\x13-.\x1e\xe6Z\xc8",
            True,
            True,
            False,
        ),
        (
            "aBcDeF%@14",
            b"\x98\x99kJ\x03\x98r\xec \x9d\xd6\xbaG\xc2P\xbb9\x00\xe53(\x98\xb9\x1a,\x13-.\x1e\xe6Z\xc8",
            True,
            False,
            b'<9y~\xba\xfdqv\xa0\xb5\x0f\xf9v6 lht\xf4\x17\xcfmw"J\xac8bkx\xc3\xfa',
        ),
        (
            "aBcDeF%@14",
            b"\x98\x99kJ\x04\x98r\xec \x9d\xd6\xbaG\xc2P\xbb9\x00\xe53(\x98\xb9\x1a,\x13-.\x1e\xe6Z\xc8",
            False,
            False,
            False,
        ),
    ]
    for case in cases:
        ctx = create_ctx(mocker, [])
        tc_verifier = TCCodeVerification(ctx)
        tc_verifier.capture_from_keypad = mocker.MagicMock(return_value=case[0])

        with patch("builtins.open", mock_open(read_data=case[1])):
            if case[4]:
                assert (
                    tc_verifier.capture(changing_tc_code=case[3], return_hash=True)
                    == case[4]
                )
            elif case[2]:
                assert tc_verifier.capture(changing_tc_code=case[3]) == True
            else:
                assert tc_verifier.capture(changing_tc_code=case[3]) == False

        keypad_label = "Current Tamper Check Code" if case[3] else "Tamper Check Code"
        tc_verifier.capture_from_keypad.assert_called_once_with(
            keypad_label,
            [NUM_SPECIAL_1, LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_2],
            scan_fn=(None if case[3] else tc_verifier._load_qr_tc_code),
        )


def test_tc_code_verification_esc_key(amigo, mocker):
    from krux.pages.tc_code_verification import TCCodeVerification
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    # Simulate user pressing ESC key
    cases = [
        # 1 - Simple ESC key after entering TC Code then pressing "Yes" in prompt
        (
            BUTTON_PAGE_PREV,  # Navigate to ESC key
            BUTTON_PAGE_PREV,  # Navigate to ESC key
            BUTTON_ENTER,  # Press ESC key
            BUTTON_ENTER,  # Confirm "Yes" in prompt
        ),
        # 2 - ESC key after entering TC Code, then "No" in prompt
        # then pressing ESC again and then "Yes" to exit
        (
            BUTTON_PAGE_PREV,  # Navigate to ESC key
            BUTTON_PAGE_PREV,  # Navigate to ESC key
            BUTTON_ENTER,  # Press ESC key (first time)
            BUTTON_PAGE_PREV,  # Navigate to "No" in prompt
            BUTTON_ENTER,  # Select "No" - stay in keypad
            BUTTON_ENTER,  # Press ESC key again (cursor stays on ESC)
            BUTTON_ENTER,  # Select "Yes" - exit (default selection)
        ),
    ]

    for case in cases:
        ctx = create_ctx(mocker, case)
        tc_verifier = TCCodeVerification(ctx)
        result = tc_verifier.capture()

        assert result == False
        assert ctx.input.wait_for_button.call_count == len(case)


def test_tc_code_qr_sanitization(amigo, mocker):
    from krux.pages.tc_code_verification import TCCodeVerification

    tc_verifier = TCCodeVerification(create_ctx(mocker, []))
    cases = [
        ("aBcDeF%@14", "aBcDeF%@14"),
        (b"https://it-tools.tech", "https://it-tools.tech"),
        (b"  aBcDeF%@14  ", "  aBcDeF%@14  "),
        (b"  aBcDeF%@14\r\n", None),
        (None, None),
        (b"\xff", None),
        ("", None),
        ("first\nsecond", None),
        ("unexpected-á", None),
        (123456, None),
    ]

    for qr_data, expected in cases:
        assert tc_verifier._sanitize_qr_tc_code(qr_data) == expected


def test_load_qr_tc_code(amigo, mocker):
    from krux.pages.qr_capture import QRCodeCapture
    from krux.pages.tc_code_verification import TCCodeVerification

    tc_verifier = TCCodeVerification(create_ctx(mocker, []))
    mocker.patch.object(
        QRCodeCapture,
        "qr_capture_loop",
        side_effect=[(" qr-code ", None), ("first\nsecond", None)],
    )

    assert tc_verifier._load_qr_tc_code() == " qr-code "
    assert tc_verifier._load_qr_tc_code() is None
    tc_verifier.ctx.display.flash_text.assert_called_once_with(
        "Failed to load", 248, 2000, highlight_prefix=""
    )

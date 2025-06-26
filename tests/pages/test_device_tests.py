import pytest
from . import create_ctx


@pytest.fixture
def mocked_print_qr(mocker):
    """Fixture to mock the print QR function"""
    return mocker.patch("krux.pages.utils.Utils.print_standard_qr")


@pytest.fixture
def mocked_run_one_test(mocker):
    """Fixture to mock the test suite function"""
    return mocker.patch("krux.pages.device_tests.DeviceTests.run_one_test")


@pytest.fixture
def mock_fail_hw_acc_hashing(mocker):
    """Fixture to mock the hardware acceleration hashing test to fail"""
    # Force hash outputs to cause assertion failure
    bad_digest = b"\x00" * 32

    f_hash = mocker.patch(
        "uhashlib_hw.sha256", return_value=mocker.Mock(digest=lambda: bad_digest)
    )
    f_hmac = mocker.patch(
        "uhashlib_hw.pbkdf2_hmac_sha256", side_effect=lambda pwd, salt, iter: bad_digest
    )
    return f_hmac, f_hash


@pytest.fixture
def mock_fail_hashlib_sha256(mocker):
    """Fixture to mock the hashlib sha256 function to fail"""
    # Force hash outputs to cause assertion failure
    bad_digest = b"\x00" * 32

    return mocker.patch(
        "hashlib.sha256", return_value=mocker.Mock(digest=lambda: bad_digest)
    )


@pytest.fixture
def mock_fail_hexlify_endianess(mocker):
    """Fixture to mock the binascii hexlify function to fail"""
    from hashlib import sha256
    from binascii import hexlify, unhexlify

    # start like the original deflate_compression function
    uncompressed = sha256(b"").digest()
    uncompressed += hexlify(sha256(uncompressed).digest())  # append as bytes

    # reverse byte order of both parts
    # to simulate an endianess issue
    part1 = uncompressed[:32][::-1]
    part2 = unhexlify(uncompressed[32:])[::-1]  # decode then reverse
    bad_digest = part1 + part2

    return mocker.patch(
        "binascii.hexlify", return_value=mocker.Mock(digest=lambda: bad_digest)
    )


@pytest.fixture
def mock_fail_b2a_base64_endianess(mocker):
    """Fixture to mock the binascii b2a_base64 function to fail"""
    from hashlib import sha256
    from binascii import hexlify, unhexlify, b2a_base64, a2b_base64

    part1 = sha256(b"").digest()
    part2 = hexlify(sha256(part1).digest())
    part3 = b2a_base64(sha256(part1 + part2).digest())

    # Reverse each part
    rev1 = part1[::-1]
    rev2 = hexlify(unhexlify(part2)[::-1])
    rev3 = b2a_base64(a2b_base64(part3)[::-1])

    # Combine reversed parts
    bad_digest = rev1 + rev2 + rev3

    return mocker.patch(
        "binascii.b2a_base64", return_value=mocker.Mock(digest=lambda: bad_digest)
    )


def test_printer_test_tool(amigo, mocker, mocked_print_qr):
    """Test that the print tool is called with the correct text"""
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER

    # Confirm print, then leave
    BTN_SEQUENCE = [BUTTON_ENTER]

    # Create a context with the mocked input sequence
    ctx = create_ctx(mocker, BTN_SEQUENCE)

    # Create an instance of the DeviceTests page
    test_tools = DeviceTests(ctx)
    test_tools.print_test()

    # Assert that the print function was called with the expected text
    mocked_print_qr.assert_called_with(
        "Krux Printer Test QR", title="Krux Printer Test QR", check_printer=False
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_skip_all_tests(m5stickv, mocker, mocked_print_qr, mocked_run_one_test):
    """Test skipping all tests in the DeviceTests page.
    It enters the test suite page and then backs to the main menu"""
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    # enter the menu and then back to the main menu
    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,
        BUTTON_ENTER,
    )

    # Create a context with the mocked input sequence
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    result = page.run()

    assert result

    # assert that none of the tests run
    mocked_print_qr.assert_not_called()
    mocked_run_one_test.assert_not_called()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_hw_acc_hashing_fail(m5stickv, mocker, mock_fail_hw_acc_hashing):
    """Directly test hw_acc_hashing() hitting the except block"""
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # assert that the hardware acceleration hashing test function was called
    f_hash, f_hmac = mock_fail_hw_acc_hashing
    assert f_hash.call_count > 0
    assert f_hmac.call_count > 0

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 54%\nfailed: 5/11", info_box=True
            )
        ]
    )


def test_deflate_compression_fail_from_wrong_sha256(
    m5stickv, mocker, mock_fail_hashlib_sha256
):
    """Directly test hw_acc_hashing() hitting the except block"""
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # assert that the hardware acceleration hashing test function was called
    mock_fail_hashlib_sha256.assert_has_calls(
        [
            mocker.call(b""),
        ]
    )

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 54%\nfailed: 5/11", info_box=True
            )
        ]
    )


def test_deflate_compression_fail_from_wrong_hexilify(
    m5stickv, mocker, mock_fail_hexlify_endianess
):
    """Directly test hw_acc_hashing() hitting the except block"""
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # assert that the hardware acceleration hashing test function was called
    mock_fail_hexlify_endianess.assert_has_calls(
        [
            mocker.call(
                b"]\xf6\xe0\xe2v\x13Y\xd3\n\x82u\x05\x8e)\x9f\xcc\x03\x81SEE\xf5\\\xf4>A\x98?]L\x94V"
            ),
        ]
    )

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 54%\nfailed: 5/11", info_box=True
            )
        ]
    )


def test_deflate_compression_fail_from_wrong_b2a_base64(
    m5stickv, mocker, mock_fail_b2a_base64_endianess
):
    """Directly test hw_acc_hashing() hitting the except block"""
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # assert that the hardware acceleration hashing test function was called
    mock_fail_b2a_base64_endianess.assert_has_calls(
        [
            mocker.call(
                b"\xbfy\xbf\x1b=\xce=\x9c\xd4o\x95\x86\xf0\xbd\x87W\xfb\xe2\xf5\xbb\xc1\xa4\x01\xfb{U\xeei\xea\xa3/h"
            ),
        ]
    )

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 54%\nfailed: 5/11", info_box=True
            )
        ]
    )


def test_run_test_suite_only(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # while prototyping: run_test_suite() purposely fails 4 of 10 tests
    # page.ctx.display.draw_hcentered_text.assert_has_calls([mocker.call(
    #    "Test Suite Results\nsuccess rate: 100%", info_box=True
    # )])
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 63%\nfailed: 4/11", info_box=True
            )
        ]
    )


def test_run_test_suite_plus_individual_test(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE,  # select a unit test
        BUTTON_ENTER,  # run the unit test
        BUTTON_PAGE,  # fulfill wait-for-button
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # while prototyping: run_test_suite() purposely fails 4 of 11 tests
    # page.ctx.display.draw_hcentered_text.assert_has_calls([mocker.call(
    #    "Test Suite Results\nsuccess rate: 100%", info_box=True
    # )])
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 63%\nfailed: 4/11", info_box=True
            )
        ]
    )


def test_run_one_test_test_hw_acc_hashing(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_ENTER,  # hit enter to proceed
        BUTTON_PAGE_PREV,  #
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)

    # since bypassing test-suite, fake existing results
    page.results = [(page.hw_acc_hashing, False)]
    page.run_one_test(page.hw_acc_hashing)
    assert page.results == [(page.hw_acc_hashing, True)]


def test_run_one_test_deflate_compression(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_ENTER,  # hit enter to proceed
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)

    # since bypassing test-suite, fake existing results
    page.results = [(page.deflate_compression, False)]
    page.run_one_test(page.deflate_compression)
    assert page.results == [(page.deflate_compression, True)]


def test_run_one_test_touch_gestures(amigo, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import (
        BUTTON_ENTER,
        BUTTON_PAGE_PREV,
        BUTTON_TOUCH,
        SWIPE_RIGHT,
        SWIPE_LEFT,
        SWIPE_UP,
        SWIPE_DOWN,
    )

    BTN_SEQUENCE = (
        BUTTON_TOUCH,
        SWIPE_RIGHT,
        SWIPE_LEFT,
        SWIPE_UP,
        SWIPE_DOWN,
        BUTTON_ENTER,  # hit enter to proceed
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)

    # since bypassing test-suite, fake existing results
    page.results = [(page.touch_gestures, False)]
    page.run_one_test(page.touch_gestures)
    assert page.results == [(page.touch_gestures, True)]


def test_run_one_test_fail_touch_gestures(amigo, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import (
        BUTTON_ENTER,
        BUTTON_PAGE_PREV,
        BUTTON_TOUCH,
    )

    BTN_SEQUENCE = (
        BUTTON_TOUCH,  # correct
        BUTTON_TOUCH,  # should have been swipe-right
        BUTTON_TOUCH,  # should have been swipe-left
        BUTTON_TOUCH,  # should have been swipe-up
        BUTTON_TOUCH,  # should have been swipe-down
        BUTTON_ENTER,  # hit enter to proceed
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)

    # since bypassing test-suite, fake existing results
    page.results = [(page.touch_gestures, True)]
    page.run_one_test(page.touch_gestures)
    assert page.results == [(page.touch_gestures, False)]


def test_run_one_test_without_touch_gestures(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_ENTER,  # hit enter to proceed
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)

    # since bypassing test-suite, fake existing results
    page.results = [(page.touch_gestures, False)]
    page.run_one_test(page.touch_gestures)
    assert page.results == [(page.touch_gestures, True)]

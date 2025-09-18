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
def mock_multi_layer_decrypt(mocker):
    """Fixture to mock multi_layer_decrypt failing"""

    return mocker.patch(
        "krux.kef.Cipher.decrypt", side_effect=lambda cpl, version: None
    )


@pytest.fixture
def mock_hw_acc_hashing(mocker):
    """Fixture to mock the hardware acceleration hashing test to fail"""
    bad_digest = b"\x00" * 32

    f_hash = mocker.patch(
        "uhashlib_hw.sha256", return_value=mocker.Mock(digest=lambda: bad_digest)
    )
    f_hmac = mocker.patch(
        "uhashlib_hw.pbkdf2_hmac_sha256", side_effect=lambda pwd, salt, iter: bad_digest
    )
    return f_hmac, f_hash


@pytest.fixture
def mock_hashlib_sha256(mocker):
    """Fixture to mock the hashlib sha256 function to fail"""
    bad_digest = b"\x00" * 32

    return mocker.patch(
        "hashlib.sha256", return_value=mocker.Mock(digest=lambda: bad_digest)
    )


@pytest.fixture
def mock_hexlify_endianess(mocker):
    """Fixture to mock the binascii hexlify function to fail"""
    from hashlib import sha256
    from binascii import hexlify, unhexlify

    # start like the original deflate_compression function
    uncompressed = sha256(b"").digest()
    uncompressed += hexlify(sha256(uncompressed).digest())  # append as bytes

    # reverse byte order of both parts to simulate an endianess issue
    part1 = uncompressed[:32][::-1]
    part2 = unhexlify(uncompressed[32:])[::-1]
    bad_digest = part1 + part2

    return mocker.patch(
        "binascii.hexlify", return_value=mocker.Mock(digest=lambda: bad_digest)
    )


@pytest.fixture
def mock_b2a_base64_endianess(mocker):
    """Fixture to mock the binascii b2a_base64 function to fail"""
    from hashlib import sha256
    from binascii import hexlify, unhexlify, b2a_base64, a2b_base64

    # start like the original deflate_compression function
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


@pytest.fixture
def mock_deflate(mocker):
    """Fixture to mock the deflate_compression function to fail"""
    deflate_compress = mocker.patch(
        "krux.bbqr.deflate_compress", return_value=b"\x00" * 32
    )
    deflate_decompress = mocker.patch(
        "krux.bbqr.deflate_decompress", return_value=b"krux"
    )

    return deflate_compress, deflate_decompress


@pytest.fixture
def mock_maixpy_code(mocker):
    from krux.bbqr import deflate_decompress as real_deflate_decompress

    mock_exptected = b"{\xbc\xe1\x88\xd3\x8c?2\"\xb3~\x7f913\x7f\xa7\x8a\xfa:\xc7')\xb3'\xfb,\x99:S\xba\"hG\xa8iJ\x9aY\xaaA\xaa\x91\xb9\x99\xa1\xb1\xa9e\x8a\xb1A\xa2\x85\x91\xb9\xa9\x81\xa9E\xaa\x91\xa5eZr\xb2\x81\xb1\x85\xa1\xa9\xb1\x89\xa9\x89i\x9a\xa9ir\x9a\x89q\xaa\x89\xa1\xa5\x85q\x9ai\x8aI\xb2\xa5\x89\xa9Y\x99q\xae\xbe{\x95\xb1\x7f@TUh\x92i\xb8\xbb\x85\x8f\x91G\x98~Y\xa6eR\x99S\x81\xa3\x87y\xaaaDibja\x96\x8fQ\xba-\x17\x00"

    def fake_deflate_decompress(data):
        if data == mock_exptected:
            return b"wrong-output"
        return real_deflate_decompress(data)

    return mocker.patch(
        "krux.bbqr.deflate_decompress", side_effect=fake_deflate_decompress
    )


@pytest.fixture
def mock_zlib_code(mocker):
    return mocker.patch(
        "krux.bbqr.deflate_decompress", side_effect=lambda _: b"wrong-output"
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


def test_fail_multi_layer_decrypt(m5stickv, mocker, mock_multi_layer_decrypt):
    """Directly test multi_layer_decrypt() hitting the except block"""
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # assert that kef.Cipher.decrypt was called
    decrypt = mock_multi_layer_decrypt
    assert decrypt.call_count > 0

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 75%\nfailed: 1/4", info_box=True
            )
        ]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_fail_hw_acc_hashing(m5stickv, mocker, mock_hw_acc_hashing):
    """Directly test hw_acc_hashing() hmac hitting the except block"""
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
    f_hash, f_hmac = mock_hw_acc_hashing
    assert f_hash.call_count > 0
    assert f_hmac.call_count > 0

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 50%\nfailed: 2/4", info_box=True
            )
        ]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_fail_sha256(m5stickv, mocker, mock_hashlib_sha256):
    """Directly test hw_acc_hashing() sha256 hitting the except block"""
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
    mock_hashlib_sha256.assert_has_calls(
        [
            mocker.call(b""),
        ]
    )

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 75%\nfailed: 1/4", info_box=True
            )
        ]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_fail_hexilify(m5stickv, mocker, mock_hexlify_endianess):
    """Directly test hexilify function"""
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
    mock_hexlify_endianess.assert_has_calls(
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
                "Test Suite Results\nsuccess rate: 75%\nfailed: 1/4", info_box=True
            )
        ]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_fail_b2a_base64(m5stickv, mocker, mock_b2a_base64_endianess):
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
    mock_b2a_base64_endianess.assert_has_calls(
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
                "Test Suite Results\nsuccess rate: 75%\nfailed: 1/4", info_box=True
            )
        ]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_fail_deflate_compression(m5stickv, mocker, mock_deflate):
    """Directly test deflate compression and decompression hitting the except block"""
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # assert that the deflate_compress and deflate_decompress were called
    deflate_compress, deflate_decompress = mock_deflate
    deflate_compress.assert_has_calls(
        [
            mocker.call(
                b"\xe3\xb0\xc4B\x98\xfc\x1c\x14\x9a\xfb\xf4\xc8\x99o\xb9$'\xaeA\xe4d\x9b\x93L\xa4\x95\x99\x1bxR\xb8U5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456v3m/Gz3OPZzUb5WG8L2HV/vi9bvBpAH7e1XuaeqjL2g=\n"
            )
        ]
    )

    deflate_decompress.assert_has_calls(
        [
            mocker.call(
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            )
        ]
    )

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 75%\nfailed: 1/4", info_box=True
            )
        ]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_fail_maixpy_code(m5stickv, mocker, mock_maixpy_code):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (BUTTON_PAGE_PREV, BUTTON_ENTER)
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # assert that the deflate_decompress were called
    mock_maixpy_code.assert_has_calls(
        [
            mocker.call(
                b"{\xbc\xe1\x88\xd3\x8c?2\"\xb3~\x7f913\x7f\xa7\x8a\xfa:\xc7')\xb3'\xfb,\x99:S\xba\"hG\xa8iJ\x9aY\xaaA\xaa\x91\xb9\x99\xa1\xb1\xa9e\x8a\xb1A\xa2\x85\x91\xb9\xa9\x81\xa9E\xaa\x91\xa5eZr\xb2\x81\xb1\x85\xa1\xa9\xb1\x89\xa9\x89i\x9a\xa9ir\x9a\x89q\xaa\x89\xa1\xa5\x85q\x9ai\x8aI\xb2\xa5\x89\xa9Y\x99q\xae\xbe{\x95\xb1\x7f@TUh\x92i\xb8\xbb\x85\x8f\x91G\x98~Y\xa6eR\x99S\x81\xa3\x87y\xaaaDibja\x96\x8fQ\xba-\x17\x00"
            ),
        ]
    )

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 75%\nfailed: 1/4", info_box=True
            )
        ]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_fail_zlib_code(m5stickv, mocker, mock_zlib_code):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (BUTTON_PAGE_PREV, BUTTON_ENTER)
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.test_suite()

    # assert that the deflate_decompress were called
    mock_zlib_code.assert_has_calls(
        [
            mocker.call(
                b"\x01\x8d\x00r\xff\xe3\xb0\xc4B\x98\xfc\x1c\x14\x9a\xfb\xf4\xc8\x99o\xb9$'\xaeA\xe4d\x9b\x93L\xa4\x95\x99\x1bxR\xb8U5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456v3m/Gz3OPZzUb5WG8L2HV/vi9bvBpAH7e1XuaeqjL2g=\n",
            ),
        ]
    )

    # assert that the test suite results are displayed correctly
    # and that the on-device-test failed
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 75%\nfailed: 1/4", info_box=True
            )
        ]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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

    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [mocker.call("Test Suite Results\nsuccess rate: 100%", info_box=True)]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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

    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [mocker.call("Test Suite Results\nsuccess rate: 100%", info_box=True)]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_run_intreactively(m5stickv, mocker):
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
    page.test_suite(interactive=True)

    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [mocker.call("Test Suite Results\nsuccess rate: 100%", info_box=True)]
    )

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_run_one_test_multi_layer_decrypt(m5stickv, mocker):
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
    page.results = [(page.multi_layer_decrypt, False)]
    page.run_one_test(page.multi_layer_decrypt)
    assert page.results == [(page.multi_layer_decrypt, True)]

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


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

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_test_touch(mocker, amigo):
    from krux.pages.device_tests import DeviceTests
    from krux.buttons import PRESSED

    ctx = create_ctx(mocker, [])
    ctx.input.touch.release_point = (1, 1)
    ctx.input.touch_value = mocker.MagicMock(side_effect=[PRESSED, None])
    ctx.input.page_value = mocker.MagicMock(side_effect=[PRESSED, None])
    DeviceTests(ctx).test_touch()

    ctx.display.fill_rectangle.assert_called()
    ctx.input.wait_for_release.assert_called()
    assert ctx.input.touch.gesture == None

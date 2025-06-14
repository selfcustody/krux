import pytest
from unittest.mock import patch
from . import create_ctx


def test_printer_test_tool(amigo, mocker):
    """Test that the print tool is called with the correct text"""
    from krux.pages.device_tests import DeviceTests
    from krux.themes import theme
    from krux.input import BUTTON_ENTER

    BTN_SEQUENCE = [BUTTON_ENTER]  # Confirm print, then leave

    with patch("krux.pages.utils.Utils.print_standard_qr") as mocked_print_qr:
        ctx = create_ctx(mocker, BTN_SEQUENCE)
        test_tools = DeviceTests(ctx)
        test_tools.print_test()

        mocked_print_qr.assert_called_with(
            "Krux Printer Test QR", title="Krux Printer Test QR", check_printer=False
        )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_skip_all_tests(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )
    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    result = page.run()


def test_run_test_suite_only(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

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

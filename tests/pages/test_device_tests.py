import pytest
from . import create_ctx


def test_skip_run_test_suite(m5stickv, mocker):
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
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV

    BTN_SEQUENCE = (
        BUTTON_ENTER,  # go test-suite
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.run()

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
        BUTTON_ENTER,  # go test-suite
        BUTTON_PAGE,  # select a unit test
        BUTTON_ENTER,  # run the unit test
        BUTTON_PAGE,  # fulfill wait-for-button
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
        BUTTON_PAGE_PREV,  # select back
        BUTTON_ENTER,  # go back
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.run()

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

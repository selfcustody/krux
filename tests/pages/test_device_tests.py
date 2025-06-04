import pytest
from . import create_ctx


def test_skip_run_test_suite(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    BTN_SEQUENCE = ([BUTTON_PAGE], [BUTTON_ENTER])  # select Back  # go Back

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.run_test_suite()


def test_run_test_suite(m5stickv, mocker):
    from krux.pages.device_tests import DeviceTests
    from krux.input import BUTTON_ENTER, BUTTON_PAGE

    BTN_SEQUENCE = (
        [BUTTON_ENTER],  # go Test-Suite
        [BUTTON_ENTER],  # hit button after test-suite results
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    page = DeviceTests(ctx)
    page.run_test_suite()

    # while prototyping: run_test_suite() purposely fails 4 of 7 tests
    # page.ctx.display.draw_hcentered_text.assert_has_calls([mocker.call(
    #    "Test Suite Results\nsuccess rate: 100%", info_box=True
    # )])
    page.ctx.display.draw_hcentered_text.assert_has_calls(
        [
            mocker.call(
                "Test Suite Results\nsuccess rate: 42%\nfailed: 4/7", info_box=True
            )
        ]
    )

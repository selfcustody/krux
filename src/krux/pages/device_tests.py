# The MIT License (MIT)

# Copyright (c) 2021-2025 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from . import Page, Menu
from ..display import DEFAULT_PADDING, FONT_HEIGHT, FONT_WIDTH
from ..krux_settings import t


class DeviceTests(Page):
    """On-Device test-suite"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Test Suite"), self.run_test_suite),
                ],
            ),
        )

    def run_test_suite(self):
        """run each on-device tests in all_tests, report summary and details"""
        # on-device test methods:
        # * small/simple/effective as possible for smallest firmware,
        # * complete quickly, else consider feeding the watchdog
        # * return something True on success
        # * return False/empty/None/Exception on failure
        all_tests = [
            # all below are prototyping/pseudo-tests
            self.test_success,
            self.test_non_empty,
            self.test_long_named_test_function,
            self.test_exception,  # failure
            self.test_false,  # failure
            self.test_empty,  # failure
            self.test_none,  # failure
        ]

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing.."))

        # run tests, gather results
        failures, total = 0, 0
        results = []
        for test in all_tests:
            try:
                result = test()
                results.append((test.__name__, bool(result)))
                if not result:
                    failures += 1
            except Exception:
                results.append((test.__name__, False))
                failures += 1
            total += 1

        # info_box summary
        self.ctx.display.clear()
        num_lines = self.ctx.display.draw_hcentered_text(
            "\n".join(
                [
                    x
                    for x in [
                        t("Test Suite Results"),
                        t("success rate:")
                        + " {}%".format(int((total - failures) / total * 100)),
                        (
                            t("failed:") + " {}/{}".format(failures, total)
                            if failures
                            else None
                        ),
                    ]
                    if x is not None
                ]
            ),
            info_box=True,
        )

        # details
        columns = (self.ctx.display.width() - DEFAULT_PADDING * 2) // FONT_WIDTH
        line_fmt = "{:" + str(columns - 3) + "s} {:>2s}"
        self.ctx.display.draw_hcentered_text(
            "\n".join(
                [
                    line_fmt.format(x[0][: columns - 3], "ok" if x[1] else "X")
                    for x in results
                ]
            ),
            offset_y=(num_lines + 1) * FONT_HEIGHT,
        )
        self.ctx.input.wait_for_button()

    # all below are prototyping/pseudo-tests
    # pylint: disable=C0116
    def test_success(self):
        return True

    def test_non_empty(self):
        return "it worked"

    def test_exception(self):
        raise ValueError("ValueError raised")

    def test_false(self):
        return False

    def test_empty(self):
        return []

    def test_none(self):
        pass

    def test_long_named_test_function(self):
        return True

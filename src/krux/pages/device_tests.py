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
from ..wdt import wdt


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
        all_tests = [
            self.hw_acc_hashing,
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
        chars_per_line = (self.ctx.display.width() - DEFAULT_PADDING * 2) // FONT_WIDTH

        # run tests, gather results
        failures = 0
        results = []
        for idx, test in enumerate(all_tests):
            self.ctx.display.draw_centered_text(" " * chars_per_line)  #
            self.ctx.display.draw_centered_text(
                t("Processing..") + " {}/{}".format(idx + 1, len(all_tests))
            )
            try:
                assert test()
                results.append((test.__name__, True))
            except Exception as err:
                print(
                    "DeviceTests.run_test_suite: {} failed: {}".format(
                        test.__name__, err
                    )
                )
                results.append((test.__name__, False))
                failures += 1

            wdt.feed()

        # info_box summary
        self.ctx.display.clear()
        num_lines = self.ctx.display.draw_hcentered_text(
            "\n".join(
                [
                    x
                    for x in [
                        t("Test Suite Results"),
                        t("success rate:")
                        + " {}%".format(int((idx + 1 - failures) / (idx + 1) * 100)),
                        (
                            t("failed:") + " {}/{}".format(failures, idx + 1)
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
        line_fmt = "{:" + str(chars_per_line - 3) + "s} {:>2s}"
        self.ctx.display.draw_hcentered_text(
            "\n".join(
                [
                    line_fmt.format(x[0][: chars_per_line - 3], "ok" if x[1] else "X")
                    for x in results
                ]
            ),
            offset_y=(num_lines + 1) * FONT_HEIGHT,
        )
        self.ctx.input.wait_for_button()

    # on-device unit-test methods:
    # * small/simple/effective as possible for smallest firmware,
    # * complete quickly, else consider feeding the watchdog
    # * return something True on success
    # * return False/empty/None/Exception on failure

    def hw_acc_hashing(self):
        """churns nonce through sha256() and pbkdf_hmac(sha256,) calls, asserts expected results"""
        from uhashlib_hw import sha256 as f_hash
        from uhashlib_hw import pbkdf2_hmac_sha256 as f_hmac

        # pylint: disable=C0301
        expecteds = [
            b"\xaaj\xc2\xd4\x96\x18\x82\xf4*4\\v\x15\xf4\x13=\xde\x8emn|\x1bk@\xaeO\xf6\xeeR\xc3\x93\xd0",
            b"\x9e?wG\xe9\rI\xac\xb3\n\xceZt7\xce\xa8\xf6\xe5\xa6\xfe\xa2H\xaa\xf2_\x16Y\xcc\x9a$\xe0\x80",
            b'\xdc\xee\x1fc\xa0\x17\x85\xffda\xd8{\xc91\xd0\xab:\\\x9d@\xec\xc96s\xf0\xc5\xe8"r\x8b\xf1^',
            b'\xdc\xee\x1fc\xa0\x17\x85\xffda\xd8{\xc91\xd0\xab:\\\x9d@\xec\xc96s\xf0\xc5\xe8"r\x8b\xf1^',
            b'\x1fdFbl\x13\xe6\x93\xfb\xd1\x13\xacj\xf5\x9f"<\xf1\xa2@\x168\x04=\x95<`i\xb3\xcc\x7f\x98',
            b"\x1d\x98\xdc\x98\x9f\xda\x91=\xd3\xefC\xc3_\xd4qivyU\x84\x11K\xe5s+\xa8\xbc\x97\x83\x00Y\xd1",
        ]

        hashes = []
        nonce = b""
        for i in range(32):
            nonce = f_hash(nonce).digest()
            hashes.append(nonce)

            nonce = f_hash(nonce[-i:]).digest()
            hashes.append(nonce)

            nonce = f_hash(nonce * (i + 1)).digest()
            hashes.append(nonce)

            # short password and salt
            nonce = f_hmac(nonce[-i:], nonce[:-i], (i + 1) * 2)
            hashes.append(nonce)

            # long password
            nonce = f_hmac(nonce * (i + 1), nonce, (i + 1) * 4)
            hashes.append(nonce)

            # long salt (clipped at 1024)
            nonce = f_hmac(nonce, (nonce * (i + 1))[:1024], (i + 1) * 8)
            hashes.append(nonce)
        nonce = f_hash(b"".join(hashes)).digest()

        calculateds = [
            # 3rd churned digest is solely from sha256
            hashes[2],
            # last nonce is sha256 of contatenated hashes from all sha256/hmac churns above
            nonce,
            # long_password == sha256(long_password), next two tests prove this
            f_hmac(b"".join(hashes), nonce, 16),
            f_hmac(f_hash(b"".join(hashes)).digest(), nonce, 16),
            # a long salt is not treated like a long password, next two tests prove this
            f_hmac(nonce, b"".join(hashes)[:1024], 32),
            f_hmac(nonce, f_hash(b"".join(hashes)[:1024]).digest(), 32),
        ]

        err = ""
        for i, (expected, calculated) in enumerate(zip(expecteds, calculateds)):
            try:
                assert expected == calculated
            except:
                err += "\nTest case: {}\n   expected: {}\n calculated: {}".format(
                    i, repr(expected), repr(calculated)
                )
        if err:
            raise AssertionError(err)

        return True

    # next 7 tests below are prototyping/pseudo-tests -- these will be removed
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

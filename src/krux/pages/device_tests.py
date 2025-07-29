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

from . import Page, Menu, MENU_CONTINUE
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
                    (t("Print Test QR"), self.print_test),
                    (t("Test Suite"), self.test_suite),
                ],
            ),
        )
        self.results = []

    def print_test(self):
        """Handler for the 'Print Test QR' menu item"""
        title = t("Krux Printer Test QR")
        self.display_qr_codes(title, title=title)

        from .utils import Utils

        utils = Utils(self.ctx)
        utils.print_standard_qr(title, title=title, check_printer=False)
        return MENU_CONTINUE

    # pylint: disable=W0613
    def test_suite(self, interactive=False):
        """run each on-device tests in all_tests, report summary and details"""
        all_tests = [
            self.hw_acc_hashing,
            self.deflate_compression,
            self.touch_gestures,
            # # all below are prototyping/pseudo-tests
            # self.test_success,
            # self.test_non_empty,
            # self.test_long_named_test_function,
            # (self.test_interactive, interactive),  # interactive test
            # self.test_exception,  # failure
            # self.test_false,  # failure
            # self.test_empty,  # failure
            # self.test_none,  # failure
        ]

        self.ctx.display.clear()
        chars_per_line = (self.ctx.display.width() - DEFAULT_PADDING * 2) // FONT_WIDTH

        # if no previous results, run tests, gather results
        if len(self.results) == 0:
            for idx, test in enumerate(all_tests):
                self.ctx.display.draw_centered_text(" " * chars_per_line)  #
                self.ctx.display.draw_centered_text(
                    t("Processing..") + " {}/{}".format(idx + 1, len(all_tests))
                )

                test_name = test.__name__ if callable(test) else test[0].__name__
                try:
                    if not callable(test):
                        test_fn = test[0]
                        args = test[1 : len(test)]
                        if not test_fn(*args):
                            raise ValueError
                        self.results.append((test_fn, True))
                    else:
                        if not test():
                            raise ValueError
                        self.results.append((test, True))
                except Exception as err:
                    print(
                        "DeviceTests.run_test_suite: {} failed: {}".format(
                            test_name, err
                        )
                    )
                    self.results.append((test, False))
                wdt.feed()

        # info_box summary
        self.ctx.display.clear()
        failures = len([x for x in self.results if not x[1]])
        total = len(self.results)
        num_lines = self.ctx.display.draw_hcentered_text(
            "\n".join(
                [
                    x
                    for x in [
                        t("Test Suite Results"),
                        t("success rate:")
                        + " {}%".format(int((total - failures) / (total) * 100)),
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

        # results menu
        line_fmt = "{:" + str(chars_per_line - 3) + "s} {:>2s}"
        results_menu = Menu(
            self.ctx,
            [
                (
                    line_fmt.format(
                        (
                            x[0][0].__name__
                            if isinstance(x[0], tuple)
                            else x[0].__name__
                        )[: chars_per_line - 3],
                        "ok" if x[1] else "X",
                    ),
                    lambda: None,
                )
                for x in self.results
            ],
            offset=(num_lines + 1) * FONT_HEIGHT,
        )
        idx, _ = results_menu.run_loop()
        if idx == len(self.results):
            return MENU_CONTINUE
        return self.run_one_test(self.results[idx][0])

    def run_one_test(self, test):
        """run a single test w/ interactive=True, display success/fail and results"""

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing..") + " " + test.__name__)
        success = False
        try:
            result = test(interactive=True)
            success = bool(result)
        except Exception as err:
            result = err
        idx = [i for i, (t, r) in enumerate(self.results) if t == test][0]
        self.results[idx] = (test, success)

        self.ctx.display.clear()

        # info_box summary
        self.ctx.display.clear()
        num_lines = self.ctx.display.draw_hcentered_text(
            "\n".join(
                [
                    t("Test:") + " " + test.__name__,
                    t("Result")
                    + " ({}): {}".format(
                        type(result).__name__, "pass" if success else "fail"
                    ),
                ]
            ),
            info_box=True,
        )

        # output of result
        self.ctx.display.draw_hcentered_text(
            result if isinstance(result, str) else repr(result),
            offset_y=(num_lines + 1) * FONT_HEIGHT,
        )
        self.ctx.input.wait_for_button()
        return self.test_suite()

    # pylint: disable=W0613

    # On-Device Unit-Test Methods:
    # * small/simple/effective as possible for smallest firmware,
    # * complete quickly, else consider feeding the watchdog
    # * accept an optional "interactive" parameter;
    #   using interative=False by default to disable user interaction for test-suite
    #   or interactive=True to enable user interaction during single tests
    # * return something True on success
    # * return False/empty/None/Exception on failure

    def hw_acc_hashing(self, interactive=False):
        """
        churns nonce through sha256() and pbkdf_hmac(sha256,) calls,
        raises ValueError if calculated results don't match expected results
        """
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

        results = []
        err = ""
        for i, (expected, calculated) in enumerate(zip(expecteds, calculateds)):
            try:
                if expected != calculated:
                    raise ValueError("test failed")
                results.append("test case {}: ok".format(i))
            except:
                err += "\nTest case: {}\n   expected: {}\n calculated: {}".format(
                    i, repr(expected), repr(calculated)
                )
        if err:
            raise AssertionError(err)

        return "\n\n".join(results)

    def deflate_compression(self, interactive=False):
        """test deflate compression between MaixPy and python3:zlib"""
        from ..bbqr import deflate_compress, deflate_decompress
        from binascii import hexlify, b2a_base64
        from hashlib import sha256

        # pylint: disable=C0301
        expecteds = {
            "length": 141,
            "sha256": b"\xcd\x87y\xd8\x0c\x1e]:\xcc\xdb@ Bc\xb4E\xbf\xe2\xbc\x04[\xf0\x8a_d\xd5\t]\xab\t\xb7\x0c",
            "MaixPy:deflate": b"{\xbc\xe1\x88\xd3\x8c?2\"\xb3~\x7f913\x7f\xa7\x8a\xfa:\xc7')\xb3'\xfb,\x99:S\xba\"hG\xa8iJ\x9aY\xaaA\xaa\x91\xb9\x99\xa1\xb1\xa9e\x8a\xb1A\xa2\x85\x91\xb9\xa9\x81\xa9E\xaa\x91\xa5eZr\xb2\x81\xb1\x85\xa1\xa9\xb1\x89\xa9\x89i\x9a\xa9ir\x9a\x89q\xaa\x89\xa1\xa5\x85q\x9ai\x8aI\xb2\xa5\x89\xa9Y\x99q\xae\xbe{\x95\xb1\x7f@TUh\x92i\xb8\xbb\x85\x8f\x91G\x98~Y\xa6eR\x99S\x81\xa3\x87y\xaaaDibja\x96\x8fQ\xba-\x17\x00",
            "python3-zlib:v1.2.11-v1.3": b"\x01\x8d\x00r\xff\xe3\xb0\xc4B\x98\xfc\x1c\x14\x9a\xfb\xf4\xc8\x99o\xb9$'\xaeA\xe4d\x9b\x93L\xa4\x95\x99\x1bxR\xb8U5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456v3m/Gz3OPZzUb5WG8L2HV/vi9bvBpAH7e1XuaeqjL2g=\n",
        }

        uncompressed = sha256(b"").digest()
        uncompressed += hexlify(sha256(uncompressed).digest())
        uncompressed += b2a_base64(sha256(uncompressed).digest())
        uncompressed_length = len(uncompressed)
        uncompressed_sha256 = sha256(uncompressed).digest()

        results = []
        if (
            uncompressed_length != expecteds["length"]
            or uncompressed_sha256 != expecteds["sha256"]
        ):
            raise AssertionError("failed to generate uncompressed control")

        if deflate_decompress(deflate_compress(uncompressed)) != uncompressed:
            raise AssertionError("failed to compress and decompress control")
        results.append("local compression: ok")

        for src in [k for k in expecteds if k not in ("length", "sha256")]:
            if deflate_decompress(expecteds[src]) != uncompressed:
                raise AssertionError("failed to decompress control from {}".format(src))
            results.append("{} decompress: ok".format(src))
        return "\n\n".join(results)

    def touch_gestures(self, interactive=False):
        """test touchscreen gestures interactively -- if available"""
        from krux.input import (
            BUTTON_TOUCH,
            SWIPE_RIGHT,
            SWIPE_LEFT,
            SWIPE_UP,
            SWIPE_DOWN,
        )

        tests = (
            ("Touch screen", BUTTON_TOUCH),
            ("Swipe right", SWIPE_RIGHT),
            ("Swipe left", SWIPE_LEFT),
            ("Swipe up", SWIPE_UP),
            ("Swipe down", SWIPE_DOWN),
        )

        if not interactive:
            return "Cannot test non-interactively"

        if self.ctx.input.touch is None:
            return "Touch not available"

        results = []
        for i, test in enumerate(tests):
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                "{}/{}: {}".format(i + 1, len(tests), test[0])
            )
            btn = self.ctx.input.wait_for_button()
            results.append((test[0], test[1] == btn))

        failures = [test for test, res in results if not res]
        if failures:
            raise ValueError("failed: {}".format(failures))

        return True

    # # next 8 tests below are prototyping/pseudo-tests
    # # pylint: disable=C0116
    # def test_success(self, interactive=False):
    #     return True

    # def test_non_empty(self, interactive=False):
    #     return "it worked"

    # def test_exception(self, interactive=False):
    #     raise ValueError("ValueError raised")

    # def test_false(self, interactive=False):
    #     return False

    # def test_empty(self, interactive=False):
    #     return []

    # def test_none(self, interactive=False):
    #     pass

    # def test_long_named_test_function(self, interactive=False):
    #     return True

    # def test_interactive(self, interactive=False):
    #     from ..display import BOTTOM_PROMPT_LINE
    #     if not interactive:
    #         return "Cannot test non-interactively"
    #     return self.prompt(
    #         "Printer go Brrr...\nSeparate money and state?", BOTTOM_PROMPT_LINE
    #     )

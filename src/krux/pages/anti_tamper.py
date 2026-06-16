# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

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
from ..krux_settings import t, Settings
from ..display import FONT_HEIGHT, DEFAULT_PADDING
from ..themes import theme
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
)

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MS = 300000


class AntiTamper(Page):
    """Anti-tamper display and security status"""

    def __init__(self, ctx):
        super().__init__(ctx)
        self.failed_attempts = 0

    def show_tamper_warning(self, reason=""):
        """Display a prominent tamper warning screen"""
        self.ctx.display.clear()
        color = theme.error_color

        self.ctx.display.draw_centered_text(
            "⚠ " + t("TAMPER DETECTED") + " ⚠",
            color=color,
        )

        y = self.ctx.display.height() // 3
        if reason:
            self.ctx.display.draw_hcentered_text(
                reason, offset_y=y, color=color
            )
            y += 2 * FONT_HEIGHT

        self.ctx.display.draw_hcentered_text(
            t("Device may have been tampered with"),
            offset_y=y,
        )
        y += 2 * FONT_HEIGHT

        self.ctx.display.draw_hcentered_text(
            t("Check TC Flash Hash"),
            offset_y=y,
        )

        self.ctx.input.wait_for_button()

    def show_security_status(self):
        """Display current security status"""
        settings = Settings()
        tc_code_set = False
        boot_hash_enabled = False

        try:
            from ..krux_settings import TC_CODE_PATH
            import os

            tc_code_set = os.path.exists(TC_CODE_PATH)
        except Exception:
            pass

        boot_hash_enabled = settings.security.boot_flash_hash

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Security Status"))

        y = self.ctx.display.height() // 3
        status_items = []

        if tc_code_set:
            status_items.append(
                (t("TC Code") + ": " + t("Enabled"), theme.highlight_color)
            )
        else:
            status_items.append(
                (t("TC Code") + ": " + t("Disabled"), theme.error_color)
            )

        if boot_hash_enabled:
            status_items.append(
                (t("Boot Hash") + ": " + t("Enabled"), theme.highlight_color)
            )
        else:
            status_items.append(
                (t("Boot Hash") + ": " + t("Disabled"), theme.error_color)
            )

        auto_shutdown = settings.security.auto_shutdown
        if auto_shutdown > 0:
            status_items.append(
                (t("Auto Shutdown") + ": %dm" % auto_shutdown,
                 theme.highlight_color)
            )
        else:
            status_items.append(
                (t("Auto Shutdown") + ": " + t("Disabled"),
                 theme.fg_color)
            )

        for text, color in status_items:
            self.ctx.display.draw_hcentered_text(text, offset_y=y, color=color)
            y += 2 * FONT_HEIGHT

        self.ctx.input.wait_for_button()

    def check_failed_attempts(self):
        """Check if too many failed attempts have occurred"""
        if self.failed_attempts >= MAX_FAILED_ATTEMPTS:
            self.show_tamper_warning(
                t("Too many failed attempts") + ": %d/%d"
                % (self.failed_attempts, MAX_FAILED_ATTEMPTS)
            )
            self.failed_attempts = 0
            return True
        return False

    def record_failed_attempt(self):
        """Record a failed verification attempt"""
        self.failed_attempts += 1
        if self.failed_attempts >= MAX_FAILED_ATTEMPTS:
            self.show_tamper_warning(
                t("Too many failed attempts") + ": %d/%d"
                % (self.failed_attempts, MAX_FAILED_ATTEMPTS)
            )
            self.failed_attempts = 0

    def security_menu(self):
        """Security settings and status menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Security Status"), self.show_security_status),
                (t("TC Flash Hash"), self._show_flash_hash),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def _show_flash_hash(self):
        """Show TC Flash Hash verification"""
        from ..flash_tools import FlashHash

        flash_hash = FlashHash(self.ctx)
        flash_hash.export()
        return MENU_CONTINUE

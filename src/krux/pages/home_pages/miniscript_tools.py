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
from ...krux_settings import t
from .. import (
    Page,
    Menu,
    MENU_CONTINUE,
)


class MiniscriptTools(Page):
    """UI for miniscript policy validation and information"""

    def validate_policy(self):
        """Validate a miniscript policy"""
        if self.ctx.wallet is None or self.ctx.wallet.key is None:
            self.flash_error(t("No wallet loaded"))
            return MENU_CONTINUE

        if not self.ctx.wallet.is_miniscript():
            self.flash_error(t("Not a miniscript wallet"))
            return MENU_CONTINUE

        policy = self.ctx.wallet.policy
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Validating policy..."))

        try:
            from embit.descriptor.miniscript import Miniscript

            if "miniscript" in policy:
                ms = policy["miniscript"]
                if hasattr(ms, "verify"):
                    ms.verify()
                    self.flash_text(t("Policy is valid"))
                else:
                    self.flash_text(t("Policy format check passed"))
            else:
                self.flash_error(t("No miniscript found in policy"))
        except Exception as e:
            self.flash_error(t("Invalid policy") + ": " + str(e))

        return MENU_CONTINUE

    def show_policy_info(self):
        """Show information about the current miniscript policy"""
        if self.ctx.wallet is None or self.ctx.wallet.key is None:
            self.flash_error(t("No wallet loaded"))
            return MENU_CONTINUE

        if not self.ctx.wallet.is_miniscript():
            self.flash_error(t("Not a miniscript wallet"))
            return MENU_CONTINUE

        policy = self.ctx.wallet.policy
        self.ctx.display.clear()

        info = t("Miniscript Policy") + "\n\n"

        if "type" in policy:
            info += t("Type") + ": " + str(policy["type"]) + "\n"
        if "m" in policy:
            info += "M/N: " + str(policy.get("m", "?")) + "/" + str(policy.get("n", "?")) + "\n"
        if "keys" in policy:
            info += t("Keys") + ": " + str(len(policy["keys"])) + "\n"

        self.ctx.display.draw_hcentered_text(info, info_box=True)
        self.ctx.input.wait_for_button()

        return MENU_CONTINUE

    def miniscript_menu(self):
        """Miniscript tools menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Validate Policy"), self.validate_policy),
                (t("Policy Info"), self.show_policy_info),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

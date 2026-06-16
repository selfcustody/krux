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
from ..krux_settings import t
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
)


class PSBTv2Tools(Page):
    """UI for PSBTv2 information and tools"""

    def show_psbt_info(self):
        """Show information about the current PSBT"""
        if self.ctx.wallet is None:
            self.flash_error(t("No wallet loaded"))
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("PSBT Information"))

        info = ""
        if hasattr(self.ctx.wallet, "policy"):
            policy = self.ctx.wallet.policy
            if policy:
                info += t("Policy") + ": " + str(policy.get("type", "?")) + "\n"

        if hasattr(self.ctx.wallet.key, "network"):
            info += t("Network") + ": " + self.ctx.wallet.key.network + "\n"

        if info:
            self.ctx.display.draw_hcentered_text(info, info_box=True)

        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def psbtv2_menu(self):
        """PSBTv2 tools menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("PSBT Info"), self.show_psbt_info),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

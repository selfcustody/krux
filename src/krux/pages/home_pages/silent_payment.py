from ...display import FONT_HEIGHT, DEFAULT_PADDING
from ...krux_settings import t
from .. import (
    Menu,
    Page,
    MENU_CONTINUE,
)


class SilentPayment(Page):
    """UI for BIP-352 Silent Payment address generation"""

    def export(self):
        """Main entry point: show silent payment options menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("SP Address"), self._generate_address),
                (t("SP Address with Label"), self._generate_labeled_address),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def _generate_address(self):
        """Generate and display a silent payment address without label"""
        return self._show_sp_address(label=None)

    def _generate_labeled_address(self):
        """Prompt user for a numeric label, then generate address"""
        from ..utils import Utils

        utils = Utils(self.ctx)
        label = ""

        while label == "":
            label = utils.capture_index_from_keypad(t("Label"))
        if label is None:
            return MENU_CONTINUE
        return self._show_sp_address(label=label)

    def _show_sp_address(self, label=None):
        """Derive and display the silent payment address"""
        from ...silent_payment import (
            derive_bip352_key,
            encode_silent_payment_address,
        )

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing…"))

        root = self.ctx.wallet.key.root
        network = self.ctx.wallet.key.network

        # Determine network name for address HRP (coin_type 0 = mainnet)
        embit_network = "main" if network.get("bip32") == 0 else "test"

        scan_hd = derive_bip352_key(root, network, is_scan_key=True)
        spend_hd = derive_bip352_key(root, network, is_scan_key=False)

        scan_privkey = scan_hd.key
        spend_pubkey = spend_hd.key.get_public_key()

        sp_address = encode_silent_payment_address(
            scan_privkey, spend_pubkey, label=label, network=embit_network
        )

        info = t("Silent Payment Address")
        info += (
            "\n\n" + t("Label") + ": " + str(label)
            if label is not None
            else ""
        )
        info += "\n\n" + sp_address

        while True:
            menu_items = [
                (
                    t("QR Code"),
                    lambda: self._show_qr(sp_address),
                ),
            ]
            self.ctx.display.clear()
            info_len = self.ctx.display.draw_hcentered_text(info)
            info_len = info_len * FONT_HEIGHT + DEFAULT_PADDING
            submenu = Menu(
                self.ctx,
                menu_items,
                offset=info_len,
            )
            index, _ = submenu.run_loop()
            if index == submenu.back_index:
                break
        return MENU_CONTINUE

    def _show_qr(self, sp_address):
        """Display the silent payment address as a QR code"""
        self.display_qr_codes(data=sp_address)

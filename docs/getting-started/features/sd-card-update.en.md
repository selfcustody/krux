### Upgrade via microSD card
Once you've installed Krux firmware on your device via USB, you can either continue updating the device via USB or you can perform upgrades via microSD card to keep the device airgapped.

<img src="../../../img/maixpy_m5stickv/firmware-update-250.png" align="right" class="m5stickv">
<img src="../../../img/maixpy_amigo/firmware-update-300.png" align="right" class="amigo">

To perform an upgrade, simply copy the [official release](https://github.com/selfcustody/krux/releases) `firmware.bin` and `firmware.bin.sig` files to the root of a FAT32 MBR formatted microSD card, insert the card into your device, and reboot the device. If it detects the new firmware file and is able to verify the signature, you will be prompted to install it. Only official releases are signed.

Once installation is complete, you will be prompted to remove firmware files from the SD Card, if you do not remove it, upon reboot you will be prompted to install it again.

----8<----
sd-card-info-faq.en.txt
----8<----

<div style="clear: both"></div>

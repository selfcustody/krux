### Upgrade via microSD card
Once you've installed the initial firmware on your device via USB, you can either continue updating the device by flashing or you can perform upgrades via microSD card to keep the device airgapped.

To perform an upgrade, simply copy the `firmware.bin` and `firmware.bin.sig` files to the root of a FAT-32(MBR) formatted microSD card, insert the card into your device, and reboot the device. If it detects the new firmware file and is able to verify the signature, you will be prompted to install it.

Once installation is complete, eject the microSD card and delete the firmware files before reinserting and rebooting.
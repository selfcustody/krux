### Upgrade via microSD card
Once you've installed the initial firmware on your device via USB, you can either continue updating the device by flashing via USB or you can perform upgrades via microSD card to keep the device airgapped.

To perform an upgrade, simply copy the `firmware.bin` and `firmware.bin.sig` files to the root of a FAT-32(MBR) formatted microSD card, insert the card into your device, and reboot the device. If it detects the new firmware file and is able to verify the signature, you will be prompted to install it.

Once installation is complete, eject the microSD card and delete the firmware files before reinserting and rebooting. Otherwise you will be prompted to install it again.

We cannot guarantee that a microSD card is compatible and will work in your device; you'll need to test it on the device to be sure, read the [FAQ](faq.en.md/#why-isnt-krux-detecting-my-microsd-card-or-presenting-an-error) for more info.
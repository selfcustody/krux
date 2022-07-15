This page explains how to install Krux from an official, pre-built release. If you would like to build and install Krux from source, please read the [Installing from source](../installing-from-source) guide.

### Requirements
#### Hardware
You will need the M5StickV, a USB-C cable, and a computer with a USB port to continue. Consult the [part list](../../parts) for more information.

If you wish to perform airgapped firmware updates, want persistent settings, or wish to use Krux in a different language, you will also need a [supported microSD card](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md#tf-cardmicrosd-test).

### Download the latest release
Head over to the [releases](https://github.com/selfcustody/krux/releases) page and download the latest signed release.

### Verify the files
Before installing the release, it's a good idea to check that:

1. The SHA256 hash of `krux-vX.Y.Z.zip` matches the hash in `krux-vX.Y.Z.zip.sha256.txt`
2. The signature file `krux-vX.Y.Z.zip.sig` can be verified with the [`selfcustody.pem` public key](https://github.com/selfcustody/krux/blob/main/selfcustody.pem) found in the root of the krux repository.

You can either do this manually or with the `krux` shell script, which contains helper commands for this:
```bash
./krux sha256 krux-vX.Y.Z.zip
./krux verify krux-vX.Y.Z.zip selfcustody.pem
```

Fun fact: Each Krux release is signed with Krux!

### Flash the firmware onto the M5StickV
Connect the M5StickV to your computer via USB, power it on (left-side button), and run the following:
```bash
unzip krux-vX.Y.Z.zip && cd krux-vX.Y.Z
./ktool -B goE -b 1500000 maixpy_m5stickv/kboot.kfpkg
```

If `ktool` fails to run, you may need to give it executable permissions with `chmod +x ./ktool`, or in Windows or Mac explicitly allow the tool to run by adding an exception for it.

If the flashing process fails midway through, check the connection, restart the device, and try the command again.

When the flashing process completes, you should see...

<img src="../../img/logo-150.png">

If after 30 seconds you still see a black screen, try power cycling the device by holding down the power button for six seconds.

Congrats, you're now running Krux!

### Multilingual support
<img src="../../img/login-locale-de-de-150.png" align="right">

Prefer a different language? Krux has support for multiple languages, including:

- de-DE (German)
- es-MX (Spanish)
- fr-FR (French)
- vi-VN (Vietnamese)
- Are we missing one? Make a PR!

To use a translation, first copy the [`i18n/translations`](https://github.com/selfcustody/krux/tree/main/i18n/translations) folder to a `translations` folder at the root of a FAT-32 formatted microSD card, then insert the card into your M5StickV, and reboot the device. Once at the start screen, go to `Settings`, followed by `Locale`, and select the locale you wish to use. Your preference will be automatically saved to a `settings.json` file at the root of your microSD card.

### Upgrade via microSD card
Once you've installed the initial firmware on your device via USB, you can either continue updating the device by flashing or you can perform upgrades via microSD card to keep the device airgapped.

To perform an upgrade, simply copy the `firmware.bin` and `firmware.bin.sig` files to the root of a FAT-32 formatted microSD card, insert the card into your M5StickV, and reboot the device. If it detects the new firmware file and is able to verify the signature, you will be prompted to install it.

Once installation is complete, eject the microSD card and delete the firmware files before reinserting and rebooting.

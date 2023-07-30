This page explains how to install Krux from an official, pre-built release.

If command-line is not your thing and you want to install with few mouse clicks, please read [Installing from GUI](./installing-from-gui.en.md) guide.

If you would like to build and install Krux from source, please read the [Installing from source](../installing-from-source) guide.

### Requirements
#### Hardware
You will need a K210-based device such as the M5StickV, Maix Amigo, Maix Dock, or Maix Bit and a USB-C cable to continue. Consult the [part list](../../parts) for more information.

If you wish to perform airgapped firmware updates or want persistent settings, you will also need a [supported microSD card](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md#tf-cardmicrosd-test).

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

### Flash the firmware onto the device
Extract the latest version of Krux you downloaded and enter the folder:
```bash
unzip krux-vX.Y.Z.zip && cd krux-vX.Y.Z
```

Connect the device to your computer via USB, power it on, and run the following, replacing `DEVICE` with either `m5stickv`, `amigo_tft`, `amigo_ips`, or `bit`:
```bash
./ktool -B goE -b 1500000 maixpy_DEVICE/kboot.kfpkg
```

For `dock` the `-b` parameter changes, so run:
```bash
./ktool -B dan -b 1500000 maixpy_dock/kboot.kfpkg
```

If `ktool` fails to run, you may need to give it executable permissions with `chmod +x ./ktool`, or you might need to use "sudo" if your user don't have access to serial port. In Windows or Mac you may need to explicitly allow the tool to run by adding an exception for it.

If the flashing process fails midway through, check the connection, restart the device, and try the command again.

When the flashing process completes, you should see the Krux logo:

<img src="../../img/maixpy_m5stickv/logo-125.png">
<img src="../../img/maixpy_amigo_tft/logo-150.png">

If after 30 seconds you still see a black screen, try power cycling the device by holding down the power button for six seconds.

Congrats, you're now running Krux!

#### A note about the Amigo
Some Amigo screens have inverted x coordinates while others don’t.

If after flashing `maixpy_amigo_tft` to your device you notice that the buttons on keypad input screens appear to be in the wrong order, please try flashing `maixpy_amigo_ips` instead (or vice versa) which should correct the issue. 

### Multilingual support
Prefer a different language? Krux has support for multiple languages. Once at the start screen, go to `Settings`, followed by `Locale`, and select the locale you wish to use. If you have a microSD card inserted into the device, your preference will be automatically saved to a `settings.json` file at the root of the card.

### Upgrade via microSD card
Once you've installed the initial firmware on your device via USB, you can either continue updating the device by flashing or you can perform upgrades via microSD card to keep the device airgapped.

To perform an upgrade, simply copy the `firmware.bin` and `firmware.bin.sig` files to the root of a FAT-32 formatted microSD card, insert the card into your device, and reboot the device. If it detects the new firmware file and is able to verify the signature, you will be prompted to install it.

Once installation is complete, eject the microSD card and delete the firmware files before reinserting and rebooting.

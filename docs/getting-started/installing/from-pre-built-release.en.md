This page explains how to install Krux from an official, pre-built release.

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

Connect the device to your computer via USB (for Amigo, make sure you’re using bottom port), power it on, and run the following, replacing `DEVICE` with either `m5stickv`, `amigo_tft`, `amigo_ips`, or `bit`:
```bash
./ktool -B goE -b 1500000 maixpy_DEVICE/kboot.kfpkg
```

For `dock` the `-b` parameter changes, so run:
```bash
./ktool -B dan -b 1500000 maixpy_dock/kboot.kfpkg
```



When the flashing process completes, you should see the Krux logo:

<img src="../../../img/maixpy_amigo_tft/logo-150.png">
<img src="../../../img/maixpy_m5stickv/logo-125.png">

If after 30 seconds you still see a black screen, try power cycling the device by holding down the power button for six seconds.

Congrats, you're now running Krux!

#### Troubleshooting
If `ktool` fails to run, you may need to give it executable permissions with `chmod +x ./ktool`, or you might need to use "sudo" if your user don't have access to serial port. In Windows or Mac you may need to explicitly allow the tool to run by adding an exception for it.

If the flashing process fails midway through, check the connection, restart the device, and try the command again.

Two serial ports are created when `Amigo` and `Bit` are connected to a PC. Sometimes Ktool will pick the wrong and flash will fail. Manually specify the serial port to overcome this issue using `-p` argument. Ex:

```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo_tft/kboot.kfpkg -p /dev/ttyUSB1
```

Check por names of devices manager on Windows (ex: COM1, COM9), or list the ports on linux

```bash
ls /dev/ttyUSB*
```

List ports on Mac

```bash
ls /dev/cu.usbserial*
```
Different OS versions may have different port names, and the absence of ports may indicate a connection, driver or hardware related issue.

#### A note about the Amigo
Some Amigo screens have inverted x coordinates while others don’t.

If after flashing `maixpy_amigo_tft` to your device you notice that the buttons on keypad input screens appear to be in the wrong order, please try flashing `maixpy_amigo_ips` instead (or vice versa) which should correct the issue. 

### Multilingual support
Prefer a different language? Krux has support for multiple languages. Once at the start screen, go to `Settings`, followed by `Locale`, and select the locale you wish to use. If you have a microSD card inserted into the device, your preference will be automatically saved to a `settings.json` file at the root of the card.

### Upgrade via microSD card
Once you've installed the initial firmware on your device via USB, you can either continue updating the device by flashing or you can perform upgrades [via microSD](../features/sd-card-update.md) card to keep the device airgapped.

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

Connect the device to your computer via USB (for Maix Amigo, make sure you’re using bottom port), power it on, and run the following, replacing `DEVICE` with either `m5stickv`, `amigo`, `bit` or `yahboom` (to yahboom you may need to manually specify the port):
```bash
./ktool -B goE -b 1500000 maixpy_DEVICE/kboot.kfpkg
```

For `dock` the `-B` parameter changes, so run:
```bash
./ktool -B dan -b 1500000 maixpy_dock/kboot.kfpkg
```

----8<----
flash-krux-logo.en.txt
----8<----

----8<----
amigo-more-info-faq.en.txt
----8<----

#### Troubleshooting
If `ktool` fails to run, you may need to give it executable permissions with `chmod +x ./ktool`, or you might need to use "sudo" if your user don't have access to serial port. In Windows or Mac you may need to explicitly allow the tool to run by adding an exception for it.

If the flashing process fails midway through, check the connection, restart the device, and try the command again.

Two serial ports are created when `Amigo` and `Bit` are connected to a PC. Sometimes Ktool will pick the wrong and flash will fail. Manually specify the serial port to overcome this issue using `-p` argument:

```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo/kboot.kfpkg -p /dev/ttyUSB1
```

Check por names of devices manager on Windows (e.g. COM1, COM9), or list the ports on linux

```bash
ls /dev/ttyUSB*
```

List ports on Mac

```bash
ls /dev/cu.usbserial*
```
Different OS versions may have different port names, and the absence of ports may indicate a connection, driver or hardware related issue. See [FAQ](../../faq.md/#why-isnt-my-device-charging-or-being-recognized-when-connected-to-the-computers-usb) for more info.

----8<----
tips-after-install.en.txt
----8<----

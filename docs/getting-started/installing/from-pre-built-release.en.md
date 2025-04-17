This page explains how to download and install Krux firmware from our official, pre-built latest release.

[<img src="../../../img/badge_github.png" width="186">](https://github.com/selfcustody/krux/releases)

### Verify the files
Before installing the release, it's a good idea to check that:

1. The *SHA256 hash* of `{{latest_krux}}.zip` matches the hash in `{{latest_krux}}.zip.sha256.txt`
2. The *signature file* `{{latest_krux}}.zip.sig` can be verified with the [`selfcustody.pem` public key](https://github.com/selfcustody/krux/blob/main/selfcustody.pem) found in the root of the krux repository.

You can either do this manually or with the `krux` shell script, which contains helper commands for this:
```bash
### Using krux script ###
# Hash checksum
./krux sha256 {{latest_krux}}.zip
# Signature
./krux verify {{latest_krux}}.zip selfcustody.pem

### Manually ###
# Hash checksum
sha256sum {{latest_krux}}.zip.sha256.txt -c
#Signature
openssl sha256 <{{latest_krux}}.zip -binary | openssl pkeyutl -verify -pubin -inkey selfcustody.pem -sigfile {{latest_krux}}.zip.sig
```

On Mac you may need to install `coreutils` to be able to use `sha256sum`
```
brew install coreutils
```

Fun fact: Each new Krux release is signed with Krux!

### Flash the firmware onto the device
Extract the latest version of Krux you downloaded and enter the folder:
```bash
unzip {{latest_krux}}.zip && cd {{latest_krux}}
```

Connect the device to your computer via USB (for Maix Amigo, make sure you’re using bottom port), power it on, and run the following, replacing `DEVICE` with either `m5stickv`, `amigo`, `bit`, `cube` or `yahboom` (to Yahboom you may need to manually specify the port, for example `/dev/ttyUSB0` on Linux or `COM6` on Windows):
```bash
./ktool -B goE -b 1500000 maixpy_DEVICE/kboot.kfpkg
```

For `dock` or `wonder_mv` use the `-B dan` parameter:
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

Two serial ports are created when `Amigo` and `Bit` are connected to a PC. Sometimes Ktool will pick the wrong port and flashing will fail. Manually specify the serial port to overcome this issue using `-p` argument:

##### Linux
See the correct port using `ls /dev/ttyUSB*`, in the example below we use `/dev/ttyUSB0`:
```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo/kboot.kfpkg -p /dev/ttyUSB1
```

##### Windows
See the correct port at **Device Manager -> Ports (COM & LPT)**, in the example below we use `COM6`:
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_amigo\kboot.kfpkg -p COM6
```

##### Mac
Remove the Gatekeeper quarantine extended attribute from ktool-mac:
```bash
xattr -d com.apple.quarantine ktool-mac
```

See the correct port using the command line: `ls /dev/cu.usbserial*`, in the example below we use `/dev/cu.usbserial-10` (If the output isn't what you expect try a different cable, preferably a smartphone usb-c charger cable):
```bash
./ktool-mac -B goE -b 1500000 maixpy_amigo/kboot.kfpkg -p /dev/cu.usbserial-10
```

Different OS versions may have different port names, and the absence of ports may indicate a connection, driver or hardware related issue. See [Troubleshooting](../../troubleshooting.md/#device-not-charging-or-being-recognized) for more info.

----8<----
tips-after-install.en.txt
----8<----

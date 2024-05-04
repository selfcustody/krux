## Troubleshooting LCD Settings on Maix Amigo
### Buttons in the Wrong Order
If the buttons on keypad input screens appear to be in the wrong order, this might be due to inverted X coordinates. To correct this:

1. Go to Settings > Hardware > Display.
2. Change the value of Flipped X Coordinates.
### Incorrect Colors
If the colors displayed on the interface or camera preview are incorrect, you can try the following options:

#### Inverted Colors
If, for example, the background color is white when it should be black, go to Settings > Hardware > Display and toggle  `Inverted Colors` .

#### BGR Colors
If, for example, you are using the Orange theme, and instead of orange the colors appear bluish, toggle `BGR Colors` in the display settings.

#### LCD Type
**Warning!**  Only try changing this setting if you failed to fix colors with previous ones.

If adjusting `BGR Colors` and `Inverted Colors` doesn't fix the color issue, try changing the LCD Type:

1. After changing this setting, you will be warned that the device will reboot automatically if this change does not resolve the issue (if it fails, the screen will turn black, and you'll not see anything).
2. After proceeding with the warning, if you see a message prompting you to press the `PREVIOUS` (UP) button, it means that the new setting worked. Follow the instructions and press UP.
3. If you notice menu options but the colors are still wrong, try again with different combinations of `Inverted Colors` and `BGR Colors`. This time, it is likely you will find a combination that correctly displays the colors of themes and the camera feed.

If, after the warning in step 1, the screen turns black and you don't see anything, don't panic or press any buttons. Just wait 5 seconds, and the device will automatically reboot with the previous display settings. This means you should keep the default LCD Type setting and maybe try again with `Inverted Colors` and `BGR Colors`.

If you accidentally pressed `PREVIOUS` (UP) and saved the wrong setting, you will have to perform a wipe to remove all stored settings to be able to see the screen working again. On Linux, go to the folder where you downloaded the Krux firmware and use Ktool to fully wipe your device:

`./ktool-linux -B goE -b 1500000 -E`

(Soon Krux-Installer will have a full wipe button too)

Then flash the fimrware again.

`./ktool-linux -B goE -b 1500000 maixpy_amigo/kboot.kfpkg`

## Why doesn't my Maix Amigo touchscreen work with v24.03.0 if it worked fine with v23.09.1?
<img src="../img/amigo-inside-switch-up.jpg" align="right">

We added IRQ to the firmware, so when you open your Maix Amigo, you will see a switch in the middle of the device board, it must be in the upper position for the touchscreen to work with v24.03.0 and later.

<div style="clear: both"></div>

## Why isn't my device charging or being recognized when connected to the computer's USB?
If you have a Maix Amigo, make sure you're using the USB-C port at the bottom of the device, not the one on the left side.

Different computer hosts have varying hardware, operating systems, and behaviors regarding their USB ports. Below are the expected behaviors:

### USB-A:
Your device should charge and turn on when connected to a USB-A port, even if it was initially turned off. You can also turn off the device while it continues to charge. However, some hosts' USB-A ports may behave like USB-C ports, as described below.

### USB-C:

- If the device is turned off and connected to a USB-C port, it should turn on and start charging. You can turn it off again, and it will continue to charge.

- If the device is already turned on and connected to a USB-C port, it may not charge or be recognized by the computer. In this case, turn off the device to initiate recognition and charging. Once turned off and reconnected, the device should restart, be recognized by the computer, and charging should be triggered by USB-C hosts.
If your device is not charging or being recognized as expected, try using a different USB port or a different computer to determine if the issue is with the device or the host's USB port.

## Why isn't my M5stickV device being recognized and charged when connected to the computer's USB-C?
----8<----
m5stickv-usb-c.en.txt
----8<----

## Why does my Krux device randomly freeze or restart when connected to the computer?
Windows is known to have issues with the USB-C devices. If you are experiencing random crashes or even reboots and your device does not have a battery, try using a phone charger or other power source such as a power bank.

## Why won't my Linux OS list a serial port after connecting my device?
If you get the following error when trying to flash your device: `Failed to find device via USB. Is it connected and powered on?`
Make sure your device is being detected and serial ports are being mounted by running:
```bash
ls /dev/ttyUSB*
```
Expect one port to be listed for devices like M5stickV and Maix Dock `/dev/ttyUSB0`, and two ports for Maix Amigo and Maix Bit `/dev/ttyUSB0  /dev/ttyUSB1`.

If you don't see them, your OS may not be loading the correct drivers to create the serial ports to connect to. Ubuntu has a known bug where the `brltty` driver "kidnaps" serial devices. You can solve this problem by removing it:
```bash
sudo apt-get remove brltty
```

## My device didn't reboot after flashing the firmware and when I turned it off and on again, it just stayed blank without showing anything on the screen. What should I do?
Check if the downloaded file matches the device, this can also occur due to data corruption. Try downloading binaries again. You can install [MaixPy IDE](https://dl.sipeed.com/shareURL/MAIX/MaixPy/ide/v0.2.5) to help with debugging, Tools > Open Terminal > New Terminal > Connect to serial port > Select a COM port available (if it doesn't work, try another COM port). It will show the terminal and some messages, a message about an empty device or with corrupted firmware appears like: "interesting, something's wrong, boot failed with exit code 233, go to find your vendor."

## What are all the features available? What are the additional features of the Test or Beta version? Is there an Android app?
For [official releases](https://github.com/selfcustody/krux/releases) you will find all the features detailed here on the [Getting Started page](getting-started/index.md) with a brief summary on the [Navigation Overview page](getting-started/navigation.md). The latest and most experimental features, which we sometimes share on our social media, can be found only in the [test (beta) repository](https://github.com/odudex/krux_binaries/). Only official releases are signed, Test or Beta is just for trying new things and providing feedback. Krux Android app is available as an `apk` on the [test (beta) repository](https://github.com/odudex/krux_binaries/) (requires Android 6.0 or above).

## Why does Krux show an xpub for a segwit address?
The xpub that Krux displays follows the [bitcoin core descriptors spec](https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md/#key-origin-identification) and includes key origin and derivation info that, in theory, makes zpubs (and ypubs) unnecessary *if the wallet software being shown this extra information can parse it*. 

From the spec:
> Every public key can be prefixed by an 8-character hexadecimal fingerprint plus optional derivation steps (hardened and unhardened) surrounded by brackets, identifying the master and derivation path the key or xpub that follows was derived with.

However, in practice not all wallet software supports this extended format, so Krux still provides a zpub as a fallback.

For more information, check out [https://outputdescriptors.org/](https://outputdescriptors.org/).

## Why isn't Krux scanning my QR code?
The level of detail that you see is what Krux sees. If the QR code shown on the device's screen is blurry, the camera lens of the device may be out of focus. It can be adjusted by rotating it clockwise or counter-clockwise to achieve a clearer result. The lenses usually comes with a drop of glue that makes id harder to adjust for the first time. You can use your fingertip, tweezers or small precision pliers to help, being careful to don't damage the fragile lenses.

If you have adjusted the lens already, the device may be too far away or too close to the code to read it. Start by holding the device as close to the QR code as possible and pulling away slowly until all or most of the QR code is viewable within the screen. If the code on the screen looks crisp, Krux should read it quickly and give you immediate feedback.

If you are in a dark environment, you can hold down the `ENTER` button of the M5StickV or Maix Amigo to turn on their LED light to potentially increase visibility. M5stickV and Amigo also has an anti-glare mode to better capture images from high brightness screens or with incident light, to enable/disable the anti-glare just press the PAGE button while scanning.

## Why am I getting an error when I try to scan a QR code?
If Krux is recognizing that it sees a QR code but is displaying an error message after reading it, the likely reason is that the QR code is not in a format that Krux works with. We have listed the supported formats below:

For BIP-39 mnemonics:

1. BIP-39 Plaintext (Used by Krux and [https://iancoleman.io/bip39/](https://iancoleman.io/bip39/))
2. SeedSigner [SeedQR and CompactSeedQR](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md) Formats
3. [UR Type `crypto-bip39`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-006-urtypes.md)
4. Encrypted QR Code (Format created by Krux, [more info here](getting-started/features/encrypted-mnemonics.md))

For Wallet output descriptor:

1. JSON with at least a `descriptor` key containing an output descriptor string
2. Key-value INI files with at least `Format`, `Policy`, and `Derivation` keys
3. [UR Type `crypto-output`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-010-output-desc.md)

For PSBT (Partially Signed Bitcoin Transactions):

1. Base43, Base58, and Base64-encoded bytes
2. Raw Bytes
3. [UR Type `crypto-psbt`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-006-urtypes.md)

Additionally, Krux recognizes animated QR codes that use either the plaintext `pMofN` (the Specter QR format) or binary [`UR`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md) encodings.

## Why can't my computer read the QR code that Krux displays?
If you are using an M5StickV, the small screen makes it difficult for laptop webcams to capture enough detail to parse the QR codes it displays.
You can toggle brightness of QR codes from public keys and PSBTs by pressing PAGE button.
In the future, more work will be done to support displaying lower density QR codes. For now, a workaround you can do is to take a picture or video of the QR code with a better-quality camera (such as your phone), then enlarge and display the photo or video to your webcam. Alternatively, it may be simpler to use a mobile wallet such as BlueWallet with the M5StickV since phone cameras don't seem to have issues reading the small QR codes. You can also save the PSBT on a microSD card for Krux to sign and then save the signed transaction to the microSD card to transfer the file to the computer or phone.

## Why isn't Krux detecting my microSD card or presenting an error?
Starting from version 23.09.0, Krux supports SD card hot plugging. If you are using older versions, it may only detect the SD card at boot, so make sure Krux is turned off when inserting the microSD into it. To test the card compatibility use Krux [Tools>Check SD Card](getting-started/features/tools.md/#check-sd-card).
Make sure the SD card is using MBR/DOS partition table and FAT32 format.

Here is some [supported microSD cards](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md/#tf-cardmicrosd-test), and here is the MaixPy FAQ explaining [Why my micro SD card cannot be read](https://wiki.sipeed.com/soft/maixpy/en/others/maixpy_faq.html#Micro-SD-card-cannot-be-read).

## Why insert an SD card into my device? What is it for? Does it save something?
SD card use is optional, most people use Krux only with QR codes. But you can use SD card to to upgrade the firmware, save settings, cnc/file, QR codes, XPUBs, encrypted mnemonics, and to save and load PSBTs, messages and wallet output descriptors.
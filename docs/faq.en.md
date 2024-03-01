## Why are the buttons on my Maix Amigo in the wrong order? Why is my Amigo screen displaying the wrong colors?
Some Amigo screens have inverted X coordinates while others don’t. If you notice that the buttons on keypad input screens appear to be in the wrong order, please go to `Settings > Hardware > Display` and change the value of `Flipped X Coordinates` which should correct the issue.

Others have found that there are issues with the colors displayed in the interface and camera preview. To fix this we have two options in `Settings > Hardware > Display`, `BGR Colors` and `Inverted Colors`, test with them until the colors appear to be correct on your device.

## Why isn't my Maix Amigo device being recognized when connected to the computer's USB?
Make sure you’re using the USB-C port at the bottom of the device, not the one on the left side. There could also be an issue with the cable. Try using a different cable to see if that resolves the problem. If you're connecting to a USB-C port on your desktop computer, you may need to shut down and restart the device while it's connected. This ensures the driver loads correctly and creates the necessary serial ports.

## Why isn't my M5stickV device being recognized and charged when connected to the computer's USB-C?
M5stickV's USB-C port lacks pull up resistors required for it to be recognized and powered by host(computer) USB-C ports. If you don't have an USB-A available, you can use a USB hub connected between your computer's USB-C and M5stickV

## Why does my Krux device randomly freeze or restart when connected to the computer? Why doesn't my device (which has a battery) charge when connected to power?
Windows is known to have issues with the USB-C devices. If you are experiencing random crashes or even reboots, try using a phone charger or other power source such as a power bank. If your problem is with charging, it is expected that USB-A will always charge and turn on the device if it is turned off, you can also turn it off and continue charging. For USB-C, if it is turned off, it will turn on and start charging, it can also be turned off and continue charging, but if it is already turned on, it may not charge, nor be recognized by the computer, it must be turned off to be recognized, it will restart, it will be recognized and USB-C hosts will trigger charging.

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

## What are all the features available? What are the additional features of the Test (Beta) version? Is there an Android app?
For [official releases](https://github.com/selfcustody/krux/releases) you will find all the features detailed here on the [Getting Started page](getting-started/index.md) with a brief summary on the [Navigation Overview page](getting-started/navigation.md). The latest and most experimental features, which we sometimes share on our social media, can be found only in the [test (beta) repository](https://github.com/odudex/krux_binaries/). Only official releases are signed, Test (Beta) is just for trying new things and providing feedback. Krux Android app ia available as an `apk` on the [test (beta) repository](https://github.com/odudex/krux_binaries/).

## Why does Krux show an xpub for a segwit address?
The xpub that Krux displays follows the [bitcoin core descriptors spec](https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md/#key-origin-identification) and includes key origin and derivation info that, in theory, makes zpubs (and ypubs) unnecessary *if the wallet software being shown this extra information can parse it*. 

From the spec:
> Every public key can be prefixed by an 8-character hexadecimal fingerprint plus optional derivation steps (hardened and unhardened) surrounded by brackets, identifying the master and derivation path the key or xpub that follows was derived with.

However, in practice not all wallet software supports this extended format, so Krux still provides a zpub as a fallback.

For more information, check out [https://outputdescriptors.org/](https://outputdescriptors.org/).

## Why isn't Krux scanning my QR code?
The level of detail that you see is what Krux sees. If the QR code shown on the device's screen is blurry, the camera lens of the device may be out of focus. It can be adjusted by rotating it clockwise or counter-clockwise to achieve a clearer result. The lenses usually comes with a drop of glue that makes id harder to adjust for the first time. You can use your fingertip, tweezers or small precision pliers to help, being careful to don't damage the fragile lenses.

If you have adjusted the lens already, the device may be too far away or too close to the code to read it. Start by holding the device as close to the QR code as possible and pulling away slowly until all or most of the QR code is viewable within the screen. If the code on the screen looks crisp, Krux should read it quickly and give you immediate feedback.

If you are in a dark environment, you can hold down the ENTER button of the M5StickV or Maix Amigo to turn on their LED light to potentially increase visibility. M5stickV and Amigo also has an anti-glare mode to better capture images from high brightness screens or with incident light, to enable/disable the anti-glare just press the PAGE button while scanning.

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

For Partially Signed Bitcoin Transactions (PSBT):

1. Base43, Base58, and Base64-encoded bytes
2. Raw Bytes
3. [UR Type `crypto-psbt`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-006-urtypes.md)

Additionally, Krux recognizes animated QR codes that use either the plaintext `pMofN` (Specter QR format) or binary [`UR`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md) encodings.

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
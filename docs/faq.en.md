## Why does Krux show an xpub for a segwit address?
The xpub that Krux displays follows the [bitcoin core descriptors spec](https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md#key-origin-identification) and includes key origin and derivation info that, in theory, makes zpubs (and ypubs) unnecessary *if the wallet software being shown this extra information can parse it*. 

From the spec:
> Every public key can be prefixed by an 8-character hexadecimal fingerprint plus optional derivation steps (hardened and unhardened) surrounded by brackets, identifying the master and derivation path the key or xpub that follows was derived with.

However, in practice not all wallet software supports this extended format, so Krux still provides a zpub as a fallback.

For more information, check out [https://outputdescriptors.org/](https://outputdescriptors.org/).

## Why am I unable to sign a PSBT from BlueWallet?
As mentioned above, some wallet software does not support the descriptor key expression format. In this case, BlueWallet will ignore the key origin and derivation info when importing the xpub to create a single-sig wallet. This will result in the wrong derivation being used in BlueWallet and thus the inability to sign an outbound transaction in Krux.

Currently, the way to properly create a single-sig wallet in BlueWallet is to export the second QR code that Krux displays which contains the zpub. BlueWallet can then correctly infer the derivation path when creating the wallet.

## Why isn't Krux scanning my QR code?
The level of detail that you see is what Krux sees. If the QR code shown on the device's screen is blurry, the camera lens of the device may be out of focus. It can be adjusted by rotating it (with your fingertip) clockwise or counter-clockwise to achieve a clearer result. 

If you have adjusted the lens already, the device may be too far away or too close to the code to read it. Start by holding the device as close to the QR code as possible and pulling away slowly until all or most of the QR code is viewable within the screen. If the code on the screen looks crisp, Krux should read it quickly and give you immediate feedback.

If you are in a dark environment, you can hold down the ENTER button of the M5StickV or Maix Amigo to turn on their LED light to potentially increase visibility.

## Why am I getting an error when I try to scan a QR code?
If Krux is recognizing that it sees a QR code but is displaying an error message after reading it, the likely reason is that the QR code is not in a format that Krux understands.

For mnemonics, Krux recognizes:

1. BIP-39 Plaintext (Used by Krux and [https://iancoleman.io/bip39/](https://iancoleman.io/bip39/))
2. SeedSigner SeedQR and CompactSeedQR Formats
3. [UR Type `crypto-bip39`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-006-urtypes.md)

For loading wallets, Krux recognizes:

1. JSON with at least a `descriptor` key containing an output descriptor string
2. Key-value INI files with at least `Format`, `Policy`, and `Derivation` keys
3. [UR Type `crypto-output`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-010-output-desc.md)

For PSBTs, Krux recognizes:

1. Base43, Base58, and Base64-encoded bytes
2. Raw Bytes
3. [UR Type `crypto-psbt`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-006-urtypes.md)

Additionally, Krux recognizes animated QR codes that use either the plaintext `pMofN` or binary [`UR`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md) encodings.

## Why can't my computer read the QR code that Krux displays?
If you are using an M5StickV, the small screen makes it difficult for laptop webcams to capture enough detail to parse the QR codes it displays. In the future, more work will be done to support displaying lower density QR codes. For now, a workaround you can do is to take a picture or video of the QR code with a better-quality camera (such as your phone), then enlarge and display the photo or video to your webcam. Alternatively, it may be simpler to use a mobile wallet such as BlueWallet with the M5StickV since phone cameras don't seem to have issues reading the small QR codes.

## Why isn't my Amigo device being recognized?
Make sure you’re using the bottom USB-C port, not the one on the left side.

## Why won't my (Linux) OS list a serial port after connecting my device?
If you get the following error when trying to flash your device: `Failed to find device via USB. Is it connected and powered on?`
Make sure your device is being detected and serial ports are being mounted by running:
```bash
ls /dev/ttyUSB*
```
Expect one port to be listed for devices like M5stickV and Dock `/dev/ttyUSB0`, and two ports for Amigo and Bit `/dev/ttyUSB0  /dev/ttyUSB1`.

If you don't see them, your OS may not be loading the correct drivers to create the serial ports to connect to. Ubuntu has a known bug where the `brltty` driver "kidnaps" serial devices. You can solve this problem by removing it:
```bash
sudo apt-get remove brltty
```

## Why are the buttons on my Amigo in the wrong order?
Some Amigo screens have inverted x coordinates while others don’t.

If after flashing `maixpy_amigo_tft` to your device you notice that the buttons on keypad input screens appear to be in the wrong order, please try flashing `maixpy_amigo_ips` instead (or vice versa) which should correct the issue. 


## Why isn't Krux detecting my microSD card?
## Why does the option to save to SD not appear?
First, make sure you are using a [supported microSD card](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md#tf-cardmicrosd-test). We hope to add support for more cards in the future.

Second, make sure that Krux is powered off when you insert your microSD into the device. The firmware does not have support for hot plugging and can only detect the card on boot.

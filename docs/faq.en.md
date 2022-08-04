## Why does Krux show an xpub for a segwit address?
The xpub that Krux displays follows the bitcoin core descriptors spec and includes key origin and derivation info that, in theory, makes zpubs (and ypubs) unnecessary *if the wallet software being shown this extra information can parse it*. 

From the spec:
> Every public key can be prefixed by an 8-character hexadecimal fingerprint plus optional derivation steps (hardened and unhardened) surrounded by brackets, identifying the master and derivation path the key or xpub that follows was derived with.

However, in practice not all wallet software supports this extended format, so Krux still provides a zpub as a fallback.

## Why isn't Krux scanning my QR code?
The level of detail that you see is what Krux sees. If the QR code shown on the device's screen is blurry, the camera lens of the device may be out of focus. It can be adjusted by rotating it (with your fingertip) clockwise or counter-clockwise to achieve a clearer result. 

If you have adjusted the lens already, the device may be too far away or too close to the code to read it. Start by holding the device as close to the QR code as possible and pulling away slowly until all or most of the QR code is viewable within the screen. If the code on the screen looks crisp, Krux should read it quickly and give you immediate feedback.

If you are in a dark setting, you can hold down the front button of the M5StickV to turn on its LED light to potentially increase visibility.

## Why am I getting an error when I try to scan a QR code?
If Krux is recognizing that it sees a QR code but is displaying an error message after reading it, the likely reason is that the QR code is not in a format that Krux understands.

For mnemonics, Krux recognizes:

1. BIP-39 Plaintext (Used by Krux and [https://iancoleman.io/bip39/](https://iancoleman.io/bip39/))
2. SeedSigner Seed QR Format
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
If you are using an M5StickV, the small screen makes it difficult for laptop webcams to capture enough detail to parse the QR codes it displays. In the future, more work will be done to support displaying lower density QR codes. For now, a workaround you can do is to take a picture or video of the QR code with a better-quality camera (such as your phone), then enlarge and display the photo or video to your webcam. Alternatively, it may be simpler to use a mobile wallet such as BlueWallet with the M5StickV.
Krux is an airgapped hardware signer built on top of the [M5StickV](https://shop.m5stack.com/products/stickv), an open-source hardware device from [M5Stack](https://m5stack.com/about-us).

All operations in Krux are done via QR code. You can load your BIP-39 mnemonic, import a wallet descriptor, and sign transactions without ever having to plug the device into your computer (other than to flash the firmware). It reads QR codes in with its camera and writes QR codes out to its screen or [to paper via an optional thermal printer attachment](/guides/printing).

Unlike a hardware wallet, Krux does not come with its own wallet software. Instead, you can use Krux with wallet coordinators to manage wallets and create transactions from your computer while never giving them access to your private keys. Krux was built to be vendor agnostic and works with many popular wallet coordinators, including:

- [Specter Desktop](https://specter.solutions/)
- [Sparrow Wallet](https://www.sparrowwallet.com/)
- [BlueWallet](https://bluewallet.io/)
- [Electrum](https://electrum.org/)

These applications let you create and manage your multisig and single-key wallets, generate receive addresses, and send funds by creating partially signed bitcoin transactions (PSBTs) that you can sign with your hardware wallets and signers, such as Krux.

# About
Krux is an airgapped hardware signer built on top of the [M5StickV](https://shop.m5stack.com/products/stickv), an open-source hardware device from [M5Stack](https://m5stack.com/about-us).

All operations in Krux are done via QR code. You can load your BIP-39 mnemonic, import a wallet descriptor, and sign transactions without having to plug the device into your computer (except to initially flash the firmware). It reads QR codes in with its camera and outputs QR codes to its screen or to paper via an optional [thermal printer attachment](../getting-started/printing).

Krux does not come with its own desktop wallet software. Instead, you can use Krux with third-party wallet coordinators to create and manage wallets and send transactions from your computer or mobile device while keeping your keys offline. Krux was built to be vendor agnostic and works with many popular wallet coordinators, including:

- [Specter Desktop](https://specter.solutions/)
- [Sparrow Wallet](https://www.sparrowwallet.com/)
- [BlueWallet](https://bluewallet.io/)

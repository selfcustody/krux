## Is Krux a hardware wallet?

No, Krux is a bitcoin wallet which is called a hardware signer. A hardware wallet is able to sign and broacast the transaction. Whereas, a hardware signer device, for security purposes, remains offline and only signs the `PSBT` (partially-signed-bitcoin-transaction). Using QR codes, hardware signers are used in conjuction with wallet coordinators which are able to broadcast the `PSBT` QR codes from Krux. For example, [Sparrow Wallet](https://sparrowwallet.com/) for desktop or [Nunchuk](https://nunchuk.io/) for mobile. 

## Derivation Paths

Imagine your bitcoin wallet is like a treasure chest with many compartments, each needing a special key to open.

- **Extended Public Key (XPUB)**: This is like a main key that allows you to derive public keys but not private keys.

- **Derivation Path**: Think of it as a set of instructions that tells you how to find a specific public key to open a compartment, including the script type (like BIP44, BIP49, or BIP84).

**Example**:

- **Extended Public Key (XPUB)**: `xpub6BosfCnifzxcF.......SoekkudhUd9yLb6qx39T9nMdj`
- **Derivation Path (BIP44)**: `m/44'/0'/0'/0/1`

In this example the derivation path `m/44'/0'/0'/0/1` tells you how to find the public key to open the second compartment (`1`) in the first level (`0`) of your treasure chest, following the BIP44 standard.

Derivation paths help organize and manage different parts of your bitcoin securely, like different compartments in a treasure chest, according to specific standards like BIP44, BIP49, or BIP84.

## Descriptors

The `xpub` that Krux displays follows the [bitcoin core descriptors spec](https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md/#key-origin-identification) and includes key origin and [derivation path](https://selfcustody.github.io/krux/faq/#derivation-path) info. Descriptors allow you to import and export seeds and keys. That's useful if you want to move between different wallets, and create backups. 

**Extended Public Key (XPUB) [examples](https://github.com/satoshilabs/slips/blob/master/slip-0132.md#bitcoin-test-vectors):**

>`xpub6BosfCnifzxcF.......SoekkudhUd9yLb6qx39T9nMdj`
>>`ypub6Ww3ibxVfGzLr.......WxHcrArf3zbeJJJUZPf663zsP`
>>>`zpub6rFR7y4Q2AijB.......DKf31mGDtKsAYz2oz2AGutZYs`


**Extended Descriptor example:**

> `[d34db33f/44'/0'/0']xpub6ERApfZwUNrhL.......rBGRjaDMzQLcgJvLJuZZvRcEL/0/*`


However, in practice not all wallet software supports this extended format, so Krux still provides a `zpub` as a fallback.

For more information, check out https://bitcoindevkit.org/descriptors/#descriptors.

## Beta version?

The latest and most experimental features, which we sometimes share on our social media, can be found only in the [test (beta) repository](https://github.com/odudex/krux_binaries/). Only official releases are signed, Test or Beta is just for trying new things and providing feedback.

## Android app?

Krux Android app is available as an `apk` on the [test (beta) repository](https://github.com/odudex/krux_binaries/) (requires Android 6.0 or above).

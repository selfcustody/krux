Once you have either a 12- or 24-word BIP-39 mnemonic, choose `Load Mnemonic` on Krux's start menu, and you will be presented with several input methods:

<img src="../../../img/maixpy_amigo/load-mnemonic-options-150.png">
<img src="../../../img/maixpy_m5stickv/load-mnemonic-options-125.png">

## Input Methods
<img src="../../../img/maixpy_m5stickv/load-mnemonic-camera-options-125.png" align="right">
<img src="../../../img/maixpy_amigo/load-mnemonic-camera-options-150.png" align="right">

### Via Camera

You can choose to use the camera to scan a `QR code` or `Tiny Seed` metal plate backup.

----8<----
camera-scan-tips.en.txt
----8<----

<div style="clear: both"></div>

#### QR Code

It's unpleasant having to manually enter 12 or 24 words every time you want to use Krux. To remedy this you can instead use the device's camera to read a QR code containing the words. Krux will decode QR codes of four types:

- **Plain text QR**: The mnemonic words encoded as text, with words separated by spaces.
- [SeedQR](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md): Basically, it is the mnemonic words of the respective BIP-39 numbers concatenated, encoded as text.
- [Compact SeedQR](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md/#compactseedqr-specification): Basically, it is the mnemonic words bits concatenated as bytes.
- [Encrypted Mnemonic](../features/encrypted-mnemonics.md): A specification created by Krux that encrypts the mnemonic words bits and adds some information about the encryption used.

After opening your wallet via one of the manual methods you can use Krux to create QR codes of all types above, transcript them to paper or metal using the transcription helpers or attach a thermal printer to your Krux and print out the mnemonic. Check out the [Printing section](../features/printing.md) for more information.
You can also use [an offline QR code generator for this](https://iancoleman.io/bip39/) (ideally on an airgapped device).

#### Tiny Seed, OneKey KeyTag or Binary Grid
Tiny Seed (and similar methods) directly encode a seed as binary, allowing for a very compact mnemonic storage method when compared to SeedQR and Compact SeedQR.

Krux devices have machine vision capabilities that allow users to scan these metal plates and instantly load mnemonics engraved on them. (This feature is not available in Krux on Android)

To properly scan them place the Tiny Seed (or similar) over a black background and paint the punched bits black to increase contrast. You can also scan the thermally printed version, or a filled template.

[You can find some examples of seeds encoded with each of the supported formats here.](../features/tinyseed.md)

Retail versions of this type of seed can be purchased here:
[Tiny Seed](https://tinyseed.io/)
[Onekey KeyTag](https://onekey.so/products/onekey-keytag/)

Alternatively, you can find templates to scan or print [here](https://github.com/odudex/krux_binaries/tree/main/templates).

### Via Manual Input
<img src="../../../img/maixpy_m5stickv/load-mnemonic-manual-options-125.png" align="right">
<img src="../../../img/maixpy_amigo/load-mnemonic-manual-options-150.png" align="right">

Manually type `Words`, `Word Numbers`, `Tiny Seed` (toggle the bits or punches) or [`Stackbit`](https://stackbit.me) (model 1248 metal plate backup).

<div style="clear: both"></div>

#### Words
<img src="../../../img/maixpy_m5stickv/load-mnemonic-via-text-word-125.png" align="right">
<img src="../../../img/maixpy_amigo/load-mnemonic-via-text-word-150.png" align="right">

Enter each word of your BIP-39 mnemonic one at a time. Krux will disable impossible-to-reach letters as you type and will attempt to autocomplete your words to speed up the process.

<div style="clear: both"></div>

#### Word Numbers
<img src="../../../img/maixpy_m5stickv/load-mnemonic-via-numbers-word-125.png" align="right">
<img src="../../../img/maixpy_amigo/load-mnemonic-via-numbers-word-150.png" align="right">

##### Decimal
Enter each word of your BIP-39 mnemonic as a number (1-2048) one at a time. You can use [this list](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt) for reference.

##### Hexadecimal and Octal
You can also enter your BIP-39 mnemonic word's numbers (1-2048) in hexadecimal format, with values ranging from 0x1 to 0x800, or in octal format, with values ranging from 01 to 04000. This is useful with some metal plate backups that uses those formats.

<div style="clear: both"></div>

#### Tiny Seed (Bits)
<img src="../../../img/maixpy_m5stickv/load-mnemonic-via-tinyseed-filled-125.png" align="right">
<img src="../../../img/maixpy_amigo/load-mnemonic-via-tinyseed-filled-150.png" align="right">

Enter the BIP-39 mnemonic word's numbers (1-2048) in binary format, toggling necessary bits to recreate each of the word's respective number. The last word will have checksum bits dynamically toggled while you fill the bits.

<div style="clear: both"></div>

#### Stackbit 1248
<img src="../../../img/maixpy_m5stickv/load-mnemonic-via-stackbit-filled-125.png" align="right">
<img src="../../../img/maixpy_amigo/load-mnemonic-via-stackbit-filled-150.png" align="right">

Enter the BIP-39 mnemonic word's numbers (1-2048) using the Stackbit 1248 metal plate backup method, where each of the four digits of the word's number is a sum of the numbers marked (punched) 1, 2, 4, or 8. For example, to enter the word "pear", number 1297, you must punch (1)(2)(1+8=9)(1+2+4=7).

<div style="clear: both"></div>

### From Storage
<img src="../../../img/maixpy_m5stickv/load-mnemonic-storage-options-125.png" align="right">
<img src="../../../img/maixpy_amigo/load-mnemonic-storage-options-150.png" align="right">

You can retrieve mnemonics previously stored on device's internal flash or external (SD card). All stored mnemonics are encrypted, to load them you'll have to enter the same key you used to encrypt them.

<div style="clear: both"></div>

## Wallet Loading

### Confirm Mnemonic Words
<img src="../../../img/maixpy_m5stickv/load-mnemonic-seq-mnemonic-125.png" align="right">
<img src="../../../img/maixpy_amigo/load-mnemonic-seq-mnemonic-150.png" align="right">

Once you have entered your mnemonic, you will be presented with the full list of words to confirm.

<div style="clear: both"></div>

### Confirm Wallet Attributes

You will be presented with a screen containing wallet attributes, if they are as expected just press `Load Wallet` and you'll be ready to use your loaded key.

<img src="../../../img/maixpy_m5stickv/load-mnemonic-seq-overview-125.png" align="bottom">
<img src="../../../img/maixpy_amigo/load-mnemonic-seq-overview-150.png" align="bottom">

#### Attributes

**Fingerprint**
<p align="center">
    <code>73c5da0a</code>
</p>

The BIP-32 master wallet's fingerprint, if you have it noted down, will help you make sure you entered the correct mnemonic and passphrase (optional) and will load the expected wallet.

**Network**
<p align="center">
    <code>Mainnet</code>
</p>

Check if you are loading a `Testnet` or `Mainnet` wallet.

**Single/Multisig**
<p align="center">
    <code>Single-sig</code>
</p>

Check if you are loading a `Single-sig` or `Multisig` wallet.

**Derivation Path**
<p align="center">
    <code>m/84'/0'/0'</code>
</p>

The derivation path is a sequence of numbers, or "nodes", that define the script type, network, and account index of your wallet.

1. Script Type: The first number defines the script type. The default is 84', corresponding to a Native Segwit wallet. Other values include:

    `44'` for Legacy

    `49'` for Nested Segwit

    `86'` for Taproot

    `48'` for Multisig


2. Network: The second number defines the network:

    `0'` for Mainnet

    `1'` for Testnet


3. Account Index: The third number is the account index, with `0'` being the default.

For multisig wallets, a fourth node with the value `2'` is added to the derivation path.

**Passphrase**
<p align="center">
    <code>No Passphrase</code>
</p>

Informs if the wallet has a loaded passphrase.

### Changing Wallet Attributes

You can change any of the attributes before and after loading a wallet.
It is also possible to change default settings for `Network` and `Single/Multisig` on settings.

#### Passphrase

<img src="../../../img/maixpy_m5stickv/passphrase-load-options-125.png" align="right">
<img src="../../../img/maixpy_amigo/passphrase-load-options-150.png" align="right">

You can type or scan a BIP-39 passphrase. When typing, swipe left :material-gesture-swipe-left: or right :material-gesture-swipe-right: to change keypads if your device has a touchscreen. For scanning, you can also create a QR code from your offline passphrase in [Tools](../features/tools.md/#create-qr-code).

<div style="clear: both"></div>

#### Customize

<img src="../../../img/maixpy_m5stickv/wallet-customization-options-125.png" align="right">
<img src="../../../img/maixpy_amigo/wallet-customization-options-150.png" align="right">

Press `Customize` to open a menu where you can change the `Network`, `Single/Multisig`, `Script Type` and `Account`.


<div style="clear: both"></div>

Now, onto the main menu...

<div style="clear: both"></div>

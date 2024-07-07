After entering your mnemonic, and loading a wallet, you will find yourself on Krux's main menu. Below is a breakdown of the entries available:

<img src="../../../img/maixpy_amigo/home-options-150.png">
<img src="../../../img/maixpy_m5stickv/home-options-125.png">

<div style="clear: both"></div>

### Backup Mnemonic
<img src="../../../img/maixpy_m5stickv/backup-options-125.png" align="right">
<img src="../../../img/maixpy_amigo/backup-options-150.png" align="right">

This will open a new submenu with different types of backups. `QR Code` based, `Encrypted`  and `Other Formats`

If you set a [printer driver](../../settings/#driver), it will also give the option to print them!

<div style="clear: both"></div>

#### QR Code

- **Plaintext QR**

<img src="../../../img/maixpy_m5stickv/backup-qr-plain-text-125.png" align="right">
<img src="../../../img/maixpy_amigo/backup-qr-plain-text-150.png" align="right">

Generate a QR containing the mnemonic words as regular text, where words are separated by spaces. Any QR code can be printed if a thermal printer driver is set.

<div style="clear: both"></div>

- **Compact SeedQR**

<img src="../../../img/maixpy_m5stickv/backup-compact-qr-125.png" align="right">
<img src="../../../img/maixpy_amigo/backup-compact-qr-150.png" align="right">

A QR code is created from a binary representation of mnemonic words. Format created by SeedSigner, more info [here](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md#compactseedqr-specification).

<div style="clear: both"></div>

- **SeedQR**

<img src="../../../img/maixpy_m5stickv/backup-seed-qr-125.png" align="right">
<img src="../../../img/maixpy_amigo/backup-seed-qr-150.png" align="right">

Words are converted to their BIP-39 numeric indexes, those numbers are then concatenated as a string and finally converted to a QR code. Format created by SeedSigner, more info [here](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md).

<div style="clear: both"></div>

- **Encrypted QR Code**

This option converts the encrypted mnemonic into a QR code. Enter an encryption key and, optionally, a custom ID. When you scan this QR code through "Load Mnemonic" -> "Via Camera" -> "QR Code," you will be prompted to enter the decryption key to load the mnemonic stored in it. Like any QR code, it can be printed if a thermal printer driver is set up.

See this page to find out more about: [Krux Mnemonics Encryption](../../getting-started/features/encrypted-mnemonics.md).

<div style="clear: both"></div>

#### Encrypted
<img src="../../../img/maixpy_m5stickv/home-encrypt-options-125.png" align="right">
<img src="../../../img/maixpy_amigo/home-encrypt-options-150.png" align="right">

This feature allows you to back up your mnemonic by encrypting it and storing it on the device's flash memory, an SD card, or in QR code format. You can customize the encryption method and parameters in the settings.

For convenience, you may choose to store the encrypted mnemonic on flash memory or an SD card, but it is advisable not to rely solely on these methods for backup. Flash storage can degrade over time and may be subject to permanent damage, resulting in the loss of stored information.

When using any of the encryption methods, you will be prompted to enter an encryption key. This key can be provided in text or QR code format. Additionally, you have the option to set a custom ID for easier management of your mnemonics. If a custom key is not specified, the device's current loaded wallet fingerprint will be used as the ID.


- **Store on Flash**

This option stores the encrypted mnemonic in the device's flash memory. You can decrypt and load it later through the "Load Mnemonic" -> "From Storage" option.

- **Store on SD Card**

If an SD card is available, this option stores the encrypted mnemonic on it. You can decrypt and load it later through the "Load Mnemonic" -> "From Storage" option.

- **Encrypted QR Code**
It's another path for the same functionality present on QR Code backups, described above.

#### Other Formats

- **Words**
<img src="../../../img/maixpy_m5stickv/backup-mnemonic-words-125.png" align="right">
<img src="../../../img/maixpy_amigo/backup-mnemonic-words-150.png" align="right">

Display the mnemonic words as text so you can write them down.

<div style="clear: both"></div>

- **Numbers**
<img src="../../../img/maixpy_m5stickv/backup-mnemonic-numbers-125.png" align="right">
<img src="../../../img/maixpy_amigo/backup-mnemonic-numbers-150.png" align="right">

Display the mnemonic word numbers in decimal, hex, or octal format.

<div style="clear: both"></div>



<div style="clear: both"></div>

- **Stackbit 1248**
<img src="../../../img/maixpy_m5stickv/backup-stackbit-125.png" align="right">
<img src="../../../img/maixpy_amigo/backup-stackbit-150.png" align="right">

This metal backup format represents the BIP-39 mnemonic word's numbers (1-2048). Each of the four digits is converted to a sum of 1, 2, 4 or 8. This option does not print even if a printer driver is set.

<div style="clear: both"></div>

- **Tiny Seed**
<img src="../../../img/maixpy_m5stickv/backup-tiny-seed-125.png" align="right">
<img src="../../../img/maixpy_amigo/backup-tiny-seed-150.png" align="right">

This metal backup format represents the BIP-39 mnemonic word's numbers (1-2048) in binary format on a metal plate, where the 1's are marked (punched) and the 0's are left intact. You can also print your mnemonic in this format if a thermal printer driver is set.

<div style="clear: both"></div>

### Extended Public Key

A menu will be presented with options to display your master extended public key (xPub) as text and as a QR code. Depending on whether a single-sig or multisig wallet was loaded, the options shown will be xPub, zPub, or ZPub. When displayed as text, the extended public key can be stored on an SD card if available. If you choose to export a QR code, you can not only scan it but also save it as an image on an SD card or print it if a thermal printer is attached.

<img src="../../../img/maixpy_m5stickv/extended-public-key-menu-125.png" align="bottom">
<img src="../../../img/maixpy_m5stickv/extended-public-key-wsh-xpub-text-125.png" align="bottom">
<img src="../../../img/maixpy_m5stickv/extended-public-key-wsh-xpub-qr-125.png" align="bottom">
<img src="../../../img/maixpy_amigo/extended-public-key-menu-150.png" align="bottom">
<img src="../../../img/maixpy_amigo/extended-public-key-wsh-xpub-text-150.png" align="bottom">
<img src="../../../img/maixpy_amigo/extended-public-key-wsh-xpub-qr-150.png" align="bottom">

All QR codes will contain [key origin information in key expressions](https://github.com/bitcoin/bips/blob/master/bip-0380.mediawiki#Key_Expressions). If your coordinator cannot parse this information, it will not be capable of importing the wallet's fingerprint. As a result, Krux will not be able to sign transactions created by it unless you manually add the fingerprint so that it can be used to create Krux compatible PSBTs.

<div style="clear: both"></div>

### Wallet Descriptor

When you select this option for the first time, you will be prompted to load a wallet. The camera will activate, and you will need to scan a wallet backup QR code generated by your wallet coordinator software. If the scan is successful, a preview of the wallet will be displayed for confirmation. If you abort the scan, you can alternatively load the wallet descriptor from an SD card.

<img src="../../../img/maixpy_m5stickv/wallet-wsh-load-prompt-fingerprints-125.png" align="top">
<img src="../../../img/maixpy_m5stickv/wallet-wsh-load-prompt-xpubs-125.png" align="top">
<img src="../../../img/maixpy_amigo/wallet-wsh-load-prompt-fingerprints-150.png" align="top">
<img src="../../../img/maixpy_amigo/wallet-wsh-load-prompt-xpubs-150.png" align="top">

If you access this option again after having loaded your wallet, you will see the wallet's name, fingerprints and the abbreviated XPUBs of all cosigners, along with a QR code containing the exact data that was initially loaded. If an SD card is inserted, you can save the descriptor to it. Additionally, if you have a thermal printer attached, you can print this QR code.

Please note that once a wallet is loaded, it cannot be changed. To load a different wallet, you will need to restart the device and re-enter your mnemonic.

<div style="clear: both"></div>

### Address
<img src="../../../img/maixpy_m5stickv/address-menu-125.png" align="right">
<img src="../../../img/maixpy_amigo/address-menu-150.png" align="right">

Scan, verify, export or print your wallet addresses.

<div style="clear: both"></div>

#### Scan Address
<img src="../../../img/maixpy_m5stickv/scan-address-scanned-address-125.png" align="right">
<img src="../../../img/maixpy_amigo/scan-address-scanned-address-150.png" align="right">

This option turns on the camera and allows you to scan in a QR code of a receive address. Upon scanning, it will render its own QR code of the address back to the display along with the (text) address below it. You could use this feature to scan the address of someone you want to send coins to and display the QR back to your wallet coordinator rather than copy-pasting an address. If you have a thermal printer attached, you can also print this QR code. 

After proceeding through this screen, you will be asked if you want to check that the address belongs to your wallet. If you confirm, it will exhaustively search through as many addresses derived from your wallet as you want in order to find a match.

This option exists as an extra security check to verify that the address your wallet coordinator has generated is authentic and belongs to your wallet.

<div style="clear: both"></div>

#### Receive Addresses
<img src="../../../img/maixpy_m5stickv/list-address-receive-125.png" align="right">
<img src="../../../img/maixpy_amigo/list-address-receive-150.png" align="right">

List your wallet receiving addresses, you can browse to select an arbitrary address to show your QR code and print if you want.

<div style="clear: both"></div>

#### Change Addresses
<img src="../../../img/maixpy_m5stickv/list-address-change-125.png" align="right">
<img src="../../../img/maixpy_amigo/list-address-change-150.png" align="right">

List your wallet change addresses, you can browse to select an arbitrary address to show your QR code and print if you want.

<div style="clear: both"></div>

### Sign
<img src="../../../img/maixpy_m5stickv/sign-options-125.png" align="right">
<img src="../../../img/maixpy_amigo/sign-options-150.png" align="right">

Under *Sign*, you can choose to sign a PSBT or a message. You can load both PSBTs and messages scanning QR codes or loading from files on a SD card.

<div style="clear: both"></div>

#### PSBT
<img src="../../../img/maixpy_m5stickv/sign-psbt-sign-prompt-125.png" align="right">
<img src="../../../img/maixpy_amigo/sign-psbt-sign-prompt-150.png" align="right">

To sign a Bitcoin PSBT, you have the following options:

- **Scan an Animated QR Code**: Turn on the camera and scan an animated QR code of a PSBT generated by your wallet coordinator software. If you have any issues, see [FAQ](../../faq.md/#why-isnt-krux-scanning-my-qr-code).
- **Load from SD Card**: Load an unsigned PSBT file from your SD card.

Upon loading the PSBT, you will be presented with a preview showing the amount of BTC being sent, the recipient's address, and the transaction fee. Amounts are displayed according to your locale and the International Bureau of Weights and Measures, while still adhering to the concept of the [Satcomma standard format](https://medium.com/coinmonks/the-satcomma-standard-89f1e7c2aede).

If you choose to proceed and sign the transaction, the signed PSBT can be exported in two ways:

- *As an animated QR code*, which can be scanned back into your coordinator wallet.
- *As a signed PSBT file*, which can be saved to your SD card and then loaded back into your coordinator wallet for broadcasting.

If a thermal printer is attached to your device, you can also print the PSBT QR codes for record-keeping or further processing.

<div style="clear: both"></div>

#### Message

Similar to PSBTs, Krux can load, sign, and export signatures for messages. This feature allows you to attest not only to the ownership of the messages themselves but also to the ownership of Bitcoin addresses and the authorship of documents and files.

##### Standard Messages and Files

<img src="../../../img/maixpy_m5stickv/sign-message-sha256-sign-prompt-125.png" align="right">
<img src="../../../img/maixpy_amigo/sign-message-sha256-sign-prompt-150.png" align="right">

You can scan or load a file from an SD card, the content can be plaintext or the SHA-256 hash of a message. Upon loading, you will be shown a preview of the message's SHA-256 hash for confirmation before signing.

If you confirm, a signature will be generated, and you will see a base64-encoded version of it. You can then choose to export it as a QR code or save it to an SD card. If a thermal printer is attached, you can also print the QR code.

Following this, you will see and be allowed to export your raw (master) public key in hexadecimal form, which can be used by others to verify your signature. If a thermal printer is attached, you can also print this QR code.

This feature is used to sign Krux releases, airgapped, using a Krux device.

<div style="clear: both"></div>

##### Messages at Address

<img src="../../../img/maixpy_m5stickv/sign-message-at-address-prompt-125.png" align="right">
<img src="../../../img/maixpy_amigo/sign-message-at-address-prompt-150.png" align="right">

Coordinators like Sparrow and Specter offer the possibility to sign messages at a Bitcoin receive address, allowing you to attest ownership of that address. Krux will detect if the message is of this type and present a similar workflow for signing. The main difference is that the address will be displayed along with the raw message, and since the message is signed with a derived address instead of the master public key, Krux won't offer the option to export the raw public key after the signature.

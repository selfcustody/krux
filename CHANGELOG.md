# Changelog 24.04.beta8 - November 20, 2023

## Changes

### IRQ Interfaces
Button and touch presses are now detected by the application through IO interrupts. Meaning inputs events will be registered and handled even if they happened when other tasks were being executed by the processor, resulting in a better UX.

### Save and Load Wallet Output Descriptor from SD card
Create or load from a wallet output descriptor file on a SD card. The backup file format is compatible with most coordinators.

### Restore Default Settings
Option to restore the device's settings to its factory state.

### Wipe Device
Option on settings to wipe the device, permanently removing settings and stored encrypted mnemonics by erasing every single bit of user's flash space.

### Screensaver
Optional screensaver to reduce pixels' burn-in and grab attention of the user when the device is left powered on.

### Maix Dock Simulator
Now Krux PC simulator can also run in Maix Dock mode, mimetizing appearance and characteristics of the most DIY Krux device

### Update Embit to version 0.7
Use latest Embit release

### Optimized QR codes
QR codes rendering is faster and uses less RAM

### Mnemonic Numbers
To match the input options, export mnemonics as decimal, hexadecimal or octal numbers
When loading from numbers, a new numbers confirmation screen was added.

### Addresses Exploring
More receive and change addresses per page are shown on bigger screens

### Export QR Codes as Images to SD Card
Some QR codes can be exported as images to SD card

### Optimized Settings Storage
Device's storage is now used more efficiently, data is stored less frequently, only in case a setting is changed from defaults.

### Other Small Fixes and Code Optimizations
Many other small fixes and optimizations under the hood


# Version 23.09.1 - November 18, 2023
This release contain bugfixes:

Encrypted Mnemonic QR codes would fail to decrypt if PBKDF2 iterations settings was changed to non multiple of 10,000.

QR code transcription helpers that highlight regions could crash on edges of some QR code sizes.

Address navigation "previous" menu option wouldn't show correct number.

# Version 23.09.0 - September 12, 2023
After a long year, new features are finally coming out of beta and making their way into a stable release. Also @jreesun appointed @odudex as the new lead maintainer of the project.

## Changes

### Battery Indicator
Check battery status of M5stickV or Maix Amigo on top right of the screen.

### New Mnemonic From Camera
Use camera as a source of entropy to quickly create a mnemonic.

### Tiny Seed - Export, Print, Punch, Manually Load or Scan
Import and export a binary representation of your mnemonic, in a format popularized by Tiny Seed metal plates. BIP39 mnemonic words number, ranging from 1 to 2048 are punched in binary format on a rectangular grid.
Krux will automatically convert a mnemonic to Tiny Seed format allowing to print or transcript it. You can also load a tiny seed toggling word bits on screen, or make use of machine vision capabilities of K210 chip to directly scan a Tiny Seed mnemonic backup stored on metal or paper.

### Stackbit - Import and Export
Without needing tools, guides or dictionaries, import and export another metal plate backup format, where each of the four digits of the word's number is a sum of marked (punched) numbers 1,2,4 and 8.

### Enter Mnemonic as Word Numbers - Hex and Octal formats
Also available in some metal plate backup formats, you could load your mnemonic words from its decimal BIP39 word number (1-2048), now you can also load from its hexadecimal(0x1-0x800) or octal(01-04000) word number.

### Encryption and Storage
Conveniently store your mnemonics on device's internal flash memory or removable SD card, protecting them with encryption. It is now possible to export encrypted QR codes too.

### Addresses
Beyond verifying your wallet's receive addresses, you can now also list, export and print receive and change addresses.

### SD Card Hot plugging
SD cards can now be inserted and removed at any time, making it easier to use it for signing transactions, messages and storing encrypted mnemonics.

### Transcript Tools for QR codes
Different visualization modes which make it easier to transcript QR codes.

### Transaction Details
When signing a transaction, more information is presented, ensuring that the user sees all details before signing.

### Tools
#### Check SD Card
Check if the SD card is detected and explore its content.

#### Delete Mnemonic
Delete any stored encrypted mnemonic, on device's internal flash memory or SD card.

#### Print Test QR
Quickly print a test QR code to check and optimize your printer setup.

#### Create QR Code
Enter a text input to create, print or transcript a QR code that can be later used as an encryption key or as a passphrase.

### Themes
Choose your color theme according to your preference.

### Thermal Printing and CNC
More mnemonic export formats and tools to create and print generic QR codes to be used as passphrases or encryption keys. You can also export QR codes to gcode files and save them in SD cards, allowing you to machine them GRBL compatible CNCs without the need of computers and CAD tools.

### More Settings
#### Persist
Choose where you want to store your settings, on internal flash memory or SD card.

#### Touchscreen
If your device has touchscreen you can change the touch detection threshold.

### Languages
Dutch translations were added.

### UI Tweaks
Small changes to optimize user experience.

### Under the Hood
Small bugfixes, optimizations and code refactoring, targeting better compatibility with coordinator softwares, faster boot and better RAM management.


# Version 22.08.2 - September 13, 2022

This patch release reverts the zpub QR code format, once again including key origin derivation info which is necessary for BlueWallet to use when preparing PSBTs for signing with single-key wallets.

It is recommended to update to this version if you are using a single-key "Imported Watch-only" wallet with BlueWallet and are seeing a "cannot sign" error message when trying to send an outgoing transaction. If so, please do the following:

1. Upgrade Krux to this new release
2. Delete the affected wallet in BlueWallet (funds are safu as long as you have your mnemonic)
3. Create a new wallet in BlueWallet by importing from the new zpub QR code that Krux now displays.
4. Open the wallet in BlueWallet and pull down to fetch the old wallet's transaction history.
5. Create a new outgoing transaction and scan the QR code with Krux.
6. Krux should display the tx information and allow you to sign.
7. Display the signed QR back to BlueWallet.
8. Broadcast!

# Version 22.08.1 - August 11, 2022

This release is to fix a bug that would have prevented Amigos from performing airgapped upgrades to the next release.

# Version 22.08.0 - August 10, 2022

This latest version of Krux is brought to you by @odudex, who tirelessly worked for months to get Krux working on three new devices: the Maix Amigo, Maix Bit, and Maix Dock. Thank you for all your hard work! 

Many other improvements to Krux were made along the way which will be listed below. 

Enjoy!

## Installing
For instructions on how to install this release, please follow the *Getting Started* guide on [https://selfcustody.github.io/krux/](https://selfcustody.github.io/krux/).

To perform an airgapped upgrade (with a microSD card) from a previous signed release, please follow the directions here: [https://selfcustody.github.io/krux/getting-started/installing/#upgrade-via-microsd-card](https://selfcustody.github.io/krux/getting-started/installing/#upgrade-via-microsd-card)

## Changes
### ¡Three Amigos!
Krux now supports three new devices: Maix Amigo, Maix Bit, and Maix Dock. The Amigo is an all-in-one device with a touchscreen display, while the Dock and Bit are more DIY-focused kits where some assembly is required.
 
### New touchscreen UI + UX enhancements
Along with being usable on multiple devices now, Krux also has native touchscreen support and many refinements to its UI to make better use of the screen space it has. More work has gone into improving UX including the ability to escape out of the mnemonic loading or creation screens at any point.

### Built-in translations + Portuguese
Krux now includes translations in the firmware due to using a more space-efficient font format. With this change, the rendering issues with Vietnamese characters have also been fixed. A new Portuguese translation has been added.

### Amigo support added to Krux Simulator
The Krux Simulator, which lets you simulate on your PC what it would be like to run Krux on a device, was updated to support the Amigo. There is also now a PC option if you want to run Krux "natively" on your PC (**NOTE**: This is a toy for fun and is *not recommended* for real usage).

### CompactSeedQR support
Support for scanning SeedSigner’s newer "CompactSeedQR" QR codes

### BIP39 passphrases
Support has been added for BIP39 passphrases. After loading a mnemonic, you will be asked if you want to "Add a passphrase?" to it.

### Export signed PSBTs to microSD
You can now save a signed PSBT to microSD which should help users having trouble getting their webcams to read the tiny QR codes on the M5StickV. Furthermore, Krux supports loading a PSBT from microSD as well if you want to forgo QR codes entirely.

### Better mnemonic generation
The flow for entering rolls has been streamlined to allow more rapid input, with your string of rolls now being visible along the top of the screen as you go. We also introduced a change to how the D6 roll string is built, no longer including "-" between rolls prior to hashing to have consistency with ColdCard and SeedSigner. 

Note: We continue to use a "-" separator between D20 rolls to avoid reducing state space due to collisions (e.g., rolling 1-17 and 11-7 would result in the same 117 string without a separator, and would thus have the same hash)

### Back button and rotary encoders
All devices, even the M5StickV, support moving backward in the UI now. The left-side power button on the M5StickV no longer does one-press resets and instead acts as a third input button. Note: You can still shutdown the device by holding it down for 5 seconds.

Support for using a rotary encoder as the previous and next buttons has also been added. Check out @odudex’s open source case design with instructions on how to use one with the Dock:
[https://github.com/odudex/DockEncoderCase](https://github.com/odudex/DockEncoderCase)

Just to note, he also has a case design for the Bit:

[https://github.com/odudex/MaixBitCase](https://github.com/odudex/MaixBitCase)

### Updated website + i18n future
The Github Pages site has been updated with new documentation and screenshots for the Amigo.

A new internationalization (i18n) framework has been added by @qlrd that will allow the website to be easily translated to other languages so we can eventually have documentation for every language that Krux supports!

@qlrd is also working on a graphical installer we hope to start making use of in the future when it’s ready. Keep tabs on it here: [https://github.com/qlrd/krux-installer](https://github.com/qlrd/krux-installer)

# Version 22.03.0 - March 31, 2022
Finally, after much TODO, the first official release of Krux is out!

Krux will be following a calendar version release schedule similar to Ubuntu, hence the first release is version (20)22.03.0. If any glaring security issues or important bugfixes come up, they will make their way into point releases such as 22.03.1, 22.03.2, etc. All new work will go toward major releases which will get a new year and month combo.

Thank you to everyone who contributed their time and effort toward this release. It's been very cool to see people take an interest in the project! Also, a special thank you is due to @stepansnigirev for creating the embit library that Krux leans so heavily on.

## Installing
For instructions on how to install this release, please follow the Getting Started guide on [https://selfcustody.github.io/krux/](https://selfcustody.github.io/krux/).

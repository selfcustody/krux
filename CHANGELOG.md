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

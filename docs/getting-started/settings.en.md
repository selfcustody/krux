In the Krux home menu, there is a `Settings` entry. Below is a breakdown of the options you can change:

<img src="../../img/maixpy_amigo/settings-options-150.png">
<img src="../../img/maixpy_m5stickv/settings-options-125.png">

### Bitcoin - Network
<img src="../../img/maixpy_m5stickv/network-options-125.png" align="right">
<img src="../../img/maixpy_amigo/network-options-150.png" align="right">

This option allows you to switch between `mainnet` (the default) and `testnet`. `Testnet` can be used to try out different wallet coordinators or for development. 

<div style="clear: both"></div>

### Encryption
<img src="../../img/maixpy_m5stickv/encryption-options-125.png" align="right">
<img src="../../img/maixpy_amigo/encryption-options-150.png" align="right">

Modify the encryption method and parameters to fit your needs. This will be used when storing encrypted mnemonics or creating encrypted QR codes. For more info see [Krux Encrypted Mnemonics](./features/encrypted-mnemonics.md).

<div style="clear: both"></div>

#### PBKDF2 Iter. (Iterations)
<img src="../../img/maixpy_m5stickv/encryption-options-pbkdf2-125.png" align="right">
<img src="../../img/maixpy_amigo/encryption-options-pbkdf2-150.png" align="right">

When you enter the encryption key, it is not directly used to encrypt your data. In order to protect against brute force attacks, the key is derived multiple times using hashing functions. PBKDF2 (Password-Based Key Derivation Function) iterations stands for the amount of derivations that will be performed over your key prior to encrypt/decrypt your mnemonic.

If you increase this value it will make the encryption harder, at the cost of taking longer to encrypt/decrypt your mnemonics.

Values must be multiple of 10,000. This was done to save data space on QR codes.

<div style="clear: both"></div>

#### Encryption Mode
<img src="../../img/maixpy_m5stickv/encryption-options-mode-125.png" align="right">
<img src="../../img/maixpy_amigo/encryption-options-mode-150.png" align="right">

Choose between well known and widely used AES (Advanced Encryption Standard) modes:

##### AES-ECB
ECB (Electronic Codebook), its a simpler method where encryption data blocks are encrypted individually. It will be faster and simpler to encrypt, QR codes will have a lower density and will be easier to transcribe.

##### AES-CBC
CBC (Cipher-block Chaining) is considered more secure as in the first data block an initialization vector (IV) is used to add random data to the encryption. The encryption of subsequent blocks depends on the data from previous blocks, ensuring chaining.

Encryption will take longer because a snapshot will be needed to generate the IV. This IV will be stored together with encrypted data, making encrypted QR codes denser and harder to transcribe.

<div style="clear: both"></div>

### Hardware
<img src="../../img/maixpy_amigo/settings-options-hardware-150.png" align="right">

Customize the parameters available for your device and change printer settings.

#### Encoder (Maix Dock only)
If your device has a rotary encoder, you can change the debounce threshold in milliseconds. With lower values, faster movements and navigation will be allowed.

The caveat is low values can cause issues, such as double step and unexpected movements, especially with lower quality encoders. If this is the case increase the value to make navigation more stable.

#### Display (Maix Amigo only)
<img src="../../img/maixpy_amigo/settings-options-hardware-display-150.png" align="right">

Some Maix Amigo screens are different, here you can customize the BGR Colors, Flipped X Coordinates and Inverted Colors. For more info see [FAQ](../faq.md/#why-are-the-buttons-on-my-amigo-in-the-wrong-order-why-is-my-amigo-screen-displaying-the-wrong-colors)

<div style="clear: both"></div>

### Printer
<img src="../../img/maixpy_m5stickv/printer-options-125.png" align="right">
<img src="../../img/maixpy_amigo/printer-options-150.png" align="right">

You can set up a thermal printer or tell Krux to store a GRBL CNC instructions file on a SD card to machine QR codes

#### CNC
Define several machining parameters according to the desired size, material you'll use, and your CNC characteristics and capabilities.

#### Thermal
Printers can come with different baudrates from the manufacturer. By default, Krux assumes the connected printer will have a baudrate of `9600`. If yours is different, you can change it here.

Also setup the TX Pin you'll use (e.g. 35 for M5stickV and 7 for Maix Amigo) and tweak other parameters according to your printer recommendations. For most printers you will only need to connect 2 cables, the device TX to the printer RX and ground. Consult the [part list](../parts.md/#optional-thermal-printer) page for supported printers.

#### Driver
Here you choose between Thermal, CNC or none (default). Leave this setting to "none" if you won't use a printer and don't want to be bothered by print prompts.

<div style="clear: both"></div>

#### Touchscreen (Maix Amigo and Yahboom only)
<img src="../../img/maixpy_amigo/touchscreen-150.png" align="right">

If your device has touchscreen you can change the touch detection threshold. If it is being too sensitive or detecting false (ghost) touches, you should increase the threshold value, making it less sensitive. The other way is also valid, reduce the threshold to make the screen more sensitive to touches.

<div style="clear: both"></div>

### Language - Locale
<img src="../../img/maixpy_m5stickv/locale-options-125.png" align="right">
<img src="../../img/maixpy_amigo/locale-options-150.png" align="right">

Here you can change Krux to your desired language.

<div style="clear: both"></div>

### Persist
<img src="../../img/maixpy_m5stickv/persist-options-125.png" align="right">
<img src="../../img/maixpy_amigo/persist-options-150.png" align="right">

Choose between flash (device's internal memory) or SD card for the place where your settings will be stored.

<div style="clear: both"></div>

### Appearance
<img src="../../img/maixpy_m5stickv/settings-options-appearance-125.png" align="right">
<img src="../../img/maixpy_amigo/settings-options-appearance-150.png" align="right">

Configure screensaver time and change Krux to your desired theme.

<div style="clear: both"></div>

#### Screensaver time
<img src="../../img/maixpy_m5stickv/settings-options-appearance-screensaver-125.png" align="right">
<img src="../../img/maixpy_amigo/settings-options-appearance-screensaver-150.png" align="right">

Set how long to wait idle before the screensaver appears. Enter 0 to disable the screensaver.

<div style="clear: both"></div>

#### Theme
Choose your color theme according to your preference. Some themes may be more suitable for some devices, coordinator cameras and environments. As an example, it may be easier to scan QR codes from Krux devices using light theme in brighter environments.

<img src="../../img/maixpy_amigo/theme-1-150.png">
<img src="../../img/maixpy_amigo/theme-2-150.png">
<img src="../../img/maixpy_amigo/theme-3-150.png">
<img src="../../img/maixpy_m5stickv/theme-1-125.png">
<img src="../../img/maixpy_m5stickv/theme-2-125.png">
<img src="../../img/maixpy_m5stickv/theme-3-125.png">

### Factory Settings
<img src="../../img/maixpy_m5stickv/settings-options-factory-settings-125.png" align="right">
<img src="../../img/maixpy_amigo/settings-options-factory-settings-150.png" align="right">

Restore device to factory settings and reboot.

<div style="clear: both"></div>
In the Krux home menu, there is a `Settings` entry. Some submenu entries have too many options to fit on one screen, swipe up :material-gesture-swipe-up: or down :material-gesture-swipe-down: to navigate between the screens if your device has a touchscreen. Below is a breakdown of the options you can change:

<img src="../../img/maixpy_amigo/settings-options-150.png">
<img src="../../img/maixpy_m5stickv/settings-options-125.png">

### Default Wallet

Set the default attributes for wallet loading.

#### Multisig

Set this to true if you are more likely to use Krux for multisig setups. This way, you won't need to "Customize" your wallet attributes every time you load a key.

<div style="clear: both"></div>

#### Network
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
ECB (Electronic Codebook) is a simpler method where data blocks are encrypted individually. Compared to CBC, it will be faster and simpler to encrypt, QR codes will have a lower density and will be easier to transcribe.

##### AES-CBC
CBC (Cipher-block Chaining) is considered more secure than ECB.  The first data block, an initialization vector (IV), is used to add random data to the encryption. The encryption of subsequent blocks depends on the data from previous blocks, ensuring chaining.

Encryption will take longer because a snapshot will be needed to generate the IV. This IV will be stored together with the encrypted data, making encrypted QR codes denser and harder to transcribe.

<div style="clear: both"></div>

### Hardware
<img src="../../img/maixpy_m5stickv/settings-options-hardware-125.png" align="right">
<img src="../../img/maixpy_amigo/settings-options-hardware-150.png" align="right">

Customize the parameters available for your device and change printer settings.

<div style="clear: both"></div>

#### Encoder (Maix Dock only)
If your device has a rotary encoder, you can change the debounce threshold in milliseconds. With lower values, faster movements and navigation will be allowed.

The caveat is low values can cause issues, such as double step and unexpected movements, especially with lower quality encoders. If this is the case increase the value to make navigation more stable.

#### Display (Maix Amigo only)
<img src="../../img/maixpy_amigo/settings-options-hardware-display-150.png" align="right">

Some Maix Amigo screens are different, here you can customize the `BGR Colors`, `Flipped X Coordinates`, `Inverted Colors` and `LCD Type`. For more info see [Troubleshooting](../troubleshooting.md/#troubleshooting-lcd-settings-on-maix-amigo)

<div style="clear: both"></div>

### Printer
<img src="../../img/maixpy_m5stickv/printer-options-125.png" align="right">
<img src="../../img/maixpy_amigo/printer-options-150.png" align="right">

You can set up a TTL serial thermal printer or tell Krux to store a GRBL CNC instructions file on a SD card to machine QR codes.

#### CNC
Define several machining parameters according to the desired size, material you'll use, and your CNC characteristics and capabilities.

#### Thermal
Printers can come with different baudrates from the manufacturer. By default, Krux assumes the connected printer will have a baudrate of `9600`. If yours is different, you can change it here.

Also setup the TX Pin you'll use (e.g. 35 for M5StickV and 7 for Maix Amigo) and tweak other parameters according to your printer recommendations. For most printers you will only need to connect 2 cables, the device TX to the printer RX and ground. Current uses of printing are listed [here](features/printing.md). Consult the [parts list](../parts.md/#optional-ttl-serial-thermal-printer) for supported printers.

#### Driver
Here you choose between Thermal, CNC or none (default). Leave this setting to "none" if you won't use a printer and don't want to be bothered by print prompts.

<div style="clear: both"></div>

#### Touchscreen (Maix Amigo, Yahboom and WonderMV only)
<img src="../../img/maixpy_amigo/touchscreen-150.png" align="right">

If your device has touchscreen you can change the touch detection threshold. If it is being too sensitive or detecting false or ghost touches, you should increase the threshold value, making it less sensitive. The other way is also valid, reduce the threshold to make the screen more sensitive to touches.

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

### Security
Adjust settings that may impact your security protocols.

#### Shutdown Time
Set the time it takes for Krux to automatically shut down. This feature not only conserves your device's battery, if it has one, but also serves as an important security measure. If you forget your device with private keys loaded, it will shut down automatically after the set time.

Please note that devices without batteries and power management will not shut down but will reboot instead, which is sufficient to unload private keys.

#### TC Flash Hash at Boot
Chose if you would like to run [Tamper Check Flash Hash](features/tamper-detection.en.md) every time the device is powered on.

Activating *TC Flash Hash* at boot helps prevent unauthorized use by requiring the *TC Code*. But is important to note, unlike a PIN, the TC Code does not provide access control over USB. This means that the device's memory remains accessible for reading and writing via USB, allowing it to be flashed with firmware that does not require the *TC Code*, which could then allow unauthorized use through its human interface.

#### Hide Mnemonics
When "Hide Mnemonics" mode is set to "True", your device will not display private key data or backup tools when a key is loaded. It will only show public key information and allow signing operations.

#### Tamper Check Code
Create or modify a Tamper Check Code. This code will be required every time [Tamper Check Flash Hash](features/tamper-detection.en.md) is executed.

After creating the code, you will be prompted to fill the empty memory spaces with random entropy from the camera. This step is important to make *TC Flash Hash* more resilient to data manipulation by eliminating empty memory spaces that could be exploited in a sophisticated tamper attempt.

The filling process requires good entropy images. If, for any reason, such as starting the process in a dark room, you fail to capture good entropy images, you can restart the filling process by resetting your *TC Code*.

The *TC Code* will be deleted if the device is wiped or user data is erased, which will consequently disable *TC Flash Hash*.

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
<img src="../../img/maixpy_amigo/theme-4-150.png">
<img src="../../img/maixpy_amigo/theme-5-150.png">

<img src="../../img/maixpy_m5stickv/theme-1-125.png">
<img src="../../img/maixpy_m5stickv/theme-2-125.png">
<img src="../../img/maixpy_m5stickv/theme-3-125.png">
<img src="../../img/maixpy_m5stickv/theme-4-125.png">
<img src="../../img/maixpy_m5stickv/theme-5-125.png">

### Factory Settings
<img src="../../img/maixpy_m5stickv/settings-options-factory-settings-125.png" align="right">
<img src="../../img/maixpy_amigo/settings-options-factory-settings-150.png" align="right">

Restore device to factory settings and reboot.

<div style="clear: both"></div>

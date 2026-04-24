In Krux first menu, there is a `Settings` entry. Some submenu entries have too many options to fit on a single screen, swipe up :material-gesture-swipe-up: or down :material-gesture-swipe-down: to navigate between the screens - if your device has a touchscreen. Below is a breakdown of the options you can change:

<img src="../../img/maixpy_amigo/settings-options-300.png" class="amigo">
<img src="../../img/maixpy_m5stickv/settings-options-250.png" class="m5stickv">

### Default Wallet

Set the default attributes for wallet loading.

#### Network
<img src="../../img/maixpy_m5stickv/network-options-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/network-options-300.png" align="right" class="amigo">

This option allows you to switch between `mainnet` (the default) and `testnet`. `Testnet` can be used to try out different wallet coordinators or for development. 

<div style="clear: both"></div>

#### Policy Type
<img src="../../img/maixpy_m5stickv/policy-options-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/policy-options-300.png" align="right" class="amigo">

Choose between `Single-sig`, `Multisig`, or `Miniscript` to avoid having to customize the policy type every time you load a key.

<div style="clear: both"></div>

#### Script Type
<img src="../../img/maixpy_m5stickv/script-options-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/script-options-300.png" align="right" class="amigo">

As with `Policy Type`, pre-select the most commonly used script type so that you don't have to change it every time you load a wallet. Your options are `Native Segwit`, `Neste Segwit`, `Taproot (Experimental)`, and `Legacy`. If you choose a script type that isn’t implemented for the selected policy type—such as a `Legacy` script for `Miniscript`—the system will default to `Native Segwit`.

**Note**: These settings do not restrict further changes to these wallet attributes, they just set their default values.

<div style="clear: both"></div>

### Encryption
<img src="../../img/maixpy_m5stickv/encryption-options-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/encryption-options-300.png" align="right" class="amigo">

Modify the encryption method and parameters to fit your needs. This will be used when storing encrypted mnemonics or creating encrypted QR codes. For more info see [Krux Encryption - Regarding BIP39 Mnemonics](features/encryption/encryption.md/#regarding-bip39-mnemonics).

<div style="clear: both"></div>

#### PBKDF2 Iter. (Iterations)
<img src="../../img/maixpy_m5stickv/encryption-options-pbkdf2-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/encryption-options-pbkdf2-300.png" align="right" class="amigo">

When you enter the encryption key, it is not directly used to encrypt your data. In order to protect against brute force attacks, the key is derived multiple times using hashing functions. PBKDF2 (Password-Based Key Derivation Function) iterations stands for the amount of derivations that will be performed over your key prior to encrypt/decrypt your mnemonic.

**Note**: Increasing this value will make the encryption harder, at the cost of taking longer to encrypt/decrypt your mnemonics. Values must be multiple of 10,000 (to save data space on QR codes).

<div style="clear: both"></div>

#### Encryption Mode
<img src="../../img/maixpy_m5stickv/encryption-options-mode-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/encryption-options-mode-300.png" align="right" class="amigo">

Choose between well known and widely used AES (Advanced Encryption Standard) modes:

##### AES-ECB
ECB (Electronic Codebook) is a simpler method where data blocks are encrypted individually. Compared to CBC, it will be faster and simpler to encrypt, QR codes will have a lower density and will be easier to [transcribe](features/QR-transcript-tools.md).

##### AES-CBC
CBC (Cipher-block Chaining) is considered more secure than ECB. The first data block, an initialization vector (IV), is used to add random data to the encryption. The encryption of subsequent blocks depends on the data from previous blocks, ensuring chaining.

Encryption will take longer because a snapshot will be needed to generate the IV. This IV will be stored together with the encrypted data, making encrypted QR codes denser and harder to [transcribe](features/QR-transcript-tools.md).

<div style="clear: both"></div>

### Hardware
<img src="../../img/maixpy_m5stickv/settings-options-hardware-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-options-hardware-300.png" align="right" class="amigo">

Customize the parameters available for your device and change printer settings.

<div style="clear: both"></div>

#### Buttons
<img src="../../img/maixpy_m5stickv/settings-btn-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-btn-300.png" align="right" class="amigo">

You can change the debounce threshold in milliseconds. With lower values, faster movements and navigation will be allowed.

The caveat is low values can cause issues, such as double click and unexpected movements, especially with lower quality buttons or encoders. If this is the case increase the value to make navigation more stable.

<div style="clear: both"></div>

#### Display
<img src="../../img/maixpy_m5stickv/settings-options-hardware-display-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-options-hardware-display-300.png" align="right" class="amigo">

Available display settings vary based on your device. Amigo has several options detailed below, Yahboom and WonderMV have an option for flipped orientation, others will have brightness control and Dock does not have this submenu.

Few Maix Amigo screens are different, here you can customize the `BGR Colors`, `Flipped X Coordinates`, `Inverted Colors` and `LCD Type`. For more info see [Troubleshooting](../troubleshooting.md/#troubleshooting-lcd-settings-on-maix-amigo)

<div style="clear: both"></div>

### Printer
<img src="../../img/maixpy_m5stickv/printer-options-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/printer-options-300.png" align="right" class="amigo">

You can set up a TTL serial thermal printer or GRBL. It is also possible to store a GRBL g-code CNC instructions file on an SD card to engrave QR codes.

#### CNC
Define several machining parameters according to the desired size, material you'll use, and your CNC characteristics and capabilities. See [CNC Engraving](features/printing/cnc.md) for more details.

#### Thermal
Printers can come with different baudrates from the manufacturer. By default, Krux assumes the connected printer will have a baudrate of `9600`. If yours is different, you can change it here.

Also setup the TX Pin you'll use (i.e., 35 on M5StickV, 7 on Maix Amigo, 8 on Yahboom, 25 on Cube, 28 on WonderMV) and tweak other parameters according to your printer recommendations. For most printers you will only need to connect 2 cables, the device TX to the printer RX and ground. Current uses of printing are listed [here](features/printing/printing.md). Consult the [parts list](../parts.md/#optional-ttl-serial-thermal-printer) for supported printers.

<div style="clear: both"></div>

#### Driver
<img src="../../img/maixpy_m5stickv/settings-printer-driver-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-printer-driver-300.png" align="right" class="amigo">

Here you choose between `thermal/adafruit`, `cnc/file`, `cnc/grbl` or `none` (default). Leave this setting to `none` if you won't use a printer and don't want to be bothered by print prompts.

<div style="clear: both"></div>

#### Touchscreen (Maix Amigo, Yahboom, WonderMV, TZT or Embed Fire only)
<img src="../../img/maixpy_amigo/touchscreen-300.png" align="right" class="amigo">

If your device has touchscreen you can change the touch detection threshold. If it is being too sensitive or detecting false or ghost touches, you should increase the threshold value, making it less sensitive. The other way is also valid, reduce the threshold to make the screen more sensitive to touches.

**Tip**: If your Amigo or WonderMV's touchscreen is not working properly, you can disable it by turning on the device with your finger pressing the screen. This will allow you to operate the device using buttons only.

<div style="clear: both"></div>

### Language - Locale
<img src="../../img/maixpy_m5stickv/locale-options-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/locale-options-300.png" align="right" class="amigo">

Here you can change Krux to your language.

<div style="clear: both"></div>

### Persist
<img src="../../img/maixpy_m5stickv/persist-options-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/persist-options-300.png" align="right" class="amigo">

Choose between `flash` (device's internal memory) or `SD card` for the place where your settings changes will be stored (default values are not persisted).

<div style="clear: both"></div>

### Security
<img src="../../img/maixpy_m5stickv/security-options-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/security-options-300.png" align="right" class="amigo">

Adjust settings that may impact your security protocols.

#### Shutdown Time
Set the time it takes for Krux to automatically shut down. This feature not only conserves your device's battery, if it has one, but also serves as an important security measure. If you forget your device with private keys loaded, it will shut down automatically after the set time.

**Note**: Devices without batteries and power management will not shut down but reboot, which will also unload keys.

<div style="clear: both"></div>

#### TC Flash Hash at Boot
<img src="../../img/maixpy_m5stickv/settings-tc-boot-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-tc-boot-300.png" align="right" class="amigo">

Chose if you would like to run [Tamper Check Flash Hash](features/tamper-detection.md) every time the device is powered on.

Activating *TC Flash Hash* at boot helps prevent unauthorized use by requiring the *TC Code*. But is important to note, unlike a PIN, the *TC Code* does not provide access control over USB. This means that the device's memory remains accessible via USB, allowing it to be flashed with firmware that does not require the *TC Code*.

<div style="clear: both"></div>

#### Hide Mnemonics
<img src="../../img/maixpy_m5stickv/settings-hide-mnemonic-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-hide-mnemonic-300.png" align="right" class="amigo">

When `True`, Krux will disable the [New Mnemonic](./usage/generating-a-mnemonic.md) menu and hide the words when [Loading a Mnemonic](./usage/loading-a-mnemonic.md). It will also hide the words when using [BIP85 to create a BIP39 Mnemonic](./usage/navigating-the-main-menu.md#bip85) and disable the [Backup Mnemonic](./usage/navigating-the-main-menu.md#backup-mnemonic) menu.

<div style="clear: both"></div>

#### Tamper Check Code
<img src="../../img/maixpy_m5stickv/tamper_check_settings-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/tamper_check_settings-300.png" align="right" class="amigo">

Create or modify a Tamper Check Code. This code will be required every time [Tamper Check Flash Hash](features/tamper-detection.md) is executed.

After creating the code, you will be prompted to fill the empty memory spaces with random entropy from the camera. This step is important to make *TC Flash Hash* more resilient to data manipulation by eliminating empty memory spaces that could be exploited in a sophisticated tamper attempt.

The filling process requires good entropy images. If, for any reason, such as starting the process in a dark room, you fail to capture good entropy images, you can restart the filling process by resetting your *TC Code*.

The *TC Code* will be deleted if the device is wiped or user data is erased, which will consequently disable *TC Flash Hash*.

<div style="clear: both"></div>

### Appearance
<img src="../../img/maixpy_m5stickv/settings-options-appearance-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-options-appearance-300.png" align="right" class="amigo">

Configure `screensaver time` and change Krux to your desired `theme`.

<div style="clear: both"></div>

#### Screensaver time
<img src="../../img/maixpy_m5stickv/settings-options-appearance-screensaver-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-options-appearance-screensaver-300.png" align="right" class="amigo">

Set how long to wait idle before the screensaver appears. Enter 0 to disable the screensaver.

<div style="clear: both"></div>

#### Theme
Choose your color theme according to your preference. Some themes may be more suitable for some devices, coordinator cameras and environments. As an example, it may be easier to scan QR codes from Krux devices using light theme in brighter environments.

<img src="../../img/maixpy_amigo/theme-1-300.png" class="amigo">
<img src="../../img/maixpy_amigo/theme-2-300.png" class="amigo">
<img src="../../img/maixpy_amigo/theme-3-300.png" class="amigo">
<img src="../../img/maixpy_amigo/theme-4-300.png" class="amigo">
<img src="../../img/maixpy_amigo/theme-5-300.png" class="amigo">

<img src="../../img/maixpy_m5stickv/theme-1-250.png" class="m5stickv">
<img src="../../img/maixpy_m5stickv/theme-2-250.png" class="m5stickv">
<img src="../../img/maixpy_m5stickv/theme-3-250.png" class="m5stickv">
<img src="../../img/maixpy_m5stickv/theme-4-250.png" class="m5stickv">
<img src="../../img/maixpy_m5stickv/theme-5-250.png" class="m5stickv">

### Factory Settings
<img src="../../img/maixpy_m5stickv/settings-options-factory-settings-250.png" align="right" class="m5stickv">
<img src="../../img/maixpy_amigo/settings-options-factory-settings-300.png" align="right" class="amigo">

Restore device to factory settings and reboot.

<div style="clear: both"></div>

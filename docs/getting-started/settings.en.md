On Krux's start menu, there is a *Settings* option.

<img src="../../img/maixpy_m5stickv/settings-options-125.png">
<img src="../../img/maixpy_amigo_tft/settings-options-150.png">

Below is a breakdown of the settings you can change:

### Bitcoin - Network
<img src="../../img/maixpy_m5stickv/network-options-125.png" align="right">
<img src="../../img/maixpy_amigo_tft/network-options-150.png" align="right">

This option allows you to switch between `mainnet` (the default) and `testnet`. This is mostly useful for development. 

<br><br><br><br><br>

### Encryption

Modify the encryption method and parameters to fit your needs. The encryption settings will be used both to store mnemonics and create encrypted QR codes.

#### PBKDF2 Iterations

When you enter a encryption key it is not directly used to encrypt your data. As a feature to increase safety, specially against brute force attacks, the keys is derived multiple times using hashing functions. PBKDF2(Password-Based Key Derivation Function) iterations stands for the amount of derivations that will be performed over your key prior to encrypt/decrypt your mnemonic.

If increase this value to make your encryption harder at the cost of taking longer to encrypt and decrypt your mnemonics

#### Encryption Mode

Choose between well known and widely used AES(Advanced Encryption Standard) modes:

##### AES-ECB

ECB(Electronic Codebook), its a simpler method where encryption data blocks are encrypted individually. It will be faster and simpler to encrypt, QR codes will have a lower density of information and will be easier to transcribe.

##### AES-CBC

CBC(Cipher-block Chaining) is considered safer, because at the first data block an initial vector(IV) is used to add random data to the encryption and from subsequent blocks depends on data from the previous block, giving its chaining feature.
It will take longer to encrypt, because it will be required to take a snapshot to generate a random initial vector. This initial vector must be stored together with encrypted data, making encrypted QR codes denser and harder to transcript.

<br><br><br><br><br>

### Language - Locale
<img src="../../img/maixpy_m5stickv/locale-options-125.png" align="right">
<img src="../../img/maixpy_amigo_tft/locale-options-150.png" align="right">

Here you can change the language that Krux uses.

<br><br><br><br><br>

### Logging
<img src="../../img/maixpy_m5stickv/debug-options-125.png" align="right">
<img src="../../img/maixpy_amigo_tft/debug-options-150.png" align="right">

Krux is capable of logging out information as it runs to a `.krux.log` file on the root of an inserted microSD card. **By default, it logs nothing**.

Unless you are running into a bug and trying to get more information to diagnose the problem, it is **strongly recommended** to leave the *Log Level* here as *NONE*.

If you experience an error and want to see more information about it, including a stack trace, you can change the *Log Level* to *ERROR*. If you're developing and want to see _everything_, you can change *Log Level* to either *INFO* or *DEBUG*.

Note that *DEBUG* could inadvertently write your private keys to the log file if you have it enabled when entering your mnemonic, so set it with care. To help prevent an accident like this from happening, Krux will display a colored rectangle on the upper left corner of the screen, of which the color is relative to the logging level, being green the DEBUG color.

<br><br><br><br><br>

### Persist

Choose between flash(device's internal memory) or SD card for the place where your settings will be stored.

<br><br><br><br><br>

### Printer

<img src="../../img/maixpy_m5stickv/printer-options-125.png" align="right">
<img src="../../img/maixpy_amigo_tft/printer-options-150.png" align="right">

You can set up a thermal printer or tell Krux to store a GRBL CNC instructions file on a SD card to machine QR codes

#### CNC

Define several machining parameters according to the desired size, material you'll use, and your CNC characteristics and capabilities.

#### Thermal

Printers can come with different baudrates from the manufacturer. By default, Krux assumes the connected printer will have a baudrate of `9600`. If yours is different, you can change this here.
Also setup the IOs you'll use and tweak parameters according to your printer recommendations.

#### Driver

Here you choose between Thermal, CNC or none(default). Leave this setting to "none" if you won't use a printer and don't want to be bothered by print prompts.

<br><br><br><br><br>

### Theme

Choose your color theme according to your preference. Some themes may be more suitable for some devices, coordinator cameras and environments. Light theme, for example, may be easier to scan QR codes from in brighter environments.

<br><br><br><br><br>

### Touchscreen

If your device has a touchscreen you can change the touch detection threshold. If it is too sensitive or detecting false (ghost) touches, you should increase the threshold value, making it less sensitive. The other way also valid, reduce the threshold to make the screen more sensitive to touches.

<br><br><br><br><br>

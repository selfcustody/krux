# PIN and Anti-Tamper Mechanism (Experimental)


## Krux Security Model - Good Practices and Limitations

To ensure the security of your Krux device, it's essential to verify the authenticity of the firmware before installation, especially when flashing via USB.

### Firmware Verification Methods

- **Using OpenSSL Command-Line Tool:** Follow the Krux documentation to verify the firmware's signature manually. This method provides a high level of assurance but requires familiarity with command-line operations.

- **Using Krux-Installer:** For a more user-friendly experience, verify the Krux-Installer's signature using GPG. Graphical interfaces like Sparrow Wallet can facilitate this process. Krux-Installer automatically verifies the firmware signature, informs you of the results, and guides you through manual verification if desired.

### Recommendations

- **Learn Verification Tools:** Familiarize yourself with verification methods and tools to maintain control over your device's security.

- **Build from Source:** Consider building the firmware from source code and verifying its reproducibility for maximum assurance.

- **Use SD Card for Updates:** After the initial flash, perform subsequent updates via the SD card. This keeps your device air-gapped and allows the existing firmware to verify new updates before installation.

Note: The effectiveness of the PIN and "Flash Hash" anti-tamper features relies on running legitimate, uncompromised firmware

## PIN
A PIN, composed of numbers, letters and special characters, with a minimum length of six characters, can be stored and required to boot the main application on Krux devices.

Before being stored in the device’s flash, the PIN is hashed together with the K210 chip’s unique ID and stretched using PBKDF2. This ensures the PIN is not retrievable via a flash dump and can only be brute-forced outside the device if the attacker also has access to the device’s unique ID. By allowing letters, special characters, and running 100,000 iterations of PBKDF2, brute-forcing the PIN from dumped data becomes more time-consuming and resource-intensive.

The PIN requirement is disabled if the user wipes the device or flashes an older firmware version.

### Enhancing Anti-Tamper
After setting the PIN, you are prompted to fill empty flash memory blocks with random entropy from the camera. This process strengthens the anti-tamper feature by preventing attackers from exploiting unused memory space.

## Flash Hash - Anti-tamper Tool
### Introduction

The "Flash Hash" tool enables you to verify if the flash memory content has been altered.

### How It Works

The tool generates a unique image and four anti-tamper words based on a hash of your PIN, the device's UID, and the flash content. The flash memory is divided into two regions:

- **Firmware Region:** Generates the image and the first two words.

- **User Region:** Generates the last two words.

<div style="text-align: center;">
    <img src="../../img/flash_hash_temp.bmp" alt="Flash Hash Temp" width="200"/>
</div>

*Example: The blue symbol and the words "tail monkey" are derived from the firmware region, while "wrestle over" comes from the user region.*

Any change in the flash content results in a different image or words:

- **Firmware Changes:** Alterations in the firmware region, including the bootloader, change the image and the first two words.

- **User Data Changes:** Modifications in the user region, such as new settings or stored mnemonics, change the last two words.

- **PIN Changes:** Updating the PIN alters the image and all four words.

### Filling Empty Flash Blocks

Krux performs a memory sweep while simultaneously capturing a live feed from the camera. Whenever an empty block is found in the flash memory, Krux estimates the image's entropy by evaluating its color variance. Krux waits until minimum threshold is met, then uses the data from the image to fill these empty spaces with rich, random entropy.

### Ensuring Tamper Resistance

The Flash Hash function securely hashes the combination of the PIN, UID, and flash content:

`hash(PIN -> UID -> Flash content)` -> Image + Words

## Potential Attack Scenarios and Their Mitigation
### Challenge for an Attacker

An attacker attempting to replace the firmware faces significant hurdles:

- **Lack of Original Flash Data:** Without the exact original flash content, the attacker cannot reproduce the correct hash.

- **Sequential Hash Dependency:** The hash function processes data sequentially (PIN, UID, flash content), preventing the attacker from injecting or rearranging data to produce the same hash.

- **One-Way Hash Functions:** Cryptographic hash functions like SHA-256 are one-way, making it infeasible to reverse-engineer or manipulate the hash without the original inputs.

### Why Tampered Firmware Cannot Bypass Verification

- **Cannot Reconstruct the Hash:** Without the original flash data, the attacker cannot generate the correct hash, even if they know the UID and PIN after the user enters it.

- **Hash Sensitivity:** Any alteration in the flash content changes the hash output, which will be evident through a different image or anti-tamper words.

- **Entropy Filling:** Filling empty flash blocks with camera-generated entropy leaves no space for malicious code and any changes to these blocks will alter the hash.

### Possible Attack Strategies and Failures

- **Precomputing Hashes:** The attacker cannot precompute the correct hash without the PIN, UID, and exact flash content.

- **Storing Hashes:** Storing hash(flash content) is ineffective because the overall hash depends on the sequential combination of PIN, UID, and flash data.

- **Inserting Malicious Code:** Attempting to insert code into empty spaces fails because the entropy filling process and hash verification will detect any changes.

## Conclusion

The Flash Hash tool significantly enhances security by making it infeasible for attackers to tamper with the firmware without detection. By combining PIN hashing, filling empty memory with random entropy, and verifying flash integrity through unique images and words, Krux significantly enhances the detection of any tampering attempts.

Note: The strength of this defense strategy depends on maintaining a strong, confidential PIN and following secure practices when unlocking the device.

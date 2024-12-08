# Tamper Detection Mechanism (Experimental)
Krux's tamper detection tool combines cryptographic hashes, a *Tamper Check Code (TC Code)*, and camera-generated entropy to create a tamper indicator that is unique to each device, represented by a memorable image and two sets of two words.

Before we get into details, let's start with some limitations and necessary prerequisites to allow the feature to work.

## Krux Security Model - Good Practices and Limitations

To secure your Krux device, always verify firmware authenticity before installation, particularly when flashing via USB.

### Firmware Verification Methods

- **Using OpenSSL Command-Line Tool:** Follow [from pre-built official release](../installing/from-pre-built-release.md/#verify-the-files) instructions to verify the firmware's signature manually. This method provides a high level of assurance but requires familiarity with command-line operations.

- **Using Krux-Installer:** Our [Krux-Installer GUI](../installing/from-gui/index.md) can facilitate this process by downloading our firmware from Github and verifying its signature. It also guides you through manual verification if desired. Just don't forget to verify the integrity of the Krux-Installer as well.


### Recommendations

- **Build from Source:** Consider building the firmware [from source code](../installing/from-source.md) and verifying its [reproducibility](../installing/from-source.md/#reproducibility) for maximum assurance.

- **Use SD Card for Updates:** After the initial flash through USB, perform subsequent [updates via the SD card](../features/sd-card-update.md). This keeps your device air-gapped and allows the existing firmware to verify the new one before installation.

Note: The effectiveness of *TC Flash Hash* tamper detection feature relies on running legitimate, uncompromised firmware and safely protecting your *TC Code*.

## Tamper Check Code (TC Code)
A *TC Code*, composed of numbers, letters and special characters, with a minimum length of six characters, can be stored and required to execute *TC Flash Hash* tamper verification before Krux boots at the main application, or optionally as a feature available in `Tools -> Flash Tools`.

Before being stored in the device’s flash, the *TC Code* is hashed together with the K210 chip’s unique ID and stretched using PBKDF2. This ensures the *TC Code* is not retrievable via a flash dump and can only be brute-forced outside the device if the attacker also has access to the device’s unique ID (UID). By allowing letters, special characters, and running 100k iterations of PBKDF2, brute-forcing the *TC Code* from dumped data becomes more time-consuming and resource-intensive.

### Enhancing Tamper Detection
After setting the *TC Code*, you are prompted to fill empty flash memory blocks with random entropy from the camera. This process ensures that attackers cannot exploit unused memory space.

## Tamper Check Flash Hash (TC Flash Hash) - A Tamper Detection Tool

The *TC Flash Hash* tool enables you to verify if the device's internal flash memory content has been altered. This tool generates a unique image and two sets of two tamper detection words based on a hash of your *TC Code*, the device's UID, and its internal flash content. The flash memory is divided into two regions:

- **Firmware Region:** The area only filled with firmware code. It generates the memorable image and the first set of two words.

- **User's Region:** The area used to stored encrypted mnemonics, settings and TC Code. It generates the last set of two words.

<div style="text-align: center;">
    <img src="../../../img/flash_hash.bmp" alt="TC Flash Hash" width="200"/>
</div>

*Example: The blue symbol and words 'tail monkey' represents the firmware region, while 'wrestle over' user's region.*

Any change in the flash content results in a different image and words:

- **Firmware Changes:** Alterations in the firmware region, including the bootloader, change the image and the first set of two words.

- **User's Data Changes:** Changes in the user's region, such as new settings or stored mnemonics, change the last set of two words.

- ***TC Code* Changes:** Replacing the *TC Code* alters the image and all sets of words.

### Filling Empty Flash Memory Blocks

Use this to enhance tamper detection. Krux performs a memory sweep while capturing a live feed from the camera. Whenever an empty block is found in the flash memory, it uses the data from the image to fill these empty spaces with rich, random entropy. It estimates the image's entropy by evaluating its color variance waiting until a minimum threshold is met. 

### Ensuring Tamper Detection

The *TC Flash Hash* function securely hashes the combination of the *TC Code*, device's UID, and flash memory contents. The hash properties ensure that without knowing these three elements, an attacker will not be able to reproduce the *TC Flash Hash* results.

## Executing *TC Flash Hash*

After setting a *TC Code* user can use the *TC Flash Hash* feature, available in `Tools -> Flash Tools -> TC Flash Hash`.

By navigating to `Settings -> Security -> TC Flash Hash at Boot`, users can set Krux to always require *TC Flash Hash* verification after device is turned on. If a wrong *TC Code* is typed at boot, the device will turn off. Nothing else will happen if the wrong *TC Code* is entered multiple times. As *TC Code* verification data is stored in the user's region of memory, the requirement to type at boot is disabled if the user [erases user's data](../features/tools.md/#erase-users-data) or [wipe device](../installing/from-gui/usage.md/#wipe-device). Flashing an older firmware version will also disable this feature.

## Potential Attack Scenarios and Their Mitigation
### Challenge for an Attacker

An attacker faces major challenges in replacing the firmware:

- **Lack of Original Flash Data:** Without the exact original flash content, the attacker cannot reproduce the correct hash.

- **Sequential Hash Dependency:** The hash function processes data sequentially (*TC Code*, device's UID, and flash memory contents), preventing the attacker from injecting or rearranging data to produce the same hash.

- **One-Way Hash Functions:** Cryptographic hash functions like SHA-256 are one-way, making it infeasible to reverse-engineer or manipulate the hash without the original inputs.

### Why Tampered Firmware Cannot Bypass Verification

- **Cannot Reconstruct the Hash:** Without the original flash data, the attacker cannot generate the correct hash, even if it knows the device's UID and the *TC Code* (after the user enters it).

- **Hash Sensitivity:** Any alteration in the flash content changes the hash output, which will be evident through a different image or the set of two words.

- **Entropy Filling:** Filling empty flash blocks with camera-generated entropy leaves no space for malicious code and any changes to these blocks will alter the hash.

### Possible Attack Strategies and Failures

- **Precomputing Hashes:** The attacker cannot precompute the correct hash without the *TC Code*, device's UID, and exact contents of the flash memory.

- **Storing Hashes:** Storing `hash(flash_content)` is ineffective because the overall hash depends on the sequential combination of *TC Code*, device's UID, and the flash data.

- **Inserting Malicious Code:** Attempting to insert code into empty spaces fails because after the entropy filling process, the hash verification will detect any changes.

- **Using an SD Card to Store a Copy of Original Flash Content:** An attacker could extract an exact copy of the flash contents to an SD card and subsequently install malicious firmware. This firmware could read the device's UID and the *TC Code* (after the user enters it), then hash the content of the SD card instead of the flash memory. Although this would make the verification process slower, it introduces a potential security risk. To mitigate this vulnerability, it is advisable to avoid performing verifications while an SD card is inserted. 

## Conclusion

The *TC Flash Hash* tool significantly enhances security by making it impossible for attackers to tamper with firmware without being detected. By combining *TC Code* hashing, filling empty memory with random entropy, and verification of the the unique image and set of words, Krux allows the detection of any tamper attempts.

Note: The strength of this defense strategy depends on maintaining a strong, confidential *TC Code* and remove the SD card before unlocking the device.

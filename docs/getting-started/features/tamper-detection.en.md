# Tamper Detection Mechanism (Experimental)
Krux's tamper detection tool combines cryptographic hashes, a *Tamper Check Code*, and camera-generated entropy to create a tamper indicator that is unique to each device, represented by a memorable image and four words.

Before we get into details, let's start with some limitations and necessary prerequisites to allow the feature to work.

## Krux Security Model - Good Practices and Limitations

To secure your Krux device, always verify firmware authenticity before installation, particularly when flashing via USB.

### Firmware Verification Methods

- **Using OpenSSL Command-Line Tool:** Follow the Krux documentation to verify the firmware's signature manually. This method provides a high level of assurance but requires familiarity with command-line operations.

- **Using Krux-Installer:** For a more user-friendly experience, verify the Krux-Installer's signature using GPG. Graphical interfaces like Sparrow Wallet can facilitate this process. Krux-Installer automatically downloads the firmware from Github, verifies the firmware signature, informs you of the results, and guides you through manual verification if desired.

### Recommendations

- **Learn Verification Tools:** Familiarize yourself with verification methods and tools to maintain control over your device's security.

- **Build from Source:** Consider building the firmware from source code and verifying its [reproducibility](../installing/from-source.md#reproducibility) for maximum assurance.

- **Use SD Card for Updates:** After the initial flash through USB, perform subsequent updates via the SD card. This keeps your device air-gapped and allows the existing firmware to verify new updates before installation.

Note: The effectiveness of the *TC Flash Hash* tamper detection feature relies on running legitimate, uncompromised firmware and safely protecting your *Tamper Check Code*.

## Tamper Check Code (TC Code)
A *Tamper Check Code*, composed of numbers, letters and special characters, with a minimum length of six characters, can be stored and required to execute *Tamper Check (TC) Flash Hash* tamper verification before Krux boots at the main application, or optionally as a feature available in `Tools -> Flash Tools`.

Before being stored in the device’s flash, the *TC Code* is hashed together with the K210 chip’s unique ID and stretched using PBKDF2. This ensures the *TC Code* is not retrievable via a flash dump and can only be brute-forced outside the device if the attacker also has access to the device’s unique ID. By allowing letters, special characters, and running 100k iterations of PBKDF2, brute-forcing the *TC Code* from dumped data becomes more time-consuming and resource-intensive.

### Enhancing Tamper Detection
After setting the *TC Code*, you are prompted to fill empty flash memory blocks with random entropy from the camera. This process ensures that attackers cannot exploit unused memory space.

## Tamper Check (TC) Flash Hash - A Tamper Detection Tool
### Introduction

The "TC Flash Hash" tool enables you to verify if the flash memory content has been altered.

### How It Works

The tool generates a unique image and four tamper detection words based on a hash of your *TC Code*, the device's UID, and the flash content. The flash memory is divided into two regions:

- **Firmware Region:** Generates the image and the first two words.

- **User's Region:** Generates the last two words.

<div style="text-align: center;">
    <img src="../../../img/flash_hash.bmp" alt="TC Flash Hash" width="200"/>
</div>

*Example: The blue symbol and words 'tail monkey' represent the firmware region, while 'wrestle over' reflects the user region.*

Any change in the flash content results in a different image or words:

- **Firmware Changes:** Alterations in the firmware region, including the bootloader, change the image and the first two words.

- **User's Data Changes:** Modifications in the user's region, such as new settings or stored mnemonics, change the last two words.

- ***TC Code* Changes:** Replacing the *TC Code* alters the image and all four words.

### Filling Empty Flash Blocks

Krux performs a memory sweep while simultaneously capturing a live feed from the camera. Whenever an empty block is found in the flash memory, Krux estimates the image's entropy by evaluating its color variance. Krux waits until minimum threshold is met, then uses the data from the image to fill these empty spaces with rich, random entropy.

### Ensuring Tamper Detection

The TC Flash Hash function securely hashes the combination of the *TC Code*, UID, and flash content:

`hash(TC Code,UID,Flash content)` -> Image + Words

Hash properties ensure that without knowing the *TC Code*, UID, and flash content, an attacker cannot reproduce the TC Flash Hash results.

## Executing *TC Flash Hash*

After setting a *TC Code* user can use the *TC Flash Hash* feature, available in `Tools -> Flash Tools -> TC Flash Hash`.

By navigating to `Settings -> Security -> TC Flash Hash at Boot`, you can set Krux to always require *TC Flash Hash* verification after device is turned on.

If a wrong *TC Code* is typed at boot, the device will turn off. As storing code typing attempts count on flash would change its contents, there will be no consequences if wrong *TC Code* is typed multiple times.

As *TC Code* verification data is stored in the user's region of memory, *TC Flash Hash* and *TC Code* requirement is disabled if the user wipes the device. Flashing an older firmware version will also disable the feature.

## Potential Attack Scenarios and Their Mitigation
### Challenge for an Attacker

An attacker faces major challenges in replacing the firmware:

- **Lack of Original Flash Data:** Without the exact original flash content, the attacker cannot reproduce the correct hash.

- **Sequential Hash Dependency:** The hash function processes data sequentially (*TC Code*, UID, flash content), preventing the attacker from injecting or rearranging data to produce the same hash.

- **One-Way Hash Functions:** Cryptographic hash functions like SHA-256 are one-way, making it infeasible to reverse-engineer or manipulate the hash without the original inputs.

### Why Tampered Firmware Cannot Bypass Verification

- **Cannot Reconstruct the Hash:** Without the original flash data, the attacker cannot generate the correct hash, even if they know the UID and *TC Code* after the user enters it.

- **Hash Sensitivity:** Any alteration in the flash content changes the hash output, which will be evident through a different image or tamper detection words.

- **Entropy Filling:** Filling empty flash blocks with camera-generated entropy leaves no space for malicious code and any changes to these blocks will alter the hash.

### Possible Attack Strategies and Failures

- **Precomputing Hashes:** The attacker cannot precompute the correct hash without the *TC Code*, UID, and exact flash content.

- **Storing Hashes:** Storing `hash(flash content)` is ineffective because the overall hash depends on the sequential combination of *TC Code*, UID, and flash data.

- **Inserting Malicious Code:** Attempting to insert code into empty spaces fails because the entropy filling process and hash verification will detect any changes.

- **Using an SD Card to Store a Copy of Original Flash Content:** An attacker could extract an exact copy of the flash contents to an SD card and subsequently install malicious firmware. This firmware could capture the chip's UID and the user's TC Code, then hash the content of the SD card instead of the flash memory. Although this would make the verification process slower, it introduces a potential security risk. To mitigate this vulnerability, it is advisable to avoid performing verifications while an SD card is inserted. 

## Conclusion

The *TC Flash Hash* tool significantly enhances security by making it infeasible for attackers to tamper with the firmware without detection. By combining *TC Code* hashing, filling empty memory with random entropy, and verifying flash integrity through unique images and words, Krux significantly enhances the detection of any tamper attempts.

Note: The strength of this defense strategy depends on maintaining a strong, confidential *TC Code* and following secure practices when unlocking the device.

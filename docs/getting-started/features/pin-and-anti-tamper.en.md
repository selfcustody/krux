# PIN and Anti-Tamper Mechanism (Experimental)

## Krux Security Model - Good Practices and Limitations

It is crucial for users to verify the authenticity of the firmware being flashed onto the device, especially when doing so via USB.

Users can verify the firmware's signature by following the documentation and using OpenSSL command-line tool. Alternatively, when using Krux-Installer, users should verify Krux-Installer’s signature using GPG. This method is more user-friendly, as verification can be done through graphical user interfaces (GUIs) like Sparrow. Krux-Installer performs the firmware signature verification, informs the users of the results, and guides them through performing the verification manually, providing details about the firmware location and the necessary commands.

Learning about verification methods and tools is highly recommended. Building the firmware from source and verifying its reproducibility are also excellent steps towards maintaining control and ensuring the security of your device.

After the initial flash, it is advisable to perform subsequent updates through the SD card. SD card updates not only keep the device air-gapped but also ensure that the previous firmware verifies the signature of subsequent updates before installation.

Keeping the device air-gapped is a highly recommended practice, as the USB port presents a significant attack surface.

The PIN and "Flash Hash" anti-tamper features, described below, will only be effective under the assumption that the flashed firmware is legitimate and uncompromised.

## PIN
A PIN, composed of numbers, letters and special characters, with a minimum length of six characters, can be stored and required to boot the main application on Krux devices.

Before being stored in the device’s flash, the PIN is hashed together with the K210 chip’s unique ID and stretched using PBKDF2. This ensures the PIN is not retrievable via a flash dump and can only be brute-forced outside the device if the attacker also has access to the device’s unique ID. By allowing letters, special characters, and running 100,000 iterations of PBKDF2, brute-forcing the PIN from dumped data becomes more time-consuming and resource-intensive.

The PIN requirement is disabled if the user wipes the device or flashes an older firmware version.

## Flash Hash - Anti-tamper Tool
### Introduction
Once a PIN is defined, users can generate a 'flash hash' to verify whether the flash content has been altered.

The flash hash translates the flash content, combined with the user's PIN and the microcontroller's unique ID (UID), into an easy-to-recognize image and four anti-tamper words. The image’s shape, color, and the words are deterministically derived from the combination of the PIN, UID, and flash content.

The flash hash evaluates the entire flash memory, divided into two regions: the firmware region and the user's region.

- The firmware region hash generates an image and two anti-tamper words.
- The user’s region hash generates another two words.

<div style="text-align: center;">
    <img src="../../img/flash_hash_temp.bmp" alt="Flash Hash Temp" width="200"/>
</div>
In the example image, the blue symbol and the words "tail monkey" are derived from the firmware region, while "wrestle over" comes from the user’s region of memory.

A single bit change in either region will produce different results:

- A change in the firmware region (which includes the bootloader) will result in a different image and the first two words.
- A change in the user’s region, such as new settings or storing an encrypted mnemonic, will change the last two words.
- A PIN change will alter the image and all four words.

To ensure the flash hash is resistant to tampering, the PIN and K210 chip’s UID are hashed along with the flash contents.

`hash(PIN -> UID -> Flash content)` -> Image + Words

### Possible Attack Scenarios
If an attacker replaces the firmware and the user enters the correct PIN, here’s how the tampered firmware might attempt to bypass verification:

#### The Challenge for the Attacker
Let’s break down how the tampered firmware might attempt to generate the correct hash:

1. Tampered Firmware Has Knowledge of the Original Hash:

- The attacker may know the hash of the original firmware `hash(flash data)`, but not the original firmware content itself.
- They cannot reverse-engineer the hash to recover the original firmware, as cryptographic hash functions like SHA-256 are one-way functions.

2. Attacker Receives the User’s PIN:

- After the user enters the PIN, the tampered firmware now knows the correct PIN and UID.
- However, the tampered firmware still needs to compute `hash(PIN + UID + original flash data)` to match what the original firmware would have produced.

3. Hash Function with Sequential Data Blocks:

- The hash depends on the PIN (first), UID (second), and the flash data (subsequently in sequential blocks).
- Since the tampered firmware lacks the original flash data, it cannot generate the correct sequential hash `hash(PIN + UID + original flash data)`.

#### Why the Tampered Firmware Can't Mock the Hash:
- Impossibility of Reconstructing the Original Hash: Even though the tampered firmware knows hash(original flash data) and the user’s PIN, it cannot generate the correct hash `hash(PIN + UID + original flash data)` for the following reasons:

- Hashing is Sensitive to Input Order: The hash function processes the PIN and then the flash data sequentially. The tampered firmware can’t simply "insert" the original flash data hash into this process. To generate the correct overall hash, the tampered firmware would need access to the actual original flash content itself, not just its hash.

- Hash Function Properties: Cryptographic hash functions, like SHA-256, are collision-resistant and deterministic. The tampered firmware can’t produce the same hash unless it provides the exact same sequence of data blocks that were used to create the original hash. The hash function works on the entire content (PIN + UID + flash data), not just their final hashes.

- Time of PIN Entry: If the PIN is entered after the device has already booted the tampered firmware, the attacker would have no chance to modify the hash input to simulate the original flash data hash without full knowledge of the firmware’s content.

#### Possible Tampered Firmware Strategies (and Why They Fail):
1. Precompute and Store `hash(PIN + UID + flash data)`:

- If the tampered firmware precomputes `hash(PIN + UID + flash data)` using the original firmware and stores it somewhere, it could potentially return the correct hash after receiving the PIN.
- This strategy only works if the attacker had access to the PIN, the device (to extract UID) and the original firmware at the time of tampering, which contradicts the purpose of using an unknown PIN.

2. Use of Stored `hash(flash data)`:

- The attacker might try to store `hash(flash data)` from the original firmware and somehow combine it with the PIN to mock the final hash.
- But, the process of hashing PIN + UID + firmware as a block sequence ensures that merely combining the final hashes won’t produce a valid result.

#### Conclusion:
The tampered firmware cannot mock the correct result of `hash(PIN + UID + flash data)` unless it has access to the PIN, the device, and the exact original flash content. Simply knowing `hash(flash data)` or even precomputing certain hashes in advance wouldn’t help, because the hash function operates sequentially on the combined data (PIN + UID + flash data).

In conclusion, this approach provides improved security because:

- The PIN remains secret and is only input by the user.
- The 'flash hash' hash depends on the PIN, UID and the entire flash content, making it infeasible for attackers to tamper with the firmware and pass verification without having previous access to the PIN and the device, to extract UID and exact flash content.

Although this feature makes it much harder for an attacker to tamper the device with a malicious firmware without being noticed, an attack is still possible:
When the attacker manages to get the PIN. So the PIN strength and users protocol is crucial for this defense strategy.
Users can enforce their PIN by making them long and using letters and special characters. Privacy while unlocking the devices is also crucial.
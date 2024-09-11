# PIN and Anti-Tamper Mechanism (Experimental)

## Krux Security Model - Good Practices and Limitations

It is crucial for users to verify the authenticity of the firmware being flashed onto the device, especially when doing so via USB.

Users can verify the firmware's signature by following the documentation and using OpenSSL command-line tool. Alternatively, when using Krux-Installer, users should verify Krux-Installer’s signature using GPG. This method is more user-friendly, as verification can be done through graphical user interfaces (GUIs) like Sparrow. Krux-Installer performs the firmware signature verification, informs the users of the results, and guides them through performing the verification manually, providing details about the firmware location and the necessary commands.

Learning about verification methods and tools is highly recommended. Building the firmware from source and verifying its reproducibility are also excellent steps towards maintaining control and ensuring the security of your device.

After the initial flash, it is advisable to perform subsequent updates through the SD card. SD card updates not only keep the device air-gapped but also ensure that the previous firmware verifies the signature of the update before installation.

Keeping the device air-gapped is a highly recommended practice, as the USB port presents a significant attack surface.

The PIN and flash snapshot anti-tamper features, described below, will only be effective under the assumption that the flashed firmware is legitimate and uncompromised.

## PIN
A PIN, with a minimum length of six digits, can be stored and required to boot main application on Krux devices.

Before being stored in the device’s flash, the PIN is hashed together with the K210 chip’s unique ID. This ensures that the PIN is not retrievable via a flash dump. It can only be brute-forced outside the device if the attacker has access to the device’s unique ID.
PIN requirement will be disabled if the user wipes the device or flash an older firmware version.

## Flash Snapshot - Anti-tamper Tool
### Introduction
Once a PIN is defined, users can generate a 'flash snapshot' to verify whether the flash content has been altered.

The flash snapshot will translate the content of the flash, tied to user's PIN and micro-controller's unique ID to an easy to recognize image and two anti-tamper words.

A single bit flip in flash will result in a completely different image and words.

As the snapshot evaluates the whole flash, firmware updates, simple configuration changes, or new stored data, like an encrypted mnemonic, will result in new, completely different snapshot.

In order to make the snapshot immune to being mocked, the PIN and K210 chip's unique ID are hashed previously than the flash.

`hash(PIN -> UID -> Flash content)` -> Image + words

### Possible Attack Scenarios
In a scenario where the attacker has replaced the firmware and the user inputs the correct PIN, it’s important to consider how the tampered firmware might try to bypass the verification process. Here's the key question you’re asking:

Can the tampered firmware, after learning the correct PIN, mock the correct hash for `hash(PIN + firmware)` when it doesn’t have the original firmware but knows the hash result of the original firmware?

#### The Challenge for the Attacker
Let’s break down how the tampered firmware might attempt to generate the correct hash:

1. Tampered Firmware Has Knowledge of the Original Hash:

- The attacker knows the hash of the original firmware (`hash(flash data)`), but they don’t have the original firmware content itself.
- The attacker cannot simply reverse the hash to retrieve the original firmware, as cryptographic hash functions (like SHA-256) are one-way functions.

2. Attacker Receives the User’s PIN:

- After the user enters the PIN, the tampered firmware now knows the correct PIN.
- However, the tampered firmware still needs to compute hash(PIN + original flash data) to match what the original firmware would have produced.

3. Hash Function with Sequential Data Blocks:

- The hash depends on both the PIN (hashed first) and the original flash data (hashed sequentially in subsequent blocks).

- The tampered firmware cannot access the full original original flash data to feed into the hash function, meaning it can’t produce the correct sequential hash based on `hash(PIN + original flash data)`.

#### Why the Tampered Firmware Can't Mock the Hash:
- Impossibility of Reconstructing the Original Hash: Even though the tampered firmware knows hash(original flash data) and the user’s PIN, it cannot generate the correct hash `hash(PIN + original flash data)` for the following reasons:

- Hashing is Sensitive to Input Order: The hash function processes the PIN and then the flash data sequentially. The tampered firmware can’t simply "insert" the original flash data hash into this process. To generate the correct overall hash, the tampered firmware would need access to the actual original flash content itself, not just its hash.

- Hash Function Properties: Cryptographic hash functions, like SHA-256, are collision-resistant and deterministic. The tampered firmware can’t produce the same hash unless it provides the exact same sequence of data blocks that were used to create the original hash. The hash function works on the entire content (PIN + flash data), not just their final hashes.

- Time of PIN Entry: If the PIN is entered after the device has already booted the tampered firmware, the attacker would have no chance to modify the hash input to simulate the original flash data hash without full knowledge of the firmware’s content.

#### Possible Tampered Firmware Strategies (and Why They Fail):
1. Precompute and Store `hash(PIN + flash data)`:

- If the tampered firmware precomputes `hash(PIN + flash data)` using the original firmware and stores it somewhere, it could potentially return the correct hash after receiving the PIN.
- This strategy only works if the attacker had access to both the PIN and the original firmware at the time of tampering, which contradicts the purpose of using an unknown PIN.

2. Use of Stored `hash(flash data)`:

- The attacker might try to store `hash(flash data)` from the original firmware and somehow combine it with the PIN to mock the final hash.
- But, the process of hashing PIN + firmware as a block sequence ensures that merely combining the final hashes won’t produce a valid result.

#### Conclusion:
The tampered firmware cannot mock the correct result of `hash(PIN + flash data)` unless it has access to the exact original firmware content. Simply knowing `hash(flash data)` or even precomputing certain hashes in advance wouldn’t help, because the hash function operates sequentially on the combined data (PIN + flash data).

In conclusion, this approach provides strong security because:

- The PIN remains secret and is only input by the user.
- The 'flash snapshot' hash depends on both the PIN and the entire flash content, making it infeasible for attackers to tamper with the firmware and pass verification without having full access to the original firmware.
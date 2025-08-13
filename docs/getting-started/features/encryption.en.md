## Introduction

Encryption is an advanced feature that offers enhanced protection to hide a "secret".  However, if used incorrectly, the consequence could be hiding a secret in a way that it cannot be recovered without another plain-text backup.  Before using this feature, it is highly suggested to become familiar with the rest of this document, and to heed the warnings contained herein.

### In General

Within `Settings / Encryption Settings`, preferences: `PBKDF2 Iterations` and `Encryption Mode` may be customized before loading a wallet.  Then, whenever encrypting -- and depending on what is being encrypted, krux will use those preferences to make better choices that fit the particular secret being encrypted.  The result will be an encrypted KEF envelope, exported as a QR or saved to SD.

While encrypting, the user may be offered to override their encryption preferences, or may actually have a choice to select a particular version.  Above all: **It is CRUCIAL for users to understand that the encryption `key` used MUST BE STRONG!** If a KEF envelope is created with a "weak" key and then shared online, or accessible to others, users should assume that it provides NO protection and that their secret will been leaked.


<img src="../../../img/maixpy_m5stickv/load-mnemonic-kef-via-qr-250.png" align="right" class="m5stickv">
<img src="../../../img/maixpy_amigo/load-mnemonic-kef-via-qr-300.png" align="right" class="amigo">

When krux encounters data that appears to be an encrypted KEF envelope, the user will be prompted with a choice to "Decrypt?", displaying the KEF version, the envelope's ID (or label), and the number of PBKDF2 Key Iterations used at the time the envelope was created.  After confirmimg to decrypt, use the same `key` -- either typed or scanned, as was used orinally to encrypt the envelope.  Once decrypted, krux will use the resulting plain-text within the context it was loaded.  If the user instead declines to decrypt, krux will use the data as is, likely resulting in an error since a KEF envelope is effectively useless data -- without decryption.

<div style="clear: both"></div>

KEF envelopes are intentionally vague, without any description of what they contain or what `key` should be used to decrypt them.  It is up to the user to keep track of this -- by recording what each envelope contains and how to decrypt it, and by using an ID at the time of encryption which will help the user recall its contents and find the right `key`.  While encrypting, krux will suggest an ID, then offer for the user to update it. For mnemonics: the suggested ID will be the wallet fingerprint w/o passphrase; for wallet output descriptors: it will be the generic policy for that wallet.

Within the Tools menu, users may experiment with [datum tool](../tools#datum-tool) for encrypting small to mid-sized contents (less than 50K bytes) and for decrypting KEF envelopes.

### Regarding BIP39 Mnemonics

There are many possible security layers one could add to protect a wallet’s private key. Adding a BIP39 passphrase to the mnemonic is the most common method. Encrypting a BIP39 mnemonic has a similar use case as the BIP39 passphrase, but the user experience may differ depending on the implementation. The main difference between BIP39 passphrases and Krux’s encrypted mnemonic implementation is that when users type the wrong key, encrypted mnemonics will return an error instead of loading a different wallet, as BIP39 passphrases do. This difference may be desired or not. The implementation also has the convenience of storing a mnemonic ID together with the stored, or QR code, encrypted mnemonic. Lastly, a mnemonic may be encrypted after a wallet has already been initialized to better protect that secret, and may be encrypted with different keys for the same wallet.  Mnemonic encryption, with its own key, can be used together with BIP39 passphrase as an extra security layer.

## AES Modes-of-Operation

Krux uses standard AES encryption with modes-of-operation: ECB, CBC, CTR and GCM.  The user may set their preference within `Settings, Encryption Settings, Encryption Mode`.  Krux uses GCM as the default mode-of-operation, but you may have valid reasons for making your own choice, ie:

* maybe you want compatibility with other software or devices you use,
* maybe you want the smallest QR possible for high-entropy secrets like mnemonics or passhprases,
* etc.

### AES-ECB

ECB (Electronic Codebook) is a simpler method where data blocks are encrypted individually. This mode is faster and simpler to encrypt, resulting in QR codes with lower density that are easier to [transcribe](./QR-transcript-tools.md). It is generally considered less secure than others because it does not provide data chaining, meaning identical plaintext blocks would produce identical ciphertext blocks, making it vulnerable to pattern analysis. However, in Krux's implementation, encrypting plaintext via ECB which contains duplicate blocks has been intentionally disabled.

### AES-CBC

CBC (Cipher-block Chaining) is considered more secure than ECB. In the first data block, an initialization vector (IV) is used to add random data to the encryption. The encryption of subsequent blocks depends on the data from previous blocks, characterizing chaining. Tradeoffs are that encryption/decryption must be done in series and when encrypting, a camera snapshot will be needed to generate the IV, so it's a slower process.  The IV will always stored together with encrypted data, making encrypted QR codes denser and harder to [transcribe](./QR-transcript-tools.md). This mode is often available on other microcontroller devices.

### AES-CTR
CTR (Counter Mode) like CBC is more secure than ECB, because of the use of an Initialization Vector, and also most efficient as a stream cipher, capable of encrypting and decrypting in parallel.  This mode is often available on other microcontroller devices.

### AES-GCM
GCM (Galois Counter-Mode).  Similar to CBC and CTR, the cipher is initialized with a nonce from a camera snapshot.  Like CTR, it is a paralellizable stream cipher, and also adds Galois Field authentication inherently. Capable of optimized performance, with built-in authentication and ease of implementation, this mode is the krux default unless the user has selected otherwise.

## Initialization Vector

Modes ECB, CBC, and GCM use an Initialization Vector (IV), where IV is better termed `nonce` for GCM.  The IV will be generated from a snapshot taken with the camera.  It is a fixed-size input value used to initialize the cipher, adding randomness to the encryption, and ensuring that data encrypted with the same key will produce different ciphertexts each time. The IV, or nonce, is not secret and will be transmitted along with the ciphertext. However, like any nonce, it should not be reused to maintain security.

## Key Stretching (PBKDF2 Iterations)

When you enter the encryption key, it is not directly used to encrypt your data. In order to protect against brute force attacks, the user supplied key is derived multiple times -- stretched to 256 bits via `pbkdf2_hmac_sha256`. PBKDF2 (Password-Based Key Derivation Function) Iterations refer to the number of derivations that will be performed over your key -- as the `password` -- `salted` with an ID, prior to encrypting/decrypting your secret.  Users may set a preferred `PBKDF2 Iterations` value in `Encryption Settings`, then krux will propose a slightly different value -- within a 10% delta, whenever encrypting.


## KEF Encryption Format
When krux encrypts a secret, the result is a `KEF Envelope` -- which is a series of bytes.  Each envelope is constructed similarly, containing fixed-length and variable-length fields representing: a custom `ID` for the envelope, a `Version`, number of PBKDF2 `Iterations`, and a `Cipher PayLoad`, so that any devices or software supporting KEF may recognize the envelope and know how to decrypt it -- given the correct `key`.  These fields, within each KEF envelope are:

| ID length (1) | ID (2) | Version (3) | Key Derivations (4) | Cipher PayLoad (5, 6, and 7) |
| :---: | :---: | :---: | :---: | :---: |
| 1 Byte | Variable | 1 Byte | 3 Bytes | Variable |

* **Visible data** (1 to 4):
    * **(1)** Mnemonic ID length (1 Byte).
    * **(2)** Mnemonic ID (variable length): Custom `ID` (wallet fingerprint for mnemonics).
    * **(3)** Version (1 Byte): Version of encryption method; currently twelve are available -- details later.
    * **(4)** key derivation Iterations (3 bytes): Number of PBKDF2 key derivations. if <= 10,000, multiplied by 10,000.
* **Cipher PayLoad** (5, 6, and 7):
    * **(5)** IV (12 or 16 bytes, optional): Initialization Vector for modes: CBC or CTR, and nonce for GCM.
    * **(6)** Encrypted Ciphertext.
    * **(7)** Authentication/validation data (3, 4, or 16 bytes).

## KEF Version Details
While all KEF envelopes share the above format, each version differs -- offering choices to the user, as trade-offs that may better fit a particular use-case.  For technical details, see: [KEF specifications](./kef-specifications.md)

| Version | Name       | Mode | IV | Compressed | Intended Use Case                 |
|---------|------------|------|----|------------|-----------------------------------|
|       0 | AES-ECB v1 | ECB  | -- | --         | Legacy: mnemonic entropy          |
|       1 | AES-CBC v1 | CBC  | 16 | --         | Legacy: mnemonic entropy          |
|         |            |      |    |            |                                   |
|       5 | AES-ECB    | ECB  | -- | --         | Smallest QR; mnemonic, passphrase |
|       6 | AES-ECB +p | ECB  | -- | --         | General Mid-sized                 |
|       7 | AES-ECB +c | ECB  | -- | Yes        | Large; repetitive text            |
|         |            |      |    |            |                                   |
|      10 | AES-CBC    | CBC  | 16 | --         | Small, high-entropy               |
|      11 | AES-CBC +p | CBC  | 16 | --         | General mid-sized                 |
|      12 | AES-CBC +c | CBC  | 16 | Yes        | General large                     |
|         |            |      |    |            |                                   |
|      15 | AES-CTR    | CTR  | 12 | --         | General mid-sized                 |
|      16 | AES-CTR +c | CTR  | 12 | Yes        | General large                     |
|         |            |      |    |            |                                   |
|      20 | AES-GCM    | GCM  | 12 | --         | Default; General mid-sized        |
|      21 | AES-GCM +c | GCM  | 12 | Yes        | Default; General large            |
|         |            |      |    |            |                                   |


## Considerations
Storage of encrypted secrets on the device or SD cards are meant for convenience only and should not be considered a long-term form of backup. Always make a physical backup of your keys that is independent from electronic devices and test recovering your wallet from this backup before you send funds to it. Flash storage can degrade over time and may be subject to permanent damage, resulting in the loss of stored information.

Remember that any encrypted secret is protected by the key you defined to encrypt it. If the defined [key is weak](https://www.hivesystems.com/blog/are-your-passwords-in-the-green), your encrypted mnemonic and other secrets will **not be protected**. If you have stored sensitive secrets in the device's internal flash memory using a [weak key](https://www.hivesystems.com/blog/are-your-passwords-in-the-green), the best way to undo this is to [erase user's data](tools.md/#erase-users-data).


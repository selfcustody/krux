## Introduction

There are many possible security layers one could add to protect a wallet’s private key, adding a passphrase to the mnemonic is the most common. To encrypt a mnemonic would have similar use case as the passphrase, but, depending on how it is done, the user experience could be different. The main difference from passphrases to Krux’s encrypted mnemonic implementation is that when users type the wrong key, instead of loading a different wallet, encrypted mnemonics will return an error. This is not considered an advantage, but a difference, that may be desired or not. The implementation also has the convenience of storing a mnemonic ID together with stored or QR code encrypted mnemonics. Mnemonic encryption, with its own key, can be used together with passphrases as an extra security layer.

## Encrypted QR Codes Data and Parsing
In search of efficiency and smaller QR codes, all data is converted to bytes and organized like a Bitcoin transaction, with variable and fixed length fields. The following data is present on the QR code:

| ID length (1) | ID (2) | Version (3) | Key Derivations (4) | IV (5) | Encrypted Mnemonic (6) | Validation Block (7) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 Byte | Variable | 1 Byte | 3 Bytes | 16 Bytes <br>(optional) | 16 Bytes (12 words) <br>32 Bytes (24 words) | 16 Bytes |

* **Visible data** (1 to 4):
    * **(1)** Mnemonic ID length (1 Byte).
    * **(2)** Mnemonic ID (variable lenght): Custom ID or wallet fingerprint.
    * **(3)** Version (1 Byte): Version of encryption method, currently two are available:
        - 0: AES-ECB-PBKDF2: Electronic Codebook with PBKDF2 key derivation.
        - 1: AES-CBC-PBKDF2: Cypher Block Chaining with PBKDF2 key derivation.
    * **(4)** Key derivation iterations (3 Bytes): Number of PBKDF2 key derivations times 10,000.
* **Cipher data** (5 to 7):
    * **(5)** IV (16 Bytes-optional): Initial vector for AES-CBC encryption, possibility to be nonce for future 	AES-CTR or other encryption methods.
    * **(6)** Encrypted Mnemonic (16 Bytes - 12 words, 32 Bytes - 24 words): Mnemonic ciphertext.
    * **(7)** Validation block (16 Bytes): Currently using first 16 bytes of sha256 of the mnemonic bytes as checksum, could be used in future to store AES-AEX validation tag.

## Considerations
Storage of encrypted mnemonics on the device or SD cards are meant for convenience only and should not be considered a form of backup. Always make a physical backup of your keys that is independent from electronic devices and test recovering your wallet from this backup before you send funds to it.

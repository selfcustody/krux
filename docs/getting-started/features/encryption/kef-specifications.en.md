# KEF Encryption Format -- Technical Specification

...`The K stands for "KEF"` --anon


## Motivation

In the autumn of 2023, during the lead-up to **krux release 23.09.0**, contributors proposed a method of encrypting bip39 mnemonics that could be stored in SPI-flash, on sdcard, and/or exported to QR. Regarding the encrypted-mnemonic QR format: the layout proposed was interesting as an extensible, lite-weight, self-describing envelope that has been appreciated by users ever since.

...`"Wen passphrases, output descriptors, PSBTs, and notes?"` --plebs

This specification, and its accompanying implementation and test-suite are the result of months of exploration into improvements meant to better define, test, and extend the original encryption format that we'll refer to as KEF. It proposes ten new versions, extending its usefulness to more than mnemonics, targeting variable-length strings up to moderately sized PSBTs, flexibility to choose among four AES modes of operation, with-or-without compression, and versions optimized to result in a smaller envelope.

Above all, this specification aims to be supported by as many projects as would consider adopting it, so that users are not "locked" into a particular project when recovering their secrets. Corrections and refinement to, and scrutiny of this specification are appreciated. Proposals for more `versions` are welcome, provided they offer "value" to the user and fit within the scope of this system. Once released, because it cannot be known how many KEF envelopes may exist in-the-wild, changes to any particular version must remain backwards compatible for decryption. Adopting implementations are free to support any KEF versions they wish to support, for decryption-only or for both encryption and decryption -- with the expectation that claims-of-support made are clear and precise about what is supported.

## Overview

This system encrypts arbitrary plaintext into a versioned, self-describing, **KEF envelope** which includes:

* custom identity/label `len_id` and `id`
* version `v`
* pbkdf2-hmac iterations `i`
* and cipher-payload `cpl`

where cipher-payload `cpl` consists of:

* Initialization-Vector/Nonce (if applicable) `IV`
* ciphertext
* and authentication/validation data `auth`

KEF versions offer combinations of different **modes-of-operation**, **authentication strategies**, **padding strategies**, and **compression**, all selected via a numeric version code (0 - 21).

* Available version codes are: 0, 1, 5, 6, 7, 10, 11, 12, 15, 16, 20, 21. Not all integers in the range are assigned, and implementations may disable versions or modes.

Currently, all versions use AES and derive the 256-bit encryption key `k` as:
```
k = pbkdf2_hmac_sha256(K, id, i)
```

where:

* `K` = user-provided password/key material (bytes; if str: non-normalized encode as utf-8)
* `id` = salt (variable-length, prepended to envelope; bytes: if str: non-normalized encode as utf-8)
* `i` = iteration count (3 bytes, big-endian)

The stored iteration field `i` MUST be ≥ 1. The effective PBKDF2 iteration count is `i` if `i > 10,000`, otherwise `i * 10,000`.

Compression (when enabled) uses zlib.compress(wbits=-10) or raw deflate(micropython).

Authentication has three forms:

* When the mode has built-in authentication, like GCM: `auth` is a truncated auth tag
* When the mode does not have built-in authentication, `auth` is a truncated sha256 digest whose pre-image is of two forms:
    * if `auth` will be encrypted with plaintext, hidden, it is `sha256(plaintext)`
    * if `auth` will be appended to ciphertext, exposed, it is `sha256(version || IV || plaintext || derived-k)`

## Generalizations Regarding Implementation

It is expected that any implementation can decrypt a KEF envelope that was created by itself on the same device. Implementations are asked to make their "best-effort" to be capable of decrypting KEF envelopes for versions they support which were created by other implementations or on other devices -- but this will not always be possible. Decrypting large KEF envelopes on severely constrained devices, or ones created with flawed implementations is unrealistic. Therefore, in such cases it is the responsibility of the user to find an implementation and device capable of decrypting their KEF envelope, or to have a non-KEF form of recovery.

* Be strict while encrypting. Be tolerant -- and non-specific about errors, when decrypting.

* At its base, **a KEF envelope is a format of bytes -- so are all of its inputs**. Remember this when converting strings gathered for the `key` and `id`. Consider being strict about offering a reasonably minimal set of characters, common and available on other devices and/or international keyboards when encrypting -- then encode unicode codepoints (if not ascii) directly to their utf-8 representations without normalization. For decryption, more characters could be offered when gathering the `key`, and multiple normalization strategies may be tried, so that secrets may be recovered. Consider some capability of displaying both `key` and `id` as bytes, and gathering the `key` as bytes either directly or via hex/base64 conversion if necessary, to enable recovery. Do NOT assume that a user originally used a particular implementation to encrypt a KEF envelope.

* **On the importance of a STRONG user-supplied `key`** This cannot be stressed enough to each user of KEF. While KEF allows for key-stretching via `id` and `iterations`, and offers modes that require a random `IV` / Nonce, **KEF offers no expectation of security for a weak user-supplied `key`**. Consider making this point clear to users before encrypting and/or offer an indication of `key` strength once gathered. If a KEF envelope has been created with a "weak" `key` and stored accessible to others, user should assume that their secret has been leaked. Consider encouraging users to make sane choices about the characters they use in their `key`, aware that non-ascii characters offered by one implementation may not be easy to enter on another, or that a recognizable glyph may not exist on other devices for them to verify their `key` when decrypting.

* **On security** Not all KEF `versions` offer the same security guarantees, so implementors MUST take care to protect against "unsafe" usage. As already mentioned: be strict and fail to encrypt when "unsafe"; be tolerant and vague while decrypting. Support for decrypt-only on a particular version is perfectly valid should an implementation choose to "nudge" users towards a more-secure version where it supports full encrypt/decrypt functionality.

    * **On mode ECB**: Repeated blocks would leak patterns within ciphertext. Therefore, be strict -- refuse to encrypt using mode ECB whenever duplicate blocks are detected. Consider a compressed version which may resolve this.

    * **On block modes with NUL padding** Problems to unpad can arise decrypting where valid NUL bytes are confused with removable padding.
        * If `auth` is appended to plaintext before padding AND the `auth` bytes end in 0x00: be strict -- refuse to encrypt. Consider a version with safe padding.
        * If `auth` is appended to ciphertext after padding/encryption AND the `plaintext` bytes end in 0x00: be strict -- refuse to encrypt. Consider a version with safe padding.
        * Do not assume that other implementations adhere to the above. Be tolerant and make reasonable efforts to successfully recover secrets when decrypting. Offering a warning to users AFTER successful decryption in this case may be appropriate.

* **On modes that require IV or Nonce** Take precautions to ensure that this value is random and not reused. ie: Natural entropy captured from camera sensor (user validated and/or analyzed to ensure sensor is working / high entropy).

* **On common `bytes` encodings** Outside the strict scope that **KEF envelopes are a format of bytes** but related to this topic: implementations may be presented with encoded strings that are likely to represent bytes. For instance: base64, base43 (from electrum), base32, or hex might be representations of a KEF envelope that was previously encoded for transport. As you continue reading, it will become clear that with any bytestring, one may recognize a KEF envelope by:
    1. reading the first byte as an integer `len_id`,
    2. jumping that many bytes, over the `id`, to read the next byte as an integer `version`,
    3. if that version represents a known and supported KEF version, then the rest of the envelope may be parsed via that version's KEF rules.
    4. if parsing succeeds without errors, it is likely to be a KEF envelope and a decryption user-interface should be offered to the user.
    While the user likely knows, the process instance of a KEF implementation will learn definitively, only AFTER a successful decryption, that a bytestring was indeed a KEF envelope. If at any point along this process, an implementation finds that `version` is unknown/disabled, or if parsing fails, the expected action is NOT TO RAISE SPECIFIC ERRORS regarding this inspection. Rather, the appropriate action is to assume it was not a KEF envelope and to treat the data under another context: ie: "Unknown". Similarly, as mentioned above, being vague about errors during decryption implies that "Failed!" may be a sufficient response for any error, instead of leaking to a potential attacker specific details about the failure.

* **On Iterations** Consider that users may want to decrypt KEF envelopes on various resource-constrained devices. There is a minimum 10,000 iterations imposed in any KEF envelope (a value of 1 would be 10,000 pbkdf2_hmac iterations), and the maximum could be as high as 100,000,000 (a value of 10,000), but depending on the device used, 500,000 might be too high. Also, since the user-supplied `key` is stretched by this value, consider offering a range to users -- then adding a small `delta` as extra bits of entropy to derive different AES-256 keys that would otherwise be the same in the event the user re-uses the same `key`, `id` and `iterations` when creating many KEF envelopes.

* **On truncated Authentication** At first glance it may be concerning that `auth` bytes for many versions have been truncated and are trivially "weak". Note that KEF's use-case for authentication is to validate that the user has correctly entered their decryption `key`. In the worse case, "false-authenticated" success will occur at a rate of 1:16M (or 1:4B for others) if using an incorrect decryption `key`; similar if an attacker has modified the KEF envelope. In these "false-authenticated" success cases, data will result from decryption, but that data will NOT be the original secret or plaintext; it will be of no value.

* **On compressed versions** KEF is strict about compressing via "raw headerless deflate()" with a "wbits" window
of **10 bits (1024B)** so that other implementations on restricted hardware are capable to decompress and recover
any KEF envelope.  However, implementations may choose to use a higher wbits window for decompression.

## Common Structure of a KEF Envelope

All KEF versions' encrypted outputs follow this layout:
```
len_id + id + v + i + cpl
```

| Field     | Size           | Description |
|-----------|----------------|-------------|
| `len_id`  | 1 byte         | Length of `id` (0 - 252) |
| `id`      | `len_id` bytes | Salt for PBKDF2 |
| `v`       | 1 byte         | Version number |
| `i`       | 3 bytes        | Iteration count (big-endian; if <= 10,000: *= 10,000) |
| `cpl`     | Variable       | Cipher PayLoad (IV + ciphertext + auth) |

The Cipher PayLoad `cpl` structure varies by version. 

---

### Versions - Details

Details for currently-available versions of KEF follow. The top half of each section is pre-formatted `self-doc` text, built from the reference implementation's test-suite (using KEF `VERSION` constants as KEF's rule-set). The bottom half of each section with rich-formatted text was initially LLM-generated, prompted with the `self-doc` text, then curated and edited by hand.


#### v0: "AES-ECB v1"

```
[AES-ECB v1] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =0
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: e.encrypt(P + auth + pad)
e: AES(k, ECB)
auth: sha256(P)[:16]
pad: NUL
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: ECB
* **IV**: None
* **Padding**: NUL bytes to block boundary
* **Authentication**: First 16 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: LEGACY: consider using version 5; encryption of 16 or 32 BIP39 entropy bytes
* **Security Note**: When encrypting: fail "unsafe" if duplicate plaintext blocks, fail "unsafe" if auth ends 0x00

---

#### v1: "AES-CBC v1"

```
[AES-CBC v1] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =1
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: iv + e.encrypt(P + auth + pad)
iv: 16b
e: AES(k, CBC, iv)
auth: sha256(P)[:16]
pad: NUL
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: CBC
* **IV**: 16 bytes
* **Padding**: NUL bytes to block boundary
* **Authentication**: First 16 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[iv (16)] + [ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: LEGACY: consider using version 10; encryption of 16 or 32 BIP39 entropy bytes
* **Security Note**: When encrypting: do not re-use IV, fail "unsafe" if auth ends 0x00

---

#### v5: "AES-ECB"

```
[AES-ECB] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =5
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: e.encrypt(P + pad) + auth
e: AES(k, ECB)
pad: NUL
auth: sha256(v + P + k)[:3]
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: ECB
* **IV**: None
* **Padding**: NUL bytes to block boundary
* **Authentication**: First 3 bytes of `SHA256(version_byte + plaintext + derived_key)`, exposed
* **cpl layout**: `[ciphertext] + [auth (3)]`
* **Use Case**: smallest KEF envelope for high-entropy secrets (BIP39 entropy, passphrase, cryptographic keys)
* **Security Note**: When encrypting: fail "unsafe" if duplicate plaintext blocks, fail "unsafe" if plaintext ends 0x00

---

#### v6: "AES-ECB +p"

```
[AES-ECB +p] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =6
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: e.encrypt(P + auth + pad)
e: AES(k, ECB)
auth: sha256(P)[:4]
pad: PKCS7
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: ECB
* **IV**: None
* **Padding**: PKCS7 to block boundary
* **Authentication**: First 4 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: Mid-sized variable length plaintext
* **Security Note**: When encrypting: fail "unsafe" if duplicate plaintext blocks

---

#### v7: "AES-ECB +c"

```
[AES-ECB +c] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =7
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: e.encrypt(zlib(P, wbits=-10) + auth + pad)
e: AES(k, ECB)
auth: sha256(zlib(P, wbits=-10))[:4]
pad: PKCS7
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: ECB
* **IV**: None
* **Compression**: `zlib.compress(P, wbits=-10)`, - raw deflate
* **Padding**: PKCS7 to block boundary
* **Authentication**: First 4 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[ciphertext]` (auth embedded after compression, before padding/encryption)
* **Use Case**: Mid-sized variable length plaintext
* **Security Note**: like others, when encrypting: fail "unsafe" if duplicate blocks -- unlikely with compression 

---

#### v10: "AES-CBC"

```
[AES-CBC] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =10
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: iv + e.encrypt(P + pad) + auth
iv: 16b
e: AES(k, CBC, iv)
pad: NUL
auth: sha256(v + iv + P + k)[:4]
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: CBC
* **IV**: 16 bytes, random, prepended in `cpl`
* **Padding**: NUL bytes to block boundary
* **Authentication**: First 4 bytes of `SHA256(v + iv + P + k)`, exposed
* **cpl layout**: `[iv (16)] + [ciphertext] + [auth (4)]`
* **Use Case**: Mnemonics, passphrases, short secrets
* **Security Note**: When encrypting: do not re-use IV, fail "unsafe" if plaintext ends 0x00

---

#### v11: "AES-CBC +p"

```
[AES-CBC +p] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =11
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: iv + e.encrypt(P + auth + pad)
iv: 16b
e: AES(k, CBC, iv)
auth: sha256(P)[:4]
pad: PKCS7
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: CBC
* **IV**: 16 bytes, random, prepended in `cpl`
* **Padding**: PKCS7 to block boundary
* **Authentication**: First 4 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[iv] + [ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: General mid-sized plaintext
* **Security Note**: When encrypting: do not re-use IV

---

#### v12: "AES-CBC +c"

```
[AES-CBC +c] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =12
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: iv + e.encrypt(zlib(P, wbits=-10) + auth + pad)
iv: 16b
e: AES(k, CBC, iv)
auth: sha256(zlib(P, wbits=-10))[:4]
pad: PKCS7
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: CBC
* **IV**: 16 bytes, random, prepended in `cpl`
* **Compression**: `zlib.compress(P, wbits=-10)`, - raw deflate
* **Padding**: PKCS7 to block boundary
* **Authentication**: First 4 bytes of `SHA256(compressed plaintext)`, hidden
* **cpl layout**: `[iv (16)] + [ciphertext]` (auth embedded after compression, before padding/encryption)
* **Use Case**: Larger plaintext
* **Security Note**: When encrypting: do not re-use IV

---

#### v15: "AES-CTR"

```
[AES-CTR] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =15
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: iv + e.encrypt(P + auth)
iv: 12b
e: AES(k, CTR, iv)
auth: sha256(P)[:4]
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: CTR
* **IV**: 12 bytes, random, prepended in `cpl`
* **Padding**: None
* **Authentication**: First 4 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[iv (12)] + [ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: Small to mid-sized plaintext
* **Security Note**: When encrypting: do not re-use IV

---

#### v16: "AES-CTR +c"

```
[AES-CTR +c] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =16
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: iv + e.encrypt(zlib(P, wbits=-10) + auth)
iv: 12b
e: AES(k, CTR, iv)
auth: sha256(zlib(P, wbits=-10))[:4]
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: CTR
* **IV**: 12 bytes, random, prepended in `cpl`
* **Compression**: `zlib.compress(P, wbits=-10)`, - raw deflate
* **Padding**: None
* **Authentication**: First 4 bytes of `SHA256(compressed plaintext)`, hidden
* **cpl layout**: `[iv (12)] + [ciphertext]` (auth embedded after compression, before padding/encryption)
* **Use Case**: Larger plaintext
* **Security Note**: When encrypting: do not re-use IV

---

#### v20: "AES-GCM"

```
[AES-GCM] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =20
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: iv + e.encrypt(P) + auth
iv: 12b
e: AES(k, GCM, iv)
auth: e.authtag[:4]
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: GCM
* **IV/Nonce**: 12 bytes, random, prepended in `cpl`
* **Padding**: None
* **Authentication**: First 4 bytes of GCM authtag, exposed
* **cpl layout**: `[iv (12)] + [ciphertext] + [auth (4)]`
* **Use Case**: DEFAULT: Small to mid-sized plaintext
* **Security Note**: When encrypting: do not re-use IV/Nonce

---

#### v21: "AES-GCM +c"

```
[AES-GCM +c] KEF bytes: len_id + id + v + i + cpl
len_id: 1b
id: <len_id>b
v: 1b; =21
i: 3b big; =(i > 10K) ? i : i * 10K
cpl: iv + e.encrypt(zlib(P, wbits=-10)) + auth
iv: 12b
e: AES(k, GCM, iv)
auth: e.authtag[:4]
k: pbkdf2_hmac_sha256(K, id, i)
```

* **Mode**: GCM
* **IV/Nonce**: 12 bytes, random, prepended in `cpl`
* **Compression**: `zlib.compress(P, wbits=-10)`, - raw deflate
* **Padding**: None
* **Authentication**: First 4 bytes of GCM authtag, exposed
* **cpl layout**: `[iv (12)] + [ciphertext] + [auth (4)]`
* **Use Case**: DEFAULT: Larger plaintext
* **Security Note**: When encrypting: do not re-use IV/Nonce

---

#### Summary Table

| Ver | Name       | Mode | IV | Padding | Compress | Authentication Method  | Auth        | Intended Use Case       |
|-----|------------|------|----|---------|----------|------------------------|-------------|-------------------------|
| 0   | AES-ECB v1 | ECB  | –  | NUL     | No       | SHA256(plaintext)[:16] | 16 B        | Legacy high-entropy     |
| 1   | AES-CBC v1 | CBC  | 16 | NUL     | No       | SHA256(plaintext)[:16] | 16 B        | Legacy high-entropy     |
| 5   | AES-ECB    | ECB  | –  | NUL     | No       | SHA256(v+P+k)[:3]      | 3 B exposed | Small, high-entropy     |
| 6   | AES-ECB +p | ECB  | –  | PKCS7   | No       | SHA256(plaintext)[:4]  | 4 B         | General Mid-sized       |
| 7   | AES-ECB +c | ECB  | –  | PKCS7   | Yes      | SHA256(compressed)[:4] | 4 B         | Large; duplicate blocks |
| 10  | AES-CBC    | CBC  | 16 | NUL     | No       | SHA256(v+iv+P+k)[:4]   | 4 B exposed | Small, high-entropy     |
| 11  | AES-CBC +p | CBC  | 16 | PKCS7   | No       | SHA256(plaintext)[:4]  | 4 B         | General mid-sized       |
| 12  | AES-CBC +c | CBC  | 16 | PKCS7   | Yes      | SHA256(compressed)[:4] | 4 B         | General large           |
| 15  | AES-CTR    | CTR  | 12 | –       | No       | SHA256(plaintext)[:4]  | 4 B         | General mid-sized       |
| 16  | AES-CTR +c | CTR  | 12 | –       | Yes      | SHA256(compressed)[:4] | 4 B         | General large           |
| 20  | AES-GCM    | GCM  | 12 | –       | No       | GCM authtag[:4]        | 4 B exposed | Best, General mid-sized |
| 21  | AES-GCM +c | GCM  | 12 | –       | Yes      | GCM authtag[:4]        | 4 B exposed | Best, General large     |

---

## KEF Implementation Concepts

Using examples from, and as an introduction to the reference [KEF implementation](https://github.com/selfcustody/krux/blob/develop/src/krux/kef.py), we'll quickly cover some basic concepts that may be helpful in getting started with your own KEF implementation.

### Version Configuration
From the version details and summary table: note that all KEF versions can be defined as having a set of parameters which define that version's KEF rules. For ease-of-maintenance -- and also for extending later, it may be useful to store these in a central configuration. Within our sample reference, these are defined by constants `kef.VERSIONS`, `kef.MODE_NUMBERS` and `kef.MODE_IVS`.

### Choosing a Version
As soon as you have data to hide, KEF offers choices for which version to use. That choice may be made by the user, or by the implementation, based on what is being hidden, compatibility with others, and how it may be stored/transported. The sample reference uses a function named `kef.suggest_versions()` to make a choice based on user's preferred mode-of-operation, the plaintext being hidden, then optimizes for a smaller KEF envelope.

### Encryption, Decryption, and Authentication
Once you know what you need to hide and how you want to hide it, you'll need something to perform the encryption. You'll start by stretching the user-supplied `key`, salted with `id` for a number of `iterations` to **derive** the 256-bit AES key. Next you'll need to **encrypt** the plaintext (possibly with a random `IV` / Nonce) according to the chosen KEF version, so that the result is a cipher-payload `cpl`. To reverse this process, you'll need something to **decrypt** and **authenticate** the cipher-payload `cpl` -- again according to the rules of the particular KEF version. The sample reference uses a class named `kef.Cipher` for stretching the `key`, encrypting plaintext to `cpl`, and decrypting / authenticating `cpl` back into plaintext.

### Padding and Unpadding
Depending on the mode-of-operation of your version, you may need to **pad** the plaintext. If so, there will also be a need to **unpad** during the decryption process. The sample reference uses functions named `kef.pad()` and `kef.unpad()`, which are called from inside the `kef.Cipher` object when encrypting and decrypting.

### Data Compression: Deflate & Inflate
Depending on the version, you may also need to **deflate** plaintext so that it is compressed before encryption. Likewise, you'll need to **reinflate** it after decryption to decompress the plaintext. The sample reference uses functions named `kef.deflate()` and `kef.reinflate()`, which are also called from inside the `kef.Cipher` object when encrypting and decrypting.

### Metadata Wrapping and Unwrapping
After encryption, you'll need to **wrap** the `id`, `version`, `iterations` and `cpl` into a valid KEF envelope. Likewise, in order to reveal something hidden within a KEF envelope, you'll first need to **unwrap**, or parse it into its constituent parts (`id`, `version`, `iterations`, `cpl`) so that it may be decrypted as described above. The sample reference uses functions `kef.wrap()` and `kef.unwrap()` for these procedures.

### On Further Encoding KEF Envelopes
Outside the scope of this specification on KEF envelopes, which are strings of bytes, implementations will surely need to make choices about encoding/decoding schemes. Whether for QR transport, copy-pasting into messages, embedding into json documents, in-plain-sight within other document formats, or persisted in binary files, these choices are left to implementors.


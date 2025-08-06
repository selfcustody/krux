# KEF Encryption Format -- Specification
...`The K stands for "KEF"` --anon


## 1. Overview

This system encrypts arbitrary plaintext into a **versioned, self-describing KEF envelope** which includes:

* custom identity/label `len_id` and `id`
* Version `v`
* pbkdf2-hmac iterations `i`
* and cipher-payload `cpl`

where cipher-payload `cpl` consists of:

* Initialization-Vector/Nonce (if applicable) `IV`
* ciphertext
* and authentication/validation data `auth`

KEF versions offer combinations of different **modes-of-operation**, **authentication strategies**, **padding strategies**, and **compression**, all selected via a numeric version code (0 - 21).

Currently, all versions use AES and derive the 256-bit encryption key `k` as:
```
k = pbkdf2_hmac('sha256', K, id, i)
```

where:

* `K` = user-provided password/key material (bytes; if str: non-normalized encode as utf-8)
* `id` = salt (variable-length, prepended to envelope; bytes: if str: non-normalized encode as utf-8)
* `i` = iteration count (3 bytes, big-endian; if <= 10,000: multiplied by 10,000)


## 2. Generalizations Regarding Implementation

Above all, this specification aims to be supported by as many projects as would consider adoptng it, so that users are not "locked" into a particular project when recovering their secrets.  Corrections and refinement to this specification are welcome and appreciated. Proposals for more `versions` are welcome, provided they offer "value" to the user and "fit" within the scope of this system.  Once released, because we can never know how many KEF envelopes may exist in-the-wild, changes to any particular version must remain backwards compatible at least for decryption.  Adopting implementations are free to support any KEF versions they wish to support, for decryption-only or for both encryption and decryption -- with the expectation that claims-of-support made are clear and specific to what is supported.  Reference: latest [KEF implementation](https://github.com/selfcustody/krux/blob/develop/src/krux/kef.py) and [KEF test-suite](https://github.com/selfcustody/krux/blob/develop/tests/test_kef.py).

* Be strict while encrypting.  Be tolerant -- and non-specific about errors, when decrypting.

* At its base, **a KEF envelope is a format of bytes -- so are all of its inputs**.  Remember this when converting strings gathered for the encryption/decryption `key` and `id`.  Consider being strict about offering a reasonably minimal set of characters, common and available on other devices and/or international keyboards when encrypting -- then encode unicode codepoints directly to their utf-8 representations without normalization.  For decryption, more characters could be offered when gathering the `key` so that secrets may be recovered, and multiple normalization strategies may be tried.  Be capable of gathering these inputs as bytes, either directly or via hex/base64 conversion if necessary, to enable recovery.  Do NOT assume that a user originally used a particular implementation to encrypt a KEF envelope.

* Not all KEF `versions` offer the same security guarantees, so implementors must take care to protect against "unsafe" usage.  As already mentioned: be strict and fail to encrypt when "unsafe"; be tolerant and vague while decrypting. Support for decrypt-only on a particular version is perfectly valid should an implementation choose to "nudge" users towards a more secure version where it supports full encrypt/decrypt functionality.

    * When mode-of-operation is ECB, repeated blocks would leak patterns within ciphertext.  Therefore, refuse to encrypt using mode ECB whenever duplicate blocks are detected. Consider a compressed version which may resolve this.

    * When "unsafe" NUL padding is used for block modes, problems to unpad can arise decrypting where valid NUL bytes are confused with removable padding.
        * If `auth` is appended to plaintext before padding AND the `auth` bytes end in 0x00: be strict -- refuse to encrypt.  Consider a version with safe padding.
        * If `auth` is appended to ciphertext after padding/encryption AND the `plaintext` bytes end in 0x00: be strict -- refuse to encrypt.  Consider a version with safe padding.
        * Do not assume that other implementations adhere to the above.  Be tolerant and make "reasonable" efforts to successfully recover secrets when decrypting.  Offering a warning to users AFTER successful decryption in this case may be appropriate.

* Modes which require an `IV` (or nonce) should take precautions to ensure that this value is random and not reused. ie: Natural entropy captured from camera sensor (user validated and/or analyzed to ensure sensor is working / high entropy).

* Outside the strict scope that **KEF envelopes are a format of bytes** but related to this topic: implementations may be presented with encoded strings that are likely to represent bytes.  For instance: base64, base43 (from electrum), base32, or hex might be representations of a KEF Envelope that was previously encoded for transport.  As you continue reading, it will become clear that with any bytestring, one may recognize a KEF envelope by:
    1. reading the first byte as an integer `len_id`,
    2. jumping that many bytes, over the `id`, to read the next byte as an integer `version`,
    3. if that version represents a known and supported KEF version, then the rest of the envelope may be parsed via that version's KEF rules.
    4. If parsing succeeds w/o errors, it is likely to be a KEF envelope and a decryption UI should be offered to the user.
    While the user may know, the process instance of a KEF implementation will learn definitively, only AFTER a successful decryption, that a bytestring was indeed a KEF envelope.  If at any point along this process, an implementation finds that `version` is unknown/disabled, or if parsing fails, the expected action is NOT TO RAISE SPECIFIC ERRORS regarding this inspection. Rather, the appropriate action is to assume it was not a KEF envelope and to treat the data under another context: ie: "Unknown".  Similarly, as mentioned above, being vague about errors during decryption implies that "Failed!" may be a sufficient response for any error, instead of leaking to a potential attacker specific details about the failure.


## 3. Common Structure of a KEF Envelope

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


## 4. Specific Version Details

KEF Envelope details for currently available versions are below. Each section begins with a pre-formated `self-doc` text built from the reference implementation's test-suite (using KEF `VERSION` constants as KEF's rule-set).  The rich-formatted text which follows was initially AI-generated -- prompted with the `self-doc` text, then subsequently currated and edited by hand.


### Version 0: "AES-ECB v1"

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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: ECB
* **IV**: None
* **Padding**: NUL bytes to block boundary
* **Authentication**: First 16 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: DEPRECATED: use version 5 instead.  Legacy encryption of 16 or 32 BIP39 entropy bytes
* **Security Note**: When encrypting: fail "unsafe" if duplicate plaintext blocks, fail "unsafe" if auth ends 0x00


### Version 1: "AES-CBC v1"

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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: CBC
* **IV**: 16 bytes
* **Padding**: NUL bytes to block boundary
* **Authentication**: First 16 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[iv (16)] + [ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: DEPRECATED: use version 10 instead.  Legacy encryption of 16 or 32 BIP39 entropy bytes
* **Security Note**: When encrypting: do not re-use IV, fail "unsafe" if auth ends 0x00


### Version 5: "AES-ECB"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: ECB  
* **IV**: None
* **Padding**: NUL bytes to block boundary
* **Authentication**: First 3 bytes of `SHA256(version_byte + plaintext + derived_key)`, exposed
* **cpl layout**: `[ciphertext] + [auth (3)]`
* **Use Case**: smallest KEF envelope for high-entropy secrets (BIP39 entropy, passphrase, cryptographic keys)
* **Security Note**: When encrypting: fail "unsafe" if duplicate plaintext blocks, fail "unsafe" if plaintext ends 0x00


### Version 6: "AES-ECB +p"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: ECB  
* **IV**: None
* **Padding**: PKCS7 to block boundary
* **Authentication**: First 4 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: Mid-sized variable length plaintext
* **Security Note**: When encrypting: fail if duplicate plaintext blocks


### Version 7: "AES-ECB +c"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: ECB  
* **IV**: None
* **Compression**: `zlib.compress(P, wbits=-10)`, - raw deflate
* **Padding**: PKCS7 to block boundary
* **Authentication**: First 4 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[ciphertext]` (auth embedded after compression, before padding/encryption)
* **Use Case**: Mid-sized variable length plaintext
* **Security Note**: like others, when encrypting: fail if duplicate blocks -- unlikely with compression 


### Version 10: "AES-CBC"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: CBC  
* **IV**: 16 bytes, random, prepended in `cpl`
* **Padding**: NUL bytes to block boundary
* **Authentication**: First 4 bytes of `SHA256(v + iv + P + k)`, exposed
* **cpl layout**: `[iv (16)] + [ciphertext] + [auth (4)]`
* **Use Case**: Mnemonics, passphrases, short secrets
* **Security Note**: When encrypting: do not re-use IV, fail "unsafe" if plaintext ends 0x00


### Version 11: "AES-CBC +p"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: CBC  
* **IV**: 16 bytes, random, prepended in `cpl`
* **Padding**: PKCS7 to block boundary
* **Authentication**: First 4 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[iv] + [ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: General mid-sized plaintext
* **Security Note**: When encrypting: do not re-use IV


### Version 12: "AES-CBC +c"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: CBC  
* **IV**: 16 bytes, random, prepended in `cpl`
* **Compression**: `zlib.compress(P, wbits=-10)`, - raw deflate
* **Padding**: PKCS7 to block boundary
* **Authentication**: First 4 bytes of `SHA256(compressed plaintext)`, hidden
* **cpl layout**: `[iv (16)] + [ciphertext]` (auth embedded after compressions, before padding/encryption)
* **Use Case**: Larger plaintext
* **Security Note**: When encrypting: do not re-use IV


### Version 15: "AES-CTR"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: CTR  
* **IV**: 12 bytes, random, prepended in `cpl`
* **Padding**: None
* **Authentication**: First 4 bytes of `SHA256(plaintext)`, hidden
* **cpl layout**: `[iv (12)] + [ciphertext]` (auth embedded before padding/encryption)
* **Use Case**: Small to mid-sized plaintext
* **Security Note**: When encrypting: do not re-use IV


### Version 16: "AES-CTR +c"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: CTR  
* **IV**: 12 bytes, random, prepended in `cpl`
* **Compression**: `zlib.compress(P, wbits=-10)`, - raw deflate
* **Padding**: None
* **Authentication**: First 4 bytes of `SHA256(compressed plaintext)`, hidden
* **cpl layout**: `[iv (12)] + [ciphertext]` (auth embedded after compression, before padding/encryption)
* **Use Case**: Larger plaintext
* **Security Note**: When encrypting: do not re-use IV


### Version 20: "AES-GCM"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: GCM
* **IV/Nonce**: 12 bytes, random, prepended in `cpl`
* **Padding**: None
* **Authentication**: First 4 bytes of GCM-generated authtag, exposed
* **cpl layout**: `[iv (12)] + [ciphertext] + [auth (4)]`
* **Use Case**: DEFAULT: Small to mid-sized plaintext
* **Security Note**: When encrypting: do not re-use IV/Nonce


### Version 21: "AES-GCM +c"
   
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
k: pbkdf2_hmac(sha256, K, id, i)
```

* **Mode**: GCM
* **IV/Nonce**: 12 bytes, random, prepended in `cpl`
* **Compression**: `zlib.compress(P, wbits=-10)`, - raw deflate
* **Padding**: None
* **Authentication**: First 4 bytes of GCM authtag, exposed
* **cpl layout**: `[iv (12)] + [ciphertext] + [auth (4)]`
* **Use Case**: DEFAULT: Larger plaintext
* **Security Note**: When encrypting: do not re-use IV/Nonce


## 5. Summary Table

| Ver | Name       | Mode | IV | Padding | Compress | Authentication Method  | Auth        | Intended Use Case       |
|-----|------------|------|----|---------|----------|------------------------|-------------|-------------------------|
| 0   | AES-ECB v1 | ECB  | –  | NUL     | No       | SHA256(plaintext)[:16] | 16 B        | Legacy high-entropy     |
| 1   | AES-CBC v1 | CBC  | 16 | NUL     | No       | SHA256(plaintext)[:16] | 16 B        | Legacy high-entropy     |
| 5   | AES-ECB    | ECB  | –  | NUL     | No       | SHA256(v+P+k)[:3]      | 3 B exposed | Small, high-entropy     |
| 6   | AES-ECB +p | ECB  | –  | PKCS7   | No       | SHA256(plaintext)[:4]  | 4 B         | General Mid-sized       |
| 7   | AES-ECB +c | ECB  | –  | PKCS7   | Yes      | SHA256(compressed)[:4] | 4 B         | Large; if repetitive    |
| 10  | AES-CBC    | CBC  | 16 | NUL     | No       | SHA256(v+iv+P+k)[:4]   | 4 B exposed | Small, high-entropy     |
| 11  | AES-CBC +p | CBC  | 16 | PKCS7   | No       | SHA256(plaintext)[:4]  | 4 B         | General mid-sized       |
| 12  | AES-CBC +c | CBC  | 16 | PKCS7   | Yes      | SHA256(compressed)[:4] | 4 B         | General large           |
| 15  | AES-CTR    | CTR  | 12 | –       | No       | SHA256(plaintext)[:4]  | 4 B         | General mid-sized       |
| 16  | AES-CTR +c | CTR  | 12 | –       | Yes      | SHA256(compressed)[:4] | 4 B         | General large           |
| 20  | AES-GCM    | GCM  | 12 | –       | No       | GCM authtag[:4]        | 4 B         | Best, General mid-sized |
| 21  | AES-GCM +c | GCM  | 12 | –       | Yes      | GCM authtag[:4]        | 4 B         | Best, General large     |


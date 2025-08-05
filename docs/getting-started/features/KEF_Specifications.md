# KEF Encryption Format -- Specification

## 1. Overview

This system encrypts arbitrary plaintexts into a **versioned, self-describing envelope** that includes:

- custom identity/label `len_id` and `id`
- Version `v`
- pbkdf2-hmac iterations `i`
- and cipher-payload `cpl`

where cipher-payload consists of:

- Initialization Vector (if applicable) `IV`
- ciphertext `ct`
- and authentication/validation data `auth`

The envelope supports multiple forms of **mode-of-operation**, **authentication strategy**, **padding**, and **compression**, all selected via a numeric version code (0 - 21).

All versions derive the encryption key `k` as:
```
k = pbkdf2_hmac('sha256', K, id, i)
```

where:

- `K` = user-provided password/key material (bytes; if str: non-normalized encode as utf-8)
- `id` = salt (variable-length, prepended to envelope; if str: non-normalized encode as utf-8)
- `i` = iteration count (3 bytes, big-endian; if <= 10,000: multiplied by 10,000)

## 2. Envelope Structure (General Format)

All encrypted outputs follow this layout:
```
len_id + id + v + i + cpl
```

| Field     | Size           | Description |
|-----------|----------------|-------------|
| `len_id`  | 1 byte         | Length of `id` (0 - 252) |
| `id`      | `len_id` bytes | Salt for PBKDF2 |
| `v`       | 1 byte         | Version number |
| `i`       | 3 bytes        | Iteration count (big-endian) |
| `cpl`     | Variable       | Cipher payload (IV + ciphertext + auth) |

The `cpl` structure varies by version.   


### Version 0: AES-ECB v1 (Legacy BIP39 Encryption)

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

- **Mode**: ECB
- **Padding**: NUL bytes to AES block boundary (16-byte)
- **Authentication**: First 16 bytes of `SHA256(plaintext)`, hidden
- **cpl layout**: `[ciphertext]` (no IV; auth embedded before padding)
- **Use Case**: Legacy encryption of BIP39 entropy (e.g., mnemonic seeds)
- **Security Note**: No IV, error raised on duplicated blocks since ECB mode reveals patterns; weak padding; for backward compatibility only


### Version 1: AES-CBC v1 (Legacy BIP39 Encryption)

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

- **Mode**: CBC
- **IV**: 16 bytes, but **not included in auth** — potential weakness
- **Padding**: NUL bytes to block boundary
- **Authentication**: First 16 bytes of `SHA256(plaintext)`
- **cpl layout**: `[iv (16)] + [ciphertext]`
- **Use Case**: Legacy BIP39 encryption where IV randomness was introduced
- **Security Note**: Still uses weak NUL padding and ECB-like auth; IV not covered in integrity check — **deprecated**


### Version 5: AES-ECB (Unsafe Padding, Small High-Entropy Secrets)
   
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

- **Mode**: ECB  
- **Padding**: NUL bytes to AES block boundary (16-byte)
- **Authentication**: First 3 bytes of `SHA256(version_byte + plaintext + derived_key)`
- **cpl layout**: `[ciphertext] + [auth (3 bytes)]`
- **Use Case**: Small, high-entropy secrets (e.g., BIP39 entropy, cryptographic keys)
- **Security Note**: ECB mode leaks patterns; only safe for high-entropy, short inputs.   


### Version 6: AES-ECB +p (PKCS7 Padding, Mid-Sized Plaintext)
   
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

- **Mode**: ECB  
- **Padding**: PKCS7 to 16-byte boundary
- **Authentication**: First 4 bytes of `SHA256(plaintext)`
- **cpl layout**: `[ciphertext]` (auth embedded before padding)
- **Use Case**: Mid-sized structured data with variable length
- **Security Note**: PKCS7 prevents padding oracle if invalid padding fails silently


### Version 7: AES-ECB +c (Compressed, PKCS7 Padding, Larger Plaintext)
   
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

- **Mode**: ECB  
- **Compression**: `zlib.compress(P, wbits=-10)` — raw DEFLATE
- **Input to cipher**: `[compressed_data] + [auth (4 bytes)] + [PKCS7 padding]`
- **cpl layout**: `[ciphertext]` (no IV)
- **Use Case**: Larger plaintexts (1–50 KB), especially repetitive data
- **Security Note**: Compression breaks up block repetition, making ECB safer in practice


### Version 10: AES-CBC (Unsafe Padding, Mnemonics & Passphrases)
   
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

- **Mode**: CBC  
- **IV**: 16 bytes, prepended in `cpl`
- **Padding**: NUL bytes to block boundary
- **Authentication**: First 4 bytes of `SHA256(v + iv + P + k)`
- **cpl layout**: `[iv (16)] + [ciphertext] + [auth (4)]`
- **Use Case**: Mnemonics, passphrases, short secrets
- **Security Note**: NUL padding unsafe if plaintext contains nulls or length unknown   


### Version 11: AES-CBC +p (PKCS7 Padding, General Purpose)
   
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


- **Mode**: CBC  
- **IV**: 16 bytes, random, prepended
- **Padding**: PKCS7
- **Authentication**: First 4 bytes of `SHA256(plaintext)`
- **cpl layout**: `[iv] + [ciphertext]` (auth embedded before padding)
- **Use Case**: General mid-sized data with integrity
- **Security Note**: PKCS7 avoids padding oracle if implementation fails silently   

### Version 12: AES-CBC +c (Compressed, Larger Plaintext)
   
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


- **Mode**: CBC  
- **Compression**: `zlib(P, wbits=-10)`
- **Input to cipher**: `[compressed_data] + [auth] + [PKCS7 padding]`
- **cpl layout**: `[iv (16)] + [ciphertext]`
- **Use Case**: Larger plaintexts (1–50 KB) with redundancy
- **Security Note**: Compression reduces block repetition; CBC + IV prevents pattern leakage   


### Version 15: AES-CTR (Stream Mode, No Padding)
   
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

- **Mode**: CTR  
- **IV/Nonce**: 12 bytes, prepended
- **Padding**: None (stream cipher)
- **Authentication**: First 4 bytes of `SHA256(plaintext)`
- **cpl layout**: `[iv (12)] + [ciphertext]`
- **Input to cipher**: `P + auth` → encrypted as stream
- **Use Case**: Small to mid-sized data where padding must be avoided
- **Security Note**: Nonce must be unique per key; CTR mode is secure if IV never repeats   


### Version 16: AES-CTR +c (Compressed, Stream Mode)
   
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

- **Mode**: CTR  
- **Compression**: `zlib(P, wbits=-10)`
- **Input to cipher**: `[compressed_data] + [auth (4 bytes)]`
- **cpl layout**: `[iv (12)] + [ciphertext]`
- **No padding**: exact byte encryption
- **Use Case**: Larger plaintexts where streaming and size matter
- **Security Note**: Combines compression with secure stream cipher; ideal for variable-length data   


### Version 20: AES-GCM (Authenticated Encryption)
   
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

- **Mode**: GCM (AEAD)  
- **IV/Nonce**: 12 bytes, prepended
- **Authentication**: First 4 bytes of GCM-generated authtag
- **cpl layout**: `[iv (12)] + [ciphertext] + [auth (4)]`
- **No padding**: stream behavior
- **Use Case**: Small to mid-sized data requiring integrity + confidentiality
- **Security Note**: Truncated 4-byte tag reduces forgery resistance; nonce reuse breaks security   

### Version 21: AES-GCM +c (Compressed, Authenticated)
   
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

- **Mode**: GCM (AEAD)  
- **Compression**: `zlib(P, wbits=-10)`
- **Input to cipher**: compressed plaintext only
- **Authentication**: First 4 bytes of GCM authtag
- **cpl layout**: `[iv (12)] + [ciphertext] + [auth (4)]`
- **Use Case**: Larger plaintexts (1–50 KB) with strong integrity
- **Security Note**: Most secure version; combines AEAD, compression, and unique IVs   


## 4. Summary Table

| Ver | Name           | Mode  | IV? | IV Size | Padding     | Compress | Auth Method                     | Auth Size | Best For |
|-----|----------------|-------|-----|---------|-------------|----------|----------------------------------|-----------|----------|
| 0   | AES-ECB v1     | ECB   | No  | –       | NUL         | No       | SHA256(plaintext)[:16]          | 16 B      | Legacy BIP39 |
| 1   | AES-CBC v1     | CBC   | Yes | 16      | NUL         | No       | SHA256(plaintext)[:16]          | 16 B      | Legacy BIP39 |
| 5   | AES-ECB        | ECB   | No  | –       | NUL         | No       | SHA256(v+P+k)[:3]               | 3 B       | Small, high-entropy secrets |
| 6   | AES-ECB +p     | ECB   | No  | –       | PKCS7       | No       | SHA256(plaintext)[:4]           | 4 B       | Mid-sized, structured |
| 7   | AES-ECB +c     | ECB   | No  | –       | PKCS7       | Yes      | SHA256(compressed)[:4]          | 4 B       | Larger, repetitive data |
| 10  | AES-CBC        | CBC   | Yes | 16      | NUL         | No       | SHA256(v+iv+P+k)[:4]            | 4 B       | Mnemonics, passphrases |
| 11  | AES-CBC +p     | CBC   | Yes | 16      | PKCS7       | No       | SHA256(plaintext)[:4]           | 4 B       | General mid-sized |
| 12  | AES-CBC +c     | CBC   | Yes | 16      | PKCS7       | Yes      | SHA256(compressed)[:4]          | 4 B       | Larger plaintexts |
| 15  | AES-CTR        | CTR   | Yes | 12      | None        | No       | SHA256(plaintext)[:4]           | 4 B       | Streamed small/medium |
| 16  | AES-CTR +c     | CTR   | Yes | 12      | None        | Yes      | SHA256(compressed)[:4]          | 4 B       | Larger data, no padding |
| 20  | AES-GCM        | GCM   | Yes | 12      | None        | No       | GCM authtag (truncated to 4 B)  | 4 B       | Authenticated encryption |
| 21  | AES-GCM +c     | GCM   | Yes | 12      | None        | Yes      | GCM authtag (truncated to 4 B)  | 4 B       | Secure + compressed |
``   

---



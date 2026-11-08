# Formato de Cifrado KEF - Especificación Técnica

...`La K significa "KEF"` -anónimo


## Motivación

En otoño de 2023, durante el desarrollo de **krux release 23.09.0**, los colaboradores propusieron un método para cifrar mnemónicos bip39 que podían almacenarse en memoria flash SPI, en tarjeta SD o exportarse a un código QR. En cuanto al formato QR de mnemónicos cifrados: el diseño propuesto resultó interesante por ser un contenedor(envelope) extensible, ligero y autodescriptivo que ha sido muy bien recibido por los usuarios desde entonces.

...`"¿Cuándo las passphrases, los descriptores de salida, los PSBT y las notas?"` -la plebe

Esta especificación, junto con su implementación y conjunto de pruebas complementarias, son el resultado de meses de exploración de mejoras destinadas a definir, probar y extender mejor el formato de cifrado original al que nos referiremos como KEF. Propone diez nuevas versiones, ampliando su utilidad para abarcar más que solo mnemónicos, abarcando cadenas de longitud variable hasta PSBT de tamaño moderado, flexibilidad para elegir entre cuatro modos de operación de AES, con o sin compresión, y versiones optimizadas para obtener un contenedor de menor tamaño.

Sobre todo, esta especificación busca ser compatible con tantos proyectos como consideren adoptarla, para que los usuarios no queden limitados a un proyecto específico al recuperar sus secretos. Se agradecen las correcciones, las mejoras y el análisis de esta especificación. Se aceptan propuestas para más `versiones`, siempre que aporten "valor" al usuario y se ajusten al alcance de este sistema. Una vez publicada, dado que se desconoce la cantidad de contenedores KEF(KEF envelopes) existentes, los cambios en cualquier versión deben mantener la compatibilidad con versiones anteriores para el descifrado. Las implementaciones que adopten este sistema pueden admitir cualquier versión de KEF que deseen, ya sea solo para descifrado o para cifrado y descifrado, siempre que la información sobre la compatibilidad sea clara y precisa.

## Descripción general

Este sistema cifra texto plano arbitrario en un **contenedor KEF** autodescriptivo y versionado que incluye:

* identidad personalizada/etiqueta `len_id` y `id`
* versión `v`
* iteraciones pbkdf2-hmac `i`
* y carga útil de cifrado(cipher-payload) `cpl`

donde la carga útil de cifrado(cipher-payload) `cpl` consta de:

* Vector-de-inicialización/Nonce (si corresponde) `IV`
* texto cifrado(ciphertext)
* y datos de autenticación/validación `auth`

Las versiones de KEF ofrecen combinaciones de diferentes **modos-de-operación**, **estrategias de autenticación**, **estrategias de relleno(padding strategies)**, y **compresion**, todas seleccionadas mediante un código de versión numérico (0 - 21).

* Los códigos de versión disponibles son: 0, 1, 5, 6, 7, 10, 11, 12, 15, 16, 20, 21. No todos los (números) enteros del rango están asignados, y las implementaciones pueden deshabilitar versiones o modos.

Actualmente, todas las versiones utilizan AES y derivan la clave de cifrado de 256 bits `k` de la siguiente manera:
```
k = pbkdf2_hmac_sha256(K, id, i)
```

donde:

* `K` = contraseña o clave proporcionada por el usuario (bytes; si es una cadena (de texto): no normalizada, codificada en UTF-8)
* `id` = sal (longitud variable, antepuesta al contenedor; bytes: si es una cadena (de texto): no normalizada, codificada en UTF-8)
* `i` = número de iteraciones (3 bytes, formato big-endian)

El campo de iteración almacenado `i` DEBE ser ≥ 1. El número efectivo de iteraciones de PBKDF2 es `i` si `i > 10,000`, en caso contratio, es `i * 10,000`.

La compresión, (cuando está habilitada) utiliza zlib.compress(wbits=-10) o deflate sin procesar (Micropython).

La autenticación tiene tres formas:

* Cuando el modo tiene autenticación integrada, como GCM: `auth` es una etiqueta de autenticación truncada
* Cuando el modo no tiene autenticación integrada, `auth` es un resumen sha256 truncado cuya preimagen tiene dos formas:
    * si `auth` se cifrará con texto plano, oclto, es `sha256(plaintext)`
    * si `auth` se añadirá al texto cifrado, expuesto, es `sha256(version || IV || plaintext || derived-k)`

## Generalizaciones sobre la implementación

Se espera que cualquier implementación pueda descifrar un contenedor KEF creado por ella misma en el mismo dispositivo. Se solicita a las implementaciones que hagan "su mejor esfuerzo" por ser capaces de descifrar los contenedores KEF de las versiones que admitan y que hayan sido creados por otras implementaciones o en otros dispositivos; sin embargo, esto no siempre será posible. Descifrar contenedores KEF grandes en dispositivos con recursos muy limitados o con implementaciones defectuosas es inviable. Por lo tanto, en estos casos, es responsabilidad del usuario encontrar una implementación y un dispositivo capaces de descrifrar su contenedor KEF, o bien contar con un método de recuperación que no utilice KEF.

* Sea estricto al cifrar. Se tolerante con los errores y no especificique cuáles son al descifrar.

* En esencia, **un contenedor KEF es un formato de bytes - al igual que todas sus entradas**. Recuerda esto al convertir las cadenas recopiladas para la `key` y el `id`. Considere ser estricto al ofrecer un conjunto razonablemente mínimo de caracteres, comunes y disponibles en otros dispositivos y/o teclados internacionales al cifrar; a continuación, codifica los puntos de código Unicode (si no son ASCII) directamente a sus representaciones UTF-8 no normalizadas. Para el descifrado, se podrían ofrecer más caracteres a la hora de recopilar la `key`, y probar varias estrategias de normalización para recuperar los secretos. Considere la posibilidad de mostrar tanto la `key` como el `id` como bytes, y obtener la `key` como bytes, ya sea directamente o mediante conversión hexadecimal/base64 si fuera necesario, para permitir la recuperación. NO asuma que un usuario utilizó originalmente una implementación especifica para cifrar un conteneder KEF.

* **Sobre la importancia de una `key` FUERTE proporcionada por el usuario** Esto debe enfatizarse a cada usuario de KEF. Si bien KEF permite el fortalecimiento de la llave (key-stretching) mediante `id` e `iterations`, y ofrece modos que requieren un `IV` / Nonce aleatorio, **KEF no ofrece ninguna expectativa de seguridad con una `key` débil proporcionada por el usuario**. Considere dejar este punto claro a los usuarios antes de cifrar y/o proporcionar una indicación de la fortaleza de la `key` una vez ingresada. Si un contenedor KEF ha sido creado con una `key` "débil" y almacenado en un lugar accesible para otros, los usuarios deben asumir que su secreto ha sido filtrado. Considere recomendar a los usuarios que tomen decisiones sensatas sobre los caracteres que utilizan en su `key`, teniendo en cuenta que los caracteres no ASCII ofrecidos por una implementación podrían no ser fáciles de ingresar en otra, o que un glifo reconocible podría no existir en otros dispositivos para que puedan verificar su `key` durante el descifrado.

* **Sobre la seguridad** No todas las `versiones` de KEF ofrecen las mismas garantías de seguridad, por lo que los implementadores DEBEN tomar precausiones para evitar un uso "inseguro". Como ya se mencionó: sea estricto y rechace el cifrado cuando sea "inseguro"; sea tolerante y poco específico durante el descifrado. Es perfectamente válido ofrecer soporte únicamente para descifrado de una versión determinada si una implementación decide "orientar" a los usuarios hacia una versión más segura en la que admita funcionalidad completa del cifrado/descifrado.

    * **Sobre el modo ECB**: Los bloques repetidos revelarían patrones dentro del texto cifrado. Por lo tanto, sea estricto: rechace el cifrado utilizando el modo ECB siempre que se detecten bloques duplicados. Considere una versión con compresión, lo que podría resolver este problema.

    * **Sobre los modos de bloque con relleno NUL (NUL padding)** Pueden surgir problemas al eliminar el relleno durante el descifrado cuando bytes NUL válidos se confunden con bytes de relleno que deben eliminarse.
        * Si `auth` se añade al texto plano antes del relleno Y los bytes de `auth` terminan en 0x00: sea estricto; rechaze el cifrado. Considere una versión con relleno seguro (safe padding).
        * Si `auth` se añade al texto cifrado despúes del relleno/cifrado Y los bytes del `plaintext` terminan en 0x00: sea estricto, rechaze el cifrado. Considere una versión con relleno seguro (safe padding).
        * No asuma que otras implementaciones complen con lo anterior. Sea tolerante y haga esfuerzos razonables para recuperar correctamente los secretos durante el descifrado. En este caso, podría ser apropiado mostrar una advertencia a los usuarios DESPUÉS de un descifrado exitoso.

* **Sobre los modos que requieren IV o Nonce** Tome precauciones para asegurar que este valor es aleatorio y no reutilizado, por ejemplo: Entropia natural obtenida desde un sensor de camara (validada y/o analizada por el usuario para asegurarse de que el sensor funciona / entropia alta).

* **Sobre las codificaciones comnunes de `bytes`** Aunque queda fuera del alcance estricto de esta especificación, dado que **los contenedores KEF son un formato de bytes**, hay un tema relacionado: las implementaciones pueden encontrarse con cadenas de texto codificadas que probablemente representen bytes. Por ejemplo: base64, base43 (de electrum), base32, o hex podrían ser representaciones de un conteneder KEF que haya sido codificado previamente para su transporte. A medida que continúes leyendo, quedará claro que con cualquier cadena de bytes, es posible reconocer un contenedor KEF mediante los siguientes pasos:
    1. Leer el primer byte como número entero `len_id`,
    2. Avanzar esa cantidad de bytes, saltando el campo `id`, para leer el siguiente byte como un número entero `version`,
    3. Si esa versión corrsponde a una version de KEF conocida y compatible, el resto del contenedor puede analizarse siguiendo las reglas de KEF correspondientes a esa versión.
    4. Si el análisis se completa sin errores, es probable que se trate de un contenedor KEF y se debería ofrecer al usuario una interfaz para realizar el descifrado.
    Aunque el usuario probablemente ya lo sepa, la instancia en ejecución de una implementación de KEF solo podrá confirmar con certeza que una cadena de bytes era efectivamente un contenedor KEF DESPUÉS de un descifrado exitoso. Si en cualquier momento de este proceso una implementación detecta que `version` es desconocida o está deshabilitada, o si el análisis falla, la acción esperada es NO GENERAR ERRORES ESPECÍFICOS relacionados con esta inspección. En su lugar, lo apropiado es asumir que no se trataba de un contenedor KEF y tratar los datos en otro contexto: por ejemplo: "Unknown" (desconocido). Del mismo modo, como se mencionó anteriormente, ser poco específicocon los errores durante el descifrado implica que "Failed!" (¡Falló!) puede ser una respuesta suficiente para cualquier error, en lugar de revelar a un posible atacante detalles específicos sobre el motivo del fallo.

* **On Iterations** Consider that users may want to decrypt KEF envelopes on various resource-constrained devices. There is a minimum 10,000 iterations imposed in any KEF envelope (a value of 1 would be 10,000 pbkdf2_hmac iterations), and the maximum could be as high as 100,000,000 (a value of 10,000), but depending on the device used, 500,000 might be too high. Also, since the user-supplied `key` is stretched by this value, consider offering a range to users - then adding a small `delta` as extra bits of entropy to derive different AES-256 keys that would otherwise be the same in the event the user re-uses the same `key`, `id` and `iterations` when creating many KEF envelopes.

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
* **Security Note**: like others, when encrypting: fail "unsafe" if duplicate blocks - unlikely with compression 

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
From the version details and summary table: note that all KEF versions can be defined as having a set of parameters which define that version's KEF rules. For ease-of-maintenance - and also for extending later, it may be useful to store these in a central configuration. Within our sample reference, these are defined by constants `kef.VERSIONS`, `kef.MODE_NUMBERS` and `kef.MODE_IVS`.

### Choosing a Version
As soon as you have data to hide, KEF offers choices for which version to use. That choice may be made by the user, or by the implementation, based on what is being hidden, compatibility with others, and how it may be stored/transported. The sample reference uses a function named `kef.suggest_versions()` to make a choice based on user's preferred mode-of-operation, the plaintext being hidden, then optimizes for a smaller KEF envelope.

### Encryption, Decryption, and Authentication
Once you know what you need to hide and how you want to hide it, you'll need something to perform the encryption. You'll start by stretching the user-supplied `key`, salted with `id` for a number of `iterations` to **derive** the 256-bit AES key. Next you'll need to **encrypt** the plaintext (possibly with a random `IV` / Nonce) according to the chosen KEF version, so that the result is a cipher-payload `cpl`. To reverse this process, you'll need something to **decrypt** and **authenticate** the cipher-payload `cpl` - again according to the rules of the particular KEF version. The sample reference uses a class named `kef.Cipher` for stretching the `key`, encrypting plaintext to `cpl`, and decrypting / authenticating `cpl` back into plaintext.

### Padding and Unpadding
Depending on the mode-of-operation of your version, you may need to **pad** the plaintext. If so, there will also be a need to **unpad** during the decryption process. The sample reference uses functions named `kef.pad()` and `kef.unpad()`, which are called from inside the `kef.Cipher` object when encrypting and decrypting.

### Data Compression: Deflate & Inflate
Depending on the version, you may also need to **deflate** plaintext so that it is compressed before encryption. Likewise, you'll need to **reinflate** it after decryption to decompress the plaintext. The sample reference uses functions named `kef.deflate()` and `kef.reinflate()`, which are also called from inside the `kef.Cipher` object when encrypting and decrypting.

### Metadata Wrapping and Unwrapping
After encryption, you'll need to **wrap** the `id`, `version`, `iterations` and `cpl` into a valid KEF envelope. Likewise, in order to reveal something hidden within a KEF envelope, you'll first need to **unwrap**, or parse it into its constituent parts (`id`, `version`, `iterations`, `cpl`) so that it may be decrypted as described above. The sample reference uses functions `kef.wrap()` and `kef.unwrap()` for these procedures.

### On Further Encoding KEF Envelopes
Outside the scope of this specification on KEF envelopes, which are strings of bytes, implementations will surely need to make choices about encoding/decoding schemes. Whether for QR transport, copy-pasting into messages, embedding into json documents, in-plain-sight within other document formats, or persisted in binary files, these choices are left to implementors.


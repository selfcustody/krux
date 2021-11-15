# Hash functions for Bitcoin

extends `hashlib` micropython module with `ripemd160` and `sha512` functions.

Also adds a single-line function for pbkdf2_hmac_sha512:

`pbkdf2_hmac_sha512(password, salt, iterations, bytes_to_read)`

in Bitcoin to generate a seed:

`pbkdf2_hmac_sha512(mnemonic, 'mnemonic'+password, 2048, 64)`

## TODO:

- make API the same as in normal python
- make C-optimized `hmac` and `pbkdf2` versions with standard python API
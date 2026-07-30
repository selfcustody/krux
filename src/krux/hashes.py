# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Single point of entry for SHA-256 hashing.

Krux has software and K210 hardware implementations of SHA-256, so this module
keeps them as separate, explicitly named functions instead of selecting a
backend implicitly:

- The plain `sha256()` / `sha256d()` / `pbkdf2_hmac_sha256()` functions use
  the software implementation (`hashlib`). They preserve the backend used by
  entropy checksums, key derivation, message signing, and legacy decryption.

- The `*_hw` functions use the K210 hardware accelerator (`uhashlib_hw`). They
  preserve the backend used for firmware and flash hashing, KEF operations,
  and tamper-check-code hashing and key stretching.

Both backends produce the same SHA-256 and PBKDF2 results. Backend selection is
kept explicit to preserve runtime behavior and performance characteristics.

Application code should import from here rather than reaching for `hashlib` or
`uhashlib_hw` directly, and pick the software or `*_hw` variant deliberately --
the choice of backend is part of the behavior, not an implementation detail.
Hardware and compatibility diagnostics may import a backend directly when the
backend itself is what they test.

`sha256d()` is a double SHA-256, `SHA256(SHA256(x))`, a Bitcoin protocol
internal (BIP-137 message preimages, base58check, txids). It is NOT what a
user gets by hashing the same input by hand, so it must never be presented as
"the SHA256 of" something.
"""

import hashlib


def sha256(data=b""):
    """
    Single, software SHA-256 hasher (`hashlib.sha256`).

    Returns a hasher object, so it accepts `.update()` for streaming and
    `.digest()` for the result. Reproducible with `sha256sum`; use it for any
    hash the user verifies externally and for entropy/key material.
    """
    return hashlib.sha256(data)


def sha256d(data):
    """
    Software double SHA-256 digest, `SHA256(SHA256(data))`, as used by Bitcoin.

    Returns the digest bytes directly, since there is no meaningful streaming
    use for it. Never display this as "SHA256" -- it will not match what the
    user computes by hand.
    """
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def pbkdf2_hmac_sha256(secret, salt, iterations):
    """Software PBKDF2-HMAC-SHA256 key stretching (`hashlib`)."""
    return hashlib.pbkdf2_hmac("sha256", secret, salt, iterations)


def sha256_hw(data=b""):
    """
    Hardware-accelerated single SHA-256 hasher (K210 `uhashlib_hw`).

    Same result as `sha256()`, offloaded to the accelerator. Used by firmware,
    flash, KEF, and tamper-check-code operations.
    """
    import uhashlib_hw

    return uhashlib_hw.sha256(data)


def pbkdf2_hmac_sha256_hw(secret, salt, iterations):
    """
    Hardware-accelerated PBKDF2-HMAC-SHA256 key stretching (K210 `uhashlib_hw`).

    Used for KEF and tamper-check-code key stretching, where the iteration
    count makes hardware acceleration worthwhile.
    """
    import uhashlib_hw

    return uhashlib_hw.pbkdf2_hmac_sha256(secret, salt, iterations)

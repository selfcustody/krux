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

Krux hashes with SHA-256 for two different reasons, and the two must not be
confused, so this module keeps them as separate, explicitly named functions
instead of a single backend that changes under the hood:

- The plain `sha256()` / `sha256d()` / `pbkdf2_hmac_sha256()` functions are
  the *software* implementation (`hashlib`). They produce a value the user can
  reproduce outside Krux with `sha256sum` or any other tool, and they never
  depend on the K210 accelerator. Use them for anything shown on screen for
  verification, and for security-sensitive material -- entropy checksums, key
  derivation, message signing.

- The `*_hw` functions are the K210 hardware-accelerated implementation
  (`uhashlib_hw`), used only where throughput matters: scanning flash memory
  or the firmware file, and PBKDF2 key stretching for KEF / tamper-check code.
  They fall back to `hashlib` off-device (tooling, tests, docs).

Import from here rather than reaching for `hashlib` or `uhashlib_hw` directly,
and pick the software or `*_hw` variant deliberately -- the choice of backend
is part of the behavior, not an implementation detail.

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

    Same result as `sha256()`, offloaded to the accelerator for throughput.
    Use it only for bulk hashing where speed matters -- scanning flash memory
    or the firmware file -- never for a hash shown to the user or for
    entropy/keys. Falls back to software `hashlib` off-device.
    """
    try:
        import uhashlib_hw
    except ImportError:  # off-device (tooling, tests, docs)
        return hashlib.sha256(data)
    return uhashlib_hw.sha256(data)


def pbkdf2_hmac_sha256_hw(secret, salt, iterations):
    """
    Hardware-accelerated PBKDF2-HMAC-SHA256 key stretching (K210 `uhashlib_hw`).

    Used for KEF and tamper-check-code key stretching, where the iteration
    count makes hardware acceleration worthwhile. Falls back to software
    `hashlib` off-device.
    """
    try:
        import uhashlib_hw
    except ImportError:  # off-device (tooling, tests, docs)
        return hashlib.pbkdf2_hmac("sha256", secret, salt, iterations)
    return uhashlib_hw.pbkdf2_hmac_sha256(secret, salt, iterations)

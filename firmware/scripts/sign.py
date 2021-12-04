# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

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
import os
import sys
import hashlib
import binascii
from embit.util import secp256k1

# Pulled from firmware.py
def fsize(firmware_filename):
    """Returns the size of the firmware"""
    size = 0
    with open(firmware_filename, 'rb', buffering=0) as file:
        while True:
            chunk = file.read(128)
            if not chunk:
                break
            size += len(chunk)
    return size

# Pulled from firmware.py
def sha256(firmware_filename, firmware_size):
    """Returns the sha256 hash of the firmware"""
    hasher = hashlib.sha256()
    hasher.update(b'\x00' + firmware_size.to_bytes(4, 'little'))
    with open(firmware_filename, 'rb', buffering=0) as file:
        while True:
            chunk = file.read(128)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.digest()

private_key_hex = os.environ.get('SIGNER_PRIVKEY')
if not private_key_hex:
    sys.exit('Private key must be provided')

if len(sys.argv) != 2:
    sys.exit('Firmware must be provided')

firmware_path = sys.argv[1]
private_key = binascii.unhexlify(private_key_hex)

if not secp256k1.ec_seckey_verify(private_key):
    sys.exit('Private key is invalid')

firmware_hash = sha256(firmware_path, fsize(firmware_path))
with open(firmware_path + '.sha256.txt', 'w') as hashfile:
    hashfile.write(binascii.hexlify(firmware_hash).decode())

sig = secp256k1.ecdsa_sign(firmware_hash, private_key)
with open(firmware_path + '.sig', 'wb') as sigfile:
    sigfile.write(sig)

# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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

#!/bin/bash

device=$1
locale=$2

# Create screenshots directory
rm -rf screenshots && mkdir -p screenshots

# Create an sd folder and a fresh settings.json file
mkdir -p sd && rm -f sd/settings.json
echo "{\"settings\": {\"i18n\": {\"locale\": \"$locale\"}, \"persist\": {\"location\": \"sd\"}}}" > sd/settings.json

# Create an encrypted mnemonic file to generate "Load -> From Storage" screenshots
encrypted_mnemonics="{\"d668b8b7\": {\"version\": 0, \"key_iterations\": 100000, \"data\": \"haAyMxF\
mOVkBE5QixIeJl7P0dYKVeOiuhNodO+qyI2lA+veFUxcXben1OZvKOqTbWNI2Oj8SROTpooiS/4WJdA==\"}, \"a56dfd6c\": \
{\"version\": 0, \"key_iterations\": 100000, \"data\": \"PY9fBDrqtv2ZyZF47CsZ5QucxzXmOxaJJtjkngEQTfH\
LyLgHTQ3oX8AbZR6+UXBXZUB+eSOHwJZm1jCO8AaBxQ==\"}}"
echo "$encrypted_mnemonics" > sd/seeds.json

# Sequences

# Login
poetry run poe simulator --sequence sequences/logo.txt --sd --device $device
poetry run poe simulator --sequence sequences/about.txt --sd --device $device
poetry run poe simulator --sequence sequences/load-mnemonic-options.txt --sd --device $device
poetry run poe simulator --sequence sequences/new-mnemonic-options.txt  --sd --device $device
poetry run poe simulator --sequence sequences/load-mnemonic-sequence.txt  --sd --device $device
poetry run poe simulator --sequence sequences/load-mnemonic-double-mnemonic.txt  --sd --device $device
poetry run poe simulator --sequence sequences/load-mnemonic-kef-via-qr.txt  --sd --device $device
poetry run poe simulator --sequence sequences/edit-mnemonic.txt  --sd --device $device

# Home
poetry run poe simulator --sequence sequences/home-options.txt --sd --device $device
poetry run poe simulator --sequence sequences/encrypt-mnemonic.txt --sd --device $device
poetry run poe simulator --sequence sequences/extended-public-key-wpkh.txt --sd --device $device
poetry run poe simulator --sequence sequences/extended-public-key-wsh.txt --sd --device $device
poetry run poe simulator --sequence sequences/wallet-descriptor-wsh.txt --sd --device $device
# poetry run poe simulator --sequence sequences/wallet-descriptor-wpkh.txt --sd --device $device
poetry run poe simulator --sequence sequences/wallet-descriptor-exp-tr-minis.txt  --sd --device $device
poetry run poe simulator --sequence sequences/bip85.txt --sd --device $device
poetry run poe simulator --sequence sequences/mnemonic-xor.txt --sd --device $device
poetry run poe simulator --sequence sequences/scan-address.txt --sd --device $device
poetry run poe simulator --sequence sequences/list-address.txt --sd --device $device
poetry run poe simulator --sequence sequences/export-address.txt --sd --device $device
poetry run poe simulator --sequence sequences/sign-psbt.txt  --sd --device $device
poetry run poe simulator --sequence sequences/sign-message.txt --sd  --device $device
poetry run poe simulator --sequence sequences/sign-message-at-address.txt --sd  --device $device

# Tools
poetry run poe simulator --sequence sequences/tools-datum-tool.txt  --sd --device $device
poetry run poe simulator --sequence sequences/tools-check-sd.txt  --sd --device $device
poetry run poe simulator --sequence sequences/tools-create-QR.txt  --sd --device $device
# poetry run poe simulator --sequence sequences/tools-mnemonic.txt  --sd --device $device
poetry run poe simulator --sequence sequences/tools-device-tests-test-suite.txt  --sd --device $device
poetry run poe simulator --sequence sequences/tools-print-test-qr.txt  --sd --device $device
poetry run poe simulator --sequence sequences/tools-descriptor-addresses.txt --sd --device $device
poetry run poe simulator --sequence sequences/tools-flash.txt  --sd --device $device
poetry run poe simulator --sequence sequences/tc-flash-hash.txt --sd --device $device

# Settings
poetry run poe simulator --sequence sequences/all-settings.txt --sd --device $device

# Other
poetry run poe simulator --sequence sequences/qr-transcript.txt --sd --printer --device $device
poetry run poe simulator --sequence sequences/print-qr.txt --sd --printer --device $device
poetry run poe simulator --sequence sequences/print-qr-file.txt --sd --printer file --device $device
poetry run poe simulator --sequence sequences/print-qr-grbl.txt --sd --printer grbl --device $device

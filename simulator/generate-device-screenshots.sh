# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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

rm -rf screenshots && mkdir -p screenshots
rm -rf sd && mkdir -p sd && rm -f sd/settings.json
echo "{\"settings\": {\"i18n\": {\"locale\": \"$locale\"}}}" > sd/settings.json

poetry run python simulator.py --sequence sequences/about.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/debug-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/extended-public-key-wpkh.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/extended-public-key-wsh.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/home-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-via-bits.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-via-numbers.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-via-qr.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-via-text.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/locale-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/login-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/logo.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/mnemonic-12-word.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/mnemonic-24-word.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/network-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/new-mnemonic-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/new-mnemonic-via-d6.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/new-mnemonic-via-d20.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/print-qr.txt --with-printer True --with-sd True --device $device
poetry run python simulator.py --sequence sequences/printer-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/scan-address.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/settings-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/shutdown.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/sign-message.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/sign-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/sign-psbt.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/wallet-type-options.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/wallet-wpkh.txt --with-sd True --device $device
poetry run python simulator.py --sequence sequences/wallet-wsh.txt --with-sd True --device $device

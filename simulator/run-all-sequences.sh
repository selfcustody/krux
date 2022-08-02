#!/bin/sh

device=$1

mkdir -p screenshots

mkdir -p sd
cp -rf ../i18n/translations sd/translations
rm -f sd/settings.json

poetry run python simulator.py --sequence sequences/about.txt --device $device
poetry run python simulator.py --sequence sequences/debug-options.txt --device $device
poetry run python simulator.py --sequence sequences/extended-public-key-wpkh.txt --device $device
poetry run python simulator.py --sequence sequences/extended-public-key-wsh.txt --device $device
poetry run python simulator.py --sequence sequences/home-options.txt --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-options.txt --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-via-bits.txt --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-via-numbers.txt --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-via-qr.txt --device $device
poetry run python simulator.py --sequence sequences/load-mnemonic-via-text.txt --device $device
poetry run python simulator.py --sequence sequences/locale-options.txt --with-sd True --device $device
rm -f sd/settings.json
poetry run python simulator.py --sequence sequences/login-locale-de-de.txt --with-sd True --device $device
rm -f sd/settings.json
poetry run python simulator.py --sequence sequences/login-options.txt --device $device
poetry run python simulator.py --sequence sequences/logo.txt --device $device
poetry run python simulator.py --sequence sequences/mnemonic-12-word.txt --device $device
poetry run python simulator.py --sequence sequences/mnemonic-24-word.txt --device $device
poetry run python simulator.py --sequence sequences/network-options.txt --device $device
poetry run python simulator.py --sequence sequences/new-mnemonic-options.txt --device $device
poetry run python simulator.py --sequence sequences/new-mnemonic-via-d6.txt --device $device
poetry run python simulator.py --sequence sequences/new-mnemonic-via-d20.txt --device $device
poetry run python simulator.py --sequence sequences/print-qr.txt --with-printer True --device $device
poetry run python simulator.py --sequence sequences/printer-options.txt --device $device
poetry run python simulator.py --sequence sequences/scan-address.txt --device $device
poetry run python simulator.py --sequence sequences/settings-options.txt --device $device
poetry run python simulator.py --sequence sequences/shutdown.txt --device $device
poetry run python simulator.py --sequence sequences/sign-message.txt --device $device
poetry run python simulator.py --sequence sequences/sign-options.txt --device $device
poetry run python simulator.py --sequence sequences/sign-psbt.txt --device $device
poetry run python simulator.py --sequence sequences/wallet-type-options.txt --device $device
poetry run python simulator.py --sequence sequences/wallet-wpkh.txt --device $device
poetry run python simulator.py --sequence sequences/wallet-wsh.txt --device $device

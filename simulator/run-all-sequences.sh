#!/bin/sh

mkdir -p screenshots

mkdir -p sd
cp -rf ../i18n/translations sd/translations
rm -f sd/settings.json

poetry run python simulator.py --sequence sequences/about.txt
poetry run python simulator.py --sequence sequences/debug-options.txt
poetry run python simulator.py --sequence sequences/extended-public-key-wpkh.txt
poetry run python simulator.py --sequence sequences/extended-public-key-wsh.txt
poetry run python simulator.py --sequence sequences/home-options.txt
poetry run python simulator.py --sequence sequences/load-mnemonic-options.txt
poetry run python simulator.py --sequence sequences/load-mnemonic-via-bits.txt
poetry run python simulator.py --sequence sequences/load-mnemonic-via-numbers.txt
poetry run python simulator.py --sequence sequences/load-mnemonic-via-qr.txt
poetry run python simulator.py --sequence sequences/load-mnemonic-via-text.txt
poetry run python simulator.py --sequence sequences/locale-options.txt --with-sd True
rm -f sd/settings.json
poetry run python simulator.py --sequence sequences/login-locale-de-de.txt --with-sd True
rm -f sd/settings.json
poetry run python simulator.py --sequence sequences/login-options.txt
poetry run python simulator.py --sequence sequences/logo.txt
poetry run python simulator.py --sequence sequences/mnemonic-12-word.txt
poetry run python simulator.py --sequence sequences/mnemonic-24-word.txt
poetry run python simulator.py --sequence sequences/network-options.txt
poetry run python simulator.py --sequence sequences/new-mnemonic-options.txt
poetry run python simulator.py --sequence sequences/new-mnemonic-via-d6.txt
poetry run python simulator.py --sequence sequences/new-mnemonic-via-d20.txt
poetry run python simulator.py --sequence sequences/print-qr.txt --with-printer True
poetry run python simulator.py --sequence sequences/printer-options.txt
poetry run python simulator.py --sequence sequences/scan-address.txt
poetry run python simulator.py --sequence sequences/settings-options.txt
poetry run python simulator.py --sequence sequences/shutdown.txt
poetry run python simulator.py --sequence sequences/sign-message.txt
poetry run python simulator.py --sequence sequences/sign-options.txt
poetry run python simulator.py --sequence sequences/sign-psbt.txt
poetry run python simulator.py --sequence sequences/wallet-type-options.txt
poetry run python simulator.py --sequence sequences/wallet-wpkh.txt
poetry run python simulator.py --sequence sequences/wallet-wsh.txt

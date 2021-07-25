# Krux Wallet
## *Focus on your keys*
Krux is an open-source, airgapped bitcoin hardware wallet built with off-the-shelf parts that never stores your keys to disk and solely functions as a signer in a multisig setup.

<p align="center">
<img src="https://user-images.githubusercontent.com/87289655/126738716-518cb99c-ca3e-405d-b7ba-55b6edd34ac3.png" width="195">
</p>

---
## Disclaimer
**WARNING**: *While functional, this is currently alpha-quality software and could have bugs or other issues that might cause you to lose your coins. Use at your own risk!*

---

To use Krux, you will need to buy an [M5StickV](https://shop.m5stack.com/products/stickv). The M5StickV was chosen because it has a processor, battery, buttons, screen, camera, and SD card slot all in one small unit, has no WiFi or Bluetooth functionality, and is cheap (< $50).

All operations in Krux are done via QR code. It loads your recovery phrase, imports a multisig wallet descriptor, and signs transactions all via QR code. It reads QR codes in with its camera and writes QR codes out to its screen or [to paper via an optional thermal printer attachment](#printing-qrs).

We don't want users to rely on Krux for anything except being a safe way to sign off on a multisig transaction when supplied a key. To this end, Krux will not generate new keys for you. Good random number generation is frought with peril, so we're sidestepping the issue by expecting you to [generate your own offline](https://vault12.rebelmouse.com/seed-phrase-generation-2650084084.html).

Krux is built to work with [Specter Desktop](https://github.com/cryptoadvance/specter-desktop), a desktop application where you can create and manage your multisig wallet, generate receive addresses, and send funds by creating partially signed bitcoin transactions (PSBTs) that you can sign with your hardware wallets. 

# Getting Started
## Requirements
Docker
Python 3

## Build and flash the firmware
Connect the M5StickV to your computer via its USB-C port, then locate it on your machine with:
```bash
ls -lha /dev/tty* | grep usb
```

You should see a path like `/dev/tty.usbserial-123`.

Now, build and install the firmware by running the following, substituting `/dev/tty.usbserial-123` with your device path from the previous step:
```bash
./firmware.sh build
./firmware.sh flash /dev/tty.usbserial-123
```

## Build and flash the software
Plug a [supported microSD card](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md#tf-cardmicrosd-test) into your computer and take note of its path (after mounting), for example `/Volumes/SD`.

Install the software on the card by running the following, substituting `/Volumes/SD` with your SD card's path from the previous step:
```bash
python3 flash_sd.py /Volumes/SD
```

This is a simple script that effectively copies the contents of the `src` directory onto the root of the card to be run by the firmware.

## Boot it up
Unmount and remove the SD card from your machine, insert it into the M5StickV, and long-press its power button (left side) to boot it up! You should soon see the Krux logo appear on the screen. If after 30 seconds you still see a black screen, try power cycling the device by holding down the power button for six seconds.

Congrats, you're now running Krux!

# Using
## Opening Wallets
As stated above, Krux does not generate a 12-word BIP-39 passphrase for you, but it does expect you to have one in order to use it.

### Method: Manual 
Enter each word of your 12-word BIP-39 passphrase one at a time. Krux will attempt to autocomplete your word to speed up the process.

### Method: QR
It's unpleasant having to manually enter 12 words each time you want to use Krux. To remedy this you can instead use the device's camera to read a QR code containing the 12 words (encoded as a single space-separated string). To make a QR code for this purpose in Krux, you can connect a thermal printer and print your recovery phrase after opening your wallet via the manual method first. Check out the [Printing QRs section](#printing-qrs) below for more information.

## Configuring Multisig
To setup a new multisig wallet, you will need to first add Krux as a new device in Specter by exporting your Extended Master Public Key (xpub) to it. When adding to Specter, choose the `Other` device type and click `Scan QR Code`. Go to your Krux, select `Public Key (xpub)`, and scan the QR code. It should import as a `#0 Multisig Sig (Segwit)` key. Repeat this process for as many keys / hardware wallets as you want to be in the multisig setup.

Once you've added all your devices to Specter, add a new wallet and select the devices you want to be in the multisig. A new wallet will then be created, which you will want to import into your Krux via `Multisig Policy`. In Specter, navigate to the `Advanced` section and find `Export to Wallet` to display a QR code that Krux can read. Once loaded, you can then print this QR code to have as a backup.

## Signing PSBTs
Krux will only sign transactions for multisig wallets, so make sure you have first set up a multisig policy and imported it into Krux before continuing.

Signing is straightforward, you just need to create a transaction to send funds somewhere in Specter via the `Send` section, then select to sign off on it with your Krux. Specter will display a QR code for the unsigned PSBT that you can read in with your Krux at which point you will see details about the transaction to confirm they match. It will then ask you for confirmation to sign the PSBT and will then generate its own QR code that you can either display directly back to Specter or print for use at a later time. Once all necessary cosigners have signed the PSBT, you can choose to broadcast it from Specter to the Bitcoin network.

## Printing QRs
Krux has the ability to print all QR codes it generates, including recovery phrase, xpub, multisig policy, and signed PSBT, via a locally-connected thermal printer over its serial port. Any of [these printers from Adafruit](https://www.adafruit.com/?q=thermal+printer) should do, but [this starter pack](https://www.adafruit.com/product/600) would be the quickest way to get started. You'll also need a conversion cable with a 4-pin female Grove connector on one end (to connect to the Krux) and 4-pin male jumpers on the other end (to connect to the printer).

Once connected and powered on, all screens that display a QR code will begin showing a follow-up screen asking if you want to `Print to QR?`. You can use the middle button to confirm or the right-side button to cancel.

Originally, the idea was to print out a QR code of the recovery phrase to enable faster wallet opening over the manual method of having to input each word. Then, we realized it would be useful to backup a wallet's multisig policy on paper as well (since you need knowledge of all xpubs in a multisig wallet in order to spend from it). After that, we decided to just make it a feature across the board. Want to make a "multisig paper wallet" with codes for your recovery phrase, xpub, and multisig policy on one sheet? You can! Want to print out a signed PSBT and send it in the mail? You can!

Just be careful what you do with the codes, since most smartphones can now quickly and easily read QR codes. Treat your QR passphrase the same way you would treat a plaintext copy of it.

# Inspired by these similar projects:
- https://github.com/SeedSigner/seedsigner for Raspberry Pi (Zero)
- https://github.com/diybitcoinhardware/f469-disco for the F469-Discovery board

# Contributing
Issues and pull requests welcome! Let's make this as good as it can be.

# Support the Project
If you would like to support the project, BTC is kindly accepted!

`19f8HVt8LZKzBv8CuBYnxCqn5sd75V658J`
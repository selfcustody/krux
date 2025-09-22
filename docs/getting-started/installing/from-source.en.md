This page explains how to install Krux from source. You can check a simplified version of these instructions in our [README](https://github.com/selfcustody/krux) too.

### Fetch the code
This will download the source code of Krux as well as the code of all its dependencies inside a new folder called `krux` (needs [`git`](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)):
```bash
git clone --recurse-submodules https://github.com/selfcustody/krux
```

**Note**: When you wish to pull updates (to all submodules, their submodules, ...) to this repo, use:
```bash
git pull origin main && git submodule update --init --recursive
```

#### Prerequisite for upgrading via microSD
If you wish to perform airgapped upgrades via microSD card later, you will need to have a private and public key pair to sign your builds and verify the signatures. If you do not want to perform further airgapped upgrades, jump to [build section](#build-the-firmware-linux-or-wsl).

You can use an existing Krux installation and mnemonic to sign your builds with, **or** you can generate a keypair and sign from the [`openssl` CLI](https://wiki.openssl.org/index.php/Command_Line_Elliptic_Curve_Operations). Commands have been added to the `krux` shell script to make this easier.

In either case, you will need to update the `SIGNER_PUBKEY` field in `src/krux/metadata.py` to store your public key so that Krux can verify future builds before installing.

To generate a keypair:
```bash
./krux generate-keypair
./krux pem-to-pubkey pubkey.pem
```

The first command will create `privkey.pem` and `pubkey.pem` files you can use with openssl, and the second command will output your public key in the form expected by Krux.

Once you've updated the `SIGNER_PUBKEY` with this value, you can proceed with the regular build process.

### Build the firmware (Linux or WSL)
The [krux bash script](https://github.com/selfcustody/krux/blob/main/krux) contains commands for common development tasks. It assumes a Linux host, you will need to have [Docker Desktop or Docker Engine](https://docs.docker.com/desktop/), `openssl`, and `wget` installed at a minimum for the commands to work as expected. It works on Windows using WSL. The channel Crypto Guide from Youtube made a step-by-step video - [Krux DIY Bitcoin Signer: Build From Source & Verify (With Windows + WSL2 + Docker)](https://www.youtube.com/watch?v=Vmr_TFy2TfQ)

To build and flash the firmware:
```bash
# build firmware for Maix Amigo
./krux build maixpy_amigo
```

The first time, the build can take around an hour or so to complete. Subsequent builds should take only a few minutes. If all goes well, you should see a new `build` folder containing `firmware.bin` and `kboot.kfpkg` files when the build completes.

**Note**: if you encounter any of these errors while building, it is a problem connecting to github, try again (if the error persists, try changing the DNS/VPN or correcting the hostname resolution of github.com to an IP that is working for you):
```
error: RPC failed; curl 92 HTTP/2 stream 0 was not closed cleanly: CANCEL (err8)
fatal: the remote end hung up unexpectedly
fatal: early EOF
fatal: index-pack failed
fatal: clone of ... failed
Failed to clone ...
```

#### Reproducibility
If you build from the `main` branch of the source code, you should be able to reproduce the build process used to generate the latest release binaries and obtain exactly the same copies of the `firmware.bin` and `kboot.kfpkg` files, with matching hash checksums (to check for an older version, use the `tag` instead).

To check, use the compiled files for the target device. Each command should output the same hash for the two provided files:
```bash
sha256sum build/firmware.bin {{latest_krux}}/maixpy_DEVICE/firmware.bin
sha256sum build/kboot.kfpkg {{latest_krux}}/maixpy_DEVICE/kboot.kfpkg
```

If you want to extract and verify the `firmware.bin`file contained in `kboot.kfpkg`, use the following:

```bash
unzip kboot.kfpkg -d ./kboot/
```

### Flash the firmware onto the device
Connect the device to your computer via USB (for Maix Amigo, make sure you’re using bottom port), power it on, and run the following, replacing `DEVICE` with either `m5stickv`, `amigo`, `cube`, `dock`, `yahboom`, `wonder_mv` or `tzt`:
```bash
# flash firmware to DEVICE
./krux flash maixpy_DEVICE
```
If flashing fails try reading [Troubleshooting](../../troubleshooting.md)

----8<----
flash-krux-logo.en.txt
----8<----

----8<----
amigo-more-info-faq.en.txt
----8<----

### Signing the firmware
You can sign the firmware to [perform airgapped upgrades](#prerequisite-for-upgrading-via-microsd) using one of the two methods listed below:

#### Method 1: Signing from Krux
First, calculate the SHA256 hash of the new firmware by running:
```bash
./krux sha256 build/firmware.bin
```

Copy this hex string and turn it into a QR code using whichever QR code generator you'd like.

In Krux, enter the mnemonic of your private key that will be used for signing, and go to **Sign -> Message**. Scan the QR code you generated, and you will be asked if you wish to sign the hash. Proceed, and you will be presented with a base64-encoded string containing the signature, as text and as a QR code.

Take this string and create a signature file by running:
```bash
./krux b64decode "signature-in-base64" > build/firmware.bin.sig
```

This will generate a `firmware.bin.sig` file containing a signature of the firmware's SHA256 hash.

#### Method 2: Signing from your computer with OpenSSL
With the keypair [you generated before](#prerequisite-for-upgrading-via-microsd), you can now run:
```bash
./krux sign build/firmware.bin privkey.pem
```

This will generate a `firmware.bin.sig` file containing a signature of the firmware's SHA256 hash.

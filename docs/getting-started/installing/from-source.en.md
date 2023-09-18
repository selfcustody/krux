This page explains how to install Krux from source.

#### Software
You will need a computer with [`git`](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [`vagrant`](https://www.vagrantup.com/downloads) installed.

### Fetch the code
In a terminal, run the following:
```bash
git clone --recurse-submodules https://github.com/selfcustody/krux
```
This will pull down the Krux source code as well as the code for all its dependencies and put them inside a new `krux` folder.

Note: When you wish to pull down updates to this repo, you can run the following inside the `krux` folder:
```bash
git pull origin main && git submodule update --init --recursive
```

### Spin up a virtual machine
After you have installed Vagrant, run the following inside the `krux` folder to spin up a new VM:
```bash
vagrant up
```

### Build the firmware
#### Prerequisite for upgrading via microSD
If you wish to perform airgapped upgrades via microSD card, you will need to have a private and public key pair to sign your builds and verify the signatures.

You can use an existing Krux installation and mnemonic to sign your builds with, **or** you can generate a keypair and sign from the [`openssl` CLI](https://wiki.openssl.org/index.php/Command_Line_Elliptic_Curve_Operations). Commands have been added to the `krux` shell script to make this easier.

In either case, you will need to update the `SIGNER_PUBKEY` field in `src/krux/metadata.py` to store your public key so that Krux can verify future builds before installing.

To generate a keypair, run:
```bash
vagrant ssh -c 'cd /vagrant; ./krux generate-keypair'
vagrant ssh -c 'cd /vagrant; ./krux pem-to-pubkey pubkey.pem'
```

The first command will create `privkey.pem` and `pubkey.pem` files you can use with openssl, and the second command will output your public key in the form expected by Krux.

Once you've updated the `SIGNER_PUBKEY` with this value, you can proceed with the regular build process.

#### Build
Run the following, replacing `DEVICE` with either `m5stickv`, `amigo_tft`, `amigo_ips`, `dock`, or `bit`:
```bash
vagrant ssh -c 'cd /vagrant; ./krux build maixpy_DEVICE'
```

This will take around an hour or so to complete the first time. Subsequent builds should take only a few minutes.

If all goes well, you should see a new `build` folder containing `firmware.bin` and `kboot.kfpkg` files when the build completes.

### Flash the firmware onto the device
Connect the device to your computer via USB (for Amigo, make sure you’re using bottom port), power it on, and run the following, replacing `DEVICE` with either `m5stickv`, `amigo_tft`, `amigo_ips`, `dock`, or `bit`:
```bash
vagrant ssh -c 'cd /vagrant; ./krux flash maixpy_DEVICE'
```
If the flashing fails try one of the following common solutions:

- Running `vagrant reload` prior to flashing in order for the newly-inserted USB device to be detected and passed through to the VM on startup.
- If this command fails, even after reloading, with the error `Failed to find device via USB. Is it connected and powered on?`, make sure that your user has been added to the `vboxusers` group. On Mac or Linux, run the following command:
  ```bash
  sudo usermod -a -G vboxusers yourusername
  ```
- If the flashing process fails midway through, check the connection, restart the device, and try the command again.

When the flashing process completes, you should see the Krux logo:

<img src="../../../img/maixpy_amigo_tft/logo-150.png">
<img src="../../../img/maixpy_m5stickv/logo-125.png">

If after 30 seconds you still see a black screen, try power cycling the device by holding down the power button for six seconds.

Congrats, you're now running Krux!

#### A note about the Amigo
Some Amigo screens have inverted x coordinates while others don’t.

If after flashing `maixpy_amigo_tft` to your device you notice that the buttons on keypad input screens appear to be in the wrong order, please try flashing `maixpy_amigo_ips` instead (or vice versa) which should correct the issue. 

### Multilingual support
Prefer a different language? Krux has support for multiple languages. Once at the start screen, go to `Settings`, followed by `Locale`, and select the locale you wish to use. If you have a microSD card inserted into the device, your preference will be automatically saved to a `settings.json` file at the root of the card.

### Upgrade via microSD card
Once you've installed the initial firmware on your device via USB, you can either continue updating the device by flashing or you can perform upgrades via microSD card to keep the device airgapped.

After you've built the firmware, you can sign it using one of the following methods.

#### Method 1: Signing from Krux
First, calculate the SHA256 hash of the new firmware by running:
```bash
vagrant ssh -c 'cd /vagrant; ./krux sha256 build/firmware.bin'
```

Copy this hex string and turn it into a QR code using whichever QR code generator you'd like.

In Krux, enter the mnemonic of your private key that will be used for signing, and go to *Sign > Message*. Scan the QR code you generated, and you will be asked if you wish to sign the hash. Proceed, and you will be presented with a base64-encoded string containing the signature, as text and as a QR code.

Take this string and create a signature file by running:
```bash
vagrant ssh -c 'cd /vagrant; ./krux b64decode "signature-in-base64" > build/firmware.bin.sig'
```

This will generate a `firmware.bin.sig` file containing a signature of the firmware's SHA256 hash.

#### Method 2: Signing from your computer with OpenSSL
With the keypair [you generated before](#prerequisite-for-upgrading-via-microsd), you can now run:
```bash
vagrant ssh -c 'cd /vagrant; ./krux sign build/firmware.bin privkey.pem'
```

This will generate a `firmware.bin.sig` file containing a signature of the firmware's SHA256 hash.

### Upgrade via microSD card (continued)
To perform an upgrade, simply copy the `firmware.bin` and `firmware.bin.sig` files to the root of a FAT-32 formatted microSD card, insert the card into your device, and reboot the device. If it detects the new firmware file and is able to verify the signature, you will be prompted to install it.

Once installation is complete, eject the microSD card and delete the firmware files before reinserting and rebooting.

For now, Krux must be built from source. In the future, we will make PGP-signed releases available for download.

### Requirements
#### Hardware
You will need the M5StickV, a [supported microSD card](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md#tf-cardmicrosd-test), a USB-C cable, and a computer with a USB port to continue. Consult the [part list](../../parts) for more information.

#### Software
You will need a computer with [`git`](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [`vagrant`](https://www.vagrantup.com/downloads) installed.

### Fetch the code
In a terminal, run the following:
```bash
git clone --recurse-submodules https://github.com/jreesun/krux
```
This will pull down the Krux source code as well as the code for all its dependencies and put them inside a new `krux` folder.

Note: When you wish to pull down updates to this repo, you can run the following inside the `krux` folder:
```bash
git pull --recurse-submodules
```

### Spin up a virtual machine
After you have installed Vagrant, run the following inside the `krux` folder to spin up a new VM:
```bash
vagrant up
```

### Build the firmware inside the VM
Run the following:
```bash
vagrant ssh -c 'cd /vagrant; ./krux build-firmware'
```
Note: This will take a while to complete. Probably a good time to make some coffee.

### Flash the firmware onto the M5StickV
Connect the M5StickV to your computer via USB, power it on (left-side button), and run the following:
```bash
vagrant reload && vagrant ssh -c 'cd /vagrant; ./krux flash-firmware'
```
Note: `vagrant reload` is necessary in order for the newly-inserted USB device to be detected and passed through to the VM on startup.

If this command fails with the error `Failed to find device via USB. Is it connected and powered on?`, make sure that your user has been added to the `vboxusers` group. On Mac or Linux, run the following command:

```bash
sudo usermod -a -G vboxusers <user>
```

If the flashing process fails midway through, check the connection, restart the device, and try the command again.

If everything worked, when the device reboots you should see... a black screen!

### Build the software
To build the software, run the following:
```bash
vagrant ssh -c 'cd /vagrant; ./krux build-software en-US'
```

Prefer a different language? You can replace `en-US` in the command above with one of the following supported locales:

- de-DE (German)
- es-MX (Spanish)
- fr-FR (French)
- Are we missing one? Make a PR!

Note that due to memory constraints of the device, the translations for the language you wish to use must be baked into the software at this step and can't be changed at runtime.

### Flash the software onto the microSD card
Plug the microSD card into your computer and make sure to format it as FAT-32. After mounting the card, take note of its path on your computer, for example on a Mac it might be located at `/Volumes/SD`.

You can either manually copy over the *contents* of the `build` directory (not the folder itself) onto the root of the card, or run the following to do it for you:
```bash
./krux flash-software /Volumes/SD
```
Note: This will erase everything on the card prior to copying.

### Boot it up
Unmount and remove the microSD card from your machine, insert it into the M5StickV, and long-press its power button (left side) to boot it up. You should soon see the Krux logo appear on the screen. 

<img src="../../img/pic-krux-logo.png" width="150">

If after 30 seconds you still see a black screen, try power cycling the device by holding down the power button for six seconds.

Congrats, you're now running Krux!

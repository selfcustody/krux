# :material-linux: Download assets

For this installation, we'll use the `.deb` sources:

* [`{{latest_installer_deb}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}})
* [`{{latest_installer_deb}}.sha256.txt`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}}.sha256.txt)
* [`{{latest_installer_deb}}.sig`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}}.sig)

## Verify the integrity

----8<----
verify-the-integrity-explain.en.txt
----8<----

```bash
sha256sum --check ./{{latest_installer_deb}}.sha256.txt
```
    
## Verify the authenticity

----8<----
verify-the-signature-explain.en.txt
----8<----

```bash
gpg --verify ./{{latest_installer_deb}}.sig
```

----8<----
verify-the-signature-tip.en.txt
----8<----
    
## Install

This step it's not really an installation.
At least it will make the program's binary available somewhere on your computer;
it can be useful if you want to develop a package for your distro.

To do this you'll need two tools:

* [`ar`](https://linux.die.net/man/1/ar);
* [`bsdtar`](https://man.archlinux.org/man/bsdtar.1).

### Extract contents

- Extract the `.deb` contents:

```bash
ar xv {{latest_installer_deb}}
```

- Extract the `data.tar.zst` contents:

```bash
bsdtar -xvf data.tar.zst
```

The binary will be located at `./usr/local/bin/krux-installer`. 

## After install

----8<----
after-install-installer.en.txt
----8<----
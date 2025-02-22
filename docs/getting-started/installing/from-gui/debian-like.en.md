# :material-debian: Download assets
    
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

**Krux-Installer** isn't available on Debian or Ubuntu repositories.
Therefore, only the `apt-get install` command will not work. 
To install, it'll be necessary two steps:

- Install the .deb package itself:

```bash
sudo dpkg -i {{latest_installer_deb}}
```

- Update the installed package:

```bash
sudo apt-get install -f
```

It will warn you that your system user was added to `dialout` group and maybe you need to reboot
to activate the `sudoless` flash procedure.

## After install

----8<----
after-install-installer.en.txt
----8<----

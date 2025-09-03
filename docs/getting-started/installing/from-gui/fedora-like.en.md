# :material-fedora: Download assets
    
* [`{{latest_installer_rpm}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}})
* [`{{latest_installer_rpm}}.sha256.txt`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}}.sha256.txt)
* [`{{latest_installer_rpm}}.sig`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}}.sig)

## Verify the integrity

----8<----
verify-the-integrity-explain.en.txt
----8<----

```bash
sha256sum --check ./{{latest_installer_rpm}}.sha256.txt
```
    
## Verify the authenticity

----8<----
verify-the-signature-explain.en.txt
----8<----

```bash
gpg --verify ./{{latest_installer_rpm}}.sig
```

----8<----
verify-the-signature-tip.en.txt
----8<----

## Install

**Krux-Installer** isn't available on Fedora or RedHat repositories. You'll need to add it manually:

### Fedora

```bash
sudo dnf install {{latest_installer_rpm}}
```

### Other RedHat based distros:

```bash
sudo yum localinstall {{latest_installer_rpm}}
```
              
It will warn you that your system user was added to `dialout` group and maybe you need to reboot
to activate the `sudoless` flash procedure.

## After install

----8<----
after-install-installer.en.txt
----8<----

# :material-fedora: Download assets
    
* [`{{latest_installer_rpm}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}})

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

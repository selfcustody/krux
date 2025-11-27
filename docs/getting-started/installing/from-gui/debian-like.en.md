# :material-debian: Download assets
    
* [`{{latest_installer_deb}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}})

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

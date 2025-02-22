# :material-apple: Download assets
    
* [`{{latest_installer_mac_arm}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_mac_arm}})
* [`{{latest_installer_mac_arm}}.sha256.txt`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_mac_arm}}.sha256.txt)
* [`{{latest_installer_mac_arm}}.sig`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_mac_arm}}.sig)

## Verify the integrity

----8<----
verify-the-integrity-explain.en.txt
----8<----

```bash
sha256sum --check ./{{latest_installer_mac_arm}}.sha256.txt
```
    
## Verify the authenticity

----8<----
verify-the-signature-explain.en.txt
----8<----

```bash
gpg --verify ./{{latest_installer_mac_arm}}.sig
```
    
----8<----
verify-the-signature-tip.en.txt
----8<----

## Install

----8<----
install-installer-macos.en.txt
----8<----

## After install

----8<----
after-install-installer.en.txt
----8<----

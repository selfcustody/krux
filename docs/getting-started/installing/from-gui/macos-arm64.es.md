# :material-apple: Descargar Recursos
    
* [`{{latest_installer_mac_arm}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_mac_arm}})
* [`{{latest_installer_mac_arm}}.sha256.txt`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_mac_arm}}.sha256.txt)
* [`{{latest_installer_mac_arm}}.sig`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_mac_arm}}.sig)

## Verificar la integridad

----8<----
verify-the-integrity-explain.es.txt
----8<----

```bash
sha256sum --check ./{{latest_installer_mac_arm}}.sha256.txt
```
    
## Verificar la autenticidad

----8<----
verify-the-signature-explain.es.txt
----8<----

```bash
gpg --verify ./{{latest_installer_mac_arm}}.sig
```
    
----8<----
verify-the-signature-tip.es.txt
----8<----

## Instalar

----8<----
install-installer-macos.es.txt
----8<----

## Después de Instalar

----8<----
after-install-installer.es.txt
----8<----

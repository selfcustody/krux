# :material-fedora: Descargar Recursos
    
* [`{{latest_installer_rpm}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}})
* [`{{latest_installer_rpm}}.sha256.txt`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}}.sha256.txt)
* [`{{latest_installer_rpm}}.sig`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}}.sig)

## Verificar la integridad

----8<----
verify-the-integrity-explain.es.txt
----8<----

```bash
sha256sum --check ./{{latest_installer_rpm}}.sha256.txt
```
    
## Verificar la autenticidad

----8<----
verify-the-signature-explain.es.txt
----8<----

```bash
gpg --verify ./{{latest_installer_rpm}}.sig
```

----8<----
verify-the-signature-tip.es.txt
----8<----

## Instalar


**Krux-Installer** no está disponible en repositorios de Fedora o RedHat. Necesitarás añadirlo manualmente:

### Fedora

```bash
sudo dnf install {{latest_installer_rpm}}
```

### Otras distribuciones basadas en RedHat:

```bash
sudo yum localinstall {{latest_installer_rpm}}
```

Se le advertirá que su usuario se agregó al grupo `dialout` y que quizás deba reiniciar 
el sistema para activar el procedimiendo de flash `sudoless`.             

## Después de instalar

----8<----
after-install-installer.es.txt
----8<----

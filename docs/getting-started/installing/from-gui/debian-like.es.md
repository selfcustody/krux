# :material-debian: Descargar Recursos
    
* [`{{latest_installer_deb}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}})
* [`{{latest_installer_deb}}.sha256.txt`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}}.sha256.txt)
* [`{{latest_installer_deb}}.sig`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}}.sig)

## Verificar la integridad

----8<----
verify-the-integrity-explain.es.txt
----8<----

```bash
sha256sum --check ./{{latest_installer_deb}}.sha256.txt
```
    
## Verificar la autenticidad

----8<----
verify-the-signature-explain.es.txt
----8<----

```bash
gpg --verify ./{{latest_installer_deb}}.sig
```

----8<----
verify-the-signature-tip.es.txt
----8<----
    
## Instalar

**Krux-Installer** no está disponible en los repositorios de Debian ni Ubuntu.
Por lo tanto, el comando `apt-get install` no funcionará.
Para instalarlo, se requieren dos pasos: 

- Instalar el paquete .deb:

```bash
sudo dpkg -i {{latest_installer_deb}}
```

- Actualizar el paquete instalado:

```bash
sudo apt-get install -f
```

Se le advertirá que su usuario se agregó al grupo `dialout` y que quizás deba reiniciar 
el sistema para activar el procedimiendo de flash `sudoless`.

## Después de instalar

----8<----
after-install-installer.es.txt
----8<----

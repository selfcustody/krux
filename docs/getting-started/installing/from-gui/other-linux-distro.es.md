# :material-linux: Descargar Recursos

Para esta instalación, vamos a usar los recursos `.deb`:

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

Este paso no es realmente una instalación.
Por lo menos hará disponibles los archivos binarios del programa en algún lugar de tu computadora;
Puede ser útil si quieres desarrollar un paquete para tu distribución de Linux.

Para hacer esto necesitarás dos herramientas:

* [`ar`](https://linux.die.net/man/1/ar);
* [`bsdtar`](https://man.archlinux.org/man/bsdtar.1).

### Extraer los contenidos

- Extrae los recursos `.deb`:

```bash
ar xv {{latest_installer_deb}}
```

- Extrae los recursos `data.tar.zst`:

```bash
bsdtar -xvf data.tar.zst
```

El archivo binario será ubicado en `./usr/local/bin/krux-installer`. 

## Después de instalar

----8<----
after-install-installer.es.txt
----8<----
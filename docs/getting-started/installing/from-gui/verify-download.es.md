Antes de empezar a usar la interfaz gráfica (GUI), se **recomienda encarecidamente** verificar la autenticidad del archivo [{{latest_installer_sha}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_sha}}).
Certifica la integridad de todas las variantes ([{{latest_installer_deb}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_deb}}), [{{latest_installer_rpm}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_rpm}}), [{{latest_installer_mac_arm}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_mac_arm}}), [{{latest_installer_win}}](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_win}})).

Para ello, descargue dos archivos:

* [`{{latest_installer_sha}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_sha}});
* [`{{latest_installer_sig}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_sig}}).

## Verificar la autenticidad

**Linux/MacOS**

El siguiente paso es importar la llave del desarrollador:

```bash
gpg --keyserver {{latest_installer_keyserver}} --recv-keys {{latest_installer_key}}
```

Para verificar tu identidad, ejecuta esto:

```bash
gpg --verify {{latest_installer_sig}}
```

**Windows**

* Necesitarás tener instalado [GPG](https://gnupg.org/);
* Recomendamos instalar [GPG4Win](https://www.gpg4win.org/).

Después de la instalación, puedes continuar con los pasos para **Linux/MacOS** en la terminal.

----8<----
verify-the-signature-tip.es.txt
----8<----
> También puedes ignorar un mensaje de ADVERTENCIA si indica que la clave no es confiable (debes hacerlo manualmente).

## Verificar la integridad

Tras verificar la autenticidad del archivo [`{{latest_installer_sha}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_sha}}), podemos proceder a la comprobación de integridad en tu terminal `bash`/`zsh`:

**Linux / MacOS**

```bash
sha256sum --check {{latest_installer_sha}}
```

**Windows**

Puedes verificar la integridad con este comando en una terminal `powershell`:

```pwsh
$exe = '.\{{latest_installer_win}}'
$file = Split-Path $exe -Leaf

(Get-FileHash $exe -Algorithm SHA256).Hash -eq
(Select-String $file '.\{{latest_installer_sha}}').Line.Split()[0].ToUpper()
```

----8<----
verify-the-signature-trust-tip.es.txt
----8<----




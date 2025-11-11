# :material-microsoft-windows: Descargar recursos
 
* [`{{latest_installer_win}}`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_win}})
* [`{{latest_installer_win}}.sha256.txt`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_win}}.sha256.txt)
* [`{{latest_installer_win}}.sig`](https://github.com/selfcustody/krux-installer/releases/download/{{latest_installer}}/{{latest_installer_win}}.sig)

## Verificar la integridad

----8<----
verify-the-integrity-explain.es.txt
----8<----

```pwsh
(Get-FileHash '.\{{latest_installer_win}}').Hash.ToLower() -eq (Get-Content '.\{{latest_installer_win}}.sha256.txt').split(" ")[0]
```

El resultado en consola debería ser `True`.

Alternativamente, puedes comprobarlo más detenidamente en dos pasos:

* Calcula el hash binario sha256sum:

```pwsh
# Opción 1: Calcular de forma predeterminada
Get-FileHash '.\{{latest_installer_win}}'

# Opción 2: Calcular y filtrar la información necesaria
(Get-FileHash '.\{{latest_installer_win}}').Hash

# Opción 3: Calcular, filtrar y procesar el hash para letras minúsculas
(Get-FileHash '.\{{latest_installer_win}}').Hash.ToLower()
```

* Comparar con el hash proporcionado:

```pwsh
# Opción 1: Obtener contenido 
Get-Content '.\{{latest_installer_win}}.sha256.txt'

# Opción 2: Obtener contenido y filtrar información necesaria
(Get-Content '.\{{latest_installer_win}}.sha256.txt').split(" ")[0]
```

## Verificar la autenticidad
    
* Necesitas tener [GPG](https://gnupg.org/) instalado;
* Recomendamos instalar [GPG4Win](https://www.gpg4win.org/).

----8<----
verify-the-signature-explain.es.txt
----8<----
 
```pwsh
gpg --verify ./{{latest_installer_win}}.sig
```

----8<----
verify-the-signature-tip.es.txt
----8<----

## Instalar

Ejecuta el `{{latest_installer_win}}`. Te encontrarás una ventana azul con el mensaje "Windows a protegido su PC". Esto ocurre porque no tenemos un [certificado de firma de código](https://signmycode.com/resources/how-to-sign-an-exe-or-windows-application):

<img width="450" src="/krux/img/krux-installer/windows_warn0.jpg" alt="Windows protected your computer" />

----8<----
verify-the-signature-trust-tip.es.txt
----8<----

Sigue las instrucciones del programa para completar la instalación. Al final, presiona "Crear ícono de Escritorio":

## Después de Instalar

----8<----
after-install-installer.es.txt
----8<----

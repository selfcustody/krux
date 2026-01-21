Esta pagina explica como descargar e instalar el firmware de Krux desde nuestra última versión oficial precompilada.

[<img src="/krux/img/badge_github.png" width="186">](https://github.com/selfcustody/krux/releases)

### Verifica los archivos
Antes de instalar la versión, es una buena idea revisar que:

1. El *hash SHA256* de `{{latest_krux}}.zip` coincide con el hash en `{{latest_krux}}.zip.sha256.txt`
2. El *archivo de firma* `{{latest_krux}}.zip.sig` puede ser verificado con la [ llave pública `selfcustody.pem`](https://github.com/selfcustody/krux/blob/main/selfcustody.pem) encontrada en la base del repositorio de Krux.

Puedes hacer esto de forma manual o con el script de shell `krux`, el cual contiene comandos de ayuda para esto:
```bash
### Usando el script de Krux ###
# checksum del Hash
./krux sha256 {{latest_krux}}.zip
# Firma
./krux verify {{latest_krux}}.zip selfcustody.pem

### Manualmente ###
# checksum del Hash
sha256sum {{latest_krux}}.zip.sha256.txt -c
# Firma
openssl sha256 <{{latest_krux}}.zip -binary | openssl pkeyutl -verify -pubin -inkey selfcustody.pem -sigfile {{latest_krux}}.zip.sig
```

En Mac es posible que necesites instalar `coreutils` para poder utilizar `sha256sum`  
```
brew install coreutils
```

Dato curioso: Cada nuevo lanzamiento de Krux está firmado con Krux!

### Actualizar el firmware al dispositivo
Extrae la última version de Krux que descargaste y entra al directorio de la carpeta:
```bash
unzip {{latest_krux}}.zip && cd {{latest_krux}}
```

Conecta el dispositivo a tu computadora via USB (para el Maix Amigo, asegúrate de utilizar el puerto en la parte inferior), enciéndelo, y corre el siguiente comando, reemplazando `DEVICE` con `m5stickv`, `amigo`, `cube` o `yahboom` (para Yahboom es posible que tengas que especificar manualmente el puerto, por ejemplo `/dev/ttyUSB0` en Linux o `COM6` en Windows):
```bash
./ktool -B goE -b 1500000 maixpy_DEVICE/kboot.kfpkg
```

Para `dock`, `wonder_mv`, `tzt` o `embed_fire` usa el parámetro `-B dan`:
```bash
./ktool -B dan -b 1500000 maixpy_DEVICE/kboot.kfpkg
```

----8<----
flash-krux-logo.es.txt
----8<----

----8<----
amigo-more-info-faq.es.txt
----8<----

#### Solución de problemas
Si `ktool` no se ejecuta, puede que tenga que otorgarle permisos de ejecución con `chmod +x ./ktool`, o puede que tenga que usar "sudo" si su usuario no tiene acceso al puerto serie. En Windows o Mac, puede que tenga que permitir explícitamente la ejecución de la herramienta añadiento una excepción.

Si el proceso de actualización falla a mitad de camino, compruebe la conexión, reinicie el dispositivo y vuelva a intentar el comando.

Se crean dos puertos serie al conectar `Amigo` a un PC. En ocasiones, Ktool seleccionará el puerto incorrecto y la actualización fallará. Para solucionar este problema, especifique manualmente el puerto serie con el argumento `-p`:

##### Linux
Consulte el puerto correcto usando `ls /dev/ttyUSB*`, en el siguiente ejemplo usamos `/dev/ttyUSB0`:
```bash
./ktool-linux -B goE -b 1500000 maixpy_amigo/kboot.kfpkg -p /dev/ttyUSB1
```

##### Windows
Consulte el puerto correcto en **Administrador de dispositivos -> Puertos (COM y LPT)**, en el siguiente ejemplo usamos `COM6`:
```pwsh
.\ktool-win.exe -B goE -b 1500000 maixpy_amigo\kboot.kfpkg -p COM6
```

##### Mac
Remueva el atributo extendido de cuarentena Gatekeeper de ktool-mac:
```bash
xattr -d com.apple.quarantine ktool-mac
```

Consulte el puerto correcto utilizando la linea de comandos: `ls /dev/cu.usbserial*`, en el siguiente ejemplo usamos `/dev/cu.usbserial-10` (Si el resultado no es el esperado, pruebe otro cable, preferiblemente un cable de carga USB-C para smartphone):
```bash
./ktool-mac -B goE -b 1500000 maixpy_amigo/kboot.kfpkg -p /dev/cu.usbserial-10
```

Las diferentes versiones de sistema operativo pueden tener diferentes nombres de puertos, y la ausencia de puertos puede indicar un problema relacionado con la conexión, el controlador o el hardware. Consulte [Solución de problemas](../../troubleshooting.md/#device-not-charging-or-being-recognized) para obtener más información.

----8<----
tips-after-install.es.txt
----8<----

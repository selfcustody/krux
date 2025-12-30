Esta página explica cómo instalar Krux desde el código fuente. También puedes consultar una versión simplificada de estas instrucciones en nuestro [README](https://github.com/selfcustody/krux).

### Obtener el código
Esto descargará el código fuente de Krux, así como el código de todas sus dependencias, en una nueva carpeta llamada `krux` (requiere [`git`](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)):
```bash
git clone --recurse-submodules https://github.com/selfcustody/krux
```

**Nota**: Cuando desee extraer actualizaciones (para todos los submódulos, sus submódulos, etc.) a este repositorio, utilice:
```bash
git pull origin main && git submodule update --init --recursive
```

#### Requisito previo para actualizar mediante microSD
Si desea realizar actualizaciones posteriores sin conección a internet mediante una tarjeta micro SD, necesitará un par de claves privada y pública para firmar sus compilaciones de código y verificar las firmas. Si no desea realizar más actualizaciones sin coneccion a internet, vaya a la [sección de compilación](#build-the-firmware-linux-or-wsl).

Puedes usar una instalación de Krux existente y una clave mnemotécnica para firmar sus compilaciones de código, **o bien**, puede generar un par de claves y firmar desde la [linea de comando con `openssl`](https://wiki.openssl.org/index.php/Command_Line_Elliptic_Curve_Operations). Se han añadido comandos al script de shell de `krux` para facilitar esta tarea.

En cualquier caso, deberá actualizar el campo `SIGNER_PUBKEY` en `src/krux/metadata.py` para almacenar su clave pública, de modo que Krux pueda verificar futuras compilaciones antes de la instalación.

Para generar un par de claves:
```bash
./krux generate-keypair
./krux pem-to-pubkey pubkey.pem
```

El primer comando creará los archivos `privkey.pem` y `pubkey.pem` que puedes usar con openssl, y el segundo comando generará tu clave pública en el formato esperado por Krux.

Una vez que hayas actualizado `SIGNER_PUBKEY` con este valor, puedes continuar con el proceso de compilación normal.

### Compila el firmware (Linux o WSL)
El [script bash de Krux](https://github.com/selfcustody/krux/blob/main/krux) contiene comandos para tareas de desarrollo comunes. Se asume un host Linux; necesitará tener instalados al menos [Docker Desktop o Docker Engine](https://docs.docker.com/desktop/), `openssl`, y `wget` para que los comandos funcionen correctamente. Funciona en Windows con WSL. El canal de YouTube Crypto Guide publicó un video paso a paso: [Krux DIY Bitcoin Signer: Build From Source & Verify (With Windows + WSL2 + Docker)](https://www.youtube.com/watch?v=Vmr_TFy2TfQ)

Para compilar y flashear el firmware:
```bash
# firmware de compilación para Maix Amigo
./krux build maixpy_amigo
```

La primera vez, la compilación del código puede tardar aproximadamente una hora. Las compilaciones posteriores deberían tardar solo unos minutos. Si todo va bien, verá una nueva carpeta `build` con los archivos `firmware.bin` y `kboot.kfpkg` al finalizar la compilación.

**Nota**: Si encuentra alguno de estos errores durante la compilación, se debe a un problema de conexión a GitHub. Inténtelo de nuevo (si el error persiste, intente cambiar el DNS/VPN o corregir la resolución del nombre de host de github.com a una IP que funcione correctamente):
```
error: RPC failed; curl 92 HTTP/2 stream 0 was not closed cleanly: CANCEL (err8)
fatal: the remote end hung up unexpectedly
fatal: early EOF
fatal: index-pack failed
fatal: clone of ... failed
Failed to clone ...
```

#### Reproducibilidad
Si compila desde la rama `main` del código fuente, debería poder reproducir el proceso de compilación utilizado para generar los binarios de la última versión y obtener exactamente las mismas copias de los archivos `firmware.bin` y `kboot.kfpkg`, con las sumas de comprobación hash correspondientes (para comprobar si hay una versión anterior, utilice la etiqueta `tag`).

Para comprobarlo, utilice los archivos compilatdos para el dispositivo de destino. Cada comando debe generar el mismo hash para los dos archivos proporcionados:
```bash
sha256sum build/firmware.bin {{latest_krux}}/maixpy_DEVICE/firmware.bin
sha256sum build/kboot.kfpkg {{latest_krux}}/maixpy_DEVICE/kboot.kfpkg
```

Si desea extraer y verificar el archivo `firmware.bin` contenido en `kboot.kfpkg`, utilice lo siguiente:

```bash
unzip kboot.kfpkg -d ./kboot/
```

### Instale el firmware en el dispositivo
Conecte el dispositivo a su computadora mediante USB (para Maix Amigo, asegúrese de usar el puerto inferior), enciéndalo y ejecute lo siguiente, reemplazando `DEVICE` por `m5stickv`, `amigo`, `cube`, `dock`, `yahboom`, `wonder_mv`, `tzt` o `embed_fire`:
```bash
# flashear el firmware al DISPOSITIVO
./krux flash maixpy_DEVICE
```
Si el flasheo falla, intenta leer [Solución de problemas](../../troubleshooting.md)

----8<----
flash-krux-logo.es.txt
----8<----

----8<----
amigo-more-info-faq.es.txt
----8<----

### Firma del firmware
Puedes firmar el firmware para [realizar actualizaciones en sistemas aislados (air-gapped)](#prerequisite-for-upgrading-via-microsd) usando uno de los dos métodos que se indican a continuación:

#### Método 1: Firma desde Krux
Primero, calcula el hash SHA256 del nuevo firmware ejecutando:
```bash
./krux sha256 build/firmware.bin
```

Copia esta cadena hexadecimal y conviértela en un código QR usando el generador de códigos QR que prefieras.

En Krux, introduce la clave mnemotécnica de tu clave privada que se usará para firmar y ve a **Firmar -> Mensaje**. Escanea el código QR que generaste y se te preguntará si desdeas firmar el hash. Continúa y verás una cadena codificada en base64 que contiene la firma, tanto en texto como en código QR.

Toma esta cadena y crea un archivo de firma ejecutando:
```bash
./krux b64decode "signature-in-base64" > build/firmware.bin.sig
```

Esto generará un archivo `firmware.bin.sig` que contiene la firma del hash SHA256 del firmware.

#### Método 2: Firmar desde tu ordenador con OpenSSL
Con el par de claves [que generaste anteriormente](#prerequisite-for-upgrading-via-microsd), ahora puedes ejecutar:
```bash
./krux sign build/firmware.bin privkey.pem
```

Esto generará un archivo `firmware.bin.sig` que contiene la firma del HASH256 del firmware.

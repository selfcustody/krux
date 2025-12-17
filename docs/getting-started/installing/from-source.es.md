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

The first time, the build can take around an hour or so to complete. Subsequent builds should take only a few minutes. If all goes well, you should see a new `build` folder containing `firmware.bin` and `kboot.kfpkg` files when the build completes.

**Note**: if you encounter any of these errors while building, it is a problem connecting to github, try again (if the error persists, try changing the DNS/VPN or correcting the hostname resolution of github.com to an IP that is working for you):
```
error: RPC failed; curl 92 HTTP/2 stream 0 was not closed cleanly: CANCEL (err8)
fatal: the remote end hung up unexpectedly
fatal: early EOF
fatal: index-pack failed
fatal: clone of ... failed
Failed to clone ...
```

#### Reproducibility
If you build from the `main` branch of the source code, you should be able to reproduce the build process used to generate the latest release binaries and obtain exactly the same copies of the `firmware.bin` and `kboot.kfpkg` files, with matching hash checksums (to check for an older version, use the `tag` instead).

To check, use the compiled files for the target device. Each command should output the same hash for the two provided files:
```bash
sha256sum build/firmware.bin {{latest_krux}}/maixpy_DEVICE/firmware.bin
sha256sum build/kboot.kfpkg {{latest_krux}}/maixpy_DEVICE/kboot.kfpkg
```

If you want to extract and verify the `firmware.bin`file contained in `kboot.kfpkg`, use the following:

```bash
unzip kboot.kfpkg -d ./kboot/
```

### Flash the firmware onto the device
Connect the device to your computer via USB (for Maix Amigo, make sure you’re using bottom port), power it on, and run the following, replacing `DEVICE` with either `m5stickv`, `amigo`, `cube`, `dock`, `yahboom`, `wonder_mv`, `tzt` or `embed_fire`:
```bash
# flash firmware to DEVICE
./krux flash maixpy_DEVICE
```
If flashing fails try reading [Troubleshooting](../../troubleshooting.md)

----8<----
flash-krux-logo.en.txt
----8<----

----8<----
amigo-more-info-faq.en.txt
----8<----

### Signing the firmware
You can sign the firmware to [perform airgapped upgrades](#prerequisite-for-upgrading-via-microsd) using one of the two methods listed below:

#### Method 1: Signing from Krux
First, calculate the SHA256 hash of the new firmware by running:
```bash
./krux sha256 build/firmware.bin
```

Copy this hex string and turn it into a QR code using whichever QR code generator you'd like.

In Krux, enter the mnemonic of your private key that will be used for signing, and go to **Sign -> Message**. Scan the QR code you generated, and you will be asked if you wish to sign the hash. Proceed, and you will be presented with a base64-encoded string containing the signature, as text and as a QR code.

Take this string and create a signature file by running:
```bash
./krux b64decode "signature-in-base64" > build/firmware.bin.sig
```

This will generate a `firmware.bin.sig` file containing a signature of the firmware's SHA256 hash.

#### Method 2: Signing from your computer with OpenSSL
With the keypair [you generated before](#prerequisite-for-upgrading-via-microsd), you can now run:
```bash
./krux sign build/firmware.bin privkey.pem
```

This will generate a `firmware.bin.sig` file containing a signature of the firmware's SHA256 hash.

## **Antes de la Instalación**

### ¿El Sistema Operativo Linux no detecta el puerto serie?

Si recibe el siguiente error al intentar actualizar el dispositivo a través del cable USB: `Failed to find device via USB. Is it connected and powered on?`
Asegúrese de que su dispositivo esté siendo detecctado y de que los puertos serie estén siendo montados ejecutando:
```bash
ls /dev/ttyUSB*
```
Espere que se enumere un puerto para dispositivos como M5StickV y MAIX Doc `/dev/ttyUSB0`, y dos puertos para Maix Amigo `/dev/ttyUSB0  /dev/ttyUSB1`.

Si no los ve, es posible que su sistema operativo no esté cargando los controladores correctos para crear los puertos serie a los que conectarse. Ubuntu tiene un error conocido en el que el controlador `brltty`  "secuestra" dispositivos serie. Puede resolver este problema elimininándolo:
```bash
sudo apt-get remove brltty
```

### ¿El dispositivo no carga o no es detectado?

*Si tienes un Maix Amigo, asegurate de usar el puerto USB-C en la parte inferior del dispositivo, no utilizar el puerto del lado izquiero.* 

Los distintos ordenadores tienen hardware, sistemas operativos y comportamientos diferentes a la hora de conectarse a sus puertos USB. A continuación se describen los comportamientos esperados:

**USB-A:**

Tu dispositivo debería cargar y prender cuando se conecta el puerto USB-A, incluso si estaba inicialmente apagado. También puedes apagar el dispositivo mientras carga. Sin embargo, algunos puertos USB-A de los dispositivos pueden comportarse como puertos USB-C, como se describe a continuación.

**USB-C:**

### M5StickV, WonderMV

----8<----
usb-c-pull-up-resistor.es.txt
----8<----

#### Maix Amigo, Cube
- Si el dispositivo está apagado y conectado a un puerto USB-C, debería encenderse y comenzar a cargarse. Puede apagarlo nuevamente y continuará cargándose.

- Si el dispositivo ya está encendido y conectado a un puerto USB-C, es posible que no se cargue o que el ordenador no lo reconozca. En este caso, apague el dispositivo para que se inicie el reconocimiento y la carga. Una vez apagado y reconectado, el dispositivo debería reiniciarse, ser reconocido por el ordenadoro y la carga debería activarse mediante el USB-C del host.
Si tu dispositivo no se carga o no se reconoce correctamente, intente usar un puerto USB diferente o un ordenador distinto para determinar si el problema reside en el dispositivo o en el puerto USB del ordenador.

### ¿El dispositivo se bloquea o reinicia aleatoriamente?
Si el dispositivo se comporta de esta manera al conectarlo al ordenador, se sabe que Windows presenta problemas con los dispositivos USB-C. Si experimenta bloqueos o reinicios aleatorios y su dispositivo no tiene batería, intente usar un cargador de teléfono u otra fuente de alimentación, como una batería externa.

### Error al flashear
Si el flasheo falla con el error: `Greeting fail, check serial port (SLIP receive timeout (wait frame start))` o `[ERROR] No vaild COM Port found in Auto Detect, Check Your Connection or Specify One by --port/-p`, revise el comando utilizado. La mayoría de los dispositivos requieren el argumento `-B goE` para *ktool*, pero `dock` y `wonder_mv` utilizan el argumento `-B dan`. Para `yahboom` también debe especificar manualmente el puerto con el argumento `-p`.

----8<----
error-flashing-windows.es.txt
----8<----


## **Después de la Instalación**

### La pantalla táctil de Maix Amigo no funciona con v24.03.0 y posteriores, pero funcionó bien con v23.09.1?

<img src="../img/amigo-inside-switch-up.jpg" align="right">

Hemos añadido una IRQ(solicitud de interrupción) de hardware al firmware, por lo que cuando abra su Maix Amigo, verá un interruptor en el centro de la placa del dispositivo; debe estar en la posición superior para que la pantalla táctil funcione con la versión v24.03.0 y posteriores.

<div style="clear: both"></div>


### Solución de Problemas de la configuración de la pantalla LCD en Maix Amigo

#### Botones en orden incorrecto

Si los botones de las pantallas de entrada del teclado aparecen en el orden incorrecto, esto podría deberse a que las coordenadas X están invertidas. Para corregirlo:

1. Vaya a **Ajustes -> Hardware -> Pantalla**.
2. Cambie el valor de `Coordenadas X Invertidas`.

#### Colores incorrectos

Si los colores que se muestran en los temas de la interfaz o en la imagen de la cámara son incorrectos, puede probar las siguientes opciones:

- **Colores invertidos**: Si, por ejemplo, el color de fondo es blanco cuando debería ser negro, vaya a **Ajustes -> Hardware -> Pantalla** y active o desactive `Colores invertidos`.

- **Colores BGR**: Si, por ejemplo, está usando el tema Naranja y, en lugar de naranja, los colores aparecen azulados, vaya a **Ajustes -> Hardware -> Pantalla** y active o desactive `Colores BGR` en la configuración de pantalla.

- **Typo de LCD**: ¡Advertencia! Solo intente cambiar este ajuste si no logró corregir los colores con los ajustes anteriores.
    - Si ajustar `Colores Invertidos` o `Colores BGR` no soluciona el problema de color, intente cambiar el `Tipo de LCD`:

        - (1) Después de cambiar el  `Tipo de LCD`, se le advertirá que el dispositivo se reiniciará automáticamente si este cambio no resuelve el problema.

        - (2) Si después ve un mensaje que le pide que pulse el botón `ANTERIOR` (ARRIBA), significa que el nuevo ajuste funcionó. Si solo ve una pantalla negra, significa que falló.

        - (3) Si funciona, pero los colores siguen siendo incorrecctos, intente nuevamente con diferentes combinaciones de `Colores Invertidos` y `Colores BGR`. Esta vez, probablemente encontrará una combinación que muestre correctamente los colores de los temas de su interfaz y la imagen de la cámara.

        Si, después del paso (1), la pantalla se pone negra y no ve nada, no se preocupe, no pulse ningún botón, solo espere 5 segundos. Tras 5 segundos, el dispositivo se reiniciará automáticamente con la configuración anterior de `Tipo de LCD`. Por lo tanto, no debe cambiar esta configuración y, si es necesario, intente nuevamente solo con `Colores Invertidos` y `Colores BGR`.

        Si pulsó `ANTERIOR` (ARRIBA) y Krux guardó una configuración incorrecta de `Tipo de LCD`, deberá eliminar todas las configuraciones guardadas para que la pantalla vuelva a funcionar. Si las configuraciones estaban en la tarjeta SD, extráigala del dispositivo y edite o elimine las configuraciones manualmente. Si las configuraciones estaban en la memoria interna del dispositivo, deberá borrar toda la memoria flash. Puede usar la función [Borrar dispositivo](getting-started/installing/from-gui/usage.md/#wipe-device) del Instalador de Krux o escribir un comando en la terminal con el dispositivo conectado. En Linux, por ejemplo, diríjase a la carpeta donde descargó el firmware de Krux y use *Ktool* para borrar completamente su dispositivo (en otros sistemas operativos use `ktool-win.exe` o `ktool-mac`):

        ```bash
        ./ktool-linux -B goE -b 1500000 -E
        ```

        Luego, vuelva a instalar el firmware usando Krux-Installer o escribiendo en la terminal:

        ```bash
        ./ktool-linux -B goE -b 1500000 maixpy_amigo/kboot.kfpkg
        ```

### El dispositivo no se reinicia, la pantalla está en negro o se queda atascada en el logo

Si el dispositivo no se reinició tras actualizar correctamente el firmware, si la pantalla está en negro después de apagarlo y encenderlo, o si se queda congelado con el logotipo en la pantalla, compruebe que el archivo descargado sea compatible con su dispositivo o intente descargar los binarios de nuevo, ya que esto también podría deberse a corrupción de datos.

También puede instalar [MaixPy IDE](https://dl.sipeed.com/shareURL/MAIX/MaixPy/ide/v0.2.5) para facilitar la depuración. En su menú, vaya a **Herramientas -> Abrir Terminal -> Nueva Terminal -> Conctar al puerto serie -> Selecccione un puerto COM disponible** (si no funciona, pruebe con otro puerto COM). Se mostrará la terminal y algunos mensajes; un mensaje sobre un dispositivo vacío o con firmware dañado podría ser similar a: "interesting, something's wrong, boot failed with exit code 233, go to find your vendor."

## **Uso**

### Por qué Krux no escanea el código QR?

<video style="width: 20%; min-width: 240px;" controls class="align-right margin-left">
    <source src="../img/cam-adjust-pliers.mp4" type="video/mp4"></source>
</video>


La pantalla muestra exactamente lo que Krux ve a través de su cámara. Si el código QR se ve borroso, es posible que la lente esté desenfocada. Puede corregirlo girando suavemente la lente: gírela **en sentido antihorario (desenroscando para reducir la distancia de enfoque)** o **en sentido horario (enroscando para aumentar la distancia de enfoque)** hasta que la imagen se vea nítida. Tenga en cuenta que la lente podría estar fijada con una pequeña gota de pegamento, lo que dificulta un poco el primer ajuste. Para girar el anillo de plástico de la lente, use la yema del dedo, unas pinzas o unos alicates de precisión pequeños (idealmente envueltos con cinta aislante para evitar rayones). Una vez ajustado, enfocar en el futuro será mucho más fácil.

Si la lente ya está ajustada, el problema podría ser la distancia al código QR. Acerque el dispositivo al código y aléjelo lentamente hasta que el código QR completo quepa en la pantalla. Una vez que el código se vea nítido y claro, Krux debería detectarlo rápidamente y responder de inmediato.

----8<----
camera-scan-tips.es.txt
----8<----

<div style="clear: both"></div>

### ¿Error al escanear el código QR?

Si Krux reconoce el código QR pero muestra un mensaje de error tras leerlo, probablemente se deba a que el código QR no tiene un formato compatible con Krux. Hemos listado los formatos compatibles a continuación:

Para mnemónicos BIP39:

- Texto plano BIP39 (Usado por Krux y [https://iancoleman.io/bip39/](https://iancoleman.io/bip39/))
- Formatos [SeedQR and CompactSeedQR](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md) de SeedSigner
- [Tipo UR `crypto-bip39`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-006-urtypes.md)
- Código QR encriptado (Formato creado por Krux, [más información aquí](getting-started/features/encryption/encryption.md/#regarding-bip39-mnemonics))

Para Wallet output descriptors:

- JSON con al menos una clave `descriptor` que contenga una cadena de descriptor de salida
- Archivos INI de clave-valor con al menos las claves `Format`, `Policy` y `Derivation`
- [UR Type `crypto-output`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-010-output-desc.md)

Para PSBT (Transacciones de Bitcoin Parcialmente Firmadas):

- Bytes codificades en Base43, Base58, y Base64
- Bytes sin procesar
- [UR Type `crypto-psbt`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-006-urtypes.md)

Además, Krux reconoce códigos QR animados que usan texto plano `pMofN` (el formato QR de Specter) o codificaciones binarias [`UR`](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md).


### ¿Tu ordenador no lee el código QR que muestra Krux?

Puedes cambiar el brillo de los códigos QR de PSBT pulsando el botón `PAGE` o `PREVIOUS`. Si usas un M5StickV, la pantalla pequeña dificulta que las cámaras web de los portátiles capturen suficiente detalle para analizar los códigos QR que muestra. Por ahora, una solución alternativa es tomar una foto o grabar un vídeo del código QR con una cámara de mejor calidad (como la de tu teléfono), ampliarla y mostrarla en tu cámara web.

Como alternativa, puede ser más sencillo usar una billetera móvil (BlueWallet o Nunchuk) con el M5StickV, ya que las cámaras de los teléfonos no parecen tener problemas para leer los códigos QR pequeños. También puedes guardar el PSBT en una tarjeta microSD para que Krux lo firme y luego guardar el PSBT firmado para transferirlo al ordenador o al teléfono. Otros códigos QR mostrados por Krux también se pueden exportar como imagen a la tarjeta SD.


### ¿Por qué Krux dice que la entropía de mis cincuenta tiradas de dados no contiene 128 bits de entropía?

Comprueba cómo funciona la [medición de entropía](getting-started/features/entropy.md).

### ¿Por qué Krux no detecta mi tarjeta microSD o muestra un error?
A partir de la versión 23.09.0, Krux admite la conexión en caliente de tarjetas SD. Si usas versiones anteriores, es posible que solo detecte la tarjeta SD al arrancar, así que asegúrate de que Krux esté apagado al insertar la microSD. Para comprobar la compatibilidad de la tarjeta, utilice Krux [Herramientas -> Comprobar tarjetaa SD](getting-started/features/tools.md/#check-sd-card).

**Nota**: Asegúrese de que la tarjeta SD utilice la tabla de particiones MBR/DOS y el formato FAT32. [En este vídeo](https://www.youtube.com/watch?v=dlOiAJOPoME) Crypto Guide explica cómo hacerlo en Windows. Si sigue sin detectarse, intente eliminar todos los archivos grandes que contenga.

### ¿Por qué mi WonderMV se reinicia al insertar una tarjeta SD?

Parece que WonderMV tiene un problema de diseño de hardware: carece de un condensador de desacoplamiento en el circuito que alimenta la tarjeta SD. Algunas tarjetas SD pueden provocar una caída de la tensión de alimentación al insertarlas, lo que provoca un reinicio.

**Soluciones alternativas:**

- Inserte la tarjeta SD antes de encender el dispositivo. Por ejemplo, al firmar PSBT, inserte la tarjeta SD que contiene el PSBT sin firmar antes de encender WonderMV y cargar la clave.
- Pruebe con diferentes tarjetas SD, ya que algunas requieren menos corriente y no hacen que el dispositivo se reinicie.

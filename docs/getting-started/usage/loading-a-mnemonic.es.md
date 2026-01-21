Una vez que tengas un [mnemonico BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) de 12 o 24 palabras, seleccione `Cargar Mnemónico` en el menú de inicio de Krux (también conocido como menú de inicio de sesión) y elija un método de entrada:

<img src="/krux/img/maixpy_amigo/load-mnemonic-options-300.png" class="amigo">
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-options-250.png" class="m5stickv">

## Métodos de generación
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-camera-options-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-camera-options-300.png" align="right" class="amigo">

### Vía Cámara
Puedes usar la cámara para escanear un `código QR`, `Tinyseed`, `OneKey KeyTag` o una  `Cuadrícula Binaria`. Obtén más información sobre estas [copias de seguridad metálicas aquí](../features/tinyseed.md).

----8<----
camera-scan-tips.es.txt
----8<----

<div style="clear: both"></div>

#### Código QR 

Es incómodo tener que introducir manualmente 12 o 24 palabras cada vez que se usa Krux. Para solucionarlo, se puede usar la cámara del dispositivo para leer un código QR que contenga las palabras. Krux decodifica códigos QR de cuatro tipos:

- **Código QR de texto**: Las palabras mnemotécnicas se codifican como texto, separadas por espacios.
- [SeedQR](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md): Básicamente, son las palabras mnemotécnicas de los respectivos números BIP39 concatenadas, codificadas como texto.
- [SeedQR Compacto](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md/#compactseedqr-specification): Básicamente, son los bits de las palabras mnemotécnicas concatenados como bytes.
- [Mnemotécnico Cifrado](../features/encryption/encryption.md/#regarding-bip39-mnemonics): Una especificación creada por Krux que cifra los bits de las palabras mnemotécnicas y añade información sobre el cifrado utilizado.

Tras abrir una billetera mediante uno de los métodos disponibles, puedes usar krux para [copiar la mnemónica](navigating-the-main-menu.md#backup-mnemonic) como código QR, [transcribirla](../features/QR-transcript-tools.md) en papel o metal con las herramientas de transcipción o conectar una impresora térmica a tu Krux e imprimir la mnemónica como código QR. Consulta la [sección de impresión](../features/printing/printing.md) para obtener más información.
También puedes usar un [generador de códigos QR sin conexión para esto](https://iancoleman.io/bip39/) (idealmente en un dispositivo sin conexión a internet).

#### Tinyseed, OneKey KeyTag o Binary Grid
[Tinyseed](https://tinyseed.io/), [Onekey KeyTag](https://onekey.so/products/onekey-keytag/) y otras plataformas codifican directamente una semilla como brinario, lo que permite un almacenamiento mnemónico muy compacto. Los dispositivos Krux cuentan con funciones de visión computacional que permiten a los usuarios escanear estas placas metálicas y cargar instantáneamente los mnemónicos grabados en ellas (esta función no está disponible en la [aplicación Krux Mobile para Android ](../../faq.md#what-is-krux-mobile-android-app)).

Para garantizar un escaneo correcto, coloque la placa de respaldo sobre un fondo negro y rellene las áreas perforadas con negro para mejorar el contraste. Como alternativa, puede escanear una [versión impresa térmicamente](../features/printing/printing.md) o una plantilla completa. Puede ver algunos [ejemplos mnemónicos codificados aquí](../features/tinyseed.md) y explorar nuestras [plantillas de transcipción disponibles aquí](../templates/templates.md).

### Mediante Entrada Manual
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-manual-options-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-manual-options-300.png" align="right" class="amigo">

Escriba manualmente `Palabras`, `Números de palabra`, `Tinyseed` (alternando bits o perforaciones) o [`Stackbit 1248`](https://stackbit.me/produto/stackbit-1248/).

<div style="clear: both"></div>

#### Palabras
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-via-text-word-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-via-text-word-300.png" align="right" class="amigo">

Introduce cada palabra de tu mnemónico BIP39 una a la vez. Krux desactivará las letras que no pueden formar una palabra válida mientras escribes e intentará autocompletar tus palabras para acelerar el proceso.

<div style="clear: both"></div>

#### Números de palabras
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-via-numbers-word-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-via-numbers-word-300.png" align="right" class="amigo">

##### Decimal
Introduce cada palabra de tu mnemónico BIP39 como un número (1-2048), una a la vez. Puedes usar [esta lista](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt) como referencia.

##### Hexadecimal y Octal
También puedes ingresar los números de tu palabra mnemotécnica BIP39 (1-2048) en formato hexadecimal, con valores de 0x1 a 0x800, o en formato octal, con valores de 01 a 04000. Esto es útil con algunas copias de seguridad de placas metálicas que utilizan estos formatos.

<div style="clear: both"></div>

#### Tinyseed (Bits)
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-via-tinyseed-filled-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-via-tinyseed-filled-300.png" align="right" class="amigo">

Introduzca los números (1-2048) de la palabra mnemotécnica BIP39 en formato binario, alternando los bits necesarios para recrear el número correspondiente. La última palabra tendrá bits de suma de comprobación que se alternarán dinámicamente mientras los rellena.

**Consejo**: Puedes usar esta pantalla para generar una mnemotécnica lanzando una moneda:

- Lance una moneda; si sale cara, marque el primer espacio (valor 1) de la palabra; si sale cruz, no haga nada. Repita este paso para cada espacio hasta 1024 (si lanza 11 cruces seguidas, deje marcada la casilla 2048).
- La última palabra tiene la suma de comprobación; haga lo mismo que con las demás palabras; la única diferencia es que algunos espacios no se pueden configurar; se calculan automáticamente. Para 12 palabras, solo lanzará la moneda 7 veces: para los espacios 16, 32, 64, 128, 256, 512 y 1024. Para 24 palabras, solo lanzará la moneda 3 veces: para los espacios 256, 512 y 1024.

<div style="clear: both"></div>

#### Stackbit 1248
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-via-stackbit-filled-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-via-stackbit-filled-300.png" align="right" class="amigo">

Ingresa los números de la palabra mnemotécnica BIP39 (1-2048) usando el método de respaldo en placa metálica Stackbit 1248. En este método, cada uno de los cuatro dígitos del número de la palabra se representa como la suma de los números marcados (perforados) 1, 2, 4 u 8. Por ejemplo, para ingresar la palabra "oyster", cuyo número es 1268, debes perforar (1)(2)(2,4)(8).

<div style="clear: both"></div>

### Desde el almacenamiento
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-storage-options-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-storage-options-300.png" align="right" class="amigo">

También puedes recuperar [mnemónicos cifrados previamente almacenados](./navigating-the-main-menu.md/#encrypted) en la memoria interna o externa (tarjeta SD) del dispositivo. Para cargarlos, deberás ingresar la misma clave que usaste para cifrarlos.

<div style="clear: both"></div>

## Confirmar la configuración de la billetera
### Confirmar palabras mnemotécnicas
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-seq-mnemonic-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-seq-mnemonic-300.png" align="right" class="amigo">

Una vez que haya ingresado su mnemotécnica, se le mostrará la lista completa de palabras para confirmar. Una frase de 12 palabras solo tiene 4 bits de suma de comprobación, por lo que tiene una probabilidad de 1 entre 16 (6,25 %) de seguir siendo válida incluso si escribe mal una palabra. Una frase de 24 palabras tiene 8 bits de suma de comprobación, por lo que tiene una probabilidad de 1 entre 256 (~0,4 %) de seguir siendo válida si escribe mal una palabra.

<div style="clear: both"></div>

<img src="/krux/img/maixpy_m5stickv/load-mnemonic-seq-double-mnemonic-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-seq-double-mnemonic-300.png" align="right" class="amigo">
Si ve un asterisco (`*`) en el encabezado, significa que se trata de un [doble mnemónico](generating-a-mnemonic.md/#double-mnemonic).

<div style="clear: both"></div>

### (Opcional) Editar un Mnemotécnico
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-seq-mnemonic-edited-wrong-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-seq-mnemonic-edited-wrong-300.png" align="right" class="amigo">

Si comete un error al cargar un mnemónico, puede editarlo fácilmente. Simplemente toque o navegue hasta la palabra que desea cambiar y reemplácela. Las palabras editadas se resaltarán. Si la última palabra contiene una suma de comprobación no válida, aparecerá en rojo. Si la palabra de la suma de comprobación está en rojo, revise el mnemónico cuidadosamente, ya que podría haber un error.

<div style="clear: both"></div>

### Confirmar atributos de la billetera
<img src="/krux/img/maixpy_m5stickv/load-mnemonic-seq-overview-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/load-mnemonic-seq-overview-300.png" align="right" class="amigo">

Tras confirmar tu mnemónico, se mostrará una pantalla con un **cuadro de información en la parte superior** mostrando los atributos de la billetera. Si son los esperados, simplemente pulsa `Cargar Billetera`. Si necesitas cambiar algo puedes personalizar la billetera estableciendo una `Contraseña` o usando el boton `Personalizar`.

<div style="clear: both"></div>

#### Atributos:

##### Huella digital
* :material-fingerprint: ` 73c5da0a `:
La huella digital (fingerprint) de la billetera maestra [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) te ayuda a verificar que ingresaste correctamente el mnemónico y la contraseña (opcional), y que se está cargando la billetera esperada. El fingerprint es el mejor checksum que puedes tener, por lo que es muy recomendable anotarlo y guardarlo.

##### Red (Network)
* ` Mainnet `:
Verifica si estás cargando una billetera de `Testnet` o de `Mainnet`.

##### Tipo de política (Policy Type)
* Verifica el tipo de política de la billetera: `Single-sig`, `Multisig`, `Miniscript`, o `TR Miniscript` (Taproot).

##### Camino de derivación (Derivation Path)
* :material-arrow-right-bottom: ` m/84h/0h/0h `:
El camino de derivación es una secuencia de números, o "nodos", que definen el tipo de script, la red y el índice de cuenta de tu billetera.
    * **Tipo de script** `84h`: El primer número define el tipo de script. El valor por defecto es `84h`, que corresponde a una billetera SegWit Nativa. Otros valores incluyen:
        * `44h` para Legacy
        * `49h` para Segwit anidado (Nested SegWit)
        * `86h` para Taproot
        * `48h` para Multisig
    * **Red (Network)** `0h`: El segundo número define la red:
        * `0h` para Mainnet
        * `1h` para Testnet
    * **Indice de cuenta** `0h`: El tercer número corresponde al índice de cuenta, siendo `0h` el valor por defecto.
    * **Adicional**: En billeteras multisig, se agrega un cuarto nodo con el valor `2h` al camino de derivación.

    El camino de derivación por defecto para Miniscript es el mismo que para multisig: ` m/48'/0h/0h/2h `, aunque pueden personalizarse completamente

##### Contraseña
* ` Sin contraseña `:
Informa si la billetera tiene una frase de contraseña. Añadir o cambiar la contraseña genera una billetera y una huella digital completamente diferentes.

### Personalizar billetera
Es posible cambiar cualquiera de los **atributos de la billetera** (también se podrán cambiar más adelante, después de cargarla). Para que cargue más rápido la próxima vez, se pueden configurar algunos atributos predeterminados de la billetera en [ajustes](../settings.md): `Red`, `Tipo de política` y `Tipo de script`.

#### Contraseña
<img src="/krux/img/maixpy_m5stickv/passphrase-load-options-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/passphrase-load-options-300.png" align="right" class="amigo">

Puede escribir o escanear una frase de contraseña BIP39. Al escribir, deslice el dedo hacia la izquierda :material-gesture-swipe-left: o hacia la derecha :material-gesture-swipe-right: para cambiar de teclado si su dispositivo tiene pantalla táctil. También puede mantener pulsado el botón `PAGINA` o `ANTERIOR` al navegar entre las letras mientras escribe texto para avanzar o retroceder rápidamente. Para escanear, también puede crear un código QR a partir de su contraseña sin conexión con la [herramienta Datum](../features/tools.md/#datum-tool).

<div style="clear: both"></div>

#### Personalizar
<img src="/krux/img/maixpy_m5stickv/wallet-customization-options-250.png" align="right" class="m5stickv">
<img src="/krux/img/maixpy_amigo/wallet-customization-options-300.png" align="right" class="amigo">

Este botón abre una pantalla para cambiar la `Red`, `Tipo de Política`, `Tipo de Script`, y la  `Cuenta` de la billetera. Si el `Tipo de Política` es Miniscript, podrá introducir una ruta de derivación personalizada.

<div style="clear: both"></div>

Cuando todo esté correcto, pulsa `Cargar Billetera` y accederás al menú principal...

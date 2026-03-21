Después de ingresar tu mnemónico y cargar una cartera, llegarás al menú principal de Krux. A continuación se muestra un desglose de las opciones disponibles:

<img src="/krux/es/img/maixpy_amigo/home-options-300.png" class="amigo">
<img src="/krux/es/img/maixpy_m5stickv/home-options-250.png" class="m5stickv">

### Respaldo del mnemónico (Backup Mnemonic)
<img src="/krux/es/img/maixpy_m5stickv/backup-options-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/backup-options-300.png" align="right" class="amigo">

Esto abrirá un nuevo submenú con distintos tipos de respaldos. Basados en `Código QR`, `Encriptados` y `Otros Formatos`.

Si configuras una [impresora](../settings.md/#printer), también se habilitará la opción de imprimirlos!

<div style="clear: both"></div>

#### Código QR
- **Código QR en texto plano**

<img src="/krux/es/img/maixpy_m5stickv/backup-qr-plain-text-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/backup-qr-plain-text-300.png" align="right" class="amigo">

Genera un código QR con las palabras mnemotécnicas en texto plano, separadas por espacios. Como cualquier código QR, se puede imprimir tras configurar el controlador de la impresora.

<div style="clear: both"></div>

- **SeedQR Compacto**

<img src="/krux/es/img/maixpy_m5stickv/backup-compact-qr-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/backup-compact-qr-300.png" align="right" class="amigo">

Un código QR se crea a partir de una representación binaria de las palabras mnemotécnicas. Formato creado por SeedSigner; más información [aquí](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md#compactseedqr-specification).

<div style="clear: both"></div>

- **SeedQR**

<img src="/krux/es/img/maixpy_m5stickv/backup-seed-qr-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/backup-seed-qr-300.png" align="right" class="amigo">

Las palabras se convierten a sus indices numéricos BIP39, estos números se concatenan como una cadena de texto y finalmente se convierten en un código QR. Formato creado por SeedSigner, Más información [aquí](https://github.com/SeedSigner/seedsigner/blob/dev/docs/seed_qr/README.md).

<div style="clear: both"></div>

- **Código QR cifrado**

Esta opción convierte la frase mnemotécnica cifrada en un código QR. Introduzca una clave de cifrado y, opcionalmente, un ID personalizado. Al escanear este código QR mediante **Cargar frase mnemotécnica -> Via Cámara -> Código QR**, se le pedirá que introduzca la clave de descifrado para cargar la frase mnemotécnica almacenada en él. Cómo cualquier código QR, se puede imprimir tras configurar el controlador de la impresora.

**Transcripción de códigos QR**

Consulte [Transcripción de códigos QR](../features/QR-transcript-tools.md) para obtener más información sobre los modos de transcripción y las herramientas de ayuda.

#### Encriptado
<img src="/krux/es/img/maixpy_m5stickv/home-encrypt-options-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/home-encrypt-options-300.png" align="right" class="amigo">

Esta función te permite guardar tu mnemónico encriptando y almacenándolo en la memoria flash del dispositivo, en una tarjeta SD o en formato de código QR. Puedes personalizar el método y los parametros de encriptación en [ajustes](../settings.md/#encryption).

Al usar cualquiera de los métodos de encriptación, se te pedirá que introduzcas una clave de encriptación. Esta clave puede proporcionarse en formato de texto o código QR. Además, tienes la opción de establecer un ID personalizado para una gestión más sencilla de tus mnemónicos. Si no se especifica un ID personalizado, se utilizará la huella digital de la cartera cargada actualmente.

**Nota**: La frase mnemotécnica cifrada almacenada solo está protegida por la clave que definiste para cifrarla. Además, se recomienda no depender únicamente de métodos digitales para la copia de seguridad. Consulta la sección de consideraciones en [Cifrado de frases mnemotécnicas de Krux](../features/encryption/encryption.md/#considerations).

- **Almacenar en memoria flash**

Esta opción almacena la frase mnemotécnica cifrada en la memoria flash del dispositivo. Puedes descifrarla y cargarla posteriormente mediante **Cargar frase mnemotécnica -> Desde almacenamiento**.

- **Almacenar en tarjeta SD**

Si hay una tarjeta SD disponible, esta opción almacena la frase mnemotécnica cifrada en ella. Puedes descifrarla y cargarla posteriormente mediante **Cargar frase mnemotécnica -> Desde almacenamiento**.

- **Código QR cifrado**
Esta es otra opción de la misma funcionalidad que las copias de seguridad con código QR, descritas anteriormente.

<div style="clear: both"></div>

#### Otros formatos

- **Palabras**

<img src="/krux/es/img/maixpy_m5stickv/backup-mnemonic-words-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/backup-mnemonic-words-300.png" align="right" class="amigo">

Muestra las palabras mnemotécnicas BIP39 como texto para que puedas anotarlas.

<div style="clear: both"></div>

- **Números**

<img src="/krux/es/img/maixpy_m5stickv/backup-mnemonic-numbers-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/backup-mnemonic-numbers-300.png" align="right" class="amigo">

Muestra los números de la palabra mnemotécnica BIP39 (1-2048) en formato decimal, hexadecimal u octal.

<div style="clear: both"></div>

- **Stackbit 1248**

<img src="/krux/es/img/maixpy_m5stickv/backup-stackbit-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/backup-stackbit-300.png" align="right" class="amigo">

Este formato de copia de seguridad metálica representa los números de la palabra mnemotécnica BIP39 (1-2048). Cada uno de los cuatro dígitos se convierte en una suma de 1, 2, 4 u 8. Esta opción no imprime, incluso si hay un controlador de impresora configurado.

<div style="clear: both"></div>

- **Tinyseed**

<img src="/krux/es/img/maixpy_m5stickv/backup-tiny-seed-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/backup-tiny-seed-300.png" align="right" class="amigo">

Este formato de copia de seguridad metálica representa los numeros de la palabra mnemotécnica BIP39 (1-2048) en formato binario sobre una placa metálica, donde los 1 están marcados (perforados) y los 0 se dejan intactos. también puedes imprimir tu palabra mnemotécnica en este formato después de configurar el controlador de la impresora térmica.
<div style="clear: both"></div>

### Clave pública extendida

Se mostrará un menú con opciones para visualizar su clave pública extendida maestra (xpub) como texto y como código QR. Dependiendo del tipo de script o de si se cargó una cartera de firma simple o multifirma, las opciones mostradas serán *xpub, ypub, zpub o Zpub*. Al mostrarse como texto, la clave pública extendida se puede almacenar en una tarjeta SD, si está disponible. Si elige exportar un código QR, no solo podrá escanearlo, sino también guardarlo como imagen en una tarjeta SD o imprimirlo, después de configurar el controlador de la impresora.

<img src="/krux/es/img/maixpy_amigo/extended-public-key-menu-300.png" class="amigo">
<img src="/krux/es/img/maixpy_amigo/extended-public-key-wsh-xpub-text-300.png" class="amigo">
<img src="/krux/es/img/maixpy_amigo/extended-public-key-wsh-xpub-qr-300.png" class="amigo">
<img src="/krux/es/img/maixpy_m5stickv/extended-public-key-menu-250.png" class="m5stickv">
<img src="/krux/es/img/maixpy_m5stickv/extended-public-key-wsh-xpub-text-250.png" class="m5stickv">
<img src="/krux/es/img/maixpy_m5stickv/extended-public-key-wsh-xpub-qr-250.png" class="m5stickv">

Todos los códigos QR incluirán [información de origen de la clave en las expresiones de la clave](https://github.com/bitcoin/bips/blob/master/bip-0380.mediawiki#Key_Expressions). Si su Coordinador de Cartera no puede analizar esta información, no podrá importar la huella digital de la cartera. En consecuencia, Krux no realizará verificaciones importantes al firmar transacciones *PSBT* creadas por este Coordinador de Cartera, a menos que agregue manualmente la huella digital en el coordinador.

Siempre es preferible importar las claves públicas extendidas directamente desde Krux al configurar una cartera coordinadora, en lugar de copiarlas (o parte de ellas) de otras fuentes.

Algunos coordinadores están eliminando gradualmente la compatibilidad con variantes como ypub y zpub en favor de xpub, que incluyen datos de origen de la clave. Por lo tanto, recomendamos usar *xpub* únicamente.

### Cartera (Wallet)

<img src="/krux/es/img/maixpy_m5stickv/wallet_home_options-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/wallet_home_options-300.png" align="right" class="amigo">

Aquí puedes cargar, ver y guardar el `Descriptor de la cartera`, también puedes personalizarla estableciendo una `Contraseña` o cambiando otros atributos con el botón `Personalizar`. Es posible calcular la entropia `BIP85` para el `Mnemónico BIP39` y la `Contraseña Base64`.

<div style="clear: both"></div>

#### Descriptor de la cartera

Un descriptor de script de salida de una cartera Bitcoin (también conocido como un descriptor de cartera) codifica detalles esenciales como:

- **Script**: Especifica el tipo de script (*P2PKH, P2SH, P2WPKH, P2TR, ..*). En el caso de miniscript, define políticas y condiciones avanzadas de gasto.
- **Información de Origen**: Para cada clave, incluye la *huella digital maestra (master fingerprint)* correspondiente y  la *ruta de derivación (derivation path)* utilizada para derivarla.
- **Claves públicas extendidas**: Contiene una o más claves públicas extendidas (*xpub, ypub, zpub, ..*), cada una asociada a su propia información de origen.

Los descriptores de salida estandarizan la generación de direcciones de la cartera, garantizando una restauración precisa desde respaldos y compatibilidad entre distintas aplicaciones.

En carteras multisig y miniscript, cargar un descriptor de cartera es esencial para verificar direcciones y realizar las validaciones *PSBT*. En carteras de firma única (single-sig), sigue siendo opcional y funciona como una comprobación redundante de los atributos de la cartera definidos por el coordinador.

<img src="/krux/es/img/maixpy_m5stickv/wallet-wsh-load-prompt-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/wallet-wsh-load-prompt-300.png" align="right" class="amigo">

Al seleccionar la opción `Descriptor de cartera` por primera vez, se le pedirá que cargue la clave mediante código QR o tarjeta SD. Tras la carga, se mostrará una vista previa de los atributos del descriptor para su confirmación. Mostramos la huella digital, la ruta de derivación y el XPUB abreviado de cada clave resaltados con un color diferente.

Cargar un descriptor también es una forma rápida de configurar los atributos de la cartera, ya que toda la información necesaria se extrae automáticamente:
- Red (Mainnet or Testnet)
- Tipo de póliza (firma única, multisig o miniscript)
- Tipo de Script (Segwit nativo, Taproot, Segwit anidado, Legacy)

Esto elimina la necesidad de configuración manual y garantiza la coherencia con su cartera coordinadora.

<div style="clear: both"></div>

Los **Descriptores de miniscript** muestran una vista indentada del miniscript después de las claves. Cuando se utiliza Taproot, Krux verifica si la clave interna es “demostrablemente no gastable” (provably unspendable), lo que significa que los fondos solo pueden gastarse mediante scripts del árbol Taproot (Tap tree). En ese caso, la clave interna se muestra con un color deshabilitado.

<img src="/krux/es/img/maixpy_amigo/wallet-descriptor-tr-minis-1-300.png" class="amigo">
<img src="/krux/es/img/maixpy_amigo/wallet-descriptor-tr-minis-2-300.png" class="amigo">
<img src="/krux/es/img/maixpy_m5stickv/wallet-descriptor-tr-minis-1-250.png" class="m5stickv">
<img src="/krux/es/img/maixpy_m5stickv/wallet-descriptor-tr-minis-2-250.png" class="m5stickv">
<img src="/krux/es/img/maixpy_m5stickv/wallet-descriptor-tr-minis-3-250.png" class="m5stickv">

Vuelva a acceder a la opción "Descriptor de la Cartera" después de cargar su Cartera para ver su nombre y un código QR con los datos cargados originalmente. Si inserta una tarjeta SD, puede guardar el descriptor para usarlo posteriormente sin la ayuda de un coordinador. Como cualquier código QR, puede imprimirlo después de configurar el controlador de la impresora.

Krux también le permite verificar las direcciones de recepción y cambio de un descriptor sin necesidad de cargar claves privadas. Simplemente encienda su Krux, acceda a **Herramientas -> Direcciones del Descriptor** y cargue un descriptor de confianza desde un código QR o una tarjeta SD.

Tenga en cuenta que si personaliza los parámetros de la Cartera o reinicia el dispositivo, el descriptor se descargará y es posible que deba cargarlo nuevamente para verificar las direcciones.

#### Contraseña
<img src="/krux/es/img/maixpy_m5stickv/passphrase-load-options-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/passphrase-load-options-300.png" align="right" class="amigo">

Si olvidaste ingresar una contraseña al cargar tu billetera, o si usas varias contraseñas con la misma frase mnemotécnica, puedes agregar, reemplazar o eliminar una contraseña aquí. Simplemente elige entre escribirla o escanearla.

Para eliminar una contraseña, selecciona `Ingresar contraseña BIP39`, deja el campo en blanco y presiona `Ir`.

No olvides verificar la huella digital resultante en la barra de estado para asegurarte de haber ingresado la clave correcta.

<div style="clear: both"></div>

#### Personalizar
<img src="/krux/es/img/maixpy_m5stickv/wallet-customization-options-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/wallet-customization-options-300.png" align="right" class="amigo">

Aquí se presentan las mismas opciones de personalización que al cargar una mnemotécnica. Puede cambiar `Red`, `Tipo de póliza`, `Tipo de script` y `Cuenta`. En la página Cargar una frase mnemónica ya se detallan [los atributos de la cartera](./loading-a-mnemonic.md/#confirm-wallet-attributes).

<div style="clear: both"></div>

#### BIP85

<img src="/krux/es/img/maixpy_m5stickv/bip85-options-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/bip85-options-300.png" align="right" class="amigo">

Bitcoin *BIP85* (también conocido como Deterministic Entropy From BIP32 Keychains) permite generar entropía determinística a partir de una clave maestra BIP32. Esta entropía puede utilizarse posteriormente para crear diversas claves criptográficas y mnemónicos (por ejemplo, frases semilla BIP39). BIP85 garantiza que todas las claves y mnemónicos derivados sean determinísticos y reproducibles, lo que significa que pueden volver a generarse a partir de la misma clave maestra. Esta funcionalidad es útil para gestionar de forma segura múltiples claves hijas a partir de una única clave maestra, sin necesidad de almacenar cada una por separado.

<div style="clear: both"></div>

##### Mnemónico BIP39

<img src="/krux/es/img/maixpy_amigo/bip85-child-index-300.png" class="amigo">
<img src="/krux/es/img/maixpy_amigo/bip85-load-child-300.png" class="amigo">
<img src="/krux/es/img/maixpy_m5stickv/bip85-child-index-250.png" class="m5stickv">
<img src="/krux/es/img/maixpy_m5stickv/bip85-load-child-250.png" class="m5stickv">

Elige entre *12 o 24 palabras* y luego escribe el *index* deseado para exportar un *mnemónico secundario*. Una vez que veas el nuevo mnemónico, puedes cargarlo y usarlo de inmediato.

**Aviso**: Cualquier contraseña del mnemónico principal se eliminará al cargar un *mnemónico secundario* de BIP85.

##### Contraseña Base64

<img src="/krux/es/img/maixpy_amigo/bip85-password-len-300.png" class="amigo">
<img src="/krux/es/img/maixpy_amigo/bip85-password-created-300.png" class="amigo">
<img src="/krux/es/img/maixpy_m5stickv/bip85-password-len-250.png" class="m5stickv">
<img src="/krux/es/img/maixpy_m5stickv/bip85-password-created-250.png" class="m5stickv">

Para crear una *contraseña Base64*, que se puede usar para iniciar sesión en diversos sistemas, desde correo electrónico hasta redes sociales, elige un índice y una longitud de al menos 20 caracteres. La contraseña resultante se mostrará en pantalla y también se puede exportar a una tarjeta SD o código QR.

#### Mnemónico XOR
<img src="/krux/es/img/maixpy_m5stickv/xor-message-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/xor-message-300.png" align="right" class="amigo">

El Mnemónico XOR permite **combinar dos o más mnemónicos** aplicando una operación XOR (exclusive OR) a sus bytes de entropía, **generando un nuevo mnemónico**. Esta funcionalidad puede utilizarse para dividir un mnemónico en múltiples partes (o “fragmentos” / shares) o para combinar mnemónicos existentes.

Para obtener instrucciones detalladas sobre cómo combinar, dividir y recuperar mnemónicos mediante XOR, consulta [Mnemonic XOR](../features/mnemonic-xor.md).

<div style="clear: both"></div>

### Dirección
<img src="/krux/es/img/maixpy_m5stickv/address-menu-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/address-menu-300.png" align="right" class="amigo">

Escanee, liste, exporte o imprima las direcciones de su billetera.

<div style="clear: both"></div>

#### Escanear dirección
<img src="/krux/es/img/maixpy_m5stickv/scan-address-scanned-address-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/scan-address-scanned-address-300.png" align="right" class="amigo">

Esta opción activa la cámara y te permite escanear el código QR de una dirección. Al escanearla, mostrará el código QR en la pantalla junto con la dirección.

**Consejo**: Puedes usar esta función para escanear la dirección de alguien a quien quieras enviar monedas y mostrar el código QR a tu Coordinador de Cartera en lugar de copiar y pegar la dirección. Como cualquier código QR, puedes imprimirlo después de configurar el controlador de la impresora.

Después, se te preguntará si quieres verificar que la dirección pertenece a tu cartera. Si confirmas, buscará exhaustivamente entre las direcciones derivadas de tu cartera para encontrar una coincidencia. Esta es una verificación de seguridad adicional para comprobar que la dirección generada por el Coordinador de Cartera es auténtica y pertenece a tu cartera.

<div style="clear: both"></div>

#### Lista de direcciones
<img src="/krux/es/img/maixpy_m5stickv/list-address-receive-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/list-address-receive-300.png" align="right" class="amigo">

Muestra las *direcciones de recepción y de cambio* de tu cartera. Puedes seleccionar cualquier dirección para ver su código QR e imprimirla si lo deseas.

<div style="clear: both"></div>

#### Exportar Direcciones
<img src="/krux/es/img/maixpy_m5stickv/export-address-quantity-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/export-address-quantity-300.png" align="right" class="amigo">

Exporta las *direcciones de recepción y de cabmio* de tu cartera a partir de un *índice* y *cantidad* seleccionados a un archivo CSV en tu tarjeta SD.

<div style="clear: both"></div>

### Firma
<img src="/krux/es/img/maixpy_m5stickv/sign-options-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/sign-options-300.png" align="right" class="amigo">

Aquí puedes elegir firmar un *PSBT* o un *Mensaje*. Puedes cargarlos escaneando códigos QR o seleccionando un archivo de una tarjeta SD.

<div style="clear: both"></div>

#### PSBT
<img src="/krux/es/img/maixpy_m5stickv/sign-psbt-from-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/sign-psbt-from-300.png" align="right" class="amigo">

Para firmar un *PSBT* de Bitcoin, tienes las siguientes opciones:

- `Cargar desde la cámara`: Usa la cámara para escanear un código QR animado de un *PSBT* generado por el software de una cartera coordinadora. Si tienes algún problema, consulta [Solución de problemas](../../troubleshooting.md/#why-isnt-krux-scanning-the-qr-code).
- `Cargar desde la tarjeta SD`: Carga un archivo *PSBT* desde tu tarjeta SD.

<div style="clear: both"></div>

<img src="/krux/es/img/maixpy_m5stickv/sign-psbt-info-1-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/sign-psbt-info-1-300.png" align="right" class="amigo">

Al cargar el *PSBT* sin firmar, se mostrará una vista previa de la transacción, que incluye:

- Cuántas **Entradas** (inputs / UTXO) están involucradas y el monto en BTC.
- Cuántos **Gastos** (spend; direcciones que *no pertenecen* a tu cartera) y el monto en BTC.
- Cuántas **Autotransferencias o Cambio** (self-transfer or change; direcciones que *pertenecen* a tu cartera) y el monto en BTC.
- Cuánta **Comisión** (fee) se está pagando, el porcentaje relativo a lo enviado y una aproximación en sat/vB (no disponible si el `Policy Type` es Miniscript).

Los montos se muestran de acuerdo con tu configuración regional y las normas de la Oficina Internacional de Pesas y Medidas, manteniendo al mismo tiempo el concepto del [formato estándar Satcomma](https://medium.com/coinmonks/the-satcomma-standard-89f1e7c2aede).

<div style="clear: both"></div>

<img src="/krux/es/img/maixpy_m5stickv/sign-psbt-sign-prompt-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/sign-psbt-sign-prompt-300.png" align="right" class="amigo">

Luego puedes elegir entre revisar la PSBT o continuar con una de las siguientes opciones de firma:

- `Revisar`: Vuelve a mostrar una vista previa de la *PSBT* - incluyendo entradas, salidas (envío, autotransferencia o cambio) y comisión.
- `Firmar en Código QR`: Muestra el *PSBT* firmado como un código QR animado, listo para ser escaneado por tu cartera coordinadora.
- `Firmar en Tarjeta SD`: Guarda el archivo *PSBT* firmado en tu tarjeta SD para importarlo posteriormente a tu cartera coordinadora.

**Consejo**: Si hay una impresora térmica conectada al dispositivo, también puedes imprimir los códigos QR de la *PSBT* para escanearlos o procesarlos más tarde.

<div style="clear: both"></div>

#### Mensaje
Al igual que con los *PSBT*, Krux puede cargar, firmar y exportar firmas para *mensajes*. Esta función te permite certificar no solo la propiedad de los *mensajes* en sí, sino también la propiedad de las direcciones Bitcoin y la autoría de documentos y archivos.

- **Mensajes y archivos estándar**

<img src="/kru/es/img/maixpy_m5stickv/sign-message-sha256-sign-prompt-250.png" align="right" class="m5stickv">
<img src="/kru/es/img/maixpy_amigo/sign-message-sha256-sign-prompt-300.png" align="right" class="amigo">

Puedes escanear o cargar un archivo desde una tarjeta SD. El contenido puede ser texto plano o el hash SHA-256 de un mensaje. Al cargarlo, verás una vista previa del hash SHA-256 *del mensaje* para confirmar antes de firmar.

Si confirma, se generará una firma y verá una versión codificada en base64. Podrá exportarla como código QR o guardarla en una tarjeta SD. Si dispone de una impresora térmica, también podrá imprimir el código QR.

A continuación, verá y podrá exportar su clave pública (maestra) en formato hexadecimal, que otros podrán usar para verificar su firma. Si dispone de una impresora térmica, también podrá imprimir este código QR.

Esta función se utiliza para firmar versiones de Krux, aisladas de la red, mediante un dispositivo Krux.

<div style="clear: both"></div>

- **Firma de mensajes en una dirección**

<img src="/krux/es/img/maixpy_m5stickv/sign-message-at-address-prompt-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/sign-message-at-address-prompt-300.png" align="right" class="amigo">

Coordinadores como Sparrow y Specter permiten firmar *mensajes* asociados a una dirección de recepción de Bitcoin, lo que te permite demostrar que controlas esa dirección. Krux detectará si el *mensaje* es de este tipo y mostrará un flujo de firma similar. La principal diferencia es que se mostrará la dirección junto con el *mensaje* en bruto y, como el *mensaje* se firma con la clave derivada correspondiente a esa dirección en lugar de la clave pública maestra, Krux no ofrecerá la opción de exportar la clave pública en bruto después de la firma.

<div style="clear: both"></div>

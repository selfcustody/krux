Una vez que hayas generado una frase mnemotécnica, respaldado una copia de seguridad y probado con éxito el proceso de recuperación, estará listo para configurar un coordinador (una cartera coordinadora).

Krux funciona con:

- [Sparrow Wallet](https://www.sparrowwallet.com/) (computador)
- [Specter Desktop](https://specter.solutions/) (computador)
- [Liana](https://wizardsardine.com/liana/) (computador)
- [Bitcoin Safe](https://bitcoin-safe.org/) (computador)
- [Nunchuk](https://nunchuk.io/) (móvil)
- [BlueWallet](https://bluewallet.io/) (móvil)
- [Bitcoin Keeper](https://bitcoinkeeper.app/) (móvil)
- [BULL Wallet](https://wallet.bullbitcoin.com) (móvil)

## Paso 1: Instalar la Cartera del Coordinador

Descarga e instala la versión adecuada de la cartera del coordinador que hayas elegido para tu dispositivo y sistema operativo.

## Paso 2: Crea una Nueva Cartera con Krux como Firmante

Los pasos para añadir Krux como firmante pueden variar ligeramente según el coordinador:

- **Specter y Nunchuk Single-sig:** Añade la clave de Krux y crea una cartera que la utilice.
- **Specter y Nunchuk Multisig:** Añade la clave de Krux, añade otras claves y crea una cartera que las utilice.
- **Sparrow, Liana, Bitcoin Safe y BlueWallet**: Crea una cartera (o bóveda en BlueWallet) y añade las claves durante la configuración.
- **Bitcoin Keeper**: Añade una cartera -> Crea una cartera, selecciona clave única o multiclave y añade la(s) clave(s). O bien, añade la(s) clave(s), luego añade una cartera -> Crea una cartera y selecciona la(s) clave(s).
<!-- -->

1. Carga una frase mnemotécnica y una cartera en Krux.

    <img src="/krux/es/img/maixpy_amigo/load-mnemonic-seq-mnemonic-300.png" class="amigo">
    <img src="/krux/es/img/maixpy_amigo/load-mnemonic-seq-overview-300.png" class="amigo">
    <img src="/krux/es/img/maixpy_m5stickv/load-mnemonic-seq-mnemonic-250.png" class="m5stickv">
    <img src="/krux/es/img/maixpy_m5stickv/load-mnemonic-seq-overview-250.png" class="m5stickv">

2. En tu cartera coordinadora, selecciona **"Krux"** si aparece entre los dispositivos firmantes disponibles. De lo contrario, elige **"Other"** o un firmante compatible con códigos QR, como **"SeedSigner"**. Dado que Krux admite varios formatos QR, es posible que otras opciones disponibles también sean compatibles.

3. Cuando tu coordinador te solicite importar la clave pública del firmante, accede a la opción `Clave Pública Extendida` en Krux.

    <img src="/krux/es/img/maixpy_amigo/extended-public-key-selected-300.png" class="amigo">
    <img src="/krux/es/img/maixpy_m5stickv/extended-public-key-selected-250.png" class="m5stickv">

4. Exporta un archivo *XPUB* (o *YPUB, ZPUB*, etc., según el tipo de script) como código QR.

    <img src="/krux/es/img/maixpy_amigo/extended-public-key-xpub-qr-menu-selected-300.png" class="amigo">
    <img src="/krux/es/img/maixpy_amigo/extended-public-key-wsh-xpub-qr-300.png" class="amigo">
    <img src="/krux/es/img/maixpy_m5stickv/extended-public-key-xpub-qr-menu-selected-250.png" class="m5stickv">
    <img src="/krux/es/img/maixpy_m5stickv/extended-public-key-wsh-xpub-qr-250.png" class="m5stickv">

5. Escanee este código QR con su coordinador.
6. Asegúrece de que los atributos de la cartera del coordinador (tipo de póliza, tipo de script, huella digital y derivación) coincidan con los de Krux.

Como alternativa, puede exportar las claves públias extendidas como archivos a una tarjeta SD. En lugar de mostrarlas como códigos QR, seleccione la opción `XPUB - Texto` y, a continuación elija `Guardar en Tarjeta SD`.

<img src="/krux/es/img/maixpy_amigo/extended-public-key-menu-300.png" class="amigo">
<img src="/krux/es/img/maixpy_amigo/extended-public-key-wsh-xpub-text-300.png" class="amigo">
<img src="/krux/es/img/maixpy_m5stickv/extended-public-key-menu-250.png" class="m5stickv">
<img src="/krux/es/img/maixpy_m5stickv/extended-public-key-wsh-xpub-text-250.png" class="m5stickv">

## Paso 3: Cargar y hacer una copia de seguridad del descriptor de la cartera (Solo Multifirma)

1. En su coordinador, exporte el descriptor de la cartera que contiene información sobre la cartera y todos los cosignatarios:
    - **Sparrow**: "Descriptor"
    - **Specter**: "Exportar Cartera"
    - **Liana**: "Descriptor de Cartera"
    - **Bitcoin Safe**: "Registrar multifirma en los firmantes" en el paso 6 o "Descriptor de Cartera"
    - **Nunchuk**: "Exportar Configuración de Cartera"
    - **BlueWallet**: "Exportar Configuración de Coordinación"
    - **Bitcoin Keeper**: "Archivo de configuración de cartera"

2. Exporta el descriptor como código QR o archivo.
3. En Krux, ve a **Cartera -> Descriptor de Cartera** para escanear el código QR del descriptor o cargarlo mediante tarjeta SD.

<img src="/krux/es/img/maixpy_amigo/wallet-load-prompt-300.png" class="amigo big">
<img src="/krux/es/img/maixpy_amigo/wallet-wsh-load-prompt-300.png" class="amigo big">
<img src="/krux/es/img/maixpy_m5stickv/wallet-load-prompt-250.png" class="m5stickv big">
<img src="/krux/es/img/maixpy_m5stickv/wallet-wsh-load-prompt-250.png" class="m5stickv big">

4. Si accedes de nuevo a **Cartera -> Descriptor de Cartera**, podrás:
    - Consultar los cosignatarios de la Cartera.
    - Guardar el descriptor en una tarjeta SD (útil si lo cargaste inicialmente desde códigos QR).
    
    **Consejo**: Tener una copia de seguridad del descriptor de la cartera es esencial para recuperarla.

## Paso 4: Verificar Direcciones

<img src="/krux/es/img/maixpy_m5stickv/list-address-receive-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/list-address-receive-300.png" align="right" class="amigo">

Para firmas simples o múltiples (después de cargar un descriptor):

- Ve a `Dirección` en Krux.
- Consulta `Direcciones de recepción` y `Direcciones de cambio` o usa `Escanear dirección` para verificar si Krux reconoce las direcciones de tu coordinador.

<div style="clear: both"></div>

## Paso 5: Depositar fondos en tu cartera

Una vez verificadas las direcciones, envía una pequeña cantidad de prueba a tu cartera. Prueba a firmar y enviar una transacción antes de añadir más fondos.

## Paso 6: Firmar PSBT y mensajes 

### PSBTs

1. Crea una transacción en tu coordinador.

2. Exporta la transacción como un código QR.

3. En Krux, ve a  **Firmar -> PSBT -> Cargar desde la cámara**.

4. Escanea el código QR animado.

5. Verifica los detalles de la transacción.

6. Si son correctos, pulsa `Firmar en código QR`.

7. Escanea el código QR de la transacción firmada en el coordinador para transmitirla.

Alternativamente, puedes usar una tarjeta SD:

Guarda la transacción como un archivo en una tarjeta SD. En Krux, ve a **Firmar -> PSBT -> Cargar desde tarjeta SD** y pulsa `Firmar en tarjeta SD`. Carga la transacción firmada en el coordinador y transmítela.

### Mensajes

<img src="/krux/es/img/maixpy_m5stickv/sign-message-at-address-prompt-250.png" align="right" class="m5stickv">
<img src="/krux/es/img/maixpy_amigo/sign-message-at-address-prompt-300.png" align="right" class="amigo">

Algunos coordinadores, como Sparrow, permiten firmar mensajes vinculados a las direcciones de tu billetera. Firmar y verificar la firma de un mensaje certifica la propiedad de una dirección y sirve como prueba adicional de tu configuración.

<div style="clear: both"></div>
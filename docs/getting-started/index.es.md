<img src="../img/krux-devices.jpg" style="width: 40%; min-width: 260px;" class="align-right">

Krus es un programa de código abierto para firmar transacciones de Bitcoin, diseñado para dispositivos con el chip K210; también conocido como un dispositivo firmador. 

La firma de transacciones en Krux se realizan sin conexión a internet, mediante un código QR o una tarjeta SD utilizando la funcionalidad [PSBT](https://bitcoinops.org/en/topics/psbt/). Puedes crear/cargar tu [semilla mnemotécnica BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki), o importar un descriptor de billetera, y firmar transacciones sin tener que conectar el dispositivo a la computadora (excepto para la instalación inicial del programa). El equipo lee códigos QR con su cámara y los muestra en su pantalla o en papel mediante un [accesorio de impresora térmica](../getting-started/features/printing/printing.md). 

Krus funciona sin conexión a internet, por lo cual nunca gestiona la difusión de la transacción PSBT. En su lugar, puedes utilizar Krux con billeteras externas para enviar las transacciones desde tu computadora o dispositivo móbil conectado, manteniendo siempre tus claves privadas fuera de linea. 

Estas son billeteras externas actualmente **compatibles con Krux**:

- [Sparrow Wallet](https://www.sparrowwallet.com/) (computador)
- [Specter Desktop](https://specter.solutions/) (computador)
- [Liana](https://wizardsardine.com/liana/) (computador)
- [Bitcoin Safe](https://bitcoin-safe.org/) (computador)
- [Nunchuk](https://nunchuk.io/) (móbil)
- [BlueWallet](https://bluewallet.io/) (móbil)
- [Bitcoin Keeper](https://bitcoinkeeper.app/) (móbil)

**Advertencia!** Krux es INCOMPATIBLE con:

- [Electrum Bitcoin Wallet](https://electrum.org/) (computador / móbil - error 'no es posible firmar') 

<div style="clear: both"></div>
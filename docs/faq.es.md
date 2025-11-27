## ¿Es Krux una billetera electrónica (hardware wallet)?
El término "billetera electrónica" suele referirse a dispositivos diseñados específicamente para almacenar llaves privadas y firmar transacciones. Estos dispositivos normalmente incluyen componentes de seguridad dedicados, como chips de elemento seguro (secure element chips).

Krux fue desarrollado inicialmente como un firmador (signer), funcionando exclusivamente en modo amnésico, lo que significa que el usuario debe cargar sus llaves cada vez que enciende el dispositivo. Sin embargo, Krux ha evolucionado y ahora ofrece la opción de almacenar frases mnemonicas (semillas), de manera similar a las billeteras de hardware tradicionales. Estas semillas mnemonicas pueden guardarse en la memoria interna del dispositivo o en tarjetas SD.

Krux no incluye chips de seguridad física (secure elements). La protección de los datos almacenados depende del cifrado. Puedes leer más sobre este tema en: [Krux Encryption - Regarding BIP39 Mnemonics](getting-started/features/encryption/encryption.md/#regarding-bip39-mnemonics).

**Nota**: Débido a la fragilidad inherente de los componentes electrónicos, no utilices tu dispositivo Krux ni una tarjeta SD cifrada como único método de respaldo. Mantén siempre una copia física adicional de seguridad.

## ¿Qué es la versión de prueba (beta)?
La versión de prueba o beta incluye las funciones más nuevas y experimentales, que ocasionalmente compartimos en nuestras redes sociales. el programa se encuentra exclusivamente en el [repositoro de pruebas (beta)](https://github.com/odudex/krux_binaries). Puedes usar o instalar ("flashear") el programa beta si tienes curiosidad por probar nuevas funciones o deseas participar en el proceso de desarrollo, ayudando a encontrar errores (bugs), enviando comentarios o compartiendo ideas en los grupos de Telegram y otras plataformas sociales.

Solo recuerda que para el uso habitual, se recomienda utilizar siempre las versiones oficiales, que están firmadas, completamente probadas y bien documentadas. 

## ¿Qué es la aplicación móvil Krux para Android?

### ¿Dónde puedo encontrarla?
La aplicación Krux Mobile para Android se encuentra en la fase beta y esta disponible como archivo APK en [KruxMobileApp](https://github.com/selfcustody/KruxMobileApp). Requiere Android 6.0 o superior.

### ¿Cómo se instala?
El archivo APK no está disponible en la Play Store. Puedes descargarlo directamente o transferirlo a tu dispositivo Android mediante una tarjeta SD o cable USB.
Para instalarlo, es posible que debas habilitar la opción de permitir instalaciones desde fuentes desconocidas en la configuración de tu teléfono.

### ¿Es segura de usar?
La app Krux Mobile está diseñada con fines educativos, para aprender sobre Krux y las transacciones desconectadas de Internet en Bitcoin.
Debido a las múltiples vulnerabilidades posibles en los teléfonos inteligentes —como la falta de control sobre el sistema operativo, las bibliotecas o el hardware—, **no se recomienda usar** la app para manejar billeteras con ahorros reales **ni claves importantes**.

Para una gestión segura de tus llaves, usa siempre **un dispositivo dedicado exclusivamente** a ese propósito.

